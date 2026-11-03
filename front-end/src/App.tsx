import { useEffect, useRef } from 'react'
import { ChatHeader } from './components/ChatHeader'
import { Composer } from './components/Composer'
import { MessageList } from './components/MessageList'
import { Suggestions } from './components/Suggestions'
import { useChat } from './hooks/useChat'

export default function App() {
  const { messages, pending, failure, send, retry, reset } = useChat()
  const conversationRef = useRef<HTMLElement>(null)
  const isEmpty = messages.length === 0 && !pending

  useEffect(() => {
    const conversation = conversationRef.current
    if (conversation) {
      conversation.scrollTo({ top: conversation.scrollHeight, behavior: 'smooth' })
    }
  }, [messages, pending, failure])

  return (
    <div className="app">
      <ChatHeader canReset={!isEmpty} onReset={reset} />
      <main ref={conversationRef} className="conversation">
        <div className="conversation__inner">
          {isEmpty ? (
            <Suggestions onSelect={send} />
          ) : (
            <MessageList messages={messages} pending={pending} failure={failure} onRetry={retry} />
          )}
        </div>
      </main>
      <Composer disabled={pending} onSend={send} />
    </div>
  )
}
