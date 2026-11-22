# Deploy

Backend on **Railway**, frontend on **Vercel**, both from this GitHub repo. Every push to
`main` redeploys both.

The two sites must know each other's address: the frontend calls the backend
(`VITE_API_BASE_URL`), and the backend only accepts browsers coming from the frontend
(`CORS_ALLOWED_ORIGINS`). So: deploy the backend first, then the frontend, then go back and
tell the backend the frontend's address.

## 1. Backend (Railway)

1. **New Project → Deploy from GitHub repo** → pick this repo.
2. Service **Settings**:
   - **Root Directory:** `backend`
   - **Railway Config File:** `/backend/railway.json` (sets the start command and the health
     check). If the setting isn't there, paste the start command from that file into
     **Deploy → Custom Start Command** and set the healthcheck path to `/api/health`.
   - **Networking → Generate Domain.** When asked for the port, enter `8080` (the same value
     as the `PORT` variable below). Note the domain, e.g. `spotter-backend.up.railway.app`.
3. **Variables:**

   | Name | Value |
   |---|---|
   | `DJANGO_SECRET_KEY` | a new random value (command below); not the one in your local `.env` |
   | `HERE_API_KEY` | your HERE key |
   | `DEBUG` | `false` |
   | `ALLOWED_HOSTS` | the Railway domain, without `https://` |
   | `CORS_ALLOWED_ORIGINS` | leave empty for now; set in step 3 |
   | `PORT` | `8080`. gunicorn listens on `$PORT`, and the domain must send traffic to the same port. |

   ```bash
   python3 -c "import secrets; print(secrets.token_urlsafe(50))"
   ```

4. Check: `https://<railway-domain>/api/health` shows `{"status":"ok"}`.

## 2. Frontend (Vercel)

1. **Add New → Project** → import this repo.
2. **Root Directory:** `frontend`. Vercel detects Vite (build `npm run build`, output `dist`).
3. **Environment Variable:** `VITE_API_BASE_URL` = `https://<railway-domain>` (no trailing
   slash). Vite builds this into the page, so after changing it, **redeploy**.
4. Deploy and note the address, e.g. `https://spotter-routing.vercel.app`.

## 3. Connect them

In Railway, set `CORS_ALLOWED_ORIGINS` = the Vercel address exactly (with `https://`, no
trailing slash). Railway redeploys. Then plan a trip on the Vercel site.

Vercel *preview* deployments get other addresses, so their API calls are blocked by CORS.
Only the production address is allowed, on purpose.

## If something fails

| Symptom on the site | Likely cause |
|---|---|
| "Could not reach the server" | `VITE_API_BASE_URL` wrong or not redeployed, or CORS: check the browser console for a CORS error and fix `CORS_ALLOWED_ORIGINS` |
| "The server answered with status 400" on every call | `ALLOWED_HOSTS` doesn't match the Railway domain |
| Railway shows "Application failed to respond" | The domain's port and the `PORT` variable differ; both must be `8080` |
| Railway deploy crashes at start | Missing `DJANGO_SECRET_KEY` or `HERE_API_KEY`; the log names the variable |
| "Weather service's request limit was reached" | Open-Meteo's free per-IP limit (shared IP on Railway); see DECISIONS.md |

## Why these settings

- **One gunicorn worker, 8 threads:** the weather cache lives in memory, so one process
  means every request shares it. Threads handle requests waiting on HERE and Open-Meteo.
- **Railway, not Render's free plan:** Render's free services sleep after ~15 min idle and the
  next visitor waits 30–60 s.
