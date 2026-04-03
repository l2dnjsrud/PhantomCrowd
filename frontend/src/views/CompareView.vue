<template>
  <div class="compare">
    <router-link to="/" class="back-link">← Back</router-link>
    <h1>Compare Simulations</h1>

    <div v-if="completed.length < 2" class="card">
      <p>Need at least 2 completed simulations to compare.</p>
    </div>

    <template v-else>
      <div class="select-row">
        <div class="form-group">
          <label>Simulation 1</label>
          <select v-model="selectedA">
            <option value="">Select...</option>
            <option v-for="s in completed" :key="s.id" :value="s.id">
              {{ s.title }} (Viral: {{ s.viral_score }})
            </option>
          </select>
        </div>
        <div class="form-group">
          <label>Simulation 2</label>
          <select v-model="selectedB">
            <option value="">Select...</option>
            <option v-for="s in completed" :key="s.id" :value="s.id">
              {{ s.title }} (Viral: {{ s.viral_score }})
            </option>
          </select>
        </div>
      </div>

      <div v-if="simA && simB" class="comparison-grid">
        <div class="card compare-card">
          <table class="compare-table">
            <thead>
              <tr>
                <th>Metric</th>
                <th>{{ simA.title }}</th>
                <th>{{ simB.title }}</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>Viral Score</td>
                <td :class="{ better: (simA.viral_score || 0) > (simB.viral_score || 0) }">{{ simA.viral_score }}</td>
                <td :class="{ better: (simB.viral_score || 0) > (simA.viral_score || 0) }">{{ simB.viral_score }}</td>
              </tr>
              <tr>
                <td>Audience Size</td>
                <td>{{ simA.audience_size }}</td>
                <td>{{ simB.audience_size }}</td>
              </tr>
              <tr>
                <td>Avg Sentiment</td>
                <td :class="{ better: avgSent(simA) > avgSent(simB) }">{{ avgSent(simA).toFixed(2) }}</td>
                <td :class="{ better: avgSent(simB) > avgSent(simA) }">{{ avgSent(simB).toFixed(2) }}</td>
              </tr>
              <tr>
                <td>Engagement Rate</td>
                <td :class="{ better: engRate(simA) > engRate(simB) }">{{ engRate(simA) }}%</td>
                <td :class="{ better: engRate(simB) > engRate(simA) }">{{ engRate(simB) }}%</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { listSimulations, getSimulation, type Simulation } from '../api/client'

const allSims = ref<Simulation[]>([])
const selectedA = ref('')
const selectedB = ref('')
const simA = ref<Simulation | null>(null)
const simB = ref<Simulation | null>(null)

const completed = computed(() => allSims.value.filter(s => s.status === 'completed'))

onMounted(async () => {
  const { data } = await listSimulations()
  allSims.value = data
})

watch(selectedA, async (id) => {
  if (id) { const { data } = await getSimulation(id); simA.value = data }
  else simA.value = null
})

watch(selectedB, async (id) => {
  if (id) { const { data } = await getSimulation(id); simB.value = data }
  else simB.value = null
})

function avgSent(sim: Simulation) {
  if (!sim.reactions?.length) return 0
  return sim.reactions.reduce((a, r) => a + r.sentiment_score, 0) / sim.reactions.length
}

function engRate(sim: Simulation) {
  if (!sim.reactions?.length) return 0
  const engaged = sim.reactions.filter(r => r.engagement !== 'ignore').length
  return Math.round((engaged / sim.reactions.length) * 100)
}
</script>

<style scoped>
.compare { display: flex; flex-direction: column; gap: 24px; padding-bottom: 64px; }
.back-link { color: var(--text-secondary); text-decoration: none; font-size: 14px; }
.back-link:hover { color: var(--accent); }
h1 { font-size: 24px; }

.select-row { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.form-group { display: flex; flex-direction: column; gap: 6px; }
.form-group label {
  font-size: 13px; font-weight: 600; color: var(--text-secondary);
  text-transform: uppercase; letter-spacing: 0.5px;
}

.compare-table { width: 100%; border-collapse: collapse; }
.compare-table th, .compare-table td {
  padding: 12px 16px; text-align: center; border-bottom: 1px solid var(--border);
}
.compare-table th { color: var(--text-secondary); font-size: 13px; }
.compare-table td:first-child { text-align: left; font-weight: 600; }
.better { color: var(--positive); font-weight: 700; }
</style>
