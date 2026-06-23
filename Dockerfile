# --- build the Svelte SPA ---
FROM node:22-alpine AS frontend
WORKDIR /fe
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# --- python runtime serving API + built SPA ---
FROM python:3.12-slim
WORKDIR /app
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ ./backend/
COPY --from=frontend /fe/dist ./frontend/dist

ENV MEAL_DB=/data/meals.db
ENV FRONTEND_DIST=/app/frontend/dist
VOLUME /data
EXPOSE 8000

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
