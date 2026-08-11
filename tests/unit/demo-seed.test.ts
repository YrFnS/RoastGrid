import assert from 'node:assert/strict'
import test from 'node:test'
import { getRequiredDemoSeedPassword } from '../../src/lib/demoSeed.ts'

test('demo seeding requires an explicit isolated-database opt-in', () => {
  assert.throws(
    () => getRequiredDemoSeedPassword({ DEMO_PASSWORD: 'unique-demo-password-42!' }),
    /ALLOW_DEMO_SEED=true/,
  )
})

test('demo seeding requires a sufficiently long supplied password', () => {
  assert.throws(
    () => getRequiredDemoSeedPassword({ ALLOW_DEMO_SEED: 'true' }),
    /DEMO_PASSWORD is required/,
  )
  assert.throws(
    () => getRequiredDemoSeedPassword({
      ALLOW_DEMO_SEED: 'true',
      DEMO_PASSWORD: 'too-short',
    }),
    /at least 16 characters/,
  )
})

test('demo seeding rejects placeholders and legacy shared credentials', () => {
  assert.throws(
    () => getRequiredDemoSeedPassword({
      ALLOW_DEMO_SEED: 'true',
      DEMO_PASSWORD: 'replace-with-a-unique-demo-password',
    }),
    /unique value/,
  )
  assert.throws(
    () => getRequiredDemoSeedPassword({
      ALLOW_DEMO_SEED: 'TRUE',
      DEMO_PASSWORD: 'roastgriddemo-shared-credential',
    }),
    /unique value/,
  )
})

test('demo seeding returns a trimmed, unique password after validation', () => {
  assert.equal(
    getRequiredDemoSeedPassword({
      ALLOW_DEMO_SEED: ' true ',
      DEMO_PASSWORD: '  isolated-browser-password-42!  ',
    }),
    'isolated-browser-password-42!',
  )
})
