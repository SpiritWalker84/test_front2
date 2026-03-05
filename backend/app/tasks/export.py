import asyncio
import io
import zipfile
from uuid import UUID

from app.core.config import get_settings
from app.core.database import AsyncSessionLocal
from app.models.carousel import Carousel
from app.models.design_settings import DesignSettings
from app.models.slide import Slide
from app.services.export_service import ExportService
from app.storage.s3 import S3Storage

settings = get_settings()

# Jinja2 for HTML templates
try:
    from jinja2 import Environment, PackageLoader, select_autoescape
    env = Environment(
        loader=PackageLoader("app", "templates"),
        autoescape=select_autoescape(["html"]),
    )
    slide_tpl = env.get_template("slide.html")
except Exception:
    slide_tpl = None


def _render_slide_html(slide: Slide, design: DesignSettings) -> str:
    if not slide_tpl:
        return _fallback_slide_html(slide, design)
    return slide_tpl.render(
        title=slide.title or "",
        body=slide.body or "",
        footer=slide.footer or "",
        design=design,
        viewport_width=settings.export_viewport_width,
        viewport_height=settings.export_viewport_height,
    )


def _fallback_slide_html(slide: Slide, design: DesignSettings) -> str:
    bg = design.bg_color or "#ffffff"
    if design.bg_type == "image" and design.bg_image_url:
        bg = f'url({design.bg_image_url})'
    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ width: {settings.export_viewport_width}px; height: {settings.export_viewport_height}px;
  background: {bg}; display: flex; flex-direction: column;
  padding: {design.padding}px; font-family: sans-serif; }}
h1 {{ font-size: 28px; margin-bottom: 16px; }}
p {{ font-size: 18px; line-height: 1.5; flex: 1; }}
.footer {{ font-size: 14px; color: #666; }}
</style></head><body>
<h1>{slide.title or ""}</h1>
<p>{slide.body or ""}</p>
<div class="footer">{slide.footer or ""}</div>
</body></html>"""


async def _screenshot_html(html: str, width: int, height: int) -> bytes:
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        return b""
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox"],
        )
        page = await browser.new_page(viewport={"width": width, "height": height})
        await page.set_content(html, wait_until="networkidle")
        png = await page.screenshot(type="png")
        await browser.close()
        return png


async def run_export_task(export_id: UUID) -> None:
    async with AsyncSessionLocal() as session:
        exp_svc = ExportService(session)
        exp = await exp_svc.get_export(export_id)
        if not exp:
            return
        carousel = await exp_svc.get_carousel_with_slides_and_design(exp.carousel_id)
        if not carousel or not carousel.slides:
            await exp_svc.set_export_failed(export_id, "No slides or carousel not found")
            await session.commit()
            return

        design = carousel.design_settings
        if not design:
            await exp_svc.set_export_failed(export_id, "No design settings")
            await session.commit()
            return

        exp.status = "running"
        await session.commit()

    slides_list = list(carousel.slides)
    design = carousel.design_settings

    try:
        width = settings.export_viewport_width
        height = settings.export_viewport_height
        buffers: list[tuple[int, bytes]] = []

        for slide in slides_list:
            html = await asyncio.to_thread(
                _render_slide_html,
                slide,
                design,
            )
            png = await _screenshot_html(html, width, height)
            if png:
                buffers.append((slide.order, png))

        if not buffers:
            async with AsyncSessionLocal() as session:
                await ExportService(session).set_export_failed(
                    export_id, "Screenshot failed (playwright not available?)"
                )
                await session.commit()
            return

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            for order, png in sorted(buffers, key=lambda x: x[0]):
                zf.writestr(f"slide_{order:02d}.png", png)
        zip_buffer.seek(0)

        storage = S3Storage()
        zip_url = storage.upload_sync(
            f"exports/{export_id}.zip",
            zip_buffer.read(),
            "application/zip",
        )

        async with AsyncSessionLocal() as session:
            await ExportService(session).set_export_done(export_id, zip_url)
            await session.commit()
    except Exception as e:
        async with AsyncSessionLocal() as session:
            await ExportService(session).set_export_failed(export_id, str(e))
            await session.commit()
