from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from utils.connection_db import init_db, get_session
from operations.operations_db import UserOperations, TaskOperations
from data.models import Usuario, EstadoUsuario, Tarea, EstadoTarea
from typing import List, Optional
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import APIRouter


router = APIRouter()

@router.get("/")
@router.head("/")
async def root():
    return {"message": "API de Gestión de Usuarios y Tareas"}

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(lifespan=lifespan)


# --- Endpoints de Usuarios ---
@app.post("/usuarios/", response_model=Usuario, status_code=status.HTTP_201_CREATED)
async def crear_usuario(nombre: str, email: str, premium: bool = False):
    async for session in get_session():
        try:
            usuario = await UserOperations.create_user(
                session=session,
                nombre=nombre,
                email=email,
                premium=premium
            )
            await session.commit()
            return usuario
        except Exception as e:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )


@app.get("/usuarios/", response_model=List[Usuario])
async def listar_usuarios():
    async for session in get_session():
        return await UserOperations.get_all_users(session)


@app.get("/usuarios/{user_id}", response_model=Usuario)
async def obtener_usuario(user_id: int):
    async for session in get_session():
        usuario = await UserOperations.get_user_by_id(session, user_id)
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        return usuario


@app.patch("/usuarios/{user_id}/estado", response_model=Usuario)
async def actualizar_estado_usuario(user_id: int, nuevo_estado: EstadoUsuario):
    async for session in get_session():
        try:
            usuario = await UserOperations.update_user_status(
                session=session,
                user_id=user_id,
                new_status=nuevo_estado
            )
            if not usuario:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Usuario no encontrado"
                )
            await session.commit()
            return usuario
        except Exception as e:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )


@app.patch("/usuarios/{user_id}/premium", response_model=Usuario)
async def hacer_usuario_premium(user_id: int):
    async for session in get_session():
        try:
            usuario = await UserOperations.upgrade_to_premium(
                session=session,
                user_id=user_id
            )
            if not usuario:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Usuario no encontrado"
                )
            await session.commit()
            return usuario
        except Exception as e:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )


@app.get("/usuarios/activos/", response_model=List[Usuario])
async def listar_usuarios_activos():
    async for session in get_session():
        return await UserOperations.get_active_users(session)


@app.get("/usuarios/premium/activos/", response_model=List[Usuario])
async def listar_usuarios_premium_activos():
    async for session in get_session():
        return await UserOperations.get_premium_active_users(session)


# --- Endpoints de Tareas ---
@app.post("/usuarios/{user_id}/tareas", response_model=Tarea, status_code=status.HTTP_201_CREATED)
async def crear_tarea(user_id: int, nombre: str, descripcion: Optional[str] = None):
    async for session in get_session():
        try:
            usuario = await UserOperations.get_user_by_id(session, user_id)
            if not usuario:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Usuario no encontrado"
                )

            tarea = await TaskOperations.create_task(
                session=session,
                usuario_id=user_id,
                nombre=nombre,
                descripcion=descripcion
            )
            return tarea
        except Exception as e:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )


@app.get("/usuarios/{user_id}/tareas", response_model=List[Tarea])
async def obtener_tareas_usuario(user_id: int):
    async for session in get_session():
        usuario = await UserOperations.get_user_by_id(session, user_id)
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        return await TaskOperations.get_user_tasks(session, user_id)


@app.patch("/tareas/{task_id}/estado", response_model=Tarea)
async def actualizar_estado_tarea(task_id: int, nuevo_estado: EstadoTarea):
    async for session in get_session():
        try:
            tarea = await TaskOperations.update_task_status(
                session=session,
                task_id=task_id,
                new_status=nuevo_estado
            )
            if not tarea:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Tarea no encontrada"
                )
            return tarea
        except Exception as e:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )


@app.get("/tareas/{task_id}", response_model=Tarea)
async def obtener_tarea(task_id: int):
    async for session in get_session():
        tarea = await TaskOperations.get_task_by_id(session, task_id)
        if not tarea:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tarea no encontrada"
            )
        return tarea


# --- Endpoints básicos ---
@app.get("/")
async def root():
    return {"message": "API de Gestión de Usuarios y Tareas"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hola {name}, bienvenido al sistema de gestión"}