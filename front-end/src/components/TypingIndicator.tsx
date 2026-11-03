import { content } from '../content'
import { BrandMark } from './BrandMark'

export function TypingIndicator() {
  return (
    <div className="message message--assistant" role="status" aria-label={content.typingLabel}>
      <BrandMark />
      <div className="typing">
        <span />
        <span />
        <span />
      </div>
    </div>
  )
}
