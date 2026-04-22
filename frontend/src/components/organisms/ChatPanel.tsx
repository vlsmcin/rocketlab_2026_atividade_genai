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
    <section className="grid min-h-screen grid-rows-[auto_1fr_auto] px-4 py-6 sm:px-6 lg:px-8">
      <header className="mx-auto flex w-full max-w-6xl items-center justify-between gap-4 rounded-[2rem] border border-white/60 bg-white/70 px-5 py-4 shadow-[0_20px_50px_-28px_rgba(15,23,42,0.45)] backdrop-blur">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.35em] text-teal-700">
            Rocketlab Chat
          </p>
          <h1 className="mt-1 text-xl font-semibold tracking-tight text-slate-950 sm:text-2xl">
            Chat simples para perguntas e respostas
          </h1>
        </div>

        <div className="hidden rounded-full border border-teal-200 bg-teal-50 px-4 py-2 text-sm font-medium text-teal-700 sm:block">
          Conectado ao backend em `/ask`
        </div>
      </header>

      <main className="mx-auto flex w-full max-w-6xl flex-col gap-4 py-6">
        <div className="grid flex-1 gap-4 lg:grid-cols-[minmax(0,1.4fr)_18rem]">
          <section className="flex min-h-[32rem] flex-col rounded-[2.25rem] border border-white/70 bg-white/80 p-4 shadow-[0_24px_60px_-32px_rgba(15,23,42,0.55)] backdrop-blur">
            <div className="mb-4 flex items-center justify-between gap-3 border-b border-slate-200/80 pb-4">
              <div>
                <p className="text-sm font-medium text-slate-500">Conversa</p>
                <p className="text-base font-semibold text-slate-950">
                  Resposta em tempo real, sem histórico persistido
                </p>
              </div>

              <span className="rounded-full bg-slate-950 px-3 py-1 text-xs font-semibold uppercase tracking-[0.28em] text-white">
                Live
              </span>
            </div>

            <div className="flex-1 space-y-4 overflow-y-auto pr-1">
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
          </section>

          <aside className="flex flex-col gap-4 rounded-[2.25rem] border border-slate-200/70 bg-slate-950 p-6 text-white shadow-[0_24px_60px_-36px_rgba(15,23,42,0.8)]">
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
        </div>
      </main>

      <footer className="mx-auto w-full max-w-6xl pb-2">
        <ChatComposer
          isSending={isSending}
          question={question}
          onQuestionChange={setQuestion}
          onSend={submitQuestion}
        />
      </footer>
    </section>
  )
}