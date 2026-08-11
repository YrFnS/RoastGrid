const defaultTrustedAuthOrigins = [
  'https://caffe-ya.vercel.app',
  'https://roastgrid-yasserreyadh-gmailcoms-projects.vercel.app',
  'https://roastgrid-*-yasserreyadh-gmailcoms-projects.vercel.app',
] as const

function normalizeOrigin(value: string | undefined) {
  const trimmed = value?.trim()
  if (!trimmed) return null

  if (trimmed.includes('*')) {
    return /^https?:\/\/[^/]+$/.test(trimmed)
      ? trimmed.replace(/\/+$/, '')
      : null
  }

  try {
    return new URL(trimmed).origin
  } catch {
    return null
  }
}

function asHttpsOrigin(value: string | undefined) {
  const trimmed = value?.trim()
  if (!trimmed) return null
  return trimmed.startsWith('http://') || trimmed.startsWith('https://')
    ? trimmed
    : `https://${trimmed}`
}

export function buildTrustedAuthOrigins(
  baseUrl: string,
  runtimeEnv: Record<string, string | undefined> = process.env,
) {
  const configuredOrigins = (runtimeEnv.BETTER_AUTH_TRUSTED_ORIGINS ?? '').split(',')
  const candidates = [
    baseUrl,
    ...defaultTrustedAuthOrigins,
    asHttpsOrigin(runtimeEnv.VERCEL_URL),
    asHttpsOrigin(runtimeEnv.VERCEL_PROJECT_PRODUCTION_URL),
    ...configuredOrigins,
  ]

  const normalized = candidates
    .map(value => normalizeOrigin(value ?? undefined))
    .filter((value): value is string => Boolean(value))

  return [...new Set(normalized)]
}

const sslModesThatCurrentlyAliasVerifyFull = new Set([
  'prefer',
  'require',
  'verify-ca',
])

export function normalizeDatabaseUrl(connectionString: string) {
  try {
    const url = new URL(connectionString)
    const sslMode = url.searchParams.get('sslmode')

    if (!sslMode || !sslModesThatCurrentlyAliasVerifyFull.has(sslMode)) {
      return connectionString
    }

    url.searchParams.set('sslmode', 'verify-full')
    return url.toString()
  } catch {
    return connectionString
  }
}
