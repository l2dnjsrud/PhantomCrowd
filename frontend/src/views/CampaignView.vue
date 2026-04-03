<template>
  <div class="campaign" v-if="campaign">
    <router-link to="/" class="back-link">← Back</router-link>

    <!-- Header -->
    <div class="campaign-header">
      <h1>{{ campaign.title }}</h1>
      <span :class="`badge badge-${statusColor(campaign.status)}`">{{ campaign.status }}</span>
    </div>

    <!-- Pipeline Steps -->
    <div class="pipeline-steps">
      <div v-for="(step, i) in steps" :key="i" :class="['step', { active: isStepActive(step.key), done: isStepDone(step.key) }]">
        <div class="step-num">{{ isStepDone(step.key) ? '✓' : i + 1 }}</div>
        <div class="step-label">{{ step.label }}</div>
      </div>
    </div>

    <!-- Step 1: Graph Building -->
    <section v-if="campaign.status === 'graph_building'" class="card step-card">
      <h3>Building Knowledge Graph...</h3>
      <p>Extracting entities and relationships from your content and context.</p>
      <div class="progress-bar"><div class="progress-bar-fill" style="width: 30%"></div></div>
    </section>

    <!-- Step 2: Graph Ready -->
    <section v-if="graphData && graphData.stats.nodes > 0" class="card step-card">
      <h3>Knowledge Graph ({{ graphData.stats.nodes }} entities, {{ graphData.stats.edges }} relations)</h3>
      <div ref="graphContainer" class="graph-container"></div>
    </section>

    <!-- Step 3: Simulation -->
    <section v-if="simStatus && simStatus.status === 'running'" class="card step-card">
      <h3>👻 Simulation Running</h3>
      <p>Round {{ simStatus.current_round }} / {{ simStatus.total_rounds }} | {{ simStatus.actions_count }} actions</p>
      <div class="progress-bar">
        <div class="progress-bar-fill" :style="{ width: simProgress + '%' }"></div>
      </div>
    </section>

    <!-- Action Feed -->
    <section v-if="actions.length > 0" class="card step-card">
      <h3>Agent Actions ({{ actions.length }})</h3>
      <div class="action-feed">
        <div v-for="(a, i) in actions.slice(0, 30)" :key="i" class="action-item" :class="`action-${a.action}`">
          <div class="action-header">
            <strong>@{{ a.agent }}</strong>
            <span class="action-type">{{ actionEmoji(a.action) }} {{ a.action }}</span>
            <span :class="`badge badge-${a.sentiment}`">{{ a.sentiment }} {{ a.score.toFixed(1) }}</span>
          </div>
          <p v-if="a.content" class="action-content">{{ a.content }}</p>
          <p v-if="a.target" class="action-target">→ @{{ a.target }}</p>
        </div>
      </div>
    </section>

    <!-- Step 4: Report -->
    <section v-if="campaign.report" class="report-section">
      <!-- Score Cards -->
      <div class="score-grid">
        <div class="card score-card accent">
          <div class="score-label">Viral Score</div>
          <div class="score-value">{{ campaign.report.viral_score }}<span>/100</span></div>
        </div>
        <div class="card score-card">
          <div class="score-label">Agents</div>
          <div class="score-value">{{ campaign.llm_agents + campaign.rule_agents }}</div>
        </div>
        <div class="card score-card">
          <div class="score-label">Rounds</div>
          <div class="score-value">{{ campaign.sim_rounds }}</div>
        </div>
        <div class="card score-card">
          <div class="score-label">Actions</div>
          <div class="score-value">{{ actions.length }}</div>
        </div>
      </div>

      <!-- Summary -->
      <div class="card">
        <h3>Executive Summary</h3>
        <p class="summary-text">{{ campaign.report.summary }}</p>
      </div>

      <!-- Report Sections -->
      <div v-for="sec in campaign.report.sections" :key="sec.title" class="card">
        <h3>{{ sec.title }}</h3>
        <p class="section-content">{{ sec.content }}</p>
      </div>

      <!-- Recommendations -->
      <div class="card">
        <h3>Recommendations</h3>
        <ul class="rec-list">
          <li v-for="rec in campaign.report.recommendations" :key="rec">{{ rec }}</li>
        </ul>
      </div>
    </section>

    <!-- Step 5: Interview -->
    <section v-if="campaign.status === 'completed'" class="card step-card">
      <h3>💬 Interview an Agent</h3>
      <div class="interview-form">
        <select v-model="interviewAgent">
          <option value="">Select agent...</option>
          <option v-for="name in agentNames" :key="name" :value="name">{{ name }}</option>
        </select>
        <input v-model="interviewQuestion" placeholder="Ask them anything..." @keyup.enter="doInterview" />
        <button class="btn-primary" @click="doInterview" :disabled="!interviewAgent || !interviewQuestion || interviewing">
          {{ interviewing ? 'Asking...' : 'Ask' }}
        </button>
      </div>
      <div v-if="interviewResponse" class="interview-response card">
        <strong>@{{ interviewAgent }}:</strong>
        <p>{{ interviewResponse }}</p>
      </div>
    </section>

    <!-- Failed -->
    <div v-if="campaign.status === 'failed'" class="card error-card">
      <h3>Pipeline Failed</h3>
      <p>{{ campaign.summary }}</p>
    </div>
  </div>
  <div v-else class="loading">Loading campaign...</div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import * as d3 from 'd3'
import {
  getCampaign, getCampaignGraph, getCampaignSimStatus, getCampaignActions,
  interviewAgent as apiInterview,
  type Campaign, type GraphData, type SimStatus, type SimActionItem,
} from '../api/client'

const route = useRoute()
const campaign = ref<Campaign | null>(null)
const graphData = ref<GraphData | null>(null)
const simStatus = ref<SimStatus | null>(null)
const actions = ref<SimActionItem[]>([])
const graphContainer = ref<HTMLElement | null>(null)

const interviewAgentName = ref('')
const interviewQuestion = ref('')
const interviewResponse = ref('')
const interviewing = ref(false)
// Alias for template
const interviewAgent = interviewAgentName

let pollTimer: ReturnType<typeof setInterval> | null = null

const steps = [
  { key: 'graph', label: 'Knowledge Graph' },
  { key: 'profiles', label: 'Personas' },
  { key: 'sim', label: 'Simulation' },
  { key: 'report', label: 'Report' },
  { key: 'interview', label: 'Interview' },
]

const STATUS_ORDER = ['created', 'graph_building', 'graph_ready', 'generating_profiles', 'simulating', 'reporting', 'completed']

function isStepActive(key: string) {
  const s = campaign.value?.status || ''
  const map: Record<string, string[]> = {
    graph: ['graph_building', 'graph_ready'],
    profiles: ['generating_profiles'],
    sim: ['simulating'],
    report: ['reporting'],
    interview: ['completed'],
  }
  return (map[key] || []).includes(s)
}

function isStepDone(key: string) {
  const s = campaign.value?.status || ''
  const idx = STATUS_ORDER.indexOf(s)
  const doneAt: Record<string, number> = { graph: 3, profiles: 4, sim: 5, report: 6, interview: 7 }
  return idx >= (doneAt[key] || 99)
}

const simProgress = computed(() => {
  if (!simStatus.value) return 0
  const { current_round, total_rounds } = simStatus.value
  return total_rounds > 0 ? (current_round / total_rounds) * 100 : 0
})

const agentNames = computed(() => {
  const names = new Set(actions.value.filter(a => a.content && a.content.length > 5).map(a => a.agent))
  return Array.from(names)
})

function statusColor(status: string) {
  if (status === 'completed') return 'positive'
  if (status === 'failed') return 'negative'
  return 'mixed'
}

function actionEmoji(action: string) {
  const map: Record<string, string> = { post: '📝', reply: '💬', share: '🔄', like: '👍', dislike: '👎', ignore: '😐' }
  return map[action] || ''
}

async function poll() {
  const id = route.params.id as string
  const { data } = await getCampaign(id)
  campaign.value = data

  // Fetch graph if ready
  if (['graph_ready', 'generating_profiles', 'simulating', 'reporting', 'completed'].includes(data.status)) {
    try {
      const { data: gd } = await getCampaignGraph(id)
      graphData.value = gd
    } catch {}
  }

  // Fetch sim status
  if (['simulating', 'reporting', 'completed'].includes(data.status)) {
    try {
      const { data: ss } = await getCampaignSimStatus(id)
      simStatus.value = ss
    } catch {}
  }

  // Fetch actions
  if (['simulating', 'reporting', 'completed'].includes(data.status)) {
    try {
      const { data: acts } = await getCampaignActions(id)
      actions.value = acts
    } catch {}
  }

  if (data.status === 'completed' || data.status === 'failed') {
    if (pollTimer) clearInterval(pollTimer)
  }
}

async function doInterview() {
  if (!interviewAgentName.value || !interviewQuestion.value) return
  interviewing.value = true
  try {
    const { data } = await apiInterview(route.params.id as string, interviewAgentName.value, interviewQuestion.value)
    interviewResponse.value = data.response
  } catch (e: any) {
    interviewResponse.value = `Error: ${e.message}`
  } finally {
    interviewing.value = false
  }
}

// D3 graph rendering
function renderGraph() {
  if (!graphContainer.value || !graphData.value || graphData.value.nodes.length === 0) return

  const container = graphContainer.value
  container.innerHTML = ''

  const width = container.clientWidth
  const height = 400

  const svg = d3.select(container).append('svg').attr('width', width).attr('height', height)

  const nodes = graphData.value.nodes.map(n => ({ ...n }))
  const links = graphData.value.edges.map(e => ({
    source: e.source,
    target: e.target,
    label: e.label,
  }))

  const simulation = d3.forceSimulation(nodes as any)
    .force('link', d3.forceLink(links as any).id((d: any) => d.id).distance(120))
    .force('charge', d3.forceManyBody().strength(-300))
    .force('center', d3.forceCenter(width / 2, height / 2))

  const link = svg.append('g')
    .selectAll('line')
    .data(links)
    .join('line')
    .attr('stroke', '#2a2a3e')
    .attr('stroke-width', 1.5)

  const node = svg.append('g')
    .selectAll('circle')
    .data(nodes)
    .join('circle')
    .attr('r', 8)
    .attr('fill', '#7c5cfc')
    .attr('stroke', '#1a1a2e')
    .attr('stroke-width', 2)
    .call(d3.drag<any, any>()
      .on('start', (e, d: any) => { if (!e.active) simulation.alphaTarget(0.3).restart(); d.fx = d.x; d.fy = d.y })
      .on('drag', (e, d: any) => { d.fx = e.x; d.fy = e.y })
      .on('end', (e, d: any) => { if (!e.active) simulation.alphaTarget(0); d.fx = null; d.fy = null })
    )

  const label = svg.append('g')
    .selectAll('text')
    .data(nodes)
    .join('text')
    .text((d: any) => d.label)
    .attr('font-size', 11)
    .attr('fill', '#8888a0')
    .attr('dx', 12)
    .attr('dy', 4)

  simulation.on('tick', () => {
    link
      .attr('x1', (d: any) => d.source.x)
      .attr('y1', (d: any) => d.source.y)
      .attr('x2', (d: any) => d.target.x)
      .attr('y2', (d: any) => d.target.y)
    node.attr('cx', (d: any) => d.x).attr('cy', (d: any) => d.y)
    label.attr('x', (d: any) => d.x).attr('y', (d: any) => d.y)
  })
}

watch(graphData, async () => {
  await nextTick()
  renderGraph()
})

onMounted(async () => {
  await poll()
  if (campaign.value && campaign.value.status !== 'completed' && campaign.value.status !== 'failed') {
    pollTimer = setInterval(poll, 3000)
  }
})

onUnmounted(() => { if (pollTimer) clearInterval(pollTimer) })
</script>

<style scoped>
.campaign { display: flex; flex-direction: column; gap: 24px; padding-bottom: 64px; }
.back-link { color: var(--text-secondary); text-decoration: none; font-size: 14px; }
.back-link:hover { color: var(--accent); }
.campaign-header { display: flex; justify-content: space-between; align-items: center; }
.campaign-header h1 { font-size: 24px; }

/* Pipeline Steps */
.pipeline-steps { display: flex; gap: 4px; }
.step { display: flex; align-items: center; gap: 8px; padding: 8px 16px; background: var(--bg-card); border-radius: 8px; color: var(--text-secondary); font-size: 13px; }
.step.active { background: var(--accent); color: white; }
.step.done { background: rgba(74, 222, 128, 0.15); color: var(--positive); }
.step-num { font-weight: 700; font-size: 14px; }

.step-card h3 { margin-bottom: 12px; }
.step-card p { color: var(--text-secondary); line-height: 1.5; }

/* Graph */
.graph-container { width: 100%; height: 400px; background: var(--bg-secondary); border-radius: 8px; overflow: hidden; }

/* Action Feed */
.action-feed { max-height: 400px; overflow-y: auto; display: flex; flex-direction: column; gap: 8px; }
.action-item { padding: 10px 14px; background: var(--bg-secondary); border-radius: 8px; border-left: 3px solid var(--border); }
.action-item.action-post { border-left-color: var(--accent); }
.action-item.action-reply { border-left-color: var(--mixed); }
.action-item.action-share { border-left-color: var(--positive); }
.action-item.action-like { border-left-color: var(--positive); }
.action-item.action-dislike { border-left-color: var(--negative); }
.action-header { display: flex; align-items: center; gap: 8px; margin-bottom: 4px; font-size: 13px; }
.action-type { color: var(--text-secondary); }
.action-content { color: var(--text-secondary); font-style: italic; line-height: 1.4; font-size: 13px; }
.action-target { color: var(--text-secondary); font-size: 12px; }

/* Score Grid */
.score-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; }
.score-card { text-align: center; }
.score-card.accent .score-value { color: var(--accent); }
.score-label { font-size: 12px; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px; }
.score-value { font-size: 32px; font-weight: 700; }
.score-value span { font-size: 16px; color: var(--text-secondary); font-weight: 400; }

.report-section { display: flex; flex-direction: column; gap: 16px; }
.summary-text { color: var(--text-secondary); line-height: 1.6; font-size: 15px; }
.section-content { color: var(--text-secondary); line-height: 1.6; white-space: pre-wrap; }
.rec-list { padding-left: 20px; }
.rec-list li { color: var(--text-secondary); margin-bottom: 8px; line-height: 1.5; }

/* Interview */
.interview-form { display: flex; gap: 8px; margin-bottom: 16px; }
.interview-form select { width: 200px; }
.interview-form input { flex: 1; }
.interview-response { margin-top: 12px; }
.interview-response p { color: var(--text-secondary); line-height: 1.5; margin-top: 8px; }

.error-card { border-color: var(--negative); }
.error-card h3 { color: var(--negative); margin-bottom: 8px; }
.loading { text-align: center; padding: 64px; color: var(--text-secondary); }
</style>
