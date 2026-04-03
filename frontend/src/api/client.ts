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

// === V2: Campaign API ===

export interface CampaignCreate {
  title: string
  content: string
  content_type: string
  context_text?: string
  audience_config?: Record<string, unknown>
  language?: string
  llm_agents?: number
  rule_agents?: number
  sim_rounds?: number
}

export interface Campaign {
  id: string
  title: string
  content: string
  content_type: string
  status: string
  language: string
  llm_agents: number
  rule_agents: number
  sim_rounds: number
  viral_score: number | null
  summary: string | null
  report: CampaignReport | null
  created_at: string
  completed_at: string | null
}

export interface CampaignReport {
  viral_score: number
  summary: string
  sections: { title: string; content: string }[]
  recommendations: string[]
}

export interface GraphData {
  nodes: { id: string; label: string; type: string; description: string }[]
  edges: { source: string; target: string; label: string; weight: number }[]
  stats: { nodes: number; edges: number }
}

export interface SimStatus {
  campaign_id: string
  status: string
  current_round: number
  total_rounds: number
  actions_count: number
}

export interface SimActionItem {
  round: number
  agent: string
  profile: Record<string, unknown>
  action: string
  content: string
  target: string
  sentiment: string
  score: number
}

export const createCampaign = (data: CampaignCreate) =>
  api.post<Campaign>('/v2/campaigns/', data)

export const listCampaigns = () =>
  api.get<Campaign[]>('/v2/campaigns/')

export const getCampaign = (id: string) =>
  api.get<Campaign>(`/v2/campaigns/${id}`)

export const getCampaignGraph = (id: string) =>
  api.get<GraphData>(`/v2/campaigns/${id}/graph`)

export const getCampaignSimStatus = (id: string) =>
  api.get<SimStatus>(`/v2/campaigns/${id}/simulation/status`)

export const getCampaignActions = (id: string, round?: number) =>
  api.get<SimActionItem[]>(`/v2/campaigns/${id}/actions`, { params: round ? { round_num: round } : {} })

export const getCampaignReport = (id: string) =>
  api.get<CampaignReport>(`/v2/campaigns/${id}/report`)

export const interviewAgent = (id: string, agent_name: string, question: string) =>
  api.post<{ agent: string; response: string }>(`/v2/campaigns/${id}/interview`, { agent_name, question })
