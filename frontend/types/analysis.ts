export interface IdeaInterpretation {
  problem_statement: string
  solution_summary: string
  target_user: string
  assumptions: string[]
}

export interface MarketCategory {
  category: string
  similarity: number
}