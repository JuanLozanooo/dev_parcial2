from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from utils.connection_db import init_db, get_session
from operations.operations_db import UserOperations
from data.models import Usuario, EstadoUsuario
from typing import List, AsyncGenerator
from sqlmodel.ext.asyncio.session import AsyncSession


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(lifespan=lifespan)

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Obtiene una sesión de base de datos"""
    async for session in get_session():
        yield session

# Endpoint raíz
@app.get("/")
async def root():
    return {"message": "API de Gestión de Usuarios"}

# --- Endpoints existentes (mantenidos igual) ---
@app.post("/usuarios/", response_model=Usuario, status_code=status.HTTP_201_CREATED)
async def crear_usuario(nombre: str, email: str, premium: bool = False):
    session_generator = get_session()
    session = await anext(session_generator)
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
    finally:
        await session.close()

@app.get("/usuarios/", response_model=List[Usuario])
async def listar_usuarios():
    session_generator = get_session()
    session = await anext(session_generator)
    try:
        usuarios = await UserOperations.get_all_users(session)
        return usuarios
    finally:
        await session.close()

@app.get("/usuarios/{user_id}", response_model=Usuario)
async def obtener_usuario(user_id: int):
    session_generator = get_session()
    session = await anext(session_generator)
    try:
        usuario = await UserOperations.get_user_by_id(session, user_id)
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        return usuario
    finally:
        await session.close()

# --- Nuevos endpoints ---
@app.patch("/usuarios/{user_id}/estado", response_model=Usuario)
async def actualizar_estado_usuario(
    user_id: int,
    nuevo_estado: EstadoUsuario
):
    session_generator = get_session()
    session = await anext(session_generator)
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
    finally:
        await session.close()

@app.patch("/usuarios/{user_id}/premium", response_model=Usuario)
async def hacer_usuario_premium(user_id: int):
    session_generator = get_session()
    session = await anext(session_generator)
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
    finally:
        await session.close()

@app.get("/usuarios/activos/", response_model=List[Usuario])
async def listar_usuarios_activos():
    session_generator = get_session()
    session = await anext(session_generator)
    try:
        usuarios = await UserOperations.get_active_users(session)
        return usuarios
    finally:
        await session.close()

@app.get("/usuarios/premium/activos/", response_model=List[Usuario])
async def listar_usuarios_premium_activos():
    session_generator = get_session()
    session = await anext(session_generator)
    try:
        usuarios = await UserOperations.get_premium_active_users(session)
        return usuarios
    finally:
        await session.close()

# Endpoint de ejemplo adicional
@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hola {name}, bienvenido al sistema de usuarios"}