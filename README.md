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

## Optional preview and external typing

The studio has a persistent **Show live preview** toggle. Progress and session controls stay visible when the preview is hidden. **Start delay** supports whole values from **1 to 15 seconds**, including values saved in named profiles. Countdown timing uses a deadline so delayed browser timers do not extend the studio countdown.

To type into another website or Windows app, select **Another app / website (Windows)** and use the [Windows companion download](/public/downloads/TypeFlow-Windows-Companion.zip). The download is readable Python source, not a signed executable, and requires Windows and Python 3.10+ with Tkinter. Unzip it, open `Start-TypeFlow.cmd`, enable external typing and pair the website with the code shown. Your browser may ask for local network access. Then Start typing and click the destination textbox during the countdown.

The companion's independent countdown and typing keep running when the browser tab loses focus. Esc cancels globally. Changing foreground windows pauses; resume gives a fresh countdown to choose the destination again. It sends Unicode text, pacing variation and punctuation/long pauses. Studio typo simulation and boost are not applied externally. It sends no form-submission or shortcut commands. Receiving applications control whether they accept these events; elevated/protected apps and custom editors may not work. It cannot verify the destination accepted the text. Changing fields within the same foreground window changes the destination, so keep focus in the intended textbox while typing.

The companion binds only to `127.0.0.1:31965` and requires the exact production origin, an exact Host header, a random per-launch pairing token and explicit enablement in its visible window. Tokens stay in page memory and requests go directly to loopback, never through Vercel. Source text is held in memory and cleared on completion/stop; it is not logged or saved by the helper. The browser's existing local text persistence is separate. Closing the helper stops its server and typing. No autostart, administrator escalation, extension or remote relay is used.

Companion source is under `companion/windows`. Rebuild its committed ZIP using `python scripts/package-companion.py`. Run its tests with `python -m unittest discover -s tests -p test_companion.py -v`. Tests use a fake keyboard sink; they verify validation, pairing checks, countdown cancellation, Unicode sequencing, focus-change pause/resume, source-window rejection and Windows INPUT structure layout without injecting OS input. Real destination acceptance must be checked on the user's chosen app.
