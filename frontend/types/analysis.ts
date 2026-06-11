export interface IdeaMeta {
  industry: string
  subcategory: string
  target_customer: string
  business_model: string
  pain_point: string
  solution: string
}

export interface Competition {
  score: number
  level: string
}

export interface MarketIntelligence {
  market_segment: string
  cluster_id: number
  cluster_size: number

  competition: Competition

  differentiation_score: number

  opportunity_score: number
}

export interface Competitor {
  startup_id: string

  name: string

  industry: string

  subcategory: string

  target_customer: string

  business_model: string

  pain_point: string

  solution: string

  score: number

  reasons: string[]

  match_reasons: string[]
}
export interface MarketGap {
  market_saturation: string

  opportunities: string[]

  missing_features: string[]

  risks: string[]

  threats: string[]
}

export interface Recommendations {
  positioning: string[]

  feature_suggestions: string[]

  customer_segments: string[]

  monetization: string[]
}

export interface AnalysisResult {
  idea: string

  idea_meta: IdeaMeta

  market_intelligence: MarketIntelligence

  competitors: Competitor[]

  market_gap: MarketGap

  recommendations: Recommendations
}