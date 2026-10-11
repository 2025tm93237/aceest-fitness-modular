# ACEest Fitness & Gym — DevOps Assignment 1 (Modular Build)

## About This Project

ACEest Fitness & Gym is a gym and fitness-management REST API built as a DevOps
course assignment, demonstrating a full CI/CD pipeline around a Flask application.
Unlike a single-file implementation, this build uses a modular Flask Blueprint
architecture — each functional area lives in its own file under `app/blueprints/`,
with shared infrastructure (database access, BMI/calorie calculations, the SVG
progress chart, the role-based access decorator) factored into `app/extensions.py`
and `app/utils.py`.

### Functional scope

- Authentication and role-based access (`admin` / `trainer`)
- Member registry (create, list, get, delete)
- Training plan generation per member
- Membership state tracking (`active` / `suspended` / `expired`)
- Movement (exercise) library
- Workout session logging per member
- Body measurement tracking
- Member goal/target tracking
- Progress logging with an SVG progress chart
- Calorie estimation (BMR + activity factor)
- Trainer dashboard and analytics summary
- Per-member overview
- CSV and PDF export of a member's sessions/progress

### Tech stack

Python 3.11 · Flask · SQLite · Gunicorn · Docker · GitHub Actions · Jenkins · Pytest

---

## Local Setup

**Requirements:** Python 3.11 or higher.

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

No `.env` file is required — the app runs with sensible defaults out of the box.
Two environment variables are available if you want to override them:

| Variable | Purpose | Default |
|---|---|---|
| `DB_PATH` | Path to the SQLite database file | `aceest_fitness.db` |
| `SECRET_KEY` | Flask session/signing key | `dev-only-change-this-key` (override for anything beyond local use) |

### Run the app

```bash
python wsgi.py
```

### Verify it's running

```bash
curl -i http://127.0.0.1:5000/health
```

A `200 OK` confirms the app booted and the SQLite database initialized correctly.

### Default development credentials

The database seeds two accounts for local testing:

| Username | Password | Role |
|---|---|---|
| `admin` | `admin123` | admin |
| `trainer` | `trainer123` | trainer |

```bash
curl -i -c cookies.txt -X POST http://127.0.0.1:5000/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

These are dev-only seed credentials — not intended for any shared or production
deployment.

---

## Testing

Run these from the project root with the virtual environment active.

| Command | Purpose | Success looks like |
|---|---|---|
| `python -m compileall -q app wsgi.py` | Byte-compiles all modules to catch syntax errors before anything else runs | No output, exit code `0` |
| `flake8 app tests` | Lints source and test code against the project's `.flake8` rules | No output, exit code `0` |
| `pytest -v --cov=app` | Runs the full test suite with verbose output and reports line coverage for `app/` | All 25 tests `PASSED`; a coverage summary printed at the end (no fixed threshold is enforced — record whatever your run reports) |

### Running a single test file or test

```bash
pytest tests/test_members.py -v
pytest tests/test_members.py::test_create_member -v
```

---

## Docker

```bash
docker build -t aceest-fitness-modular:local .
docker run -d -p 5000:5000 aceest-fitness-modular:local
curl http://127.0.0.1:5000/health
```

---

## Git

The project is developed through meaningful, module-scoped feature branches
(`foundation/`, `access/`, `roster/`, `fitness/`, `membership/`, `catalog/`,
`training/`, `health/`, `goals/`, `progress/`, `reporting/`, `insights/`), a
focused hotfix branch, and separate infrastructure/CI/documentation branches,
each merged with `--no-ff`.

---

## Continuous Integration

Two independent CI systems run against this repository rather than one
replacing the other:

- **GitHub Actions** runs on every `push` and `pull_request`, giving fast
  feedback directly on GitHub.
- **Jenkins** polls `main` every 5 minutes on a separate, on-prem server
  (Prayogshala), acting as an independent build verification pass outside
  GitHub's own runners.

### GitHub Actions (`.github/workflows/main.yml`)

Triggers: `push` and `pull_request`.

Runs three stages in strict dependency order, so cheap checks fail fast
before expensive ones run:

1. **Build & Lint** — compiles the app and runs `flake8`. Catches syntax and
   style errors immediately, before any Docker build is attempted.
2. **Docker Image Assembly** — builds the production image. Only runs if
   stage 1 passes, avoiding wasted build minutes on broken code.
3. **Automated Testing in Container** — runs the full Pytest suite against
   the actual built image, not just the local environment, to catch
   container-specific issues (missing deps, path differences, etc.).

No branch-protection / required-status-check rule is configured on this
repository — a failed run does not currently block merging.

### Jenkins

Configured as *Pipeline script from SCM* against the Prayogshala Jenkins
server:

- **Trigger:** polls `main` every 5 minutes (`pollSCM('H/5 * * * *')`) rather
  than a push-triggered webhook, so it acts as a periodic, independent
  confirmation rather than a PR gate.
- **Stages:** `Setup Environment` → `Lint` → `Unit Tests` → `Docker Build`.
- The final stage builds a locally tagged image
  (`aceest-fitness-modular:${BUILD_NUMBER}`) as build verification — it does
  not push to a registry or deploy anywhere.

---

## Module Map

| Area | Blueprint |
|---|---|
| Login and roles | `auth` |
| Member registry | `members` |
| Training plans | `plans` |
| Membership state | `membership` |
| Movement library | `movements` |
| Sessions | `sessions` |
| Body measurements | `measurements` |
| Targets | `targets` |
| Progress + chart | `progress` |
| Calorie estimate | `nutrition` |
| Dashboard / overview / analytics | `insights` |
| CSV / PDF export | `exports` |
