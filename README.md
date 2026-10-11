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

## Local Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python wsgi.py
```

## Testing

```bash
python -m compileall -q app wsgi.py
flake8 app tests
pytest -v --cov=app
```

## Docker

```bash
docker build -t aceest-fitness-modular:local .
docker run -d -p 5000:5000 aceest-fitness-modular:local
curl http://127.0.0.1:5000/health
```

## Git

The project is developed through meaningful, module-scoped feature branches
(`foundation/`, `access/`, `roster/`, `fitness/`, `membership/`, `catalog/`,
`training/`, `health/`, `goals/`, `progress/`, `reporting/`, `insights/`), a
focused hotfix branch, and separate infrastructure/CI/documentation branches,
each merged with `--no-ff`.

## GitHub Actions

`.github/workflows/main.yml` runs on `push` and `pull_request`, performing
Build & Lint, Docker Image Assembly, and Pytest inside the built container,
in that dependency order.

## Jenkins

Configured as *Pipeline script from SCM* against the Prayogshala Jenkins
server, polling `main` every 5 minutes and running environment setup, lint,
unit tests and a Docker build on each change.

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
