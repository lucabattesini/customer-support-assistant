export type SuggestionIcon = 'guitar' | 'tag' | 'pin' | 'return' | 'clock' | 'card'

export interface Suggestion {
  icon: SuggestionIcon
  title: string
  message: string
}

export const content = {
  title: 'Virtual assistant',
  status: 'Online now',
  newConversation: 'New conversation',
  welcomeTitle: 'Hi! How can I help?',
  welcomeText:
    'Ask about instruments, prices, orders and store policies. Pick an example or type your question.',
  inputPlaceholder: 'Ask about instruments, orders or policies...',
  inputLabel: 'Message',
  sendLabel: 'Send message',
  typingLabel: 'The assistant is typing',
  disclaimer: 'The assistant can make mistakes. For important matters, confirm with the store team.',
  errors: {
    unavailable: 'I could not answer right now. Please try again in a moment.',
    invalid: 'I could not send this message. Check the text and try again.',
    network: 'Could not reach the server. Check that the API is running.',
  },
  retry: 'Try again',
  suggestions: [
    {
      icon: 'guitar',
      title: 'Acoustic guitars up to R$ 1,000',
      message: 'Which acoustic guitars do you have for up to R$1000?',
    },
    {
      icon: 'tag',
      title: 'Price of a model',
      message: 'How much is the Takamine GD20?',
    },
    {
      icon: 'pin',
      title: 'Store address',
      message: "What's the store address?",
    },
    {
      icon: 'return',
      title: 'Return an order',
      message: 'I regret my purchase, can I return my order?',
    },
    {
      icon: 'clock',
      title: 'Opening hours',
      message: 'Are you open now?',
    },
    {
      icon: 'card',
      title: 'Payment methods',
      message: 'What payment and installment options do you have?',
    },
  ] satisfies Suggestion[],
} as const
