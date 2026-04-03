<template>
  <div class="ab-test" v-if="ab">
    <router-link to="/" class="back-link">← Back</router-link>

    <div class="ab-header">
      <h1>🔀 {{ ab.title }}</h1>
      <span :class="`badge badge-${statusColor(ab.status)}`">
        {{ ab.status }}{{ ab.winner ? ` — Variant ${ab.winner} wins` : '' }}
      </span>
    </div>

    <!-- Progress -->
    <div v-if="ab.status === 'pending' || ab.status === 'running'" class="card progress-card">
      <p>👻 Running A/B test... Both variants are being tested simultaneously.</p>
      <div class="progress-bar">
        <div class="progress-bar-fill" :style="{ width: '50%' }"></div>
      </div>
    </div>

    <!-- Comparison Table -->
    <div v-if="ab.comparison" class="card comparison-card">
      <h3>Head-to-Head Comparison</h3>
      <table class="comparison-table">
        <thead>
          <tr>
            <th>Metric</th>
            <th :class="{ winner: ab.winner === 'A' }">Variant A</th>
            <th :class="{ winner: ab.winner === 'B' }">Variant B</th>
            <th>Winner</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="c in ab.comparison" :key="c.metric">
            <td>{{ c.metric }}</td>
            <td :class="{ 'cell-winner': c.winner === 'A' }">{{ c.variant_a }}</td>
            <td :class="{ 'cell-winner': c.winner === 'B' }">{{ c.variant_b }}</td>
            <td>
              <span v-if="c.winner === 'tie'" class="badge badge-neutral">Tie</span>
              <span v-else :class="`badge badge-positive`">{{ c.winner }}</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Side-by-side Variants -->
    <div v-if="ab.simulation_a && ab.simulation_b" class="variants-grid">
      <div class="card variant-card" :class="{ 'variant-winner': ab.winner === 'A' }">
        <h3>Variant A {{ ab.winner === 'A' ? '🏆' : '' }}</h3>
        <div class="variant-score">{{ ab.simulation_a.viral_score }}<span>/100</span></div>
        <p class="variant-content">{{ ab.simulation_a.content }}</p>
        <p v-if="ab.simulation_a.summary" class="variant-summary">{{ ab.simulation_a.summary }}</p>
        <router-link :to="`/simulation/${ab.simulation_a.id}`" class="detail-link">
          View full results →
        </router-link>
      </div>

      <div class="card variant-card" :class="{ 'variant-winner': ab.winner === 'B' }">
        <h3>Variant B {{ ab.winner === 'B' ? '🏆' : '' }}</h3>
        <div class="variant-score">{{ ab.simulation_b.viral_score }}<span>/100</span></div>
        <p class="variant-content">{{ ab.simulation_b.content }}</p>
        <p v-if="ab.simulation_b.summary" class="variant-summary">{{ ab.simulation_b.summary }}</p>
        <router-link :to="`/simulation/${ab.simulation_b.id}`" class="detail-link">
          View full results →
        </router-link>
      </div>
    </div>
  </div>

  <div v-else class="loading">Loading A/B test...</div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { getABTest, type ABTest } from '../api/client'

const route = useRoute()
const ab = ref<ABTest | null>(null)
let pollTimer: ReturnType<typeof setInterval> | null = null

onMounted(async () => {
  const id = route.params.id as string
  const { data } = await getABTest(id)
  ab.value = data

  if (data.status !== 'completed' && data.status !== 'failed') {
    pollTimer = setInterval(async () => {
      const { data: updated } = await getABTest(id)
      ab.value = updated
      if (updated.status === 'completed' || updated.status === 'failed') {
        if (pollTimer) clearInterval(pollTimer)
      }
    }, 3000)
  }
})

onUnmounted(() => { if (pollTimer) clearInterval(pollTimer) })

function statusColor(status: string) {
  if (status === 'completed') return 'positive'
  if (status === 'failed') return 'negative'
  if (status === 'running') return 'mixed'
  return 'neutral'
}
</script>

<style scoped>
.ab-test { display: flex; flex-direction: column; gap: 24px; padding-bottom: 64px; }
.back-link { color: var(--text-secondary); text-decoration: none; font-size: 14px; }
.back-link:hover { color: var(--accent); }
.ab-header { display: flex; justify-content: space-between; align-items: center; }
.ab-header h1 { font-size: 24px; }

.progress-card { text-align: center; }
.progress-card p { margin-bottom: 12px; color: var(--text-secondary); }

.comparison-card h3 { margin-bottom: 16px; }
.comparison-table { width: 100%; border-collapse: collapse; }
.comparison-table th, .comparison-table td {
  padding: 12px 16px; text-align: center; border-bottom: 1px solid var(--border);
}
.comparison-table th { color: var(--text-secondary); font-size: 13px; text-transform: uppercase; }
.comparison-table td:first-child { text-align: left; font-weight: 600; }
.winner { color: var(--accent); }
.cell-winner { color: var(--positive); font-weight: 700; }

.variants-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.variant-card { position: relative; }
.variant-winner { border-color: var(--accent); }
.variant-card h3 { margin-bottom: 8px; }
.variant-score { font-size: 48px; font-weight: 800; color: var(--accent); margin-bottom: 12px; }
.variant-score span { font-size: 18px; color: var(--text-secondary); font-weight: 400; }
.variant-content {
  color: var(--text-secondary); font-style: italic; line-height: 1.5;
  margin-bottom: 12px; padding: 12px; background: var(--bg-secondary); border-radius: 8px;
}
.variant-summary { color: var(--text-secondary); line-height: 1.5; margin-bottom: 12px; }
.detail-link { color: var(--accent); text-decoration: none; font-size: 14px; }
.detail-link:hover { text-decoration: underline; }

.loading { text-align: center; padding: 64px; color: var(--text-secondary); }
</style>
