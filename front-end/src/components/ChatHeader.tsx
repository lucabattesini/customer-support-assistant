import { SquarePen } from 'lucide-react'
import { content } from '../content'
import { BrandMark } from './BrandMark'

interface ChatHeaderProps {
  canReset: boolean
  onReset: () => void
}

export function ChatHeader({ canReset, onReset }: ChatHeaderProps) {
  return (
    <header className="header">
      <div className="header__inner">
        <div className="header__identity">
          <BrandMark size="medium" />
          <div>
            <h1 className="header__title">{content.title}</h1>
            <p className="header__status">
              <span className="status-dot" aria-hidden="true" />
              {content.status}
            </p>
          </div>
        </div>
        <button type="button" className="ghost-button" onClick={onReset} disabled={!canReset}>
          <SquarePen size={16} aria-hidden="true" />
          <span>{content.newConversation}</span>
        </button>
      </div>
    </header>
  )
}
