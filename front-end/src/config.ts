function requireEnv(name: string, value: string | undefined): string {
  if (!value?.trim()) {
    throw new Error(`Missing environment variable ${name}. Set it in front-end/.env.`)
  }
  return value.trim()
}

export const API_URL = requireEnv('VITE_API_URL', import.meta.env.VITE_API_URL).replace(/\/+$/, '')
