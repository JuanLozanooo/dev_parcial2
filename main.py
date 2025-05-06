from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from utils.connection_db import init_db, get_session
from operations.operations_db import UserOperations
from data.models import Usuario, EstadoUsuario
from typing import List, AsyncGenerator
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import text

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

# Endpoints de Usuarios
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

# Endpoint de ejemplo adicional
@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hola {name}, bienvenido al sistema de usuarios"}


@app.get("/debug-db")
async def debug_db():
    session_generator = get_session()
    session = await anext(session_generator)

    try:
        # Consulta mejorada para detectar el motor de base de datos
        result = await session.execute(
            text("SELECT version()")
        )
        db_version = result.scalar()

        # Consulta de tablas
        tables = await session.execute(
            text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
        )
        table_list = [t[0] for t in tables.all()]

        is_postgres = "postgresql" in db_version.lower() if db_version else False

        return {
            "database_engine": "PostgreSQL" if is_postgres else "SQLite",
            "version": db_version,
            "tables": table_list,
            "is_clever_cloud": is_postgres,
            "message": "✅ Conectado a PostgreSQL en Clever Cloud" if is_postgres
            else "⚠ Usando SQLite local (no debería ocurrir con Clever Cloud)"
        }
    except Exception as e:
        # Si falla, es probablemente SQLite
        try:
            result = await session.execute(text("SELECT sqlite_version()"))
            version = result.scalar()
            return {
                "database_engine": "SQLite",
                "version": version,
                "tables": [],
                "is_clever_cloud": False,
                "message": "⚠ Fallo al conectar a Clever Cloud. Usando SQLite local"
            }
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error grave: No se pudo conectar a ninguna base de datos. {str(e)}"
            )
    finally:
        await session.close()