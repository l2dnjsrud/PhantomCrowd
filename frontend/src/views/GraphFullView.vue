<template>
  <div class="graph-full">
    <!-- Header -->
    <div class="graph-header">
      <router-link :to="`/campaign/${campaignId}`" class="back-link">← Back to Campaign</router-link>
      <h2>Graph Relationship Visualization</h2>
      <div class="graph-stats" v-if="graphData">
        <span>{{ graphData.stats.nodes }} entities</span>
        <span>{{ graphData.stats.edges }} relations</span>
      </div>
    </div>

    <!-- Main: Graph (left) + Detail (right) -->
    <div class="graph-full-layout">
      <div class="graph-canvas-wrap">
        <div ref="graphContainer" class="graph-canvas"></div>
        <!-- Legend -->
        <div class="graph-legend">
          <span v-for="type in legendTypes" :key="type" class="legend-item">
            <span class="legend-dot" :style="{ background: getNodeColor(type) }"></span>
            {{ type }}
          </span>
        </div>
      </div>

      <div class="graph-detail-panel">
        <template v-if="selectedNode">
          <div class="detail-badge" :style="{ background: selectedNode.color }">{{ selectedNode.type }}</div>
          <h3>{{ selectedNode.label }}</h3>
          <p v-if="selectedNode.description" class="detail-desc">{{ selectedNode.description }}</p>

          <div class="detail-section">
            <h4>Connections ({{ selectedNode.connections.length }})</h4>
            <div v-for="conn in selectedNode.connections" :key="conn.target" class="detail-conn">
              <span class="conn-relation">{{ conn.label }}</span>
              <span class="conn-arrow">→</span>
              <span class="conn-entity">{{ conn.target }}</span>
            </div>
          </div>
        </template>
        <template v-else>
          <div class="detail-empty">
            <p>Click any node to inspect</p>
            <p class="hint">Drag to rearrange. Scroll to zoom.</p>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import * as d3 from 'd3'
import { getCampaignGraph, type GraphData } from '../api/client'

const route = useRoute()
const campaignId = computed(() => route.params.id as string)
const graphData = ref<GraphData | null>(null)
const graphContainer = ref<HTMLElement | null>(null)

const selectedNode = ref<{
  id: string; label: string; type: string; description: string; color: string;
  connections: { label: string; target: string }[]
} | null>(null)

const legendTypes = computed(() => {
  if (!graphData.value) return []
  return [...new Set(graphData.value.nodes.map(n => n.type || 'unknown'))]
})

const TYPE_COLORS: Record<string, string> = {
  person: '#f87171', organization: '#60a5fa', group: '#7c5cfc',
  event: '#fbbf24', product: '#4ade80', location: '#f472b6',
  award: '#fbbf24', unknown: '#8888a0',
}

function getNodeColor(type: string): string {
  const t = (type || 'unknown').toLowerCase()
  for (const [key, color] of Object.entries(TYPE_COLORS)) {
    if (t.includes(key)) return color
  }
  return TYPE_COLORS.unknown
}

function renderGraph() {
  if (!graphContainer.value || !graphData.value || graphData.value.nodes.length === 0) return

  const container = graphContainer.value
  container.innerHTML = ''
  const width = container.clientWidth
  const height = container.clientHeight

  const svg = d3.select(container).append('svg').attr('width', width).attr('height', height)
  const g = svg.append('g')

  svg.call(d3.zoom<SVGSVGElement, unknown>()
    .scaleExtent([0.2, 5])
    .on('zoom', (event) => g.attr('transform', event.transform)))

  const nodes = graphData.value.nodes.map(n => ({ ...n }))
  const links = graphData.value.edges.map(e => ({ source: e.source, target: e.target, label: e.label }))

  const connectionCount: Record<string, number> = {}
  links.forEach(l => {
    connectionCount[l.source as string] = (connectionCount[l.source as string] || 0) + 1
    connectionCount[l.target as string] = (connectionCount[l.target as string] || 0) + 1
  })

  const simulation = d3.forceSimulation(nodes as any)
    .force('link', d3.forceLink(links as any).id((d: any) => d.id).distance(180))
    .force('charge', d3.forceManyBody().strength(-600))
    .force('center', d3.forceCenter(width / 2, height / 2))
    .force('collision', d3.forceCollide().radius(50))

  // Arrows
  svg.append('defs').selectAll('marker')
    .data(['arrow']).join('marker')
    .attr('id', 'arrow').attr('viewBox', '0 -5 10 10')
    .attr('refX', 20).attr('refY', 0).attr('markerWidth', 6).attr('markerHeight', 6)
    .attr('orient', 'auto')
    .append('path').attr('d', 'M0,-5L10,0L0,5').attr('fill', '#4a4a6e')

  const link = g.append('g').selectAll('line').data(links).join('line')
    .attr('stroke', '#3a3a5e').attr('stroke-width', 1.5).attr('stroke-opacity', 0.5)
    .attr('marker-end', 'url(#arrow)')

  const edgeLabel = g.append('g').selectAll('text').data(links).join('text')
    .text((d: any) => d.label ? d.label.substring(0, 25) : '')
    .attr('font-size', 10).attr('fill', '#666680').attr('text-anchor', 'middle')

  const node = g.append('g').selectAll('circle').data(nodes).join('circle')
    .attr('r', (d: any) => Math.max(12, Math.min(30, 10 + (connectionCount[d.id] || 0) * 4)))
    .attr('fill', (d: any) => getNodeColor(d.type))
    .attr('stroke', '#0a0a0f').attr('stroke-width', 2).attr('opacity', 0.9)
    .style('cursor', 'pointer')
    .call(d3.drag<any, any>()
      .on('start', (e, d: any) => { if (!e.active) simulation.alphaTarget(0.3).restart(); d.fx = d.x; d.fy = d.y })
      .on('drag', (e, d: any) => { d.fx = e.x; d.fy = e.y })
      .on('end', (e, d: any) => { if (!e.active) simulation.alphaTarget(0); d.fx = null; d.fy = null }))

  node.on('mouseover', function() { d3.select(this).attr('stroke', '#7c5cfc').attr('stroke-width', 4) })
    .on('mouseout', function() { d3.select(this).attr('stroke', '#0a0a0f').attr('stroke-width', 2) })
    .on('click', (_e: any, d: any) => {
      const conns = links
        .filter((l: any) => (l.source?.id || l.source) === d.id || (l.target?.id || l.target) === d.id)
        .map((l: any) => ({
          label: l.label || 'related',
          target: (l.source?.id || l.source) === d.id ? (l.target?.id || l.target) : (l.source?.id || l.source),
        }))
      selectedNode.value = { id: d.id, label: d.label, type: d.type || 'unknown', description: d.description || '', color: getNodeColor(d.type), connections: conns }
    })

  const label = g.append('g').selectAll('text').data(nodes).join('text')
    .text((d: any) => d.label)
    .attr('font-size', 13).attr('font-weight', 600).attr('fill', '#e8e8f0')
    .attr('text-anchor', 'middle')
    .attr('dy', (d: any) => -(Math.max(12, 10 + (connectionCount[d.id] || 0) * 4)) - 8)

  simulation.on('tick', () => {
    link.attr('x1', (d: any) => d.source.x).attr('y1', (d: any) => d.source.y)
      .attr('x2', (d: any) => d.target.x).attr('y2', (d: any) => d.target.y)
    edgeLabel.attr('x', (d: any) => (d.source.x + d.target.x) / 2).attr('y', (d: any) => (d.source.y + d.target.y) / 2)
    node.attr('cx', (d: any) => d.x).attr('cy', (d: any) => d.y)
    label.attr('x', (d: any) => d.x).attr('y', (d: any) => d.y)
  })
}

onMounted(async () => {
  const { data } = await getCampaignGraph(campaignId.value)
  graphData.value = data
  await nextTick()
  renderGraph()
})
</script>

<style scoped>
.graph-full { display: flex; flex-direction: column; height: calc(100vh - 80px); }

.graph-header {
  display: flex; align-items: center; gap: 16px; padding-bottom: 12px;
  border-bottom: 1px solid var(--border); margin-bottom: 12px;
}
.graph-header h2 { flex: 1; font-size: 18px; margin: 0; }
.back-link { color: var(--text-secondary); text-decoration: none; font-size: 13px; }
.back-link:hover { color: var(--accent); }
.graph-stats { display: flex; gap: 12px; font-size: 13px; color: var(--text-secondary); }

.graph-full-layout { display: grid; grid-template-columns: 1fr 320px; gap: 16px; flex: 1; min-height: 0; }

.graph-canvas-wrap {
  background: var(--bg-card); border: 1px solid var(--border);
  border-radius: var(--radius); overflow: hidden; position: relative;
}
.graph-canvas { width: 100%; height: 100%; }

.graph-legend {
  position: absolute; bottom: 12px; left: 12px; display: flex; gap: 12px;
  background: rgba(10,10,15,0.8); padding: 6px 12px; border-radius: 8px;
}
.legend-item { display: flex; align-items: center; gap: 6px; font-size: 11px; color: var(--text-secondary); }
.legend-dot { width: 8px; height: 8px; border-radius: 50%; }

.graph-detail-panel {
  background: var(--bg-card); border: 1px solid var(--border);
  border-radius: var(--radius); padding: 20px; overflow-y: auto;
}
.detail-badge {
  display: inline-block; padding: 3px 10px; border-radius: 10px;
  font-size: 11px; font-weight: 600; color: white; text-transform: uppercase; margin-bottom: 8px;
}
.graph-detail-panel h3 { font-size: 20px; margin: 0 0 12px; }
.detail-desc { color: var(--text-secondary); font-size: 13px; line-height: 1.5; margin-bottom: 16px; }
.detail-section h4 { font-size: 12px; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px; }
.detail-conn { display: flex; gap: 8px; align-items: center; padding: 6px 0; border-bottom: 1px solid var(--border); font-size: 13px; }
.conn-relation { color: var(--accent); font-weight: 600; min-width: 80px; }
.conn-arrow { color: var(--text-secondary); }
.conn-entity { color: var(--text-primary); }

.detail-empty { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 200px; text-align: center; }
.detail-empty p { color: var(--text-secondary); font-size: 14px; }
.hint { font-size: 12px; margin-top: 4px; }
</style>
