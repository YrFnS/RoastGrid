# RoastGrid Launch Checklist

RoastGrid is a bilingual Next.js operations app hosted on Vercel, with Better Auth and a PostgreSQL database on Neon. Expected demo cost: **$0/month** on the Vercel and Neon free tiers. Estimated hands-on time: **45–75 minutes**.

Legend: 🧑 **You** — owner action · 🤖 **Agent** — code/CLI action · 🤝 **Together** — shared verification

## Phase 0 — Deployment blockers

- [x] 🤖 **Repair the dependency lockfile** — 10 minutes. Keep `package-lock.json` current so Vercel installs the exact tested packages.
  > Verify the committed lockfile with `npm ci --no-audit --no-fund`, then run `npm run build`.
  **You'll know it worked when:** both commands exit successfully without changing `package-lock.json`.

- [x] 🤖 **Set the production auth URL explicitly** — 5 minutes. Better Auth uses this URL to trust login requests and redirects.
  > Configure Better Auth with the validated `BETTER_AUTH_URL` environment variable. Add any extra public aliases to `BETTER_AUTH_TRUSTED_ORIGINS` when they are not already covered by the application defaults.
  **You'll know it worked when:** production login reaches the dashboard without an origin or callback error.

## Phase 1 — Accounts and prerequisites

- [x] 🤖 **Use the existing Vercel and Neon accounts** — 5 minutes. Both services have suitable free tiers for a client demo.
  > Create a Neon project in the existing organization and link this repository to Vercel.
  **You'll know it worked when:** both CLIs return the new project without prompting for another account.

## Phase 2 — Secrets and configuration

- [x] 🤖 **Store production settings in Vercel** — 5 minutes. An environment variable is a setting stored outside Git, which keeps database credentials and auth secrets out of the repository.
  > Add `DATABASE_URL`, `BETTER_AUTH_SECRET`, and `BETTER_AUTH_URL` to Vercel Production without printing or committing their values.
  **You'll know it worked when:** Vercel lists all three names for Production and the app boots successfully.

- [x] 🤖 **Keep secrets out of Git** — 2 minutes.
  > Confirm `.env*`, Neon local context, and Vercel local context files are ignored; scan the pending diff for credentials.
  **You'll know it worked when:** `git diff` contains no connection string, password hash, or auth secret.

## Phase 3 — Production database

- [x] 🤖 **Create and migrate Neon PostgreSQL** — 10 minutes. A migration creates the tables and relationships the app expects.
  > Run `npm run db:migrate` against the production Neon connection and fail if any committed migration is rejected. Do not use `db:push` on production or shared databases.
  **You'll know it worked when:** Drizzle reports the committed migration history applied successfully.

- [x] 🤖 **Seed meaningful demo data** — 5 minutes.
  > Run `npm run seed` only when the target is an isolated demo database. It populates new databases or synchronizes the RoastGrid identity, demo credentials, permissions, and settings in an existing demo database.
  **You'll know it worked when:** every demo-domain table has at least one row and all foreign keys resolve.

## Phase 4 — Deploy the app

- [x] 🤖 **Deploy the production build to Vercel** — 10–20 minutes.
  > Link `YrFnS/RoastGrid`, add the production environment variables, deploy `main`, and confirm the canonical alias becomes Ready.
  **You'll know it worked when:** the public Vercel URL returns the bilingual sign-in screen over HTTPS.

## Phase 5 — Domain

- [x] 🤖 **Use the Vercel HTTPS domain for this demo** — no extra time or cost. DNS is the address book that maps a custom name to the deployed app; a custom domain is unnecessary for the requested client demo.
  > Confirm the canonical `.vercel.app` URL is stable and uses HTTPS.
  **You'll know it worked when:** the canonical URL opens without a certificate warning.

## Phase 6 — Pre-demo verification

- [x] 🤖 **Run the production browser journey** — 15–25 minutes.
  > Sign in fresh as every seeded role, verify protected routing, dashboard data, POS products and resources, complete one representative mutation, sign out, and repeat in Arabic RTL.
  **You'll know it worked when:** each role reaches protected data, the mutation persists in Neon, and sign-out returns to sign-in.
  > Revalidated 2026-08-11: the isolated Chromium suite completed 17/17 tests with no skips, covering all four active roles, disabled-user rejection, protected routes, POS and gaming operations, procurement, reports, product recipes, responsive layouts, and Arabic RTL.

- [ ] 🤝 **Do the final client-device check** — 5 minutes.
  > Open the final URL once on the device used for the presentation and keep the demo credentials available privately.
  **You'll know it worked when:** the sign-in screen and dashboard fit the display without horizontal clipping.

## Phase 7 — After the demo

- [ ] 🧑 **Choose whether this becomes a real production system** — 15 minutes, no immediate cost. Real operations would need named employee accounts, a custom domain, monitoring, a backup policy, and credential rotation.
  Go to the Vercel project settings and Neon project settings only after the client approves continued use. Do not share production secrets in chat.
  **You'll know it worked when:** ownership, billing, backup retention, and the production domain have named owners.

No payment gateway, email provider, object storage, analytics, or external AI service is currently required by the codebase.
