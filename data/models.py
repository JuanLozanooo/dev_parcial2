from datetime import datetime
from enum import Enum
from typing import Optional
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

# --- Modelo de Usuario ---
class Usuario(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(max_length=50)
    email: str = Field(max_length=100, unique=True)
    estado: EstadoUsuario = Field(default=EstadoUsuario.ACTIVO)
    premium: bool = Field(default=False)

    # Relación opcional con tareas (1 usuario → muchas tareas)
    tareas: list["Tarea"] = Relationship(back_populates="usuario")

# --- Modelo de Tarea ---
class Tarea(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(max_length=100)
    descripcion: Optional[str] = Field(default=None, max_length=500)
    fecha_creacion: datetime = Field(default_factory=datetime.now)
    fecha_modificacion: Optional[datetime] = Field(default=None)
    estado: EstadoTarea = Field(default=EstadoTarea.PENDIENTE)
    
    # Clave foránea al usuario (relación muchos a 1)
    usuario_id: Optional[int] = Field(default=None, foreign_key="usuario.id")
    usuario: Optional[Usuario] = Relationship(back_populates="tareas")

# --- Actualizar imports para relaciones ---
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from sqlmodel import Relationship