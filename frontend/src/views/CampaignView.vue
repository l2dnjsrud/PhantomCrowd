<template>
  <div class="campaign" v-if="campaign">
    <router-link to="/" class="back-link">{{ $t('nav.back') }}</router-link>

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
      <h3>{{ $t('campaign.graphBuilding') }}</h3>
      <p>{{ $t('campaign.graphBuildingDesc') }}</p>
      <div class="progress-bar"><div class="progress-bar-fill" style="width: 30%"></div></div>
    </section>

    <!-- Step 2: Graph Ready -->
    <section v-if="graphData && graphData.stats.nodes > 0" class="card step-card">
      <h3>{{ $t('campaign.graphTitle', { nodes: graphData.stats.nodes, edges: graphData.stats.edges }) }}</h3>
      <div ref="graphContainer" class="graph-container"></div>
    </section>

    <!-- Step 3: Simulation -->
    <section v-if="simStatus && simStatus.status === 'running'" class="card step-card">
      <h3>{{ $t('campaign.simRunning') }}</h3>
      <p>{{ $t('campaign.simProgress', { current: simStatus.current_round, total: simStatus.total_rounds, actions: simStatus.actions_count }) }}</p>
      <div class="progress-bar">
        <div class="progress-bar-fill" :style="{ width: simProgress + '%' }"></div>
      </div>
    </section>

    <!-- Action Feed -->
    <section v-if="actions.length > 0" class="card step-card">
      <h3>{{ $t('campaign.actionsTitle', { count: actions.length }) }}</h3>
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
          <div class="score-label">{{ $t('report.viralScore') }}</div>
          <div class="score-value">{{ campaign.report.viral_score }}<span>/100</span></div>
        </div>
        <div class="card score-card">
          <div class="score-label">{{ $t('report.agents') }}</div>
          <div class="score-value">{{ campaign.llm_agents + campaign.rule_agents }}</div>
        </div>
        <div class="card score-card">
          <div class="score-label">{{ $t('report.rounds') }}</div>
          <div class="score-value">{{ campaign.sim_rounds }}</div>
        </div>
        <div class="card score-card">
          <div class="score-label">{{ $t('report.actions') }}</div>
          <div class="score-value">{{ actions.length }}</div>
        </div>
      </div>

      <!-- Summary -->
      <div class="card">
        <h3>{{ $t('report.summary') }}</h3>
        <p class="summary-text">{{ campaign.report.summary }}</p>
      </div>

      <!-- Report Sections -->
      <div v-for="sec in campaign.report.sections" :key="sec.title" class="card">
        <h3>{{ sec.title }}</h3>
        <p class="section-content">{{ sec.content }}</p>
      </div>

      <!-- Recommendations -->
      <div class="card">
        <h3>{{ $t('report.recommendations') }}</h3>
        <ul class="rec-list">
          <li v-for="rec in campaign.report.recommendations" :key="rec">{{ rec }}</li>
        </ul>
      </div>
    </section>

    <!-- Step 5: Interview -->
    <section v-if="campaign.status === 'completed'" class="card step-card">
      <h3>{{ $t('interview.title') }}</h3>
      <div class="interview-form">
        <select v-model="interviewAgent">
          <option value="">{{ $t('interview.selectAgent') }}</option>
          <option v-for="name in agentNames" :key="name" :value="name">{{ name }}</option>
        </select>
        <input v-model="interviewQuestion" :placeholder="$t('interview.placeholder')" @keyup.enter="doInterview" />
        <button class="btn-primary" @click="doInterview" :disabled="!interviewAgent || !interviewQuestion || interviewing">
          {{ interviewing ? $t('interview.asking') : $t('interview.ask') }}
        </button>
      </div>
      <div v-if="interviewResponse" class="interview-response card">
        <strong>@{{ interviewAgent }}:</strong>
        <p>{{ interviewResponse }}</p>
      </div>
    </section>

    <!-- Failed -->
    <div v-if="campaign.status === 'failed'" class="card error-card">
      <h3>{{ $t('campaign.failed') }}</h3>
      <p>{{ campaign.summary }}</p>
    </div>
  </div>
  <div v-else class="loading">{{ $t('common.loading') }}</div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useI18n } from 'vue-i18n'
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

const { t } = useI18n()

const steps = computed(() => [
  { key: 'graph', label: t('campaign.pipeline.graph') },
  { key: 'profiles', label: t('campaign.pipeline.personas') },
  { key: 'sim', label: t('campaign.pipeline.simulation') },
  { key: 'report', label: t('campaign.pipeline.report') },
  { key: 'interview', label: t('campaign.pipeline.interview') },
])

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

// Entity type → color mapping (MiroFish style)
const TYPE_COLORS: Record<string, string> = {
  person: '#f87171',     // red
  organization: '#60a5fa', // blue
  group: '#7c5cfc',      // purple
  event: '#fbbf24',      // yellow
  product: '#4ade80',    // green
  location: '#f472b6',   // pink
  award: '#fbbf24',      // yellow
  unknown: '#8888a0',    // gray
}

function getNodeColor(type: string): string {
  const t = (type || 'unknown').toLowerCase()
  for (const [key, color] of Object.entries(TYPE_COLORS)) {
    if (t.includes(key)) return color
  }
  return TYPE_COLORS.unknown
}

// D3 graph rendering — enhanced MiroFish-style
function renderGraph() {
  if (!graphContainer.value || !graphData.value || graphData.value.nodes.length === 0) return

  const container = graphContainer.value
  container.innerHTML = ''

  const width = container.clientWidth
  const height = 600

  const svg = d3.select(container)
    .append('svg')
    .attr('width', width)
    .attr('height', height)

  // Zoom + pan
  const g = svg.append('g')
  const zoom = d3.zoom<SVGSVGElement, unknown>()
    .scaleExtent([0.3, 4])
    .on('zoom', (event) => g.attr('transform', event.transform))
  svg.call(zoom)

  const nodes = graphData.value.nodes.map(n => ({ ...n }))
  const links = graphData.value.edges.map(e => ({
    source: e.source,
    target: e.target,
    label: e.label,
  }))

  // Count connections per node for sizing
  const connectionCount: Record<string, number> = {}
  links.forEach(l => {
    connectionCount[l.source as string] = (connectionCount[l.source as string] || 0) + 1
    connectionCount[l.target as string] = (connectionCount[l.target as string] || 0) + 1
  })

  const simulation = d3.forceSimulation(nodes as any)
    .force('link', d3.forceLink(links as any).id((d: any) => d.id).distance(160))
    .force('charge', d3.forceManyBody().strength(-500))
    .force('center', d3.forceCenter(width / 2, height / 2))
    .force('collision', d3.forceCollide().radius(40))

  // Edge lines
  const link = g.append('g')
    .selectAll('line')
    .data(links)
    .join('line')
    .attr('stroke', '#3a3a5e')
    .attr('stroke-width', 1.5)
    .attr('stroke-opacity', 0.6)

  // Edge labels
  const edgeLabel = g.append('g')
    .selectAll('text')
    .data(links)
    .join('text')
    .text((d: any) => d.label ? d.label.substring(0, 20) : '')
    .attr('font-size', 9)
    .attr('fill', '#555570')
    .attr('text-anchor', 'middle')

  // Node circles — sized by connections
  const node = g.append('g')
    .selectAll('circle')
    .data(nodes)
    .join('circle')
    .attr('r', (d: any) => Math.max(10, Math.min(25, 8 + (connectionCount[d.id] || 0) * 3)))
    .attr('fill', (d: any) => getNodeColor(d.type))
    .attr('stroke', '#0a0a0f')
    .attr('stroke-width', 2)
    .attr('opacity', 0.9)
    .style('cursor', 'grab')
    .call(d3.drag<any, any>()
      .on('start', (e, d: any) => { if (!e.active) simulation.alphaTarget(0.3).restart(); d.fx = d.x; d.fy = d.y })
      .on('drag', (e, d: any) => { d.fx = e.x; d.fy = e.y })
      .on('end', (e, d: any) => { if (!e.active) simulation.alphaTarget(0); d.fx = null; d.fy = null })
    )

  // Node hover glow
  node.on('mouseover', function() {
    d3.select(this).attr('stroke', '#7c5cfc').attr('stroke-width', 4)
  }).on('mouseout', function() {
    d3.select(this).attr('stroke', '#0a0a0f').attr('stroke-width', 2)
  })

  // Node labels
  const label = g.append('g')
    .selectAll('text')
    .data(nodes)
    .join('text')
    .text((d: any) => d.label)
    .attr('font-size', 12)
    .attr('font-weight', 600)
    .attr('fill', '#e8e8f0')
    .attr('text-anchor', 'middle')
    .attr('dy', (d: any) => -(Math.max(10, 8 + (connectionCount[d.id] || 0) * 3)) - 6)

  simulation.on('tick', () => {
    link
      .attr('x1', (d: any) => d.source.x)
      .attr('y1', (d: any) => d.source.y)
      .attr('x2', (d: any) => d.target.x)
      .attr('y2', (d: any) => d.target.y)
    edgeLabel
      .attr('x', (d: any) => (d.source.x + d.target.x) / 2)
      .attr('y', (d: any) => (d.source.y + d.target.y) / 2)
    node.attr('cx', (d: any) => d.x).attr('cy', (d: any) => d.y)
    label.attr('x', (d: any) => d.x).attr('y', (d: any) => d.y)
  })

  // Legend
  const legendData = [...new Set(nodes.map((n: any) => n.type || 'unknown'))]
  const legend = svg.append('g').attr('transform', `translate(${width - 150}, 20)`)
  legendData.forEach((type, i) => {
    legend.append('circle').attr('cx', 0).attr('cy', i * 22).attr('r', 6).attr('fill', getNodeColor(type))
    legend.append('text').attr('x', 14).attr('y', i * 22 + 4).text(type).attr('font-size', 11).attr('fill', '#8888a0')
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
.graph-container { width: 100%; height: 600px; background: var(--bg-secondary); border-radius: 8px; overflow: hidden; }

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
