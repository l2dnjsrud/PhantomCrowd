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
}

export interface Simulation {
  id: string
  title: string
  content: string
  content_type: string
  audience_size: number
  status: string
  viral_score: number | null
  summary: string | null
  suggestions: string[] | null
  created_at: string
  completed_at: string | null
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
