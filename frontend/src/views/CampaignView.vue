<template>
  <div class="campaign" v-if="campaign">
    <!-- Top bar -->
    <div class="top-bar">
      <router-link to="/" class="back-link">{{ $t('nav.back') }}</router-link>
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

    <!-- MAIN 2-PANEL LAYOUT -->
    <div class="workbench">
      <!-- LEFT: Main content area -->
      <div class="workbench-left">

        <!-- Progress (during pipeline) -->
        <div v-if="campaign.status === 'graph_building'" class="card step-card">
          <h3>{{ $t('campaign.graphBuilding') }}</h3>
          <p>{{ $t('campaign.graphBuildingDesc') }}</p>
          <div class="progress-bar"><div class="progress-bar-fill" style="width: 30%"></div></div>
        </div>

        <div v-if="simStatus && simStatus.status === 'running'" class="card step-card">
          <h3>{{ $t('campaign.simRunning') }}</h3>
          <p>{{ $t('campaign.simProgress', { current: simStatus.current_round, total: simStatus.total_rounds, actions: simStatus.actions_count }) }}</p>
          <div class="progress-bar"><div class="progress-bar-fill" :style="{ width: simProgress + '%' }"></div></div>
        </div>

        <!-- Agent Profiles -->
        <div v-if="agentProfiles.length > 0" class="card step-card">
          <h3>Agent Profiles ({{ agentProfiles.length }})</h3>
          <div class="profiles-grid">
            <div v-for="p in agentProfiles.slice(0, 12)" :key="p.name" class="profile-card" @click="selectedProfile = p">
              <div class="profile-avatar" :style="{ background: stanceColor(p.stance) }">{{ p.name.charAt(0) }}</div>
              <div class="profile-info">
                <strong>{{ p.name }}</strong>
                <span class="profile-meta">{{ p.age }}y · {{ p.occupation }}</span>
              </div>
              <span class="stance-badge" :style="{ background: stanceColor(p.stance) + '22', color: stanceColor(p.stance) }">{{ p.stance || 'neutral' }}</span>
            </div>
          </div>
        </div>

        <!-- Action Feed -->
        <div v-if="actions.length > 0" class="card step-card">
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
        </div>

        <!-- Report (when complete) -->
        <template v-if="campaign.report">
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

          <div class="report-card">
            <h3>{{ $t('report.summary') }}</h3>
            <p class="summary-text">{{ campaign.report.summary }}</p>
          </div>

          <div v-for="sec in campaign.report.sections" :key="sec.title" class="report-card">
            <h3>{{ sec.title }}</h3>
            <p class="section-content">{{ sec.content }}</p>
          </div>

          <div class="report-card">
            <h3>{{ $t('report.recommendations') }}</h3>
            <ul class="rec-list">
              <li v-for="rec in campaign.report.recommendations" :key="rec">{{ rec }}</li>
            </ul>
          </div>
        </template>

        <!-- Failed -->
        <div v-if="campaign.status === 'failed'" class="card error-card">
          <h3>{{ $t('campaign.failed') }}</h3>
          <p>{{ campaign.summary }}</p>
        </div>
      </div>

      <!-- RIGHT: Graph + Interview panel (always visible) -->
      <div class="workbench-right">
        <!-- Knowledge Graph -->
        <div class="right-panel" v-if="graphData && graphData.stats.nodes > 0">
          <h3>{{ $t('campaign.graphTitle', { nodes: graphData.stats.nodes, edges: graphData.stats.edges }) }}</h3>
          <div ref="graphContainer" class="graph-container-sm"></div>
          <!-- Node detail -->
          <div v-if="selectedNode" class="node-detail-card">
            <div class="node-detail-header">
              <span class="node-type-badge" :style="{ background: selectedNode.color }">{{ selectedNode.type }}</span>
              <h4>{{ selectedNode.label }}</h4>
            </div>
            <div v-if="selectedNode.description" class="node-description">{{ selectedNode.description }}</div>
            <div class="node-connections">
              <div v-for="conn in selectedNode.connections" :key="conn.target" class="connection-item">
                <span class="conn-label">{{ conn.label }}</span>
                <span class="conn-target">→ {{ conn.target }}</span>
              </div>
            </div>
          </div>
          <p v-else class="hint-text">Click a node to see details</p>
        </div>

        <!-- Interview Panel -->
        <div class="right-panel" v-if="campaign.status === 'completed'">
          <h3>{{ $t('interview.title') }}</h3>

          <!-- Tab: Agent Interview / Report Chat -->
          <div class="chat-tabs">
            <button :class="{ active: chatMode === 'interview' }" @click="chatMode = 'interview'">Agent Interview</button>
            <button :class="{ active: chatMode === 'report' }" @click="chatMode = 'report'">Report Chat</button>
          </div>

          <template v-if="chatMode === 'interview'">
            <select v-model="interviewAgent">
              <option value="">{{ $t('interview.selectAgent') }}</option>
              <option v-for="name in agentNames" :key="name" :value="name">{{ name }}</option>
            </select>
          </template>

          <!-- Chat history -->
          <div class="chat-history">
            <div v-for="(msg, i) in chatHistory" :key="i" :class="['chat-msg', msg.role]">
              <div class="chat-sender">{{ msg.role === 'user' ? 'You' : msg.sender }}</div>
              <p>{{ msg.content }}</p>
            </div>
          </div>

          <!-- Input -->
          <div class="chat-input-row">
            <input v-model="chatInput" :placeholder="chatMode === 'interview' ? $t('interview.placeholder') : 'Ask about the report...'" @keyup.enter="sendChat" />
            <button class="btn-primary btn-sm" @click="sendChat" :disabled="!chatInput || chatLoading">
              {{ chatLoading ? '...' : $t('interview.ask') }}
            </button>
          </div>
        </div>

        <!-- Timeline (workflow log) -->
        <div class="right-panel timeline-panel" v-if="campaign.status !== 'created'">
          <h3>Pipeline Timeline</h3>
          <div class="timeline">
            <div v-for="(event, i) in timelineEvents" :key="i" :class="['timeline-item', { done: event.done, active: event.active }]">
              <div class="timeline-dot"></div>
              <div class="timeline-content">
                <strong>{{ event.label }}</strong>
                <span v-if="event.detail" class="timeline-detail">{{ event.detail }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Profile Modal -->
    <div v-if="selectedProfile" class="profile-modal-overlay" @click.self="selectedProfile = null">
      <div class="profile-modal">
        <button class="modal-close" @click="selectedProfile = null">×</button>
        <div class="profile-modal-header">
          <div class="profile-avatar-lg" :style="{ background: stanceColor(selectedProfile.stance) }">{{ selectedProfile.name.charAt(0) }}</div>
          <div>
            <h3>{{ selectedProfile.name }}</h3>
            <p>{{ selectedProfile.age }}y · {{ selectedProfile.gender }} · {{ selectedProfile.occupation }}</p>
          </div>
        </div>
        <div class="profile-modal-body">
          <div v-if="selectedProfile.personality" class="profile-field">
            <label>Personality</label><p>{{ selectedProfile.personality }}</p>
          </div>
          <div v-if="selectedProfile.interests" class="profile-field">
            <label>Interests</label>
            <div class="tag-list"><span v-for="ii in selectedProfile.interests" :key="ii" class="tag">{{ ii }}</span></div>
          </div>
        </div>
      </div>
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

const selectedProfile = ref<any>(null)

const agentProfiles = computed(() => {
  const profiles: Record<string, any> = {}
  for (const a of actions.value) {
    if (!profiles[a.agent] && a.profile) {
      profiles[a.agent] = { name: a.agent, ...a.profile }
    }
  }
  return Object.values(profiles)
})

function stanceColor(stance: string) {
  const map: Record<string, string> = {
    supporter: '#4ade80', critic: '#f87171', neutral: '#8888a0', industry: '#60a5fa',
  }
  return map[stance] || '#8888a0'
}

const selectedNode = ref<{
  id: string; label: string; type: string; description: string; color: string;
  connections: { label: string; target: string }[]
} | null>(null)

const interviewAgentName = ref('')
const interviewAgent = interviewAgentName
const chatMode = ref<'interview' | 'report'>('interview')
const chatInput = ref('')
const chatLoading = ref(false)
const chatHistory = ref<{ role: 'user' | 'agent'; sender: string; content: string }[]>([])

// Legacy compat
const interviewQuestion = ref('')
const interviewResponse = ref('')
const interviewing = ref(false)

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

async function sendChat() {
  if (!chatInput.value || chatLoading.value) return
  const question = chatInput.value
  chatInput.value = ''
  chatHistory.value.push({ role: 'user', sender: 'You', content: question })
  chatLoading.value = true

  try {
    if (chatMode.value === 'interview' && interviewAgentName.value) {
      const { data } = await apiInterview(route.params.id as string, interviewAgentName.value, question)
      chatHistory.value.push({ role: 'agent', sender: `@${interviewAgentName.value}`, content: data.response })
    } else {
      // Report chat: interview the "ReportAgent" about the report
      const { data } = await apiInterview(route.params.id as string, agentNames.value[0] || 'ReportAgent', question)
      chatHistory.value.push({ role: 'agent', sender: 'Report Agent', content: data.response })
    }
  } catch (e: any) {
    chatHistory.value.push({ role: 'agent', sender: 'System', content: `Error: ${e.message}` })
  } finally {
    chatLoading.value = false
  }
}

const timelineEvents = computed(() => {
  const s = campaign.value?.status || 'created'
  const idx = STATUS_ORDER.indexOf(s)
  const events = [
    { label: 'Campaign Created', detail: '', done: idx >= 0, active: idx === 0 },
    { label: 'Building Knowledge Graph', detail: graphData.value ? `${graphData.value.stats.nodes} entities` : '', done: idx >= 2, active: idx === 1 },
    { label: 'Generating Personas', detail: agentProfiles.value.length ? `${agentProfiles.value.length} agents` : '', done: idx >= 3, active: idx === 3 },
    { label: 'Running Simulation', detail: simStatus.value ? `R${simStatus.value.current_round}/${simStatus.value.total_rounds}` : '', done: idx >= 5, active: idx === 4 },
    { label: 'Generating Report', detail: '', done: idx >= 6, active: idx === 5 },
    { label: 'Complete', detail: campaign.value?.viral_score ? `Viral: ${campaign.value.viral_score}/100` : '', done: idx >= 6, active: false },
  ]
  return events
})

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
  const height = container.clientHeight || 400

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

  // Node hover + click
  node.on('mouseover', function() {
    d3.select(this).attr('stroke', '#7c5cfc').attr('stroke-width', 4)
  }).on('mouseout', function() {
    d3.select(this).attr('stroke', '#0a0a0f').attr('stroke-width', 2)
  }).on('click', (_event: any, d: any) => {
    // Find connections for this node
    const conns = links
      .filter((l: any) => (l.source?.id || l.source) === d.id || (l.target?.id || l.target) === d.id)
      .map((l: any) => ({
        label: l.label || 'related',
        target: (l.source?.id || l.source) === d.id ? (l.target?.id || l.target) : (l.source?.id || l.source),
      }))
    selectedNode.value = {
      id: d.id,
      label: d.label,
      type: d.type || 'unknown',
      description: d.description || '',
      color: getNodeColor(d.type),
      connections: conns,
    }
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
.campaign { display: flex; flex-direction: column; gap: 16px; padding-bottom: 64px; }

/* Top bar */
.top-bar { display: flex; align-items: center; gap: 16px; }
.top-bar h1 { flex: 1; font-size: 20px; margin: 0; }
.back-link { color: var(--text-secondary); text-decoration: none; font-size: 14px; }
.back-link:hover { color: var(--accent); }

/* Pipeline Steps */
.pipeline-steps { display: flex; gap: 4px; }
.step { display: flex; align-items: center; gap: 6px; padding: 6px 14px; background: var(--bg-card); border-radius: 8px; color: var(--text-secondary); font-size: 12px; }
.step.active { background: var(--accent); color: white; }
.step.done { background: rgba(74, 222, 128, 0.15); color: var(--positive); }
.step-num { font-weight: 700; }

/* WORKBENCH: Left-Right Split */
.workbench { display: grid; grid-template-columns: 1fr 380px; gap: 16px; align-items: start; }
.workbench-left { display: flex; flex-direction: column; gap: 16px; }
.workbench-right { display: flex; flex-direction: column; gap: 16px; position: sticky; top: 16px; max-height: calc(100vh - 120px); overflow-y: auto; }

.step-card { background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius); padding: 20px; }
.step-card h3 { margin-bottom: 10px; font-size: 15px; }
.step-card p { color: var(--text-secondary); line-height: 1.5; font-size: 13px; }

/* Right panels */
.right-panel { background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius); padding: 16px; }
.right-panel h3 { font-size: 14px; margin-bottom: 10px; }
.hint-text { color: var(--text-secondary); font-size: 12px; }

/* Graph (compact for right panel) */
.graph-container-sm { width: 100%; height: 350px; background: var(--bg-secondary); border-radius: 8px; overflow: hidden; margin-bottom: 12px; }

.node-detail-card { display: flex; flex-direction: column; gap: 10px; }
.node-detail-header { display: flex; flex-direction: column; gap: 4px; }
.node-detail-header h4 { font-size: 15px; margin: 0; }
.node-type-badge { display: inline-block; width: fit-content; padding: 2px 8px; border-radius: 10px; font-size: 10px; font-weight: 600; color: white; text-transform: uppercase; }
.node-description { color: var(--text-secondary); font-size: 12px; line-height: 1.4; }
.node-connections { display: flex; flex-direction: column; gap: 4px; }
.connection-item { display: flex; gap: 6px; font-size: 12px; padding: 3px 0; border-bottom: 1px solid var(--border); }
.conn-label { color: var(--accent); font-weight: 600; }
.conn-target { color: var(--text-secondary); }

/* Chat tabs */
.chat-tabs { display: flex; gap: 2px; margin-bottom: 10px; background: var(--bg-secondary); border-radius: 6px; padding: 2px; }
.chat-tabs button { flex: 1; padding: 6px; background: transparent; color: var(--text-secondary); border-radius: 4px; font-size: 12px; }
.chat-tabs button.active { background: var(--accent); color: white; }

/* Chat */
.chat-history { max-height: 300px; overflow-y: auto; display: flex; flex-direction: column; gap: 8px; margin-bottom: 10px; }
.chat-msg { padding: 8px 12px; border-radius: 8px; font-size: 13px; }
.chat-msg.user { background: var(--accent); color: white; align-self: flex-end; max-width: 85%; }
.chat-msg.agent { background: var(--bg-secondary); align-self: flex-start; max-width: 85%; }
.chat-sender { font-size: 11px; font-weight: 600; margin-bottom: 2px; opacity: 0.7; }
.chat-msg p { margin: 0; line-height: 1.4; }
.chat-input-row { display: flex; gap: 4px; }
.chat-input-row input { flex: 1; font-size: 12px; padding: 8px 10px; }
.btn-sm { padding: 8px 12px; font-size: 12px; }

/* Timeline */
.timeline { display: flex; flex-direction: column; gap: 0; }
.timeline-item { display: flex; gap: 12px; padding: 8px 0; position: relative; }
.timeline-dot { width: 10px; height: 10px; border-radius: 50%; background: var(--border); margin-top: 4px; flex-shrink: 0; }
.timeline-item.done .timeline-dot { background: var(--positive); }
.timeline-item.active .timeline-dot { background: var(--accent); box-shadow: 0 0 8px var(--accent); }
.timeline-content { flex: 1; }
.timeline-content strong { font-size: 12px; display: block; }
.timeline-detail { font-size: 11px; color: var(--text-secondary); }
.timeline-item:not(:last-child)::before {
  content: ''; position: absolute; left: 4px; top: 22px; bottom: -8px;
  width: 2px; background: var(--border);
}
.timeline-item.done:not(:last-child)::before { background: var(--positive); }

/* Action Feed */
.action-feed { max-height: 350px; overflow-y: auto; display: flex; flex-direction: column; gap: 6px; }
.action-item { padding: 8px 12px; background: var(--bg-secondary); border-radius: 6px; border-left: 3px solid var(--border); }
.action-item.action-post { border-left-color: var(--accent); }
.action-item.action-reply { border-left-color: var(--mixed); }
.action-item.action-share { border-left-color: var(--positive); }
.action-item.action-like { border-left-color: var(--positive); }
.action-item.action-dislike { border-left-color: var(--negative); }
.action-header { display: flex; align-items: center; gap: 6px; margin-bottom: 3px; font-size: 12px; }
.action-type { color: var(--text-secondary); }
.action-content { color: var(--text-secondary); font-style: italic; line-height: 1.4; font-size: 12px; }
.action-target { color: var(--text-secondary); font-size: 11px; }

/* Score Grid */
.score-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }
.score-card { text-align: center; }
.score-card.accent .score-value { color: var(--accent); }
.score-label { font-size: 11px; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px; }
.score-value { font-size: 28px; font-weight: 700; }
.score-value span { font-size: 14px; color: var(--text-secondary); font-weight: 400; }

/* Report cards */
.report-card { background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius); padding: 20px; }
.report-card h3 { margin-bottom: 10px; font-size: 15px; }
.summary-text { color: var(--text-secondary); line-height: 1.6; font-size: 14px; }
.section-content { color: var(--text-secondary); line-height: 1.6; white-space: pre-wrap; font-size: 13px; }
.rec-list { padding-left: 18px; }
.rec-list li { color: var(--text-secondary); margin-bottom: 8px; line-height: 1.5; font-size: 13px; }

/* Agent Profiles */
.profiles-grid {
  display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; max-height: 300px; overflow-y: auto;
}
.profile-card {
  display: flex; align-items: center; gap: 10px; padding: 10px 12px;
  background: var(--bg-secondary); border-radius: 8px; cursor: pointer;
  transition: all 0.15s;
}
.profile-card:hover { background: var(--bg-card-hover); }
.profile-avatar {
  width: 36px; height: 36px; border-radius: 50%; display: flex; align-items: center;
  justify-content: center; font-weight: 700; color: white; font-size: 14px; flex-shrink: 0;
}
.profile-avatar-lg {
  width: 52px; height: 52px; border-radius: 50%; display: flex; align-items: center;
  justify-content: center; font-weight: 700; color: white; font-size: 20px; flex-shrink: 0;
}
.profile-info { flex: 1; min-width: 0; }
.profile-info strong { font-size: 13px; display: block; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.profile-meta { font-size: 11px; color: var(--text-secondary); }
.stance-badge { padding: 2px 8px; border-radius: 10px; font-size: 10px; font-weight: 600; text-transform: uppercase; }

/* Profile Modal */
.profile-modal-overlay {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.6); display: flex; align-items: center;
  justify-content: center; z-index: 1000;
}
.profile-modal {
  background: var(--bg-card); border: 1px solid var(--border);
  border-radius: var(--radius); padding: 28px; width: 440px; max-width: 90vw;
  position: relative;
}
.modal-close {
  position: absolute; top: 12px; right: 16px; background: none;
  color: var(--text-secondary); font-size: 24px; padding: 0; line-height: 1;
}
.profile-modal-header { display: flex; gap: 16px; align-items: center; margin-bottom: 20px; }
.profile-modal-header h3 { margin: 0; font-size: 18px; }
.profile-modal-header p { margin: 4px 0 0; color: var(--text-secondary); font-size: 13px; }
.profile-modal-body { display: flex; flex-direction: column; gap: 14px; }
.profile-field label { font-size: 11px; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.5px; display: block; margin-bottom: 4px; }
.profile-field p { color: var(--text-primary); line-height: 1.5; font-size: 14px; margin: 0; }
.tag-list { display: flex; flex-wrap: wrap; gap: 6px; }
.tag { padding: 3px 10px; background: var(--bg-secondary); border-radius: 12px; font-size: 12px; color: var(--text-secondary); }

.error-card { border-color: var(--negative); }
.error-card h3 { color: var(--negative); margin-bottom: 8px; }
.loading { text-align: center; padding: 64px; color: var(--text-secondary); }
</style>
