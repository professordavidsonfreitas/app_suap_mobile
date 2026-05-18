from fastapi import FastAPI
import os

app = FastAPI()


from routers.auth_routes import auth_router
from routers.admin_routes import admin_router
from routers.student_routes import student_router

app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(student_router)


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)