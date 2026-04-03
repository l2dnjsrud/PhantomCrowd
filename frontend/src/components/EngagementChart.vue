<template>
  <v-chart :option="option" style="height: 280px" autoresize />
</template>

<script setup lang="ts">
import { computed } from 'vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { BarChart } from 'echarts/charts'
import { GridComponent, TooltipComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import type { Reaction } from '../api/client'

use([BarChart, GridComponent, TooltipComponent, CanvasRenderer])

const props = defineProps<{ reactions: Reaction[] }>()

const option = computed(() => {
  const counts: Record<string, number> = { like: 0, share: 0, ignore: 0, dislike: 0 }
  props.reactions.forEach(r => {
    counts[r.engagement] = (counts[r.engagement] || 0) + 1
  })

  const colorMap: Record<string, string> = {
    like: '#4ade80',
    share: '#60a5fa',
    ignore: '#8888a0',
    dislike: '#f87171',
  }

  const categories = ['like', 'share', 'ignore', 'dislike']

  return {
    tooltip: { trigger: 'axis' },
    grid: { left: 60, right: 20, top: 10, bottom: 30 },
    xAxis: {
      type: 'category',
      data: categories.map(c => c.charAt(0).toUpperCase() + c.slice(1)),
      axisLabel: { color: '#8888a0' },
      axisLine: { lineStyle: { color: '#2a2a3e' } },
    },
    yAxis: {
      type: 'value',
      axisLabel: { color: '#8888a0' },
      splitLine: { lineStyle: { color: '#2a2a3e' } },
    },
    series: [{
      type: 'bar',
      barWidth: '50%',
      data: categories.map(c => ({
        value: counts[c],
        itemStyle: { color: colorMap[c], borderRadius: [4, 4, 0, 0] },
      })),
    }],
  }
})
</script>
