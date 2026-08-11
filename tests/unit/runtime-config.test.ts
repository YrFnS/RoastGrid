import assert from 'node:assert/strict'
import test from 'node:test'
import {
  buildTrustedAuthOrigins,
  normalizeDatabaseUrl,
} from '../../src/lib/runtimeConfig.ts'

test('database URLs keep certificate verification explicit', () => {
  assert.equal(
    normalizeDatabaseUrl('postgresql://user:password@example.com/roastgrid?sslmode=require'),
    'postgresql://user:password@example.com/roastgrid?sslmode=verify-full',
  )
  assert.equal(
    normalizeDatabaseUrl('postgresql://user:password@example.com/roastgrid?sslmode=disable'),
    'postgresql://user:password@example.com/roastgrid?sslmode=disable',
  )
  assert.equal(normalizeDatabaseUrl('not-a-database-url'), 'not-a-database-url')
})

test('auth origins include the public alias and account-scoped Vercel deployments', () => {
  const origins = buildTrustedAuthOrigins('https://primary.example.com/', {
    VERCEL_URL: 'roastgrid-preview-yasserreyadh-gmailcoms-projects.vercel.app',
    VERCEL_PROJECT_PRODUCTION_URL: 'roastgrid-yasserreyadh-gmailcoms-projects.vercel.app',
    BETTER_AUTH_TRUSTED_ORIGINS: 'https://ops.example.com, https://primary.example.com',
  })

  assert.equal(origins.includes('https://primary.example.com'), true)
  assert.equal(origins.includes('https://caffe-ya.vercel.app'), true)
  assert.equal(
    origins.includes('https://roastgrid-*-yasserreyadh-gmailcoms-projects.vercel.app'),
    true,
  )
  assert.equal(
    origins.includes('https://roastgrid-preview-yasserreyadh-gmailcoms-projects.vercel.app'),
    true,
  )
  assert.equal(origins.includes('https://ops.example.com'), true)
  assert.equal(new Set(origins).size, origins.length)
})
