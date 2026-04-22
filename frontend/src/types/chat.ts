export type ChatRole = 'user' | 'assistant'

export interface ChatMessage {
  id: string
  role: ChatRole
  content: string
  isLoading?: boolean
}

export interface AskResponse {
  status: string
  formatted_output: string
  result: Record<string, unknown>
}