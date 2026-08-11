import assert from 'node:assert/strict'
import { readdir, readFile } from 'node:fs/promises'
import path from 'node:path'
import test from 'node:test'

async function collectTsxFiles(directory: string): Promise<string[]> {
  const entries = await readdir(directory, { withFileTypes: true })
  const files = await Promise.all(entries.map(async entry => {
    const resolved = path.join(directory, entry.name)
    if (entry.isDirectory()) return collectTsxFiles(resolved)
    return entry.isFile() && entry.name.endsWith('.tsx') ? [resolved] : []
  }))

  return files.flat()
}

test('server components pass only serializable icon keys to EmptyState', async () => {
  const sourceRoot = path.join(process.cwd(), 'src')
  const files = await collectTsxFiles(sourceRoot)
  const offenders: string[] = []

  for (const file of files) {
    const source = await readFile(file, 'utf8')
    const isClientComponent = /^\s*(["'])use client\1/.test(source)
    if (isClientComponent || !source.includes('<EmptyState')) continue

    if (/<EmptyState\b[\s\S]*?\bicon\s*=\s*\{/.test(source)) {
      offenders.push(path.relative(process.cwd(), file))
    }
  }

  assert.deepEqual(
    offenders,
    [],
    `Server components must use EmptyState iconName instead of passing component functions: ${offenders.join(', ')}`,
  )
})
