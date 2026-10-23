# TypeFlow

A private-first typing simulation studio. This branch runs on **Next.js and Vercel**.

## Run

Node.js 22.13+ and npm:

```
npm ci
npm run dev
npm run build
npm start
node --test tests/*.test.mjs
```

## Deploy on Vercel

Import this repository with Root Directory `./`. The committed `vercel.json` selects **Next.js**, uses `npm ci`, builds with `npm run build` and serves `.next`. A push to the connected `main` branch should create a new deployment. If your existing project has old settings, use Next.js as the framework and remove conflicting custom settings; do not use the old `dist` Worker output as a static site.

## Available now

- Responsive navy/teal studio with local text input/import and live typing preview.
- WPM/variation, sentence/paragraph pauses, periodic long pauses with automatic resume, typo correction, countdown, boost, pause/resume, stop/Escape, progress and stats.
- Source/settings persist in this browser. Clear local text from Account.
- Two **device-local** named profiles: create, restore, update, rename, duplicate and delete. These are not cloud accounts and do not sync across browsers.
- All local studio controls are available as a launch preview; no paid subscription is claimed.

## Setup still required

Cloud accounts, cloud profile sync, password recovery, cloud trials, owner administration and aggregate analytics require a Vercel-compatible authenticated backend. The account API returns `503 BACKEND_NOT_CONFIGURED`; admin returns `404`. No client identity header is treated as proof of authentication on Vercel. Account setup explains the current status rather than offering a non-working login.

No payment or email provider is configured. Pro $9/month and Team $39/month (five accounts) are planned pricing only. Checkout, verified payment webhooks, activation codes, activation emails, subscription lifecycle and Team memberships/invitations/seat limits are unavailable. No fake payment, activation, customer or revenue data is produced, and no payment is collected.

The previous Sites-only backend is preserved in `platforms/sites/`, alongside its original instructions. It relies on the Sites dispatch authentication boundary and Cloudflare D1, and is **not connected to the Vercel app**. Original source is also retained in Git history. D1 schema/migrations and cloud SQL tests remain available for a future backend migration.

## Payment integration requirements

Before enabling billing, implement provider-secret checkout with server price IDs, signature-verified raw webhook requests, unique event/payment IDs and idempotent transactions. Never trust a browser success flag. Bind payment records to authenticated user IDs. Issue cryptographically random one-use activation codes only after verified payment, store hashes, show them only to the owning account and queue email via an idempotent outbox. Enforce expiry/downgrade on the server while retaining profiles. Count active members plus pending invitations when reserving the five Team seats. Provision the owner explicitly and use provider-supported 2FA.

## Privacy and source

Source text stays in this browser. Device profiles store control settings only. Files containing secrets, node_modules, build output and local runtime data are excluded from source control. `.env.example` contains names only; no credentials are required for the local studio.
