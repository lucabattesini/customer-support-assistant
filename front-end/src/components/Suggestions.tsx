import { Clock, CreditCard, Guitar, type LucideIcon, MapPin, Tag, Undo2 } from 'lucide-react'
import { content, type SuggestionIcon } from '../content'
import { BrandMark } from './BrandMark'

const ICONS: Record<SuggestionIcon, LucideIcon> = {
  guitar: Guitar,
  tag: Tag,
  pin: MapPin,
  return: Undo2,
  clock: Clock,
  card: CreditCard,
}

interface SuggestionsProps {
  onSelect: (text: string) => void
}

export function Suggestions({ onSelect }: SuggestionsProps) {
  return (
    <section className="welcome">
      <BrandMark size="large" />
      <h2 className="welcome__title">{content.welcomeTitle}</h2>
      <p className="welcome__text">{content.welcomeText}</p>
      <ul className="suggestions">
        {content.suggestions.map((suggestion) => {
          const Icon = ICONS[suggestion.icon]
          return (
            <li key={suggestion.message}>
              <button
                type="button"
                className="suggestion"
                onClick={() => onSelect(suggestion.message)}
              >
                <span className="suggestion__icon" aria-hidden="true">
                  <Icon size={18} />
                </span>
                <span className="suggestion__body">
                  <span className="suggestion__title">{suggestion.title}</span>
                  <span className="suggestion__message">{suggestion.message}</span>
                </span>
              </button>
            </li>
          )
        })}
      </ul>
    </section>
  )
}
