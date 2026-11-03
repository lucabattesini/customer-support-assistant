import { useCallback, useRef, useState } from 'react'
import { ChatApiError, type ChatErrorKind, sendMessage } from '../api/chat'

export type Role = 'user' | 'assistant'

export interface ChatMessage {
  id: string
  role: Role
  text: string
}

export interface ChatFailure {
  kind: ChatErrorKind
  message: string
}

function createId(): string {
  return crypto.randomUUID()
}

export function useChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [pending, setPending] = useState(false)
  const [failure, setFailure] = useState<ChatFailure | null>(null)
  const threadId = useRef<string | null>(null)
  const conversation = useRef(0)

  const send = useCallback(
    async (text: string) => {
      const message = text.trim()
      if (!message || pending) {
        return
      }
      const conversationAtSend = conversation.current
      setFailure(null)
      setPending(true)
      setMessages((current) => [...current, { id: createId(), role: 'user', text: message }])
      try {
        const result = await sendMessage(message, threadId.current)
        if (conversationAtSend !== conversation.current) {
          return
        }
        threadId.current = result.threadId
        setMessages((current) => [
          ...current,
          { id: createId(), role: 'assistant', text: result.reply },
        ])
      } catch (error) {
        if (conversationAtSend !== conversation.current) {
          return
        }
        const kind = error instanceof ChatApiError ? error.kind : 'unavailable'
        setFailure({ kind, message })
      } finally {
        if (conversationAtSend === conversation.current) {
          setPending(false)
        }
      }
    },
    [pending],
  )

  const retry = useCallback(() => {
    if (!failure) {
      return
    }
    const { message } = failure
    setMessages((current) => {
      const last = current.at(-1)
      return last?.role === 'user' && last.text === message ? current.slice(0, -1) : current
    })
    void send(message)
  }, [failure, send])

  const reset = useCallback(() => {
    conversation.current += 1
    threadId.current = null
    setMessages([])
    setFailure(null)
    setPending(false)
  }, [])

  return { messages, pending, failure, send, retry, reset }
}
