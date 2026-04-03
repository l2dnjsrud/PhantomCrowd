import { defineStore } from 'pinia'
import { ref } from 'vue'
import {
  listSimulations,
  createSimulation,
  getSimulation,
  getProgress,
  type Simulation,
  type SimulationCreate,
  type SimulationProgress,
} from '../api/client'

export const useSimulationStore = defineStore('simulation', () => {
  const simulations = ref<Simulation[]>([])
  const current = ref<Simulation | null>(null)
  const progress = ref<SimulationProgress | null>(null)
  const loading = ref(false)

  async function fetchList() {
    const { data } = await listSimulations()
    simulations.value = data
  }

  async function create(payload: SimulationCreate) {
    loading.value = true
    try {
      const { data } = await createSimulation(payload)
      current.value = data
      return data
    } finally {
      loading.value = false
    }
  }

  async function fetchOne(id: string) {
    const { data } = await getSimulation(id)
    current.value = data
    return data
  }

  async function pollProgress(id: string) {
    const { data } = await getProgress(id)
    progress.value = data
    return data
  }

  return { simulations, current, progress, loading, fetchList, create, fetchOne, pollProgress }
})
