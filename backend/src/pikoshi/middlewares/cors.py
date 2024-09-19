from fastapi.middleware.cors import CORSMiddleware

origins = ["http://localhost:5173"]


def add_cors_middleware(app):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Boundary"],
        max_age=600,
    )
