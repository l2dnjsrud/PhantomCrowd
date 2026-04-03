<template>
  <v-chart :option="option" style="height: 280px" autoresize />
</template>

<script setup lang="ts">
import { computed } from 'vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { PieChart } from 'echarts/charts'
import { TitleComponent, TooltipComponent, LegendComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import type { Reaction } from '../api/client'

use([PieChart, TitleComponent, TooltipComponent, LegendComponent, CanvasRenderer])

const props = defineProps<{ reactions: Reaction[] }>()

const option = computed(() => {
  const counts: Record<string, number> = { positive: 0, negative: 0, neutral: 0, mixed: 0 }
  props.reactions.forEach(r => {
    counts[r.sentiment] = (counts[r.sentiment] || 0) + 1
  })

  const colorMap: Record<string, string> = {
    positive: '#4ade80',
    negative: '#f87171',
    neutral: '#fbbf24',
    mixed: '#60a5fa',
  }

  return {
    tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      itemStyle: { borderRadius: 6, borderColor: '#1a1a2e', borderWidth: 2 },
      label: { color: '#8888a0', fontSize: 12 },
      data: Object.entries(counts)
        .filter(([, v]) => v > 0)
        .map(([k, v]) => ({ name: k, value: v, itemStyle: { color: colorMap[k] } })),
    }],
  }
})
</script>
