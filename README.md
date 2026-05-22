# SAMS — Sports Academy Management System

Full-stack multi-tenant SaaS for sports academies.
**Deploy target:** your own Linux server with Docker. Not deployed by Lovable.

## Stack

- **Backend:** Django 5, Django REST Framework, SimpleJWT, Celery, drf-spectacular
- **Database:** PostgreSQL 16
- **Cache / broker:** Redis 7
- **Frontend:** Vue 3 + Quasar 2 + Pinia + Axios + vue-i18n (EN/AR)
- **Reverse proxy:** NGINX
- **Orchestration:** Docker Compose

## What's inside

```
sams/
├── docker-compose.yml          # dev stack
├── docker-compose.prod.yml     # production overrides
├── .env.example                # copy to .env
├── nginx/nginx.conf            # /api → backend, / → SPA
├── backend/                    # Django (modular monolith)
│   ├── Dockerfile
│   ├── entrypoint.sh           # migrate + collectstatic + (optional) seed
│   ├── manage.py
│   ├── pytest.ini
│   ├── requirements/{base,dev,prod}.txt
│   ├── config/                 # settings split (base/dev/prod), urls, celery
│   └── apps/
│       ├── common/             # BaseModel, AcademyScopedModel, TenantMiddleware,
│       │                       # generic CRUD viewset, serializer factory,
│       │                       # `seed_demo` management command
│       ├── academies/          # tenant entity + /me endpoint
│       ├── accounts/           # custom User w/ role, JWT login, /me
│       ├── players/            # CRUD
│       ├── coaches/            # CRUD
│       ├── groups/             # CRUD + memberships
│       ├── sessions/           # Venues, SessionSeries, SessionOccurrence,
│       │                       # Enrollments, "generate occurrences" action
│       ├── attendance/         # CRUD + bulk_mark
│       ├── payments/           # Invoices, InvoiceLines, Payments
│       ├── notifications/      # CRUD (extend with Celery senders)
│       ├── analytics/          # /dashboard KPI endpoint
│       └── audit/ storage/ communication/ ratings/ cancellations/ reports/
│                               # (stub apps — extend per master plan)
└── frontend/                   # Quasar app
    ├── Dockerfile
    ├── quasar.config.ts
    └── src/
        ├── boot/{axios,auth,i18n}.ts
        ├── stores/auth.ts      # JWT login + persistence
        ├── services/crud.ts    # typed REST helper
        ├── components/CrudPage.vue   # reusable table+dialog
        ├── i18n/{en-US,ar}/
        ├── layouts/MainLayout.vue
        └── pages/
            ├── DashboardPage.vue     # live KPIs from /analytics/dashboard
            ├── LoginPage.vue         # JWT login
            ├── PlayersPage.vue
            ├── CoachesPage.vue
            ├── GroupsPage.vue
            ├── VenuesPage.vue
            ├── SessionsPage.vue      # list + bulk attendance dialog
            ├── PaymentsPage.vue      # invoices + payments tabs
            └── NotificationsPage.vue
```

## Run it — verified working steps

These steps are the exact, audited boot sequence. Follow them in order and the stack comes up cleanly on a fresh machine.

### Prerequisites

- Docker Engine 24+ and Docker Compose v2 (`docker compose version` should work)
- Ports **80**, **5432**, and **6379** free on the host
- ~2 GB free RAM and ~3 GB free disk for images

### Step 1 — Get the code and create `.env`

```bash
cd sams
cp .env.example .env
```

The default `.env` is valid for local dev. Do not edit it for the first run.

### Step 2 — Start the core stack (web only, no Celery)

The first boot must start only the core services so a single backend container runs migrations + seeding without racing the workers.

```bash
docker compose up --build db redis backend frontend nginx
```

Wait until the backend logs show migrations finishing, demo data seeding, and Gunicorn starting. The frontend container must report an app URL on `0.0.0.0`/network plus `localhost:9000`; this confirms Nginx can reach it from another container.

### Step 3 — Open the app

- **App:**     http://localhost/
- **API:**     http://localhost/api/v1/
- **Swagger:** http://localhost/api/docs/
- **Admin:**   http://localhost/admin/

**Demo login:** `admin@sams.local` / `Password123!`

### Step 4 (optional) — Start Celery workers

Only after the web app responds, start background workers in a second terminal:

```bash
docker compose --profile workers up -d celery_worker celery_beat
```

Workers run with `SKIP_DJANGO_STARTUP=1` and will not re-run migrations.

### Stopping and resetting

```bash
docker compose down              # stop containers
docker compose down -v           # stop + wipe DB volume (forces fresh seed next boot)
```

### Pre-applied fixes (for awareness)

These issues are already fixed in the repo; listed so you know what to expect:

- Backend `entrypoint.sh` is invoked via `sh` so it works even when the executable bit is dropped on Windows/WSL volume mounts.
- Pinia is registered in `boot/pinia.ts` before `boot/auth.ts` runs, so the auth store always exists at boot.
- Quasar pages outside `MainLayout` (Login, 404) use `<div class="fullscreen flex flex-center">` instead of `<q-page>` to avoid blank-page rendering.
- `http-server` is a real dependency in `frontend/package.json`, so the production image does not rely on `npx` resolving it at runtime.
- The `sessions` Django app is registered with label `training` to avoid colliding with Django's built-in `sessions` app.
- `make_serializer` in `apps/common/serializers.py` uses `model_fields` internally to avoid a `NameError` during DRF view import.
- `AcademyScopedModel` uses app-qualified reverse relation names, so `groups.Venue` and `training.Venue` do not collide during Django startup checks.
- `frontend/index.html` uses Quasar's required `<!-- quasar:entry-point -->` marker, so the dev server does not stop before rendering the SPA.
- Docker starts Quasar with `--host 0.0.0.0 --port 9000`, so Nginx can proxy the SPA instead of returning a white page or 502.

If logs don't match, see `PRE_FLIGHT_NOTES.md` for the full audit trail.

## Architecture rules baked in

- **Multi-tenant from day one.** Every business entity inherits `AcademyScopedModel`. A `TenantMiddleware` attaches `request.academy_id` from the authenticated user, and `AcademyScopedViewSet` enforces filtering + stamping on every create. **No query crosses tenant boundaries** unless explicitly bypassed by an internal super-admin.
- **UUID primary keys, soft deletes, audit timestamps** on every model.
- **RBAC roles** on the custom `User` (`customer`, `coach`, `operations`, `admin`, `super_admin`). Backend never trusts frontend permissions.
- **JWT (SimpleJWT)** with refresh rotation. Tokens stored in browser `localStorage`; auth attached via Axios interceptor.
- **Async via Celery + Redis** (worker + beat services already wired).
- **OpenAPI schema** auto-generated at `/api/schema/`, Swagger UI at `/api/docs/`.
- **Indexes** on `academy_id`, `(academy_id, created_at)`, `(academy_id, status)`, plus per-domain composite indexes (sessions by `starts_at`, payments by `due_date`, etc.).

## API surface

```
POST   /api/v1/auth/token/                     # JWT login
POST   /api/v1/auth/token/refresh/             # JWT refresh
GET    /api/v1/accounts/me/                    # current user
GET    /api/v1/academies/me/                   # current tenant
CRUD   /api/v1/players/
CRUD   /api/v1/coaches/
CRUD   /api/v1/groups/  + /memberships/
CRUD   /api/v1/sessions/venues/
CRUD   /api/v1/sessions/series/    + POST /{id}/generate/   # materialize occurrences
CRUD   /api/v1/sessions/occurrences/
CRUD   /api/v1/sessions/enrollments/
CRUD   /api/v1/attendance/         + POST /bulk_mark/
CRUD   /api/v1/payments/invoices/
CRUD   /api/v1/payments/invoice-lines/
CRUD   /api/v1/payments/payments/
CRUD   /api/v1/notifications/
GET    /api/v1/analytics/dashboard/
```

## Deploying on your server

Production overrides live in `docker-compose.prod.yml`.

```bash
# on the server
git clone <your repo> sams && cd sams
cp .env.example .env
# edit .env — set DJANGO_SECRET_KEY, strong DB password, real ALLOWED_HOSTS,
# CORS_ALLOWED_ORIGINS, JWT lifetimes, SENTRY_DSN, etc.
# Disable demo seed:
sed -i 's/SEED_DEMO: "1"/SEED_DEMO: "0"/' docker-compose.yml   # or remove from prod compose
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
docker compose exec backend python manage.py createsuperuser
```

Put TLS in front (Caddy, Traefik, Cloudflare, or extend `nginx/nginx.conf` to terminate on 443).

### Backups

```bash
docker compose exec db pg_dump -U $POSTGRES_USER $POSTGRES_DB > backup-$(date +%F).sql
docker run --rm -v sams_mediadata:/data -v $PWD:/out alpine \
  tar czf /out/media-$(date +%F).tgz -C /data .
```

## Tests

```bash
docker compose exec backend pytest
```

Mandatory categories from the master plan: unit, integration, permission, **tenant isolation**, payment, scheduling.

## Extending — roadmap

Phase order from `Sams_Full_Implementation_Master_Plan_1.pdf`:

1. ✅ Foundations + auth + tenants
2. ✅ Admin core: players, coaches, groups, venues
3. ✅ Scheduling: series, occurrences, enrollments, occurrence generation
4. ✅ Attendance (bulk marking)
5. ✅ Payments: invoices + payments
6. ✅ Notifications model + endpoint
7. Coach portal (filter views by `request.user`)
8. Customer portal
9. Payment gateways (Stripe / Paymob / PayTabs / Fawry) — extend `apps/payments` with a gateway abstraction + webhooks under `/api/public/`
10. Notification delivery (SendGrid / Twilio / FCM) — Celery tasks in `apps/notifications/tasks.py`
11. Advanced reporting / forecasting / mobile apps

## Handoff checklist for another AI / engineer

> "Just connect Docker" — here's what they need to know:

1. `cd sams && cp .env.example .env && docker compose up --build db redis backend frontend nginx`
2. Wait for the backend container to finish migrations + seeding.
3. Visit `http://localhost/` and log in with `admin@sams.local / Password123!`.
4. Start optional workers only after the web app is confirmed: `docker compose --profile workers up -d celery_worker celery_beat`.
5. For production: edit `.env`, set `DJANGO_SETTINGS_MODULE=config.settings.prod`, set `SEED_DEMO=0`, run with `docker-compose.prod.yml`, terminate TLS at the edge.

No Lovable, no external SaaS dependencies required to run the core platform. Optional integrations (Sentry, Stripe, SendGrid, etc.) read their keys from `.env`.
