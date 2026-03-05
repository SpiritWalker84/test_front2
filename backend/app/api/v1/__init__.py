from fastapi import APIRouter

from app.api.v1 import carousels, slides, generations, design, assets, exports, config_check

api_router = APIRouter()

api_router.include_router(config_check.router, tags=["config"])
api_router.include_router(carousels.router, prefix="/carousels", tags=["carousels"])
api_router.include_router(slides.router, prefix="/carousels", tags=["slides"])
api_router.include_router(generations.router, prefix="/generations", tags=["generations"])
api_router.include_router(design.router, prefix="/carousels", tags=["design"])
api_router.include_router(assets.router, prefix="/assets", tags=["assets"])
api_router.include_router(exports.router, prefix="/exports", tags=["exports"])
