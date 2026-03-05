<template>
  <div class="layout">
    <header class="header">
      <NuxtLink to="/" class="logo">Carousel MVP</NuxtLink>
      <NuxtLink to="/carousels/new" class="btn btn-primary">Создать карусель</NuxtLink>
    </header>
    <main class="main">
      <slot />
    </main>
  </div>
</template>

<style scoped>
.layout { min-height: 100vh; display: flex; flex-direction: column; }
.header { background: #fff; padding: 0.75rem 1rem; display: flex; align-items: center; justify-content: space-between; box-shadow: 0 1px 2px rgba(0,0,0,0.05); }
.logo { font-weight: 700; font-size: 1.25rem; }
.main { flex: 1; padding: 1rem; }
</style>
