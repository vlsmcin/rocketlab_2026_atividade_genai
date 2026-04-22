import type { FormEvent, KeyboardEvent } from 'react'

import { Button } from '../atoms/Button'

interface ChatComposerProps {
  isSending: boolean
  question: string
  onQuestionChange: (value: string) => void
  onSend: () => Promise<void> | void
}

export function ChatComposer({
  isSending,
  question,
  onQuestionChange,
  onSend,
}: ChatComposerProps) {
  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    void onSend()
  }

  function handleKeyDown(event: KeyboardEvent<HTMLTextAreaElement>) {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault()
      void onSend()
    }
  }

  return (
    <form
      className="rounded-[2rem] border border-slate-200/80 bg-white/90 p-3 shadow-[0_24px_60px_-34px_rgba(15,23,42,0.45)] backdrop-blur"
      onSubmit={handleSubmit}
    >
      <label className="sr-only" htmlFor="question">
        Sua pergunta
      </label>
      <textarea
        id="question"
        className="min-h-28 w-full resize-none rounded-[1.5rem] border border-transparent bg-slate-50 px-4 py-4 text-sm text-slate-800 outline-none transition placeholder:text-slate-400 focus:border-teal-400 focus:bg-white"
        placeholder="Pergunte algo sobre os dados, tabelas ou um resultado específico..."
        value={question}
        onChange={(event) => onQuestionChange(event.target.value)}
        onKeyDown={handleKeyDown}
      />

      <div className="mt-3 flex items-center justify-between gap-3">
        <p className="text-xs text-slate-500">
          Pressione Enter para enviar e Shift+Enter para quebrar linha.
        </p>

        <Button type="submit" disabled={isSending || question.trim().length === 0}>
          {isSending ? 'Enviando...' : 'Enviar'}
        </Button>
      </div>
    </form>
  )
}