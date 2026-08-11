export function getRequiredDemoPassword(): string {
  const password = process.env.DEMO_PASSWORD?.trim()
  if (!password) {
    throw new Error('DEMO_PASSWORD is required for Playwright demo-user authentication.')
  }
  return password
}
