import { useChat } from '../../hooks/useChat'
import { ChatComposer } from '../molecules/ChatComposer'
import { ChatMessage } from '../molecules/ChatMessage'

export function ChatPanel() {
  const {
    canSend,
    error,
    isSending,
    messages,
    messagesEndRef,
    question,
    setQuestion,
    submitQuestion,
  } = useChat()

  return (
    <section className="h-dvh overflow-hidden px-3 py-3 sm:px-6 sm:py-5 lg:px-8">
      <div className="mx-auto flex h-full w-full max-w-6xl flex-col gap-4">
        <header className="flex w-full items-center justify-between gap-4 rounded-[1.5rem] border border-white/60 bg-white/70 px-4 py-3 shadow-[0_20px_50px_-28px_rgba(15,23,42,0.45)] backdrop-blur sm:rounded-[2rem] sm:px-5 sm:py-4">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.35em] text-teal-700">
              Rocketlab Chat
            </p>
            <h1 className="mt-1 text-base font-semibold leading-tight tracking-tight text-slate-950 sm:text-xl lg:text-2xl">
              Consultas e Análises de E-Commerce em Linguagem Natural
            </h1>
          </div>
        </header>

        <main className="grid min-h-0 flex-1 gap-4 lg:grid-cols-[18rem_minmax(0,1fr)]">
          <aside className="hidden flex-col gap-4 rounded-[2.25rem] border border-slate-200/70 bg-slate-950 p-6 text-white shadow-[0_24px_60px_-36px_rgba(15,23,42,0.8)] lg:flex">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.32em] text-teal-300">
                Como usar
              </p>
              <h2 className="mt-2 text-2xl font-semibold tracking-tight">
                Um chat enxuto, modular e direto
              </h2>
            </div>

            <div className="space-y-3 text-sm leading-6 text-slate-300">
              <p>• Envie uma pergunta e receba a resposta formatada do backend.</p>
              <p>• Use Enter para enviar e Shift+Enter para quebrar linha.</p>
              <p>• Nada fica salvo: a conversa existe apenas enquanto a página está aberta.</p>
            </div>

            <div className="mt-auto rounded-[1.5rem] border border-white/10 bg-white/5 p-4 text-sm text-slate-200">
              {isSending || canSend
                ? 'A interface está pronta para receber sua próxima pergunta.'
                : 'Escreva algo e clique em enviar para começar.'}
            </div>
          </aside>

          <section className="flex min-h-0 flex-col rounded-[1.5rem] border border-white/70 bg-white/80 p-3 shadow-[0_24px_60px_-32px_rgba(15,23,42,0.55)] backdrop-blur sm:rounded-[2.25rem] sm:p-4">
            <div className="mb-4 flex items-center justify-between gap-3 border-b border-slate-200/80 pb-4">
              <div>
                <p className="text-sm font-medium text-slate-500">Conversa</p>
                <p className="text-sm font-semibold text-slate-950 sm:text-base">
                  Resposta em tempo real, sem histórico persistido
                </p>
              </div>

              <span className="rounded-full bg-slate-950 px-3 py-1 text-xs font-semibold uppercase tracking-[0.28em] text-white">
                Live
              </span>
            </div>

            <div className="min-h-0 flex-1 space-y-4 overflow-y-auto pr-1">
              {messages.map((message) => (
                <ChatMessage key={message.id} message={message} />
              ))}
              <div ref={messagesEndRef} />
            </div>

            {error ? (
              <p className="mt-4 rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
                {error}
              </p>
            ) : null}

            <div className="mt-4 border-t border-slate-200/80 pt-4">
              <ChatComposer
                isSending={isSending}
                question={question}
                onQuestionChange={setQuestion}
                onSend={submitQuestion}
              />
            </div>
          </section>
        </main>
      </div>
    </section>
  )
}