import { drizzle } from 'drizzle-orm/node-postgres'
import { Pool } from 'pg'
import { env } from './env.ts'
import { normalizeDatabaseUrl } from './runtimeConfig.ts'
import * as schema from './schema.ts'

export const dbPool = new Pool({
  connectionString: normalizeDatabaseUrl(env.DATABASE_URL),
})

export const db = drizzle(dbPool, { schema })

export type Database = typeof db
