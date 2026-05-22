# SAMS pre-flight notes (handoff to deployment AI)

This file documents every known issue that was fixed AND every remaining
known caveat. Read it once before running `docker compose up`.

## What works (verified by code review)

- Backend: Django 5 + DRF + simplejwt + django-filter + drf-spectacular,
  multi-tenant via `request.academy_id` set by `apps.common.middleware.TenantMiddleware`.
- 17 Django apps register; only 10 have models that produce migrations
  (academies, accounts, players, coaches, groups, sessions[label=training],
  attendance, payments, notifications, +django built-ins). The other 7
  (audit, cancellations, communication, permissions, ratings, reports, storage)
  are intentional empty placeholders and produce no migrations — that is fine.
- Frontend: Vue 3 + Quasar 2 (+ app-vite 2) + Pinia + vue-i18n + axios.
- Auth flow: `POST /api/v1/auth/token/` with `{email,password}` returns JWT;
  `GET /api/v1/accounts/me/` returns the current user; the SPA stores
  access/refresh in localStorage and attaches `Bearer` automatically.
- Demo seed: `SEED_DEMO=1` (default in dev compose) creates academy
  `demo`, admin user `admin@sams.local` / `Password123!`, 2 coaches,
  8 players, 1 group, 1 venue, a weekly series, 2 weeks of occurrences,
  some attendance, 5 invoices and 1 payment.

## Fixes applied in this pass

| # | File | Problem | Fix |
|---|------|---------|-----|
| 1 | `frontend/src/stores/index.ts` | Exported `defineStore` (a function), so Pinia was never instantiated. `useAuthStore()` would have thrown "no active Pinia". | Exports a real `createPinia()` instance. |
| 2 | `frontend/src/boot/pinia.ts` (new) | No boot file ever called `app.use(pinia)`. | New boot registers Pinia globally. |
| 3 | `frontend/src/boot/auth.ts` | Called `useAuthStore(store)` with an undefined `store`. | Calls `useAuthStore()` — Pinia is now app-wide. |
| 4 | `frontend/quasar.config.ts` | Wrapper import was `quasar/wrappers` (legacy) while boots used `#q-app/wrappers` (app-vite 2). Also, `pinia` boot was not registered. | Uses `#q-app/wrappers` (`defineConfig`) and lists `pinia` BEFORE `auth` in `boot:`. |
| 5 | `backend/Dockerfile` | `ENTRYPOINT ["/app/entrypoint.sh"]` relies on the file being executable, but the host volume mount overlays Dockerfile's `chmod +x` on Windows/WSL. | Changed to `ENTRYPOINT ["sh", "/app/entrypoint.sh"]`. |
| 6 | `frontend/src/pages/SessionsPage.vue` | Used `from` as a `ref` name — fragile in strict module contexts. | Renamed to `fromDate`/`toDate`. |
| 7 (earlier) | `backend/apps/sessions/apps.py` + FKs | App label collided with `django.contrib.sessions`. | Label changed to `training`; all string FKs use `training.X`. |
| 8 (earlier) | `frontend/Dockerfile` | `npm install \|\| true` swallowed install failures. | Removed `\|\| true`. |
| 9 | `frontend/src/pages/LoginPage.vue` + `ErrorNotFound.vue` | These routes are outside `MainLayout`, so wrapping them in `q-page` can render as an empty page in Quasar. | Changed them to fullscreen wrappers that render without `q-page-container`. |
| 10 | `frontend/package.json` | Production compose runs `npx http-server`, but it was not declared as a dependency. | Added `http-server` so production frontend serving does not depend on an ad-hoc download. |
| 11 | `backend/apps/common/serializers.py` | Dynamic serializers used `fields = fields` inside an inner `Meta` class, which raises `NameError` at import time and can blank/fail every API route. | Renamed the outer variable to `model_fields` and assigned that in `Meta`. |
| 12 | `backend/config/settings/base.py` | `apps.sessions` had a custom label (`training`) but settings loaded only the package path, so Django could ignore the label and collide with `django.contrib.sessions`. | Settings now loads `apps.sessions.apps.SessionsConfig` explicitly. |
| 13 | `backend/entrypoint.sh` + `docker-compose.yml` | The backend command could be passed as one shell string and fail with “file not found”; Celery containers also repeated migrations/seeding, making startup slow and confusing. | Entrypoint now executes shell command strings safely; Celery skips Django startup work and is behind the optional `workers` profile. |
| 14 | `backend/apps/common/models.py` | `groups.Venue` and `training.Venue` inherited the same `Academy.venue_set` reverse relation, so `manage.py check` failed and the backend could exit, causing 502 from NGINX. | Academy reverse relation names now include both app label and class name. |
| 15 | `frontend/index.html` | Quasar app-vite 2 rejects the legacy `<div id="q-app"></div>` placeholder and stops the dev server, leaving `localhost:9000` blank/unavailable. | Replaced it with the required `<!-- quasar:entry-point -->` marker. |
| 16 | `docker-compose.yml` + `frontend/Dockerfile` | A frontend dev server that binds only inside the container can make NGINX return 502/blank even when Quasar starts. | Quasar now starts with `--host 0.0.0.0 --port 9000` in Docker. |

## How to run (zero surprises path)

```bash
cd sams
cp .env.example .env       # edit DJANGO_SECRET_KEY if you care
docker compose up --build  # first boot installs deps + runs makemigrations + migrate + seed
```

For the first confidence check, run only the core web stack:

```bash
docker compose up --build db redis backend frontend nginx
```

Only start background workers after the web app is confirmed working:

```bash
docker compose --profile workers up -d celery_worker celery_beat
```

Open:
- http://localhost          → nginx → SPA on :9000 + API on :8000
- http://localhost:9000     → Quasar dev server directly
- http://localhost:8000/api/docs/  → Swagger UI
- http://localhost:8000/admin/     → Django admin

Login: `admin@sams.local` / `Password123!`

## Things that are intentional but might look weird

1. **`entrypoint.sh` runs `makemigrations` on every boot.** This is dev-only
   convenience because no migration files are committed yet. After first
   boot, commit the generated `apps/*/migrations/` folders, then switch
   prod's entrypoint to skip `makemigrations`.
2. **`make_serializer` excludes M2M and reverse relations.** So
   `SessionSeries.coaches` and `SessionOccurrence.coaches` won't appear
   in API responses. Add an explicit serializer if you need them.
3. **No DRF permissions per role yet.** All authenticated users in the same
   academy can CRUD everything. `apps.common.permissions.HasRole` exists
   but is not wired to viewsets — wire it per resource as needed.
4. **Frontend `env_file: .env`** in compose injects Django secrets into the
   frontend container too. Harmless (the SPA never reads them), but if
   that bothers you, split into `backend.env` and `frontend.env`.
5. **The two Venue concepts.** Only `apps.sessions.Venue` (label `training`)
   is wired into the SPA. The model in `apps.groups` is unused — feel free
   to delete it.
6. **Celery workers are optional for the current preview.** The CRUD screens,
   login, dashboard, sessions and payments do not require them, so they are
   disabled by default with a Compose profile to keep first boot simple.

## If first boot fails, the most likely cause is:

- **DB not ready when migrate runs** → entrypoint already polls with a
  socket loop; if it times out, `docker compose restart backend` once.
- **`makemigrations` produces nothing for an app** → expected for the 7
  empty-model apps. Not an error.
- **Frontend container exits** → `docker compose logs frontend` will show
  the real cause (Quasar prints errors on stderr). With the Pinia fix above
  this should no longer happen.
- **Browser shows a blank page at `/login`** → make sure the latest code is
  present; `LoginPage.vue` must use the fullscreen wrapper, not a top-level
  `q-page` outside `MainLayout`.
- **`http://localhost/` shows 502 but `frontend` logs say Quasar started** →
  make sure Compose uses `npx quasar dev --host 0.0.0.0 --port 9000`; otherwise
  NGINX may not be able to reach the dev server from another container.
- **Backend exits immediately with a long “gunicorn ... not found” message** →
  make sure `entrypoint.sh` contains `exec sh -c "$*"`; Compose passes command
  overrides as a shell-style string in this project.
