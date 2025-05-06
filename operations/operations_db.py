from typing import List, Optional
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from data.models import Usuario, EstadoUsuario

class UserOperations:
    """Operaciones CRUD para usuarios (solo por ID)"""

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