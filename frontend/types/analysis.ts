export interface IdeaInfo {
  cleaned_idea: string
  problem_being_solved: string
  target_audience: string
  core_value_proposition: string
  market_category: string
  keywords: string[]
}

export interface SimilarProduct {
  name: string
  tagline: string
  similarity: number
}

export interface ShapItem {
  feature: string
  value: number
}

export interface GapAnalysis {
  gaps: string[]
  opportunities: string[]
  crowding_level: string
  competitor_topics: string[]
}

export interface Viability {
  score: number
  features: Record<string, number>
  shap_breakdown: ShapItem[]
}

export interface AnalysisResult {
  success: boolean
  idea: string
  idea_info: IdeaInfo
  similar_products: SimilarProduct[]
  gap_analysis: GapAnalysis
  viability: Viability
  report: string
}