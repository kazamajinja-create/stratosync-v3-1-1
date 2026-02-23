# Demo Guide (Hand-off)

## 1) Run (Docker)
```bash
docker compose up --build
```
Open:
- http://localhost:8000/docs

## 2) View the included demo project (already packaged)
- Board (HTML): http://localhost:8000/board/demo:alpha
- Trend (PNG): http://localhost:8000/trend/png/demo:alpha?n=50
- Board (PDF): http://localhost:8000/board/pdf/demo:alpha?n=50

## 3) Generate fresh demo records (optional)
```bash
bash scripts/run_demo.sh
```

## 4) Evidence bundle export (admin)
Set ADMIN_TOKEN in docker-compose.yml or .env, then:
```bash
curl -X POST "http://localhost:8000/evidence/export/demo:alpha?n=200" -H "X-Admin-Token: CHANGE_ME"
```
A zip will be created under `data/`.


## v2.7.1 note
Evidence export includes `board.pdf` and `trend.png` automatically.
