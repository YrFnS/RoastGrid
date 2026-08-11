type DemoSeedEnvironment = {
  ALLOW_DEMO_SEED?: string
  DEMO_PASSWORD?: string
}

export function getRequiredDemoSeedPassword(
  environment: DemoSeedEnvironment = process.env,
): string {
  if (environment.ALLOW_DEMO_SEED?.trim().toLowerCase() !== 'true') {
    throw new Error(
      'Demo seeding is disabled. Set ALLOW_DEMO_SEED=true only for an isolated demo or test database.',
    )
  }

  const password = environment.DEMO_PASSWORD?.trim()
  if (!password) {
    throw new Error('DEMO_PASSWORD is required when demo seeding is enabled.')
  }
  if (password.length < 16) {
    throw new Error('DEMO_PASSWORD must contain at least 16 characters.')
  }

  const normalized = password.toLowerCase()
  if (normalized.startsWith('replace-with-') || normalized.includes('roastgriddemo')) {
    throw new Error(
      'DEMO_PASSWORD must be a unique value, not a placeholder or shared legacy credential.',
    )
  }

  return password
}
