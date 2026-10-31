import { CircleAlert, RotateCcw } from 'lucide-react'
import { content } from '../content'
import type { ChatFailure, ChatMessage } from '../hooks/useChat'
import { MessageBubble } from './MessageBubble'
import { TypingIndicator } from './TypingIndicator'

interface MessageListProps {
  messages: ChatMessage[]
  pending: boolean
  failure: ChatFailure | null
  onRetry: () => void
}

export function MessageList({ messages, pending, failure, onRetry }: MessageListProps) {
  return (
    <div className="messages" aria-live="polite">
      {messages.map((message) => (
        <MessageBubble key={message.id} message={message} />
      ))}
      {pending && <TypingIndicator />}
      {failure && (
        <div className="error-banner" role="alert">
          <CircleAlert size={18} aria-hidden="true" />
          <span className="error-banner__text">{content.errors[failure.kind]}</span>
          <button type="button" className="error-banner__retry" onClick={onRetry}>
            <RotateCcw size={14} aria-hidden="true" />
            {content.retry}
          </button>
        </div>
      )}
    </div>
  )
}
