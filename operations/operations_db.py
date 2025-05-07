from typing import List, Optional
from sqlmodel import select, and_
from sqlmodel.ext.asyncio.session import AsyncSession
from data.models import Usuario, EstadoUsuario, Tarea, EstadoTarea
from datetime import datetime

class UserOperations:

    @staticmethod
    async def create_user(
            session: AsyncSession,
            nombre: str,
            email: str,
            premium: bool = False,
            estado: EstadoUsuario = EstadoUsuario.ACTIVO
    ) -> Usuario:
        """Crea un nuevo usuario con estado 'Activo' por defecto"""
        new_user = Usuario(
            nombre=nombre,
            email=email,
            premium=premium,
            estado=estado
        )
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        return new_user

    @staticmethod
    async def get_all_users(session: AsyncSession) -> List[Usuario]:
        """Obtiene TODOS los usuarios (incluyendo inactivos, excepto eliminados)"""
        result = await session.execute(
            select(Usuario).where(Usuario.estado != EstadoUsuario.ELIMINADO)
        )
        return result.scalars().all()

    @staticmethod
    async def get_user_by_id(session: AsyncSession, user_id: int) -> Optional[Usuario]:
        """Obtiene un usuario por ID (incluye inactivos pero NO eliminados)"""
        result = await session.execute(
            select(Usuario).where(
                Usuario.id == user_id,
                Usuario.estado != EstadoUsuario.ELIMINADO
            ))
        return result.scalar_one_or_none()

    @staticmethod
    async def update_user_status(
            session: AsyncSession,
            user_id: int,
            new_status: EstadoUsuario
    ) -> Optional[Usuario]:
        """Actualiza el estado de un usuario (PATCH/PUT)"""
        user = await UserOperations.get_user_by_id(session, user_id)
        if not user:
            return None

        user.estado = new_status
        user.fecha_modificacion = datetime.now()

        await session.commit()
        await session.refresh(user)
        return user

    @staticmethod
    async def upgrade_to_premium(
            session: AsyncSession,
            user_id: int
    ) -> Optional[Usuario]:
        """Hace a un usuario premium (PATCH/PUT)"""
        user = await UserOperations.get_user_by_id(session, user_id)
        if not user:
            return None

        user.premium = True
        user.fecha_modificacion = datetime.now()
        await session.commit()
        await session.refresh(user)
        return user

    @staticmethod
    async def get_active_users(
            session: AsyncSession
    ) -> List[Usuario]:
        """Obtiene todos los usuarios activos (GET)"""
        result = await session.execute(
            select(Usuario).where(
                Usuario.estado == EstadoUsuario.ACTIVO
            )
        )
        return result.scalars().all()

    @staticmethod
    async def get_premium_active_users(
            session: AsyncSession
    ) -> List[Usuario]:
        """Obtiene usuarios premium+activos (GET)"""
        result = await session.execute(
            select(Usuario).where(
                and_(
                    Usuario.premium == True,
                    Usuario.estado == EstadoUsuario.ACTIVO
                )
            )
        )
        return result.scalars().all()

class TaskOperations:

    @staticmethod
    async def create_task(
            session: AsyncSession,
            usuario_id: int,
            nombre: str,
            descripcion: Optional[str] = None
    ) -> Tarea:
        """Crea una nueva tarea asociada a un usuario"""
        user = await UserOperations.get_user_by_id(session, usuario_id)
        if not user:
            raise ValueError("El usuario no existe")

        nueva_tarea = Tarea(
            nombre=nombre,
            descripcion=descripcion,
            usuario_id=usuario_id
        )
        session.add(nueva_tarea)
        await session.commit()
        await session.refresh(nueva_tarea)
        return nueva_tarea

    @staticmethod
    async def get_user_tasks(
            session: AsyncSession,
            usuario_id: int
    ) -> List[Tarea]:
        """Obtiene todas las tareas de un usuario"""
        result = await session.execute(
            select(Tarea).where(Tarea.usuario_id == usuario_id)
        )
        return result.scalars().all()

    @staticmethod
    async def update_task_status(
            session: AsyncSession,
            task_id: int,
            new_status: EstadoTarea
    ) -> Optional[Tarea]:
        """Actualiza el estado de una tarea"""
        task = await session.get(Tarea, task_id)
        if not task:
            return None

        task.estado = new_status
        task.fecha_modificacion = datetime.now()
        await session.commit()
        await session.refresh(task)
        return task

    @staticmethod
    async def get_task_by_id(
            session: AsyncSession,
            task_id: int
    ) -> Optional[Tarea]:
        """Obtiene una tarea por su ID"""
        return await session.get(Tarea, task_id)