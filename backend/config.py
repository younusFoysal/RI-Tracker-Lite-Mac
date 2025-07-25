# config.py

APP_ENV = "local"  # or "production" or "local" or "development"

URL_CONFIG = {
    "local": {
        "LOGIN": "https://remotintegrity-auth.vercel.app/api/v1/auth/login/employee",
        "PROFILE": "https://crm-amber-six.vercel.app/api/v1/employee",
        "SESSIONS": "http://localhost:3010/api/v1/sessions/app",
        "DAILY_STATS": "http://localhost:3010/api/v1/stats/daily",
        "WEEKLY_STATS": "http://localhost:3010/api/v1/stats/weekly",
        "FRONTEND_DEV": "http://localhost:5173",
        "FRONTEND_PROD": "dist/index.html",

        "DEBUG": True
    },
    "development": {
        "LOGIN": "https://remotintegrity-auth.vercel.app/api/v1/auth/login/employee",
        "PROFILE": "https://crm-amber-six.vercel.app/api/v1/employee",
        "SESSIONS": "https://tracker-beta-kohl.vercel.app/api/v1/sessions/app",
        "DAILY_STATS": "https://tracker-beta-kohl.vercel.app/api/v1/stats/daily",
        "WEEKLY_STATS": "https://tracker-beta-kohl.vercel.app/api/v1/stats/weekly",
        "FRONTEND_DEV": "http://localhost:5173",
        "FRONTEND_PROD": "dist/index.html",

        "DEBUG": True
    },
    "production": {
        "LOGIN": "https://auth.remoteintegrity.com/api/v1/auth/login/employee",
        "PROFILE": "https://crm.remoteintegrity.com/api/v1/employee",
        "SESSIONS": "https://tracker.remoteintegrity.com/api/v1/sessions/app",
        "DAILY_STATS": "https://tracker.remoteintegrity.com/api/v1/stats/daily",
        "WEEKLY_STATS": "https://tracker.remoteintegrity.com/api/v1/stats/weekly",
        "FRONTEND_DEV": "http://localhost:5173",  # Optional in production
        "FRONTEND_PROD": "dist/index.html",

        "DEBUG": False
    }
}

URLS = URL_CONFIG[APP_ENV]
