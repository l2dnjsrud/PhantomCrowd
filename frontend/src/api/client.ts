import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
})

export interface SimulationCreate {
  title: string
  content: string
  content_type: string
  audience_size: number
  audience_config?: Record<string, unknown>
  language?: string
}

export interface Simulation {
  id: string
  title: string
  content: string
  content_type: string
  audience_size: number
  language: string
  status: string
  viral_score: number | null
  summary: string | null
  suggestions: string[] | null
  created_at: string
  completed_at: string | null
  ab_test_id: string | null
  ab_variant: string | null
  reactions: Reaction[]
}

export interface Reaction {
  id: string
  persona_name: string
  persona_profile: {
    name: string
    age: number
    gender: string
    occupation: string
    interests: string[]
    personality: string
    social_media_usage: string
  }
  sentiment: string
  sentiment_score: number
  comment: string
  engagement: string
  reasoning: string | null
}

export interface SimulationProgress {
  simulation_id: string
  status: string
  total: number
  completed: number
  progress: number
}

// A/B Test types
export interface ABTestCreate {
  title: string
  content_a: string
  content_b: string
  content_type: string
  audience_size: number
  audience_config?: Record<string, unknown>
  language?: string
}

export interface ABTestComparison {
  metric: string
  variant_a: number
  variant_b: number
  winner: string
}

export interface ABTest {
  id: string
  title: string
  status: string
  winner: string | null
  comparison: ABTestComparison[] | null
  created_at: string
  completed_at: string | null
  simulation_a: Simulation | null
  simulation_b: Simulation | null
}

// Simulation API
export const createSimulation = (data: SimulationCreate) =>
  api.post<Simulation>('/simulations/', data)

export const listSimulations = () =>
  api.get<Simulation[]>('/simulations/')

export const getSimulation = (id: string) =>
  api.get<Simulation>(`/simulations/${id}`)

export const getProgress = (id: string) =>
  api.get<SimulationProgress>(`/simulations/${id}/progress`)

export const deleteSimulation = (id: string) =>
  api.delete(`/simulations/${id}`)

// A/B Test API
export const createABTest = (data: ABTestCreate) =>
  api.post<ABTest>('/ab-tests/', data)

export const listABTests = () =>
  api.get<ABTest[]>('/ab-tests/')

export const getABTest = (id: string) =>
  api.get<ABTest>(`/ab-tests/${id}`)

// Export API
export const getExportUrl = (id: string, format: 'csv' | 'json') =>
  `/api/export/simulations/${id}/${format}`
