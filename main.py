import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.v1.auth.AuthController import auth_router
from api.v1.admin import admin_router
from api.v1.user import users_router
from handler.exception_handlers import register_exception_handlers
from middleware.auth_middleware import AuthMiddleware
from core.config import settings
from core.lifespan import lifespan
from fastapi.openapi.utils import get_openapi


app = FastAPI(lifespan=lifespan)

# 注册全局异常处理器
register_exception_handlers(app)

# 注册鉴权中间件
app.add_middleware(AuthMiddleware)

origins = [
    "http://localhost",
    "http://localhost:8080",
    "https://localhost:3006",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(admin_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")


@app.get('/')
async def welcome() -> dict:
    return {"message": "Welcome to my Page!!"}



if __name__ == "__main__":
    # uvicorn_default_logger = logging.getLogger("uvicorn")
    # uvicorn_default_logger.disabled = True
    uvicorn.run(app,host="127.0.0.1",port=8000)

    
    



def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="CattleBlog API",
        version="1.0.0",
        description="CattleBlog backend",
        routes=app.routes,
    )
    components = openapi_schema.get("components", {})
    security_schemes = components.get("securitySchemes", {})
    security_schemes["bearerAuth"] = {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT",
    }
    components["securitySchemes"] = security_schemes
    openapi_schema["components"] = components
    openapi_schema["security"] = [{"bearerAuth": []}]
    paths: dict = openapi_schema.get("paths", {})
    for p, ops in paths.items():
        if p in AuthMiddleware(app).public_paths:
            for m in ops.values():
                m["security"] = []
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

    
    



