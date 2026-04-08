module.exports = {
  apps: [
    {
      name: "ecommerce-platform-backend",
      cwd: "./backend",
      script: "venv/bin/uvicorn",
      args: "app.main:app --host 0.0.0.0 --port 8000",
      interpreter: "venv/bin/python3",
      env: {
        DATABASE_URL: "postgresql://app_user:app_pass@localhost:5432/ecommerce_platform",
        REDIS_URL: "redis://localhost:6379",
        MINIO_ENDPOINT: "http://localhost:9000",
        MINIO_ACCESS_KEY: "minioadmin",
        MINIO_SECRET_KEY: "minioadmin",
        SECRET_KEY: "change-in-production",
      },
      max_restarts: 10,
    },
    {
      name: "ecommerce-platform-celery-worker",
      cwd: "./backend",
      script: "venv/bin/celery",
      args: "-A app.tasks.celery_app worker --loglevel=info",
      interpreter: "venv/bin/python3",
      env: {
        DATABASE_URL: "postgresql://app_user:app_pass@localhost:5432/ecommerce_platform",
        REDIS_URL: "redis://localhost:6379",
      },
      max_restarts: 10,
    },
    {
      name: "ecommerce-platform-celery-beat",
      cwd: "./backend",
      script: "venv/bin/celery",
      args: "-A app.tasks.celery_app beat --loglevel=info",
      interpreter: "venv/bin/python3",
      env: {
        DATABASE_URL: "postgresql://app_user:app_pass@localhost:5432/ecommerce_platform",
        REDIS_URL: "redis://localhost:6379",
      },
      max_restarts: 10,
    },
    {
      name: "ecommerce-platform-frontend-admin",
      cwd: "./frontend-admin",
      script: "npx",
      args: "vite --host 0.0.0.0 --port 3000",
      env: { PORT: 3000, VITE_API_URL: "http://localhost:8000" },
      max_restarts: 10,
    },    {
      name: "ecommerce-platform-frontend-buyer",
      cwd: "./frontend-buyer",
      script: "npx",
      args: "vite --host 0.0.0.0 --port 3001",
      env: { PORT: 3001, VITE_API_URL: "http://localhost:8000" },
      max_restarts: 10,
    },    {
      name: "ecommerce-platform-frontend-seller",
      cwd: "./frontend-seller",
      script: "npx",
      args: "vite --host 0.0.0.0 --port 3002",
      env: { PORT: 3002, VITE_API_URL: "http://localhost:8000" },
      max_restarts: 10,
    }
  ],
};
