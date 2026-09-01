# Lumira

Lumira is a skincare diagnostic concept — a portfolio piece (alongside
[[al-noir]] for restaurants and [[cassian-voicu]] for appointments), this
time for the e-commerce/product line: a skincare brand built around a
diagnostic quiz and a personalized routine. It sits between clinical
"quiz + prescription" brands (Curology) and DIY ingredient-expert brands
(The Ordinary): an instant skin diagnostic with no knowledge barrier and no
forced subscription.

The site/product itself is designed and built in **English**; the
strategy and concept documents below are written in Romanian (portfolio
documentation language).

## Docs

- **Client brief:** [`docs/client-brief.md`](./docs/client-brief.md) — the
  fictional inbound ask that frames this case study.
- **Proposal:** [`docs/proposal.md`](./docs/proposal.md) — the phased
  proposal (scope, timeline, cost) written in reply to it.
- **Concept brief:** [`docs/concept-brief.md`](./docs/concept-brief.md)
  — what it is, diagnostic flow, routine result, user account, site
  structure, visual direction, brand name, tech stack, mock screens.
- **Brand & business brief:** [`docs/brand-brief.md`](./docs/brand-brief.md)
  — positioning, target audience, value proposition, diagnostic logic,
  routine structure, tone of voice, and business model options.
- **Visual concept mockup:** [`docs/assets/lumira-skincare-mock.pdf`](./docs/assets/lumira-skincare-mock.pdf)
  — landing page, diagnostic quiz, routine result, and saved-routines
  dashboard (concept screens, Romanian copy — reference for layout and
  visual identity only; the built app below is in English).

## App

A Django app implementing the concept: diagnostic quiz → generated
morning/evening routine → optional account to save it and revisit it later.

- `routines/models.py` — `Concern`, `SkinType`, `Product`, `DiagnosticResult`,
  `Routine`, `RoutineStep`, `UserProfile`.
- `routines/diagnostics.py` — maps a diagnostic result to a concrete routine
  (concern → key ingredient/treatment step, skin type → product texture,
  experience level → number of steps).
- `routines/views.py` + `routines/templates/` — the quiz, routine result,
  sign up/log in, "My routines", and product catalog pages.

### Run it locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate   # also seeds concerns/skin types/products
python manage.py createsuperuser   # optional, for /admin/
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` to take the diagnostic and see a generated
routine. Product catalog and concerns/skin types are managed at
`http://127.0.0.1:8000/admin/`.

### Deploy to Render

`render.yaml` is a Render [Blueprint](https://render.com/docs/blueprint-spec):
it provisions a free Postgres database and a web service that runs
`migrate`/`collectstatic` on every deploy and serves the app with gunicorn.

1. Push this repo to GitHub (already done if you're reading this on GitHub).
2. On [Render](https://dashboard.render.com), **New → Blueprint**, connect
   this repo. Render reads `render.yaml` and provisions the database + web
   service automatically, generating a random `SECRET_KEY`.
3. Once deployed, open a shell for the web service (Render dashboard → your
   service → **Shell**) and run `python manage.py createsuperuser` to get
   into `/admin/`.

In production, `DEBUG=False`, `ALLOWED_HOSTS`/`CSRF_TRUSTED_ORIGINS` are
derived from Render's `RENDER_EXTERNAL_HOSTNAME`, static files are served by
WhiteNoise, and the database comes from Render's `DATABASE_URL` — all
handled in `lumira/settings.py`, no manual config needed beyond the steps
above.

> Fictional brand, created as a portfolio demonstration project.
