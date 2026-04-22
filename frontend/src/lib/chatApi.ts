import type { AskResponse } from '../types/chat'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL?.trim() ?? ''

function buildUrl(path: string): string {
  return `${API_BASE_URL}${path}`
}

export async function askQuestion(question: string): Promise<AskResponse> {
  const response = await fetch(buildUrl('/ask'), {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ question }),
  })

  if (!response.ok) {
    const payload = (await response.json().catch(() => null)) as
      | { detail?: string }
      | null

    throw new Error(payload?.detail ?? 'Nao foi possivel responder a pergunta.')
  }

  return (await response.json()) as AskResponse
}