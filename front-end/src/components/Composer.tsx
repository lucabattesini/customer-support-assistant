import { ArrowUp } from 'lucide-react'
import {
  type FormEvent,
  type KeyboardEvent,
  useEffect,
  useLayoutEffect,
  useRef,
  useState,
} from 'react'
import { content } from '../content'

const MAX_TEXTAREA_HEIGHT = 168

interface ComposerProps {
  disabled: boolean
  onSend: (text: string) => void
}

export function Composer({ disabled, onSend }: ComposerProps) {
  const [text, setText] = useState('')
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  useLayoutEffect(() => {
    const textarea = textareaRef.current
    if (!textarea) {
      return
    }
    textarea.style.height = '0px'
    const fullHeight = textarea.scrollHeight
    textarea.style.height = `${Math.min(fullHeight, MAX_TEXTAREA_HEIGHT)}px`
    textarea.style.overflowY = fullHeight > MAX_TEXTAREA_HEIGHT ? 'auto' : 'hidden'
  }, [text])

  useEffect(() => {
    if (!disabled) {
      textareaRef.current?.focus()
    }
  }, [disabled])

  const canSend = !disabled && text.trim().length > 0

  const submit = () => {
    if (!canSend) {
      return
    }
    onSend(text)
    setText('')
  }

  const handleSubmit = (event: FormEvent) => {
    event.preventDefault()
    submit()
  }

  const handleKeyDown = (event: KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === 'Enter' && !event.shiftKey && !event.nativeEvent.isComposing) {
      event.preventDefault()
      submit()
    }
  }

  return (
    <footer className="composer">
      <form className="composer__inner" onSubmit={handleSubmit}>
        <div className="composer__box">
          <textarea
            ref={textareaRef}
            className="composer__input"
            value={text}
            onChange={(event) => setText(event.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={content.inputPlaceholder}
            aria-label={content.inputLabel}
            rows={1}
          />
          <button
            type="submit"
            className="send-button"
            disabled={!canSend}
            aria-label={content.sendLabel}
          >
            <ArrowUp size={18} strokeWidth={2.5} aria-hidden="true" />
          </button>
        </div>
        <p className="composer__hint">{content.disclaimer}</p>
      </form>
    </footer>
  )
}
