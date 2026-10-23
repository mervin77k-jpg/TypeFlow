# TypeFlow

Premium dark typing simulation studio for legitimate demos, accessibility and testing. Source text remains on the device. Built with React/Vinext, Sites-managed ChatGPT authentication, and Cloudflare D1.

## Working features
- Live in-app typing; WPM and variation; sentence, paragraph and periodic long pauses; automatic resume; typo correction; countdown; boost; pause/resume; stop/Escape; progress and stats.
- Local source text/settings persistence; .txt import (500 KB limit); responsive keyboard-accessible interface.
- Sites ChatGPT sign-in/sign-out. Password recovery and 2FA are managed by the ChatGPT account.
- Per-user cloud profiles: create, restore, update, rename, duplicate, delete. Cloud records contain settings, never source text.
- Atomic server limits: Free two profiles and ten lifetime cloud session starts. Seven-day trial once per account, fifty profiles and unlimited starts. Expiry derives from server time and retains all profiles. Existing profiles remain editable.
- Personal aggregate session starts, words and completions. These are browser-reported activity counts, not audited assessment data.

## Launch preview status
All local studio controls/imports are available for preview. Paid gating of browser-local behavior is not a security boundary. Server-owned cloud records enforce their limits. No paid subscription is enabled or represented as active.

## Setup
Node >=22.13, npm, Git and tar required.

```
npm ci
npm run db:generate
npm run build
npm run dev
```

Use the Sites plugin lifecycle for deployment; preserve `.openai/hosting.json` project identity and Sites Vite integration. D1 binding is `DB`. Sites applies committed schema migrations during publication. See starter README content in the Sites plugin for local D1 commands; after building run Wrangler `d1 execute DB --local --config dist/server/wrangler.json --persist-to .wrangler/state --file <migration>` for each pending migration. Run `node --test tests/*.test.mjs` for pure typing logic checks when present.

## Provider setup still required
There is no payment provider, email provider or team membership/invitation service configured. Pro $9/month and Team $39/month (five accounts) are planned pricing only. Checkout, subscriptions, payment codes, codes by email, team seats/invitations, subscription cancellation and revenue reporting are unavailable. No fake payment success, admin authentication, customer/revenue data or activation code is generated. Custom email/password authentication is not supported by Sites; use hosted ChatGPT sign-in.

Before enabling billing implement a provider-specific adapter with server-secret API credentials. Checkout must use server-side plan/price IDs and bind to authenticated user IDs. Webhooks must verify the provider signature over raw request bytes, reject stale/replayed signatures, persist unique event IDs and unique payment IDs transactionally, and validate price/currency/status/account before issuing one cryptographically random activation code. Store only code hashes, mark redemption atomically once, and never trust a browser payment-success flag. Success/account pages should poll the authenticated server record and reveal a code only after verified confirmation, together with automatic entitlement activation. Queue an idempotent email notification using a transactional outbox. Reconcile subscription changes, failed payments, refunds, cancellation and expiry server-side; derive downgrade while retaining profiles.

Team requires server membership records and a unique owner billing account. Count active members AND pending invitations in the same transaction before reserving any of five seats. Invitation tokens must be hashed, expiring, one-use and email-bound. Build protected admin reports and audited plan/revoke/suspend operations only after explicit owner provisioning. Never infer ownership from a browser email field or grant admin to the first visitor. Owner 2FA is managed through ChatGPT where supported.

## Privacy
The browser persists source text locally under `typeflow`. Account includes a Clear local text action. Cloud telemetry contains aggregate counts only; it never submits source text. Avoid shared-device storage for sensitive text. Activity counters are not trusted billing evidence. Guest use is local and does not create cloud records.

## Security boundaries
Sites injects authenticated identity headers. Every data API derives owner identity server-side. Mutations validate Origin and scope all queries by the authenticated user. D1 conditional statements avoid profile/session/trial races. Public deployment requires explicit Sites audience configuration; creating a Site alone leaves it owner-private.

## Source publication
No credentials, environment files, build output, local runtime state or node_modules should be committed. `.env.example` documents names only. Never commit Sites source-repository access tokens.

## Optional owner console
Set the server-only `OWNER_USER_ID` runtime variable to the exact account ID shown in your signed-in Account view. No default owner is assigned. `/api/admin` returns 404 until this exact stable Sites user ID is provisioned. Owner can list at most 500 customer aggregate rows, suspend/restore an account, and revoke a trial. Suspension blocks cloud mutations and session starts. It cannot prevent offline local simulation. No revenue, payments, billing entitlement changes, codes or team controls exist yet. Audit logging and provider-based billing administration remain launch requirements before commercial operations.
