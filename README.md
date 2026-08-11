# RoastGrid

RoastGrid is a bilingual coffee-shop and gaming-center operations system built with Next.js. It combines role-aware POS, live gaming-resource management, shifts, inventory and weighted valuation, procurement, accounting, payroll, reports, audit history, and Arabic/English layouts.

## Stack

- Next.js 16 and React 19
- TypeScript
- PostgreSQL with Drizzle ORM
- Better Auth
- next-intl for Arabic and English
- Tailwind CSS
- Playwright for browser coverage

## Requirements

- Node.js 22.6 or newer
- npm
- Docker with Docker Compose

## Local setup

1. Install the exact locked dependencies:

   ```bash
   npm ci
   ```

2. Create a local environment file and replace the placeholder auth secret:

   ```bash
   cp .env.example .env
   ```

   `BETTER_AUTH_SECRET` must be unique and at least 32 characters. Keep `DEMO_MODE=false` unless the database is an isolated demonstration environment.

3. Start PostgreSQL:

   ```bash
   docker compose up -d
   ```

4. Apply the committed migrations:

   ```bash
   npm run db:migrate
   ```

5. Optionally seed the local database with the demo roles and operational data:

   ```bash
   npm run seed
   ```

6. Start the app:

   ```bash
   npm run dev
   ```

Open `http://localhost:3000`.

Do not use `db:push` against production or a shared database. Production and shared environments must advance through the committed migration history with `npm run db:migrate`.

## Verification

The main verification commands are:

```bash
npm run lint
npm run typecheck
npm run test
npm run db:migrate
npm run test:db
npm run build
npm run test:e2e
```

`test:db`, `seed`, and the mutating browser scenarios must run against an isolated database, never the production Neon database. GitHub Actions provisions disposable PostgreSQL services for the full verification and Chromium suites.

## Environment variables

| Variable | Required | Purpose |
| --- | --- | --- |
| `DATABASE_URL` | Yes | PostgreSQL connection used by the app, migrations, and scripts. |
| `BETTER_AUTH_SECRET` | Yes | Unique Better Auth signing secret with at least 32 characters. |
| `BETTER_AUTH_URL` | Yes | Canonical public origin users open in the browser. |
| `BETTER_AUTH_TRUSTED_ORIGINS` | No | Comma-separated additional trusted aliases. |
| `DEMO_MODE` | No | Exposes demo-only behavior when explicitly set to `true`; production must remain `false`. |

See `.env.example` for local defaults.

## Project structure

```text
src/
├── app/          # App Router pages, layouts, and route handlers
├── components/   # Shared interface components
├── features/     # Business modules and server actions
├── lib/          # Auth, database, schema, configuration, and utilities
└── messages/     # Arabic and English translations

drizzle/          # Ordered database migrations
tests/             # Unit, database integration, and Playwright suites
docs/              # Implementation and launch documentation
```

## Deployment

Before a production deployment:

1. Configure the required environment variables in the hosting platform.
2. Apply `npm run db:migrate` to the target PostgreSQL database.
3. Keep `DEMO_MODE=false`.
4. Run the full CI verification against an isolated database.
5. Verify the final production alias and role-based sign-in flows.

The operational deployment checklist is in `docs/launch-checklist.md`.
