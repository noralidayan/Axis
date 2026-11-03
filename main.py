
# Instalar las dependencias necesarias:
# pip install "fastapi[all]"
#
# Iniciar el servidor desde la terminal:
# uvicorn main:app --reload
# (Para detenerlo, presionar CTRL+C)
#
# API: http://127.0.0.1:8000
# Documentación interactiva de los endpoints: http://127.0.0.1:8000/docs

# ---------- Importación de librerías ----------
import json
import re
from datetime import date, datetime, timedelta
from pathlib import Path

# FastAPI: creación de la API, validación de datos y manejo de errores.
# Depends y Header permiten identificar al usuario a partir de una cabecera HTTP.
from fastapi import Depends, FastAPI, Header, HTTPException

# Permite que el frontend pueda realizar solicitudes al backend desde otro origen.
from fastapi.middleware.cors import CORSMiddleware

# Permite publicar los archivos del frontend (HTML, CSS y JavaScript).
from fastapi.staticfiles import StaticFiles

# BaseModel se utiliza para definir y validar los datos que recibe la API.
from pydantic import BaseModel


# ---------- Configuración de la aplicación ----------
app = FastAPI(title="AXIS - Turnos médicos (backend simulado)")

# CORS: permite que el frontend pueda comunicarse con la API aunque se ejecute
# desde otro origen, por ejemplo, mediante Live Server o abriendo un archivo local.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# Expresión regular utilizada para comprobar que el correo tenga un formato válido.
EMAIL_RE = re.compile(r"^[\w.+-]+@[\w-]+(\.[\w-]+)+$")


# ---------- Modelos de datos ----------
# Estos modelos definen qué información debe recibir cada operación de la API.
# Pydantic se encarga de validar los datos antes de ejecutar el endpoint.

class Login(BaseModel):
    email: str
    password: str


class Registro(BaseModel):
    nombre: str
    apellido: str
    nacimiento: str
    email: str
    telefono: str
    direccion: str = ""
    clave: str


class TurnoIn(BaseModel):
    profesional_id: int
    fecha: str  # Fecha del turno en formato AAAA-MM-DD.
    hora: str   # Horario del turno en formato HH:MM.


class ReprogramarIn(BaseModel):
    fecha: str
    hora: str


# ---------- Datos de ejemplo ----------
# En esta versión simulada, las listas funcionan como una base de datos.
# Contienen usuarios, especialidades, profesionales y turnos de prueba.

usuarios_db = [
    {"email": "martina.lopez@axis.com.ar", "nombre": "Martina", "apellido": "López", "clave": "Axis2026!",
     "telefono": "11 5555-0101", "nacimiento": "1994-03-12", "direccion": "Av. Libertador 1200"},
    {"email": "lucas.benitez@axis.com.ar", "nombre": "Lucas", "apellido": "Benítez", "clave": "lucas12345",
     "telefono": "11 5555-0202", "nacimiento": "1988-11-30", "direccion": "Belgrano 450"},
    {"email": "carolina.ruiz@axis.com.ar", "nombre": "Carolina", "apellido": "Ruiz", "clave": "Turnos2026",
     "telefono": "11 5555-0303", "nacimiento": "2001-07-05", "direccion": ""},
]

# Especialidades disponibles para la búsqueda de profesionales.
especialidades = ["Clínica médica", "Odontología", "Endocrinología", "Cardiología", "Dermatología"]

# Profesionales disponibles, identificados mediante un ID.
# Cada uno está asociado a una especialidad y a un centro médico.
profesionales_db = [
    {"id": 1, "nombre": "Dr. Ramiro Sánchez", "especialidad": "Clínica médica", "centro": "Clínica del Sol"},
    {"id": 2, "nombre": "Dra. Laura Méndez", "especialidad": "Odontología", "centro": "Clínica del Sol"},
    {"id": 3, "nombre": "Dr. Juan Pérez", "especialidad": "Endocrinología", "centro": "Clínica del Sol"},
    {"id": 4, "nombre": "Dra. Sofía Ibarra", "especialidad": "Endocrinología", "centro": "Clínica del Sol"},
    {"id": 5, "nombre": "Dr. Martín Gallo", "especialidad": "Cardiología", "centro": "Clínica del Sol"},
    {"id": 6, "nombre": "Dra. Ana Torres", "especialidad": "Dermatología", "centro": "Clínica del Sol"},
]

# Horarios que se utilizan como base para generar la disponibilidad de turnos.
HORARIOS_BASE = ["09:00", "09:30", "10:30", "11:00", "14:30", "16:00"]


# ---------- Funciones auxiliares ----------
def proximo_habil(dias):
    # Calcula una fecha a partir de hoy y avanza si cae sábado o domingo.
    d = date.today() + timedelta(days=dias)
    while d.weekday() >= 5:
        d += timedelta(days=1)
    return d.isoformat()


def nuevo_turno(id_, prof_id, fecha, hora, estado, email):
    # Busca los datos del profesional para asociarlos al turno.
    p = next(p for p in profesionales_db if p["id"] == prof_id)

    # Construye el registro del turno con los datos del paciente y del profesional.
    return {"id": id_, "email": email, "profesional_id": prof_id, "profesional": p["nombre"],
            "especialidad": p["especialidad"], "centro": p["centro"],
            "fecha": fecha, "hora": hora, "estado": estado}


# Correos utilizados para asociar los turnos de ejemplo con los pacientes.
M, L = "martina.lopez@axis.com.ar", "lucas.benitez@axis.com.ar"

# Turnos iniciales para probar el funcionamiento del sistema.
# Se incluyen distintos estados y fechas para poder probar el panel y los filtros.
turnos_db = [
    nuevo_turno(1, 1, proximo_habil(3), "10:30", "Confirmado", M),
    nuevo_turno(2, 2, proximo_habil(10), "15:00", "Pendiente", M),
    nuevo_turno(3, 3, (date.today() - timedelta(days=20)).isoformat(), "11:00", "Realizado", M),
    nuevo_turno(4, 5, proximo_habil(5), "09:30", "Confirmado", L),
]


# ---------- Persistencia en archivo ----------
# Los datos de usuarios y turnos se guardan en datos.json, ubicado junto a main.py.
# De esta manera, los cambios se conservan aunque se reinicie el servidor.
# Para recuperar los datos de ejemplo, se puede eliminar este archivo.

ARCHIVO = Path(__file__).parent / "datos.json"


def guardar():
    # Convierte las listas de usuarios y turnos a formato JSON y las escribe en el archivo.
    ARCHIVO.write_text(json.dumps({"usuarios": usuarios_db, "turnos": turnos_db},
                                  ensure_ascii=False, indent=2), encoding="utf-8")


# Al iniciar el backend, comprueba si ya existe un archivo con datos guardados.
if ARCHIVO.exists():
    # Si existe, recupera la información y actualiza las listas utilizadas por la aplicación.
    guardado = json.loads(ARCHIVO.read_text(encoding="utf-8"))
    usuarios_db[:] = guardado["usuarios"]
    turnos_db[:] = guardado["turnos"]
else:
    # Si todavía no existe, crea el archivo con los datos iniciales.
    guardar()


# ---------- Utilidades ----------
def sin_clave(u):
    # Devuelve los datos del usuario excluyendo su contraseña.
    # Se utiliza antes de enviar información del paciente al frontend.
    return {k: v for k, v in u.items() if k != "clave"}


def usuario_actual(x_user: str = Header(...)):
    """Busca al paciente correspondiente al correo recibido en la cabecera X-User."""

    # El frontend envía el correo del usuario para identificar la sesión iniciada.
    u = next((u for u in usuarios_db if u["email"] == x_user.lower()), None)

    # Si no se encuentra el correo, se rechaza la solicitud.
    if not u:
        raise HTTPException(401, "Sesión inválida. Volvé a iniciar sesión.")

    return u


def buscar_turno(turno_id, u):
    # Busca el turno por su ID y comprueba que pertenezca al paciente de la sesión.
    t = next((t for t in turnos_db if t["id"] == turno_id and t["email"] == u["email"]), None)

    # Si el turno no existe o pertenece a otro paciente, devuelve un error.
    if not t:
        raise HTTPException(404, "Turno no encontrado")

    return t


def horarios_libres(prof_id, fecha, ignorar_id=None):
    # Convierte la fecha recibida en un objeto date para poder validarla.
    try:
        d = datetime.strptime(fecha, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(400, "Fecha inválida (use AAAA-MM-DD)")

    # No se ofrecen horarios para fechas pasadas ni para sábados o domingos.
    if d < date.today() or d.weekday() >= 5:
        return []

    # Obtiene los horarios que ya están ocupados por turnos pendientes o confirmados.
    # Solo considera las reservas del profesional y de la fecha consultada.
    ocupados = {t["hora"] for t in turnos_db
                if t["profesional_id"] == prof_id and t["fecha"] == fecha
                and t["estado"] in ("Confirmado", "Pendiente") and t["id"] != ignorar_id}

    # Devuelve los horarios base que todavía no están ocupados.
    # ignorar_id permite excluir un turno al consultar su propia reprogramación.
    return [h for h in HORARIOS_BASE if h not in ocupados]


# ---------- Cuenta: inicio de sesión y registro ----------

@app.post("/api/login")
def login(datos: Login):
    # Normaliza el correo para evitar diferencias por espacios o mayúsculas.
    email = datos.email.strip().lower()

    if not EMAIL_RE.match(email):
        raise HTTPException(400, "Ingresá un correo electrónico válido")

    if len(datos.password) < 8:
        raise HTTPException(400, "La contraseña debe tener al menos 8 caracteres")

    # Comprueba que exista un usuario con ese correo y contraseña.
    u = next((u for u in usuarios_db if u["email"] == email and u["clave"] == datos.password), None)

    if not u:
        raise HTTPException(401, "Correo o contraseña incorrectos")

    # Devuelve los datos del paciente sin incluir su contraseña.
    return sin_clave(u)


@app.post("/api/registro", status_code=201)
def registro(datos: Registro):
    # Normaliza el correo antes de comprobarlo y guardarlo.
    email = datos.email.strip().lower()

    # Verifica que los campos obligatorios tengan contenido.
    if not datos.nombre.strip() or not datos.apellido.strip():
        raise HTTPException(400, "Completá nombre y apellido")

    if not EMAIL_RE.match(email):
        raise HTTPException(400, "Ingresá un correo electrónico válido")

    if len(datos.clave) < 8:
        raise HTTPException(400, "La contraseña debe tener al menos 8 caracteres")

    # Comprueba que no exista otra cuenta registrada con el mismo correo.
    if any(u["email"] == email for u in usuarios_db):
        raise HTTPException(409, "Ya existe una cuenta con ese correo")

    # Agrega el nuevo paciente a la lista y guarda los cambios en el archivo.
    usuarios_db.append({**datos.model_dump(), "email": email,
                        "nombre": datos.nombre.strip(), "apellido": datos.apellido.strip()})
    guardar()

    return {"ok": True}


# Devuelve los datos del paciente que tiene la sesión iniciada.
# Depends ejecuta usuario_actual antes de ingresar al endpoint.
@app.get("/api/paciente")
def get_paciente(u: dict = Depends(usuario_actual)):
    return sin_clave(u)


# ---------- Catálogo de especialidades y profesionales ----------

@app.get("/api/especialidades")
def get_especialidades():
    # Devuelve la lista de especialidades disponibles.
    return especialidades


@app.get("/api/profesionales")
def get_profesionales(especialidad: str | None = None):
    # Si se recibe una especialidad, devuelve solo los profesionales asociados.
    if especialidad:
        return [p for p in profesionales_db if p["especialidad"] == especialidad]

    # Si no se especifica una especialidad, devuelve todos los profesionales.
    return profesionales_db


@app.get("/api/horarios")
def get_horarios(profesional_id: int, fecha: str, ignorar_id: int | None = None):
    # Consulta los horarios disponibles para un profesional en una fecha determinada.
    return horarios_libres(profesional_id, fecha, ignorar_id)


# ---------- Gestión de turnos del paciente ----------

def mis_turnos(u):
    # Obtiene únicamente los turnos asociados al correo del paciente actual.
    return [t for t in turnos_db if t["email"] == u["email"]]


@app.get("/api/resumen")
def resumen(u: dict = Depends(usuario_actual)):
    # Calcula las cantidades que se muestran en los indicadores del panel.
    hoy = date.today().isoformat()
    mios = mis_turnos(u)

    # Considera próximos los turnos pendientes o confirmados cuya fecha no pasó.
    activos = [t for t in mios if t["estado"] in ("Confirmado", "Pendiente") and t["fecha"] >= hoy]

    return {"proximos": len(activos),
            "realizados": len([t for t in mios if t["estado"] == "Realizado"]),
            "recordatorios": len([t for t in activos if t["estado"] == "Confirmado"])}


@app.get("/api/turnos")
def get_turnos(vista: str | None = None, u: dict = Depends(usuario_actual)):
    # Obtiene los turnos del paciente y aplica el filtro solicitado.
    hoy = date.today().isoformat()
    mios = mis_turnos(u)

    if vista == "proximos":
        # Turnos pendientes o confirmados con fecha actual o futura.
        lista = [t for t in mios if t["estado"] in ("Confirmado", "Pendiente") and t["fecha"] >= hoy]

    elif vista == "historial":
        # Turnos que ya fueron realizados.
        lista = [t for t in mios if t["estado"] == "Realizado"]

    elif vista == "cancelados":
        # Turnos que fueron cancelados.
        lista = [t for t in mios if t["estado"] == "Cancelado"]

    else:
        # Si no se especifica un filtro, devuelve todos los turnos del paciente.
        lista = mios

    # Ordena los resultados por fecha y luego por horario.
    return sorted(lista, key=lambda t: (t["fecha"], t["hora"]))


@app.get("/api/turnos/{turno_id}")
def get_turno(turno_id: int, u: dict = Depends(usuario_actual)):
    # Busca un turno específico y verifica que pertenezca al paciente actual.
    return buscar_turno(turno_id, u)


@app.post("/api/turnos", status_code=201)
def crear_turno(datos: TurnoIn, u: dict = Depends(usuario_actual)):
    # Antes de crear el turno, vuelve a comprobar que el horario siga disponible.
    # Si ya está ocupado, devuelve un error 409 para evitar la reserva.
    if datos.hora not in horarios_libres(datos.profesional_id, datos.fecha):
        raise HTTPException(409, "Ese horario ya no está disponible")

    # Genera un nuevo ID y crea el turno asociado al paciente de la sesión.
    t = nuevo_turno(max([t["id"] for t in turnos_db], default=0) + 1, datos.profesional_id,
                    datos.fecha, datos.hora, "Pendiente", u["email"])

    # Agrega el turno a la lista y guarda los cambios.
    turnos_db.append(t)
    guardar()

    return t


@app.put("/api/turnos/{turno_id}/confirmar")
def confirmar_turno(turno_id: int, u: dict = Depends(usuario_actual)):
    # Busca el turno y cambia su estado a confirmado.
    t = buscar_turno(turno_id, u)
    t["estado"] = "Confirmado"

    guardar()
    return t


@app.put("/api/turnos/{turno_id}/cancelar")
def cancelar_turno(turno_id: int, u: dict = Depends(usuario_actual)):
    # Busca el turno y actualiza su estado a cancelado.
    t = buscar_turno(turno_id, u)
    t["estado"] = "Cancelado"

    guardar()
    return t


@app.put("/api/turnos/{turno_id}/reprogramar")
def reprogramar_turno(turno_id: int, datos: ReprogramarIn, u: dict = Depends(usuario_actual)):
    # Busca el turno que se desea modificar y verifica que pertenezca al paciente.
    t = buscar_turno(turno_id, u)

    # Comprueba que el nuevo horario esté disponible.
    # Se excluye el turno actual para que no aparezca como ocupado por sí mismo.
    if datos.hora not in horarios_libres(t["profesional_id"], datos.fecha, turno_id):
        raise HTTPException(409, "Ese horario ya no está disponible")

    # Actualiza la fecha y la hora, y deja el turno pendiente de confirmación.
    t["fecha"], t["hora"], t["estado"] = datos.fecha, datos.hora, "Pendiente"

    guardar()
    return t


# ---------- Publicación del frontend ----------
# Permite acceder a los archivos HTML, CSS, JavaScript e imágenes desde el servidor.
# Se coloca al final para que las rutas de la API se registren antes que las rutas estáticas.
app.mount("/", StaticFiles(directory="static", html=True), name="static")
