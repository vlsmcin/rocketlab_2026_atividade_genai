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
    <form className="space-y-2" onSubmit={handleSubmit}>
      <label className="sr-only" htmlFor="question">
        Sua pergunta
      </label>
      <div className="flex items-end gap-2 rounded-[1.5rem] border border-slate-200/80 bg-white/90 p-2 shadow-[0_16px_40px_-24px_rgba(15,23,42,0.4)]">
        <textarea
          id="question"
          className="max-h-36 min-h-12 flex-1 resize-none rounded-xl border border-transparent bg-slate-50 px-3 py-3 text-sm text-slate-800 outline-none transition placeholder:text-slate-400 focus:border-teal-400 focus:bg-white"
          placeholder="Pergunte algo sobre os dados, tabelas ou um resultado específico..."
          value={question}
          onChange={(event) => onQuestionChange(event.target.value)}
          onKeyDown={handleKeyDown}
        />

        <Button
          className="rounded-xl px-4 py-3"
          type="submit"
          disabled={isSending || question.trim().length === 0}
        >
          {isSending ? 'Enviando...' : 'Enviar'}
        </Button>
      </div>

      <p className="px-1 text-xs text-slate-500">
        Enter envia. Shift+Enter adiciona nova linha.
      </p>
    </form>
  )
}