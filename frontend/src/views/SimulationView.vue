<template>
  <div class="simulation" v-if="sim">
    <!-- Header -->
    <div class="sim-header">
      <router-link to="/" class="back">&larr; Back</router-link>
      <h2>{{ sim.title }}</h2>
      <div class="header-actions">
        <div v-if="sim.status === 'completed'" class="export-btns">
          <a :href="exportUrl('csv')" class="btn-export">CSV</a>
          <a :href="exportUrl('json')" class="btn-export">JSON</a>
        </div>
        <span :class="`badge badge-${statusColor(sim.status)}`">{{ sim.status }}</span>
      </div>
    </div>

    <!-- Progress -->
    <div v-if="sim.status === 'running'" class="card progress-card">
      <p>Phantoms are reacting... {{ progress?.completed || 0 }} / {{ progress?.total || sim.audience_size }}</p>
      <div class="progress-bar">
        <div class="progress-bar-fill" :style="{ width: `${progressPct}%` }"></div>
      </div>
    </div>

    <!-- Results Dashboard -->
    <template v-if="sim.status === 'completed'">
      <!-- Score Cards -->
      <div class="score-grid">
        <div class="card score-card">
          <div class="score-label">Viral Score</div>
          <div class="score-value" :class="viralClass">{{ sim.viral_score }}<span class="score-unit">/100</span></div>
        </div>
        <div class="card score-card">
          <div class="score-label">Audience Size</div>
          <div class="score-value">{{ sim.reactions.length }}</div>
        </div>
        <div class="card score-card">
          <div class="score-label">Avg Sentiment</div>
          <div class="score-value" :class="avgSentimentClass">{{ avgSentiment.toFixed(2) }}</div>
        </div>
        <div class="card score-card">
          <div class="score-label">Engagement Rate</div>
          <div class="score-value">{{ engagementRate }}%</div>
        </div>
      </div>

      <!-- Charts -->
      <div class="chart-grid">
        <div class="card">
          <h3>Sentiment Distribution</h3>
          <SentimentChart :reactions="sim.reactions" />
        </div>
        <div class="card">
          <h3>Engagement Breakdown</h3>
          <EngagementChart :reactions="sim.reactions" />
        </div>
        <div class="card chart-wide">
          <h3>Sentiment Score Distribution</h3>
          <ScoreHistogram :reactions="sim.reactions" />
        </div>
      </div>

      <!-- Summary & Suggestions -->
      <div class="card summary-card" v-if="sim.summary">
        <h3>AI Analysis</h3>
        <p class="summary-text">{{ sim.summary }}</p>
        <div v-if="sim.suggestions?.length" class="suggestions">
          <h4>Suggestions</h4>
          <ul>
            <li v-for="(s, i) in sim.suggestions" :key="i">{{ s }}</li>
          </ul>
        </div>
      </div>

      <!-- Reactions List -->
      <div class="card reactions-card">
        <h3>Audience Reactions ({{ sim.reactions.length }})</h3>
        <div class="reactions-list">
          <div v-for="r in sim.reactions" :key="r.id" class="reaction-item">
            <div class="persona-info">
              <span class="persona-name">{{ r.persona_name }}</span>
              <span class="persona-detail">{{ r.persona_profile.age }}y, {{ r.persona_profile.occupation }}</span>
            </div>
            <p class="reaction-comment">"{{ r.comment }}"</p>
            <div class="reaction-meta">
              <span :class="`badge badge-${r.sentiment}`">{{ r.sentiment }} ({{ r.sentiment_score.toFixed(1) }})</span>
              <span class="engagement-tag">{{ engagementEmoji(r.engagement) }} {{ r.engagement }}</span>
            </div>
          </div>
        </div>
      </div>
    </template>

    <!-- Failed -->
    <div v-if="sim.status === 'failed'" class="card error-card">
      <h3>Simulation Failed</h3>
      <p>{{ sim.summary }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useSimulationStore } from '../stores/simulation'
import { getExportUrl } from '../api/client'
import SentimentChart from '../components/SentimentChart.vue'
import EngagementChart from '../components/EngagementChart.vue'
import ScoreHistogram from '../components/ScoreHistogram.vue'

const route = useRoute()
const store = useSimulationStore()
const sim = computed(() => store.current)
const progress = computed(() => store.progress)
let pollInterval: ReturnType<typeof setInterval> | null = null

const progressPct = computed(() => progress.value?.progress || 0)

const avgSentiment = computed(() => {
  if (!sim.value?.reactions.length) return 0
  const sum = sim.value.reactions.reduce((a, r) => a + r.sentiment_score, 0)
  return sum / sim.value.reactions.length
})

const engagementRate = computed(() => {
  if (!sim.value?.reactions.length) return 0
  const engaged = sim.value.reactions.filter(r => r.engagement !== 'ignore').length
  return Math.round((engaged / sim.value.reactions.length) * 100)
})

const viralClass = computed(() => {
  const score = sim.value?.viral_score || 0
  if (score >= 70) return 'sentiment-positive'
  if (score >= 40) return 'sentiment-neutral'
  return 'sentiment-negative'
})

const avgSentimentClass = computed(() => {
  if (avgSentiment.value > 0.3) return 'sentiment-positive'
  if (avgSentiment.value < -0.3) return 'sentiment-negative'
  return 'sentiment-neutral'
})

function statusColor(status: string) {
  if (status === 'completed') return 'positive'
  if (status === 'failed') return 'negative'
  if (status === 'running') return 'mixed'
  return 'neutral'
}

function exportUrl(format: 'csv' | 'json') {
  return getExportUrl(route.params.id as string, format)
}

function engagementEmoji(eng: string) {
  const map: Record<string, string> = { like: '👍', share: '🔄', ignore: '😐', dislike: '👎' }
  return map[eng] || ''
}

async function poll() {
  const id = route.params.id as string
  const data = await store.pollProgress(id)
  if (data.status === 'completed' || data.status === 'failed') {
    if (pollInterval) clearInterval(pollInterval)
    await store.fetchOne(id)
  }
}

onMounted(async () => {
  const id = route.params.id as string
  await store.fetchOne(id)
  if (sim.value?.status === 'running' || sim.value?.status === 'pending') {
    pollInterval = setInterval(poll, 2000)
  }
})

onUnmounted(() => {
  if (pollInterval) clearInterval(pollInterval)
})
</script>

<style scoped>
.sim-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
}

.back {
  color: var(--text-secondary);
  text-decoration: none;
  font-size: 14px;
}

.back:hover {
  color: var(--accent);
}

.sim-header h2 {
  flex: 1;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.export-btns {
  display: flex;
  gap: 4px;
}

.btn-export {
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
  text-decoration: none;
  color: var(--text-secondary);
  background: var(--bg-secondary);
  border: 1px solid var(--border);
}

.btn-export:hover {
  color: var(--accent);
  border-color: var(--accent);
}

.progress-card {
  margin-bottom: 24px;
}

.progress-card p {
  margin-bottom: 12px;
  color: var(--text-secondary);
}

.score-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.score-card {
  text-align: center;
}

.score-label {
  font-size: 12px;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 8px;
}

.score-value {
  font-size: 32px;
  font-weight: 700;
}

.score-unit {
  font-size: 16px;
  color: var(--text-secondary);
  font-weight: 400;
}

.chart-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 24px;
}

.chart-wide {
  grid-column: 1 / -1;
}

.chart-grid h3 {
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 16px;
}

.summary-card {
  margin-bottom: 24px;
}

.summary-card h3 {
  margin-bottom: 12px;
}

.summary-text {
  color: var(--text-secondary);
  line-height: 1.6;
  margin-bottom: 16px;
}

.suggestions h4 {
  font-size: 14px;
  margin-bottom: 8px;
}

.suggestions ul {
  padding-left: 20px;
}

.suggestions li {
  color: var(--text-secondary);
  margin-bottom: 6px;
  line-height: 1.5;
}

.reactions-card h3 {
  margin-bottom: 16px;
}

.reactions-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-height: 600px;
  overflow-y: auto;
}

.reaction-item {
  padding: 16px;
  background: var(--bg-secondary);
  border-radius: 8px;
}

.persona-info {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.persona-name {
  font-weight: 600;
  font-size: 14px;
}

.persona-detail {
  font-size: 12px;
  color: var(--text-secondary);
}

.reaction-comment {
  font-style: italic;
  color: var(--text-secondary);
  margin-bottom: 8px;
  line-height: 1.5;
}

.reaction-meta {
  display: flex;
  gap: 12px;
  align-items: center;
}

.engagement-tag {
  font-size: 12px;
  color: var(--text-secondary);
}

.error-card {
  border-color: var(--negative);
}

.error-card h3 {
  color: var(--negative);
  margin-bottom: 8px;
}
</style>
