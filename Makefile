.PHONY: install run-backend run-frontend run test clean

install:
	cd backend && pip install -r requirements.txt
	cd frontend && npm install

run-backend:
	cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

run-frontend:
	cd frontend && npm run dev

test:
	python -c "from backend.app.main import app; print('Backend test OK')"
	cd frontend && npm run build

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf frontend/dist frontend/node_modules
