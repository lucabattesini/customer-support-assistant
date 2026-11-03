import Markdown, { type Components } from 'react-markdown'
import remarkBreaks from 'remark-breaks'
import remarkGfm from 'remark-gfm'
import type { ChatMessage } from '../hooks/useChat'
import { BrandMark } from './BrandMark'

const markdownComponents: Components = {
  a: ({ children, href }) => (
    <a href={href} target="_blank" rel="noopener noreferrer">
      {children}
    </a>
  ),
}

interface MessageBubbleProps {
  message: ChatMessage
}

export function MessageBubble({ message }: MessageBubbleProps) {
  if (message.role === 'user') {
    return (
      <div className="message message--user">
        <div className="bubble-user">{message.text}</div>
      </div>
    )
  }

  return (
    <div className="message message--assistant">
      <BrandMark />
      <div className="assistant-text markdown">
        <Markdown remarkPlugins={[remarkGfm, remarkBreaks]} components={markdownComponents}>
          {message.text}
        </Markdown>
      </div>
    </div>
  )
}
