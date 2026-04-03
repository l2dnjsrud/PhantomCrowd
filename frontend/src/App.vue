<template>
  <header class="header">
    <router-link to="/" class="logo">
      <span class="logo-icon">👻</span>
      <span class="logo-text">PhantomCrowd</span>
    </router-link>
    <p class="tagline">AI Audience Simulator</p>
  </header>
  <main>
    <router-view />
  </main>
</template>

<style scoped>
.header {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 24px 0;
  border-bottom: 1px solid var(--border);
  margin-bottom: 32px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 8px;
  text-decoration: none;
  color: var(--text-primary);
}

.logo-icon {
  font-size: 28px;
}

.logo-text {
  font-size: 22px;
  font-weight: 700;
  letter-spacing: -0.5px;
}

.tagline {
  color: var(--text-secondary);
  font-size: 14px;
}
</style>
