import type { ChatMessage as ChatMessageType } from '../../types/chat'
import { TypingDots } from '../atoms/TypingDots'

interface ChatMessageProps {
  message: ChatMessageType
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === 'user'

  return (
    <article
      className={[
        'flex w-full animate-[fade-in_180ms_ease-out] flex-col gap-2',
        isUser ? 'items-end' : 'items-start',
      ].join(' ')}
    >
      <div
        className={[
          'max-w-[min(44rem,100%)] rounded-[1.5rem] px-4 py-3 text-sm leading-6 shadow-[0_16px_30px_-22px_rgba(15,23,42,0.45)] ring-1 ring-inset',
          isUser
            ? 'rounded-br-md bg-slate-950 text-white ring-slate-950/10'
            : 'rounded-bl-md bg-white/85 text-slate-700 ring-slate-200/80',
        ].join(' ')}
      >
        <p className="whitespace-pre-wrap break-words">{message.content}</p>
        {message.isLoading ? (
          <span className="mt-3 inline-flex items-center gap-2 text-xs font-medium text-teal-600">
            <TypingDots />
            Respondendo
          </span>
        ) : null}
      </div>
    </article>
  )
}