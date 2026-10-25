# Deploy

Saavdhan ships as one Docker image: FastAPI serves the API and the built React app on one port.
OCR (Tesseract with English, Hindi and Marathi) is included in the image.

## Render (hosted demo)

The repo has a Blueprint, [`render.yaml`](../render.yaml): one free Docker web service.

1. Sign in to https://render.com with GitHub and allow Render to read `Sandesh13fr/saavdhan`.
2. **New → Blueprint**, pick the repo, keep the service name `saavdhan`, **Apply**.
3. Wait for the first build (about 5–8 minutes). The URL is `https://saavdhan.onrender.com`
   (or `saavdhan-xxxx.onrender.com` if the name is taken).
4. Check `https://<your-url>/api/health` returns `"status":"ok"`.

What the Blueprint sets:

| Variable | Value | Why |
|---|---|---|
| `SAAVDHAN_ENV` | `production` | Fail-closed security headers, CSRF, caps |
| `SAAVDHAN_HASH_SALT` | generated | Secret key for HMAC phone hashes (required in production) |
| `SAAVDHAN_DEMO_OFFICER_PASSWORD` | generated | Read-only demo officer `officer@saavdhan.example` for the synthetic pattern map. Read the value in the Render dashboard → Environment |
| `SAAVDHAN_ENABLE_LLM` | `false` | Optional LLM off by default |
| `SAAVDHAN_PUBLIC_ORIGIN`, `SAAVDHAN_ALLOWED_HOSTS` | not set | Taken from Render's `RENDER_EXTERNAL_URL` / `RENDER_EXTERNAL_HOSTNAME` |

Optional LLM: set `OPENAI_API_KEY` in the dashboard (never in git), then `SAAVDHAN_ENABLE_LLM=true`.
In production only an **admin** account may trigger LLM calls, and offer text is then sent to the
gateway (`SAAVDHAN_LLM_BASE_URL`). Disclose this to users before enabling it.

Limits of the free plan:
- The service sleeps after ~15 minutes idle; the first request takes ~1 minute to wake it.
- The disk is ephemeral: cases, check-in plans and the demo officer reset on restart or redeploy.
  The officer is re-created at startup from `SAAVDHAN_DEMO_OFFICER_PASSWORD`. That is acceptable
  for a synthetic-data demo; a real pilot needs a persistent disk or a database.
- Anonymous cases are deleted after 24 hours anyway (`SAAVDHAN_RETENTION_HOURS`).

## Local Docker

```bash
docker build -t saavdhan:local .
```

```bash
docker run --rm -p 8000:8000 -e SAAVDHAN_ENV=local saavdhan:local
```

Open http://localhost:8000. With `SAAVDHAN_ENV=production` you must also pass
`SAAVDHAN_PUBLIC_ORIGIN=https://...` and `SAAVDHAN_HASH_SALT` (16+ characters).

## Self-hosted with Caddy

[`deploy/compose.yaml`](../deploy/compose.yaml) and [`deploy/Caddyfile`](../deploy/Caddyfile) run the
image behind Caddy with HTTPS. Copy `deploy/production.env.example` to `deploy/production.env`
and fill it. Uvicorn runs with `--proxy-headers`; narrow `FORWARDED_ALLOW_IPS` to the proxy address
so the rate limit and login throttle see real client IPs.
