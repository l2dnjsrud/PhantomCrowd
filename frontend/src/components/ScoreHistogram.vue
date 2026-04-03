<template>
  <v-chart :option="chartOption" autoresize style="height: 240px" />
</template>

<script setup lang="ts">
import { computed } from 'vue'
import VChart from 'vue-echarts'
import type { Reaction } from '../api/client'

const props = defineProps<{ reactions: Reaction[] }>()

const chartOption = computed(() => {
  // Buckets from -1.0 to 1.0 in 0.25 steps
  const bucketLabels = ['-1.0', '-0.75', '-0.5', '-0.25', '0', '0.25', '0.5', '0.75', '1.0']
  const buckets = new Array(9).fill(0)

  for (const r of props.reactions) {
    const idx = Math.min(Math.floor((r.sentiment_score + 1) / 0.25), 8)
    buckets[idx]++
  }

  return {
    tooltip: { trigger: 'axis' },
    xAxis: {
      type: 'category',
      data: bucketLabels,
      axisLabel: { color: '#8888a0', fontSize: 11 },
      axisLine: { lineStyle: { color: '#2a2a3e' } },
    },
    yAxis: {
      type: 'value',
      axisLabel: { color: '#8888a0' },
      splitLine: { lineStyle: { color: '#2a2a3e' } },
    },
    series: [
      {
        type: 'bar',
        data: buckets.map((v, i) => ({
          value: v,
          itemStyle: {
            color: i < 4 ? '#f87171' : i === 4 ? '#fbbf24' : '#4ade80',
            borderRadius: [4, 4, 0, 0],
          },
        })),
        barWidth: '60%',
      },
    ],
  }
})
</script>
