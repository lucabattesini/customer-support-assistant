import { API_URL } from '../config'

export interface ChatReply {
  threadId: string
  reply: string
}

export type ChatErrorKind = 'unavailable' | 'invalid' | 'network'

export class ChatApiError extends Error {
  readonly kind: ChatErrorKind

  constructor(kind: ChatErrorKind, message: string) {
    super(message)
    this.kind = kind
  }
}

export async function sendMessage(message: string, threadId: string | null): Promise<ChatReply> {
  let response: Response
  try {
    response = await fetch(`${API_URL}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, thread_id: threadId }),
    })
  } catch (error) {
    throw new ChatApiError('network', String(error))
  }

  if (!response.ok) {
    const kind: ChatErrorKind = response.status === 422 ? 'invalid' : 'unavailable'
    throw new ChatApiError(kind, `HTTP ${response.status}`)
  }

  const body = (await response.json()) as { thread_id: string; reply: string }
  return { threadId: body.thread_id, reply: body.reply }
}
