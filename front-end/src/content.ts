export type SuggestionIcon = 'guitar' | 'tag' | 'pin' | 'return' | 'clock' | 'card'

export interface Suggestion {
  icon: SuggestionIcon
  title: string
  message: string
}

export const content = {
  title: 'Assistente virtual',
  status: 'Online agora',
  newConversation: 'Nova conversa',
  welcomeTitle: 'Olá! Como posso ajudar?',
  welcomeText:
    'Tire dúvidas sobre instrumentos, preços, pedidos e políticas da loja. Escolha um exemplo ou escreva sua pergunta.',
  inputPlaceholder: 'Pergunte sobre instrumentos, pedidos ou políticas...',
  inputLabel: 'Mensagem',
  sendLabel: 'Enviar mensagem',
  typingLabel: 'O assistente está digitando',
  disclaimer: 'O assistente pode cometer erros. Para casos importantes, confirme com a equipe da loja.',
  errors: {
    unavailable: 'Não consegui responder agora. Tente novamente em instantes.',
    invalid: 'Não consegui enviar essa mensagem. Confira o texto e tente de novo.',
    network: 'Não foi possível conectar ao servidor. Verifique se a API está rodando.',
  },
  retry: 'Tentar novamente',
  suggestions: [
    {
      icon: 'guitar',
      title: 'Violões até R$ 1.000',
      message: 'Quais opções de violões disponíveis custando até R$1000?',
    },
    {
      icon: 'tag',
      title: 'Preço de um modelo',
      message: 'Quanto custa o Takamine GD20?',
    },
    {
      icon: 'pin',
      title: 'Endereço da loja',
      message: 'Qual o endereço da loja?',
    },
    {
      icon: 'return',
      title: 'Devolução de pedido',
      message: 'Me arrependi da minha compra, posso devolver meu pedido?',
    },
    {
      icon: 'clock',
      title: 'Horário de funcionamento',
      message: 'Vocês estão abertos agora?',
    },
    {
      icon: 'card',
      title: 'Formas de pagamento',
      message: 'Quais as formas de pagamento e parcelamento?',
    },
  ] satisfies Suggestion[],
} as const
