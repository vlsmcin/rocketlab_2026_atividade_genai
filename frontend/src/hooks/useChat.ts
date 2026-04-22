import { useEffect, useMemo, useRef, useState } from 'react'

import { askQuestion } from '../lib/chatApi'
import type { ChatMessage } from '../types/chat'

function createId(prefix: string): string {
  return `${prefix}-${crypto.randomUUID()}`
}

const initialMessages: ChatMessage[] = [
  {
    id: createId('assistant'),
    role: 'assistant',
    content:
      'Digite sua pergunta sobre o banco de dados e eu retorno a resposta formatada aqui.',
  },
]

export function useChat() {
  const [messages, setMessages] = useState<ChatMessage[]>(initialMessages)
  const [question, setQuestion] = useState('')
  const [isSending, setIsSending] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const messagesEndRef = useRef<HTMLDivElement | null>(null)

  const canSend = useMemo(() => question.trim().length > 0 && !isSending, [
    isSending,
    question,
  ])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' })
  }, [messages])

  async function submitQuestion(text?: string) {
    const nextQuestion = (text ?? question).trim()

    if (!nextQuestion || isSending) {
      return
    }

    setIsSending(true)
    setError(null)
    setQuestion('')

    const userMessage: ChatMessage = {
      id: createId('user'),
      role: 'user',
      content: nextQuestion,
    }

    const assistantId = createId('assistant')
    const pendingMessage: ChatMessage = {
      id: assistantId,
      role: 'assistant',
      content: 'Analisando a pergunta...',
      isLoading: true,
    }

    setMessages((current) => [...current, userMessage, pendingMessage])

    try {
      const response = await askQuestion(nextQuestion)

      setMessages((current) =>
        current.map((message) =>
          message.id === assistantId
            ? {
                ...message,
                content: response.formatted_output,
                isLoading: false,
              }
            : message,
        ),
      )
    } catch (submitError) {
      const message =
        submitError instanceof Error
          ? submitError.message
          : 'Nao foi possivel completar a pergunta.'

      setError(message)
      setMessages((current) =>
        current.map((item) =>
          item.id === assistantId
            ? {
                ...item,
                content: message,
                isLoading: false,
              }
            : item,
        ),
      )
    } finally {
      setIsSending(false)
    }
  }

  return {
    canSend,
    error,
    isSending,
    messages,
    messagesEndRef,
    question,
    setQuestion,
    submitQuestion,
  }
}