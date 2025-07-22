# config.py

APP_ENV = "development"  # or "production"

URLS = {
    "LOGIN": "https://remotintegrity-auth.vercel.app/api/v1/auth/login/employee",
    "PROFILE": "https://crm-amber-six.vercel.app/api/v1/employee",
    "SESSIONS": "https://tracker-beta-kohl.vercel.app/api/v1/sessions",
    "FRONTEND_DEV": "http://localhost:5173",
    "FRONTEND_PROD": "dist/index.html"
}
