# 6-Figure Host Course

The course site, protected by personal access codes.

- `public/` – the course (`index.html`), the login page (`login.html`), images, PDFs and fonts.
- `functions/` – Cloudflare Pages Functions:
  - `_middleware.js` – lets people in only with a valid code; everyone else sees the login page.
  - `api/login.js` – checks the code and remembers the device (max 5 devices per code).
  - `api/thrivecart.js` – ThriveCart webhook: a purchase creates a code and sends the welcome email through Brevo; a refund switches the code off.
  - `api/admin/[action].js` – small tools for you (make, look up, reset or switch off a code).
- `src/lib.js` – shared helpers.

Every push to the `main` branch updates the live site automatically.

## One-time setup in Cloudflare

1. **Workers & Pages > KV > Create namespace**, name it `course-codes`.
2. **Workers & Pages > Create > Pages > Connect to Git**, pick this repository.
   - Framework preset: *None*. Build command: *(leave empty)*. Build output directory: `public`.
3. In the new Pages project: **Settings > Bindings > Add > KV namespace**. Variable name `CODES`, namespace `course-codes`.
4. **Settings > Variables and secrets** (type *Secret* for each):

| Name | Value |
|---|---|
| `SESSION_SECRET` | a long random text (40+ characters) |
| `THRIVECART_SECRET` | ThriveCart > Settings > API & Webhooks > ThriveCart order validation > *Secret word* |
| `ADMIN_KEY` | a long random text, only for you |
| `BREVO_API_KEY` | Brevo > SMTP & API > API keys |
| `BREVO_TEMPLATE_ID` | `6` (template "Course access code", HTML in emails/welcome.html). Activate it in Brevo before launch |
| `BREVO_LIST_ID` | `3` (the "Bought guide" list) |
| `COURSE_URL` | the course address, for example `https://course.6figurehost.com` |
| `PRODUCT_IDS` | *(optional)* ThriveCart product ID(s) of the course, comma-separated |
| `MAX_DEVICES` | *(optional)* default 5 |

5. **Deployments > Retry deployment** so the settings take effect.
6. *(Optional)* **Custom domains > Set up a custom domain**, for example `course.6figurehost.com`.
7. Once, create the `ACCESS_CODE` contact attribute in Brevo:
   `curl -X POST https://YOUR-SITE/api/admin/setup -H "x-admin-key: YOUR_ADMIN_KEY"`

## ThriveCart

Settings > API & Webhooks > Webhooks & notifications > **Add webhook**:
URL `https://YOUR-SITE/api/thrivecart`. Make a test purchase in test mode: you should receive the welcome email with a code.

## Admin tools

All are `POST` with the header `x-admin-key: YOUR_ADMIN_KEY` and a JSON body:

| URL | Body | What it does |
|---|---|---|
| `/api/admin/create` | `{"email":"...","name":"...","send":true}` | makes a code by hand (gift, team member, replacement); `send` emails it |
| `/api/admin/lookup` | `{"code":"HOST-XXXX-XXXX"}` or `{"email":"..."}` | shows the code, status and devices |
| `/api/admin/reset` | `{"code":"..."}` | forgets all devices, so the buyer can log in again |
| `/api/admin/deactivate` | `{"code":"..."}` | switches a code off |
| `/api/admin/activate` | `{"code":"..."}` | switches it back on |

## Updating the course

Change the files in `public/` and push to `main`. Cloudflare publishes the new version in about a minute.
