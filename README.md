# Todo App Backend

## Запуск

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
docker run -e POSTGRES_PASSWORD=admin -p 5433:5432 -d postgres
uvicorn app.main:app --reload --port 8080
```

API будет доступно на `http://127.0.0.1:8080`.
