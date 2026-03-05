export default defineNuxtConfig({
  compatibilityDate: "2024-11-01",
  modules: ["@pinia/nuxt"],
  runtimeConfig: {
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE || "http://localhost:8000",
    },
  },
  app: {
    head: {
      title: "Carousel MVP",
      meta: [{ charset: "utf-8" }, { name: "viewport", content: "width=device-width, initial-scale=1" }],
    },
  },
  css: ["~/assets/main.css"],
});
