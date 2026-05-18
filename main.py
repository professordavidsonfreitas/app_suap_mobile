from fastapi import FastAPI

app = FastAPI()


from routers.auth_routes import auth_router
from routers.admin_routes import admin_router
from routers.student_routes import student_router

app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(student_router)