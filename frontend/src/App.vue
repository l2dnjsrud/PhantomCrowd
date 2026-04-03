<template>
  <header class="header">
    <router-link to="/" class="logo">
      <span class="logo-icon">👻</span>
      <span class="logo-text">{{ $t('app.name') }}</span>
    </router-link>
    <p class="tagline">{{ $t('app.tagline') }}</p>
    <div class="spacer"></div>
    <button class="lang-btn" @click="toggleLang">{{ currentLang === 'en' ? '한국어' : 'EN' }}</button>
  </header>
  <main>
    <router-view />
  </main>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { setLocale, getLocale } from './i18n'

const currentLang = ref(getLocale())

function toggleLang() {
  const next = currentLang.value === 'en' ? 'ko' : 'en'
  setLocale(next)
  currentLang.value = next
}
</script>

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

.spacer {
  flex: 1;
}

.lang-btn {
  padding: 6px 14px;
  background: var(--bg-card);
  color: var(--text-secondary);
  border: 1px solid var(--border);
  border-radius: 6px;
  font-size: 13px;
  font-weight: 600;
}

.lang-btn:hover {
  color: var(--accent);
  border-color: var(--accent);
}
</style>
