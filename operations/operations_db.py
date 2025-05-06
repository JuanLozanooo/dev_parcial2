from typing import List, Optional
from sqlmodel import select, and_
from sqlmodel.ext.asyncio.session import AsyncSession
from data.models import Usuario, EstadoUsuario
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