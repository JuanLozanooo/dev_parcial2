from datetime import datetime
from enum import Enum
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship


# --- Enums para estados controlados ---
class EstadoTarea(str, Enum):
    PENDIENTE = "Pendiente"
    EN_EJECUCION = "En ejecución"
    REALIZADA = "Realizada"
    CANCELADA = "Cancelada"

class EstadoUsuario(str, Enum):
    ACTIVO = "Activo"
    INACTIVO = "Inactivo"
    ELIMINADO = "Eliminado"

class Usuario(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    email: str
    estado: EstadoUsuario = Field(default=EstadoUsuario.ACTIVO)
    premium: bool = Field(default=False)
    fecha_modificacion: Optional[datetime] = Field(default=None)

    # Relación con tareas
    tareas: List["Tarea"] = Relationship(back_populates="usuario")  # Nuevo campo


class Tarea(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(max_length=100)
    descripcion: Optional[str] = Field(default=None, max_length=500)
    fecha_creacion: datetime = Field(default_factory=datetime.now)
    fecha_modificacion: Optional[datetime] = Field(default=None)
    estado: EstadoTarea = Field(default=EstadoTarea.PENDIENTE)

    # Relación con usuario
    usuario_id: Optional[int] = Field(default=None, foreign_key="usuario.id")
    usuario: Optional[Usuario] = Relationship(back_populates="tareas")

# --- Actualizar imports para relaciones ---
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from sqlmodel import Relationship