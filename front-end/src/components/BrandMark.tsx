import { Music2 } from 'lucide-react'

interface BrandMarkProps {
  size?: 'small' | 'medium' | 'large'
}

const ICON_SIZES = { small: 14, medium: 18, large: 28 }

export function BrandMark({ size = 'small' }: BrandMarkProps) {
  return (
    <span className={`brand-mark brand-mark--${size}`} aria-hidden="true">
      <Music2 size={ICON_SIZES[size]} strokeWidth={2.25} />
    </span>
  )
}
