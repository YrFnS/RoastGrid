#!/usr/bin/env python3
from pathlib import Path
import re


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f'{label}: expected exactly one match, found {count}')
    return text.replace(old, new, 1)


legacy_password = ''.join(['RoastGrid', 'Demo2026!'])

seed_path = Path('seed.ts')
seed = seed_path.read_text()
if seed.count(legacy_password) != 2:
    raise RuntimeError(
        f'seed.ts: expected two legacy password literals, found {seed.count(legacy_password)}',
    )
seed = replace_once(
    seed,
    "import * as schema from './src/lib/schema.ts'\n",
    "import * as schema from './src/lib/schema.ts'\nimport { getRequiredDemoSeedPassword } from './src/lib/demoSeed.ts'\n",
    'seed safety import',
)
seed = replace_once(
    seed,
    f"async function syncBrandIdentity() {{\n  const password = await hashPassword('{legacy_password}')",
    "async function syncBrandIdentity(password: string) {",
    'existing-database password reset',
)
seed = replace_once(
    seed,
    "async function seed() {\n  const existing = await db.select({ id: schema.users.id }).from(schema.users).limit(1)",
    "async function seed() {\n  const password = await hashPassword(getRequiredDemoSeedPassword())\n  const existing = await db.select({ id: schema.users.id }).from(schema.users).limit(1)",
    'seed guard',
)
seed = replace_once(
    seed,
    '    await syncBrandIdentity()',
    '    await syncBrandIdentity(password)',
    'guarded synchronization',
)
seed = replace_once(
    seed,
    f"\n  const password = await hashPassword('{legacy_password}')\n  const now = new Date()",
    "\n  const now = new Date()",
    'fresh-database password reset',
)
if legacy_password in seed:
    raise RuntimeError('seed.ts still contains the legacy shared password')
seed_path.write_text(seed)

Path('src/lib/demoSeed.ts').write_text("""type DemoSeedEnvironment = {
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
""")

Path('tests/unit/demo-seed.test.ts').write_text("""import assert from 'node:assert/strict'
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
""")

Path('tests/e2e/support').mkdir(parents=True, exist_ok=True)
Path('tests/e2e/support/demoCredentials.ts').write_text("""export function getRequiredDemoPassword(): string {
  const password = process.env.DEMO_PASSWORD?.trim()
  if (!password) {
    throw new Error('DEMO_PASSWORD is required for Playwright demo-user authentication.')
  }
  return password
}
""")

e2e_matches = 0
fallback = f"process.env.DEMO_PASSWORD ?? '{legacy_password}'"
for path in sorted(Path('tests/e2e').glob('*.spec.ts')):
    text = path.read_text()
    if fallback not in text:
        continue
    text = "import { getRequiredDemoPassword } from './support/demoCredentials.ts'\n" + text
    occurrences = text.count(fallback)
    text = text.replace(fallback, 'getRequiredDemoPassword()')
    path.write_text(text)
    e2e_matches += occurrences
if e2e_matches < 1:
    raise RuntimeError('No Playwright password fallbacks were replaced')

js_path = Path('scripts/e2e-screenshot.js')
js = js_path.read_text()
js = replace_once(
    js,
    "const BASE = 'http://213.199.56.120:3000';\nconst OUT = '/tmp';",
    "const BASE = (process.env.PLAYWRIGHT_BASE_URL || 'http://localhost:3000').replace(/\\/$/, '');\nconst OUT = '/tmp';\nconst DEMO_PASSWORD = process.env.DEMO_PASSWORD?.trim();\nif (!DEMO_PASSWORD) {\n  throw new Error('DEMO_PASSWORD is required for the authenticated screenshot flow.');\n}",
    'JavaScript screenshot configuration',
)
js = replace_once(
    js,
    f"await page.fill(\"input[type='password']\", '{legacy_password}');",
    "await page.fill(\"input[type='password']\", DEMO_PASSWORD);",
    'JavaScript screenshot password',
)
js_path.write_text(js)

py_path = Path('scripts/e2e-screenshot.py')
py = py_path.read_text()
py = replace_once(py, 'import asyncio\nimport sys\n', 'import asyncio\nimport os\nimport sys\n', 'Python screenshot environment import')
py = replace_once(
    py,
    'async def main():\n    base = "http://213.199.56.120:3000"',
    'async def main():\n    password = os.environ.get("DEMO_PASSWORD", "").strip()\n    if not password:\n        raise RuntimeError("DEMO_PASSWORD is required for the authenticated screenshot flow.")\n\n    base = os.environ.get("PLAYWRIGHT_BASE_URL", "http://localhost:3000").rstrip("/")',
    'Python screenshot configuration',
)
py = replace_once(
    py,
    f'await page.fill("input[type=\'password\']", "{legacy_password}")',
    'await page.fill("input[type=\'password\']", password)',
    'Python screenshot password',
)
py_path.write_text(py)

sign_in_path = Path('src/app/[locale]/sign-in/page.tsx')
sign_in = sign_in_path.read_text()
sign_in = replace_once(sign_in, "import { env } from '@/lib/env'\n", '', 'unused demo environment import')
sign_in = replace_once(
    sign_in,
    f"          {{env.DEMO_MODE && (\n            <p className=\"mt-5 text-center text-xs text-on-surface-variant\">\n              {{t('demo')}}: admin@roastgrid.app · {legacy_password}\n            </p>\n          )}}\n",
    '',
    'client-visible demo credential hint',
)
sign_in_path.write_text(sign_in)

workflow_path = Path('.github/workflows/ci.yml')
workflow = workflow_path.read_text()
workflow, count = re.subn(
    r'(?m)^      DEMO_PASSWORD:.*$',
    '      ALLOW_DEMO_SEED: "true"\n      DEMO_PASSWORD: "ci-browser-only-password-9Q7m-2026"',
    workflow,
)
if count != 1:
    raise RuntimeError(f'CI demo password: expected one match, found {count}')
workflow_path.write_text(workflow)

env_path = Path('.env.example')
env_text = env_path.read_text().rstrip() + """

# Demo seeding is blocked unless both values are deliberately configured.
ALLOW_DEMO_SEED=false
DEMO_PASSWORD=replace-with-a-unique-demo-password-at-least-16-characters
"""
env_path.write_text(env_text.rstrip() + '\n')

readme_path = Path('README.md')
readme = readme_path.read_text()
readme = replace_once(
    readme,
    "5. Optionally seed the local database with the demo roles and operational data:\n\n   ```bash\n   npm run seed\n   ```",
    "5. Seed only an isolated demo database. Set `ALLOW_DEMO_SEED=true` and provide a unique `DEMO_PASSWORD` of at least 16 characters, then run:\n\n   ```bash\n   npm run seed\n   ```\n\n   The command refuses to run without both values and may synchronize the demo users in an existing database.",
    'README seed instructions',
)
readme = replace_once(
    readme,
    "| `DEMO_MODE` | No | Exposes demo-only behavior when explicitly set to `true`; production must remain `false`. |",
    "| `DEMO_MODE` | No | Exposes demo-only behavior when explicitly set to `true`; production must remain `false`. |\n| `ALLOW_DEMO_SEED` | Seed only | Must be exactly `true` before the destructive demo seed can run. |\n| `DEMO_PASSWORD` | Seed/E2E only | Unique demo-user password; at least 16 characters and never a shared production credential. |",
    'README environment table',
)
readme = replace_once(
    readme,
    "`test:db`, `seed`, and the mutating browser scenarios must run against an isolated database, never the production Neon database.",
    "`test:db`, `seed`, and the mutating browser scenarios must run against an isolated database, never the production Neon database. The seed command additionally requires `ALLOW_DEMO_SEED=true` and a supplied `DEMO_PASSWORD`.",
    'README isolation warning',
)
readme_path.write_text(readme)

checklist_path = Path('docs/launch-checklist.md')
checklist = checklist_path.read_text()
checklist = replace_once(
    checklist,
    "> Run `npm run seed` only when the target is an isolated demo database. It populates new databases or synchronizes the RoastGrid identity, demo credentials, permissions, and settings in an existing demo database.",
    "> Run `npm run seed` only when the target is an isolated demo database. First set `ALLOW_DEMO_SEED=true` and provide a unique `DEMO_PASSWORD` of at least 16 characters. The command refuses to run otherwise because it populates new databases or synchronizes demo identities, credentials, permissions, and settings in an existing database.",
    'launch checklist seed safety',
)
checklist_path.write_text(checklist)

ignore_path = Path('.gitignore')
ignore = ignore_path.read_text()
ignore = replace_once(
    ignore,
    '# testing\n/coverage',
    '# testing\n/coverage\n/playwright-report/\n/test-results/',
    'browser artifact ignores',
)
ignore_path.write_text(ignore)

result_path = Path('test-results/.last-run.json')
if not result_path.exists():
    raise RuntimeError('Expected tracked Playwright result file was not found')
result_path.unlink()

unexpected = []
for path in Path('.').rglob('*'):
    if not path.is_file() or '.git' in path.parts:
        continue
    try:
        text = path.read_text()
    except UnicodeDecodeError:
        continue
    if legacy_password in text:
        unexpected.append(str(path))
if unexpected:
    raise RuntimeError(f'Legacy shared password remains in: {unexpected}')

Path('.github/workflows/seed-safety-patch.yml').unlink()
Path('scripts/apply-seed-safety-hardening.py').unlink()
