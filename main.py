# Instalar: pip install "fastapi[all]"
# Iniciar:  uvicorn main:app --reload      (detener con CTRL+C)
# Web:      http://127.0.0.1:8000
# Swagger:  http://127.0.0.1:8000/docs
 
import json
import re
from datetime import date, datetime, timedelta
from pathlib import Path
from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
 
app = FastAPI(title="AXIS - Turnos médicos (backend simulado)")
 
# CORS: permite que el HTML abierto desde otro origen (file://, Live Server) llame a la API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)
 
EMAIL_RE = re.compile(r"^[\w.+-]+@[\w-]+(\.[\w-]+)+$")
 
# ---------- Entidades ----------
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
    fecha: str  # AAAA-MM-DD
    hora: str   # HH:MM
 
class ReprogramarIn(BaseModel):
    fecha: str
    hora: str
 
 
# ---------- "Base de datos" en memoria ----------
usuarios_db = [
    {"email": "martina.lopez@axis.com.ar", "nombre": "Martina", "apellido": "López", "clave": "Axis2026!",
     "telefono": "11 5555-0101", "nacimiento": "1994-03-12", "direccion": "Av. Libertador 1200"},
    {"email": "lucas.benitez@axis.com.ar", "nombre": "Lucas", "apellido": "Benítez", "clave": "lucas12345",
     "telefono": "11 5555-0202", "nacimiento": "1988-11-30", "direccion": "Belgrano 450"},
    {"email": "carolina.ruiz@axis.com.ar", "nombre": "Carolina", "apellido": "Ruiz", "clave": "Turnos2026",
     "telefono": "11 5555-0303", "nacimiento": "2001-07-05", "direccion": ""},
]
 
especialidades = ["Clínica médica", "Odontología", "Endocrinología", "Cardiología", "Dermatología"]
 
profesionales_db = [
    {"id": 1, "nombre": "Dr. Ramiro Sánchez", "especialidad": "Clínica médica", "centro": "Clínica del Sol"},
    {"id": 2, "nombre": "Dra. Laura Méndez", "especialidad": "Odontología", "centro": "Clínica del Sol"},
    {"id": 3, "nombre": "Dr. Juan Pérez", "especialidad": "Endocrinología", "centro": "Clínica del Sol"},
    {"id": 4, "nombre": "Dra. Sofía Ibarra", "especialidad": "Endocrinología", "centro": "Clínica del Sol"},
    {"id": 5, "nombre": "Dr. Martín Gallo", "especialidad": "Cardiología", "centro": "Clínica del Sol"},
    {"id": 6, "nombre": "Dra. Ana Torres", "especialidad": "Dermatología", "centro": "Clínica del Sol"},
]
 
HORARIOS_BASE = ["09:00", "09:30", "10:30", "11:00", "14:30", "16:00"]
 
 
def proximo_habil(dias):
    d = date.today() + timedelta(days=dias)
    while d.weekday() >= 5:
        d += timedelta(days=1)
    return d.isoformat()
 
 
def nuevo_turno(id_, prof_id, fecha, hora, estado, email):
    p = next(p for p in profesionales_db if p["id"] == prof_id)
    return {"id": id_, "email": email, "profesional_id": prof_id, "profesional": p["nombre"],
            "especialidad": p["especialidad"], "centro": p["centro"],
            "fecha": fecha, "hora": hora, "estado": estado}
 
 
M, L = "martina.lopez@axis.com.ar", "lucas.benitez@axis.com.ar"
turnos_db = [
    nuevo_turno(1, 1, proximo_habil(3), "10:30", "Confirmado", M),
    nuevo_turno(2, 2, proximo_habil(10), "15:00", "Pendiente", M),
    nuevo_turno(3, 3, (date.today() - timedelta(days=20)).isoformat(), "11:00", "Realizado", M),
    nuevo_turno(4, 5, proximo_habil(5), "09:30", "Confirmado", L),
]
 
 
# ---------- Persistencia en archivo ----------
# usuarios_db y turnos_db se guardan en datos.json (junto a main.py), así los registros
# NO se pierden cuando el servidor se reinicia. Para volver a los datos de ejemplo: borrar datos.json.
ARCHIVO = Path(__file__).parent / "datos.json"
 
 
def guardar():
    ARCHIVO.write_text(json.dumps({"usuarios": usuarios_db, "turnos": turnos_db},
                                  ensure_ascii=False, indent=2), encoding="utf-8")
 
 
if ARCHIVO.exists():
    guardado = json.loads(ARCHIVO.read_text(encoding="utf-8"))
    usuarios_db[:] = guardado["usuarios"]
    turnos_db[:] = guardado["turnos"]
else:
    guardar()
 
 
# ---------- Utilidades ----------
def sin_clave(u):
    return {k: v for k, v in u.items() if k != "clave"}
 
 
def usuario_actual(x_user: str = Header(...)):
    """El frontend envía el correo de la sesión en la cabecera X-User."""
    u = next((u for u in usuarios_db if u["email"] == x_user.lower()), None)
    if not u:
        raise HTTPException(401, "Sesión inválida. Volvé a iniciar sesión.")
    return u
 
 
def buscar_turno(turno_id, u):
    t = next((t for t in turnos_db if t["id"] == turno_id and t["email"] == u["email"]), None)
    if not t:
        raise HTTPException(404, "Turno no encontrado")
    return t
 
 
def horarios_libres(prof_id, fecha, ignorar_id=None):
    try:
        d = datetime.strptime(fecha, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(400, "Fecha inválida (use AAAA-MM-DD)")
 
    if d < date.today() or d.weekday() >= 5:
        return []
 
    ocupados = {t["hora"] for t in turnos_db
                if t["profesional_id"] == prof_id and t["fecha"] == fecha
                and t["estado"] in ("Confirmado", "Pendiente") and t["id"] != ignorar_id}
 
    return [h for h in HORARIOS_BASE if h not in ocupados]
 
 
# ---------- Cuenta ----------
@app.post("/api/login")
def login(datos: Login):
    email = datos.email.strip().lower()
    if not EMAIL_RE.match(email):
        raise HTTPException(400, "Ingresá un correo electrónico válido")
    if len(datos.password) < 8:
        raise HTTPException(400, "La contraseña debe tener al menos 8 caracteres")
 
    u = next((u for u in usuarios_db if u["email"] == email and u["clave"] == datos.password), None)
    if not u:
        raise HTTPException(401, "Correo o contraseña incorrectos")
    return sin_clave(u)
 
 
@app.post("/api/registro", status_code=201)
def registro(datos: Registro):
    email = datos.email.strip().lower()
    if not datos.nombre.strip() or not datos.apellido.strip():
        raise HTTPException(400, "Completá nombre y apellido")
    if not EMAIL_RE.match(email):
        raise HTTPException(400, "Ingresá un correo electrónico válido")
    if len(datos.clave) < 8:
        raise HTTPException(400, "La contraseña debe tener al menos 8 caracteres")
    if any(u["email"] == email for u in usuarios_db):
        raise HTTPException(409, "Ya existe una cuenta con ese correo")
 
    usuarios_db.append({**datos.model_dump(), "email": email,
                        "nombre": datos.nombre.strip(), "apellido": datos.apellido.strip()})
    guardar()
    return {"ok": True}
 
 
@app.get("/api/paciente")
def get_paciente(u: dict = Depends(usuario_actual)):
    return sin_clave(u)
 
 
# ---------- Catálogo ----------
@app.get("/api/especialidades")
def get_especialidades():
    return especialidades
 
 
@app.get("/api/profesionales")
def get_profesionales(especialidad: str | None = None):
    if especialidad:
        return [p for p in profesionales_db if p["especialidad"] == especialidad]
    return profesionales_db
 
 
@app.get("/api/horarios")
def get_horarios(profesional_id: int, fecha: str, ignorar_id: int | None = None):
    return horarios_libres(profesional_id, fecha, ignorar_id)
 
 
# ---------- Turnos (de la persona con sesión iniciada) ----------
def mis_turnos(u):
    return [t for t in turnos_db if t["email"] == u["email"]]
 
 
@app.get("/api/resumen")
def resumen(u: dict = Depends(usuario_actual)):
    hoy = date.today().isoformat()
    mios = mis_turnos(u)
    activos = [t for t in mios if t["estado"] in ("Confirmado", "Pendiente") and t["fecha"] >= hoy]
 
    return {"proximos": len(activos),
            "realizados": len([t for t in mios if t["estado"] == "Realizado"]),
            "recordatorios": len([t for t in activos if t["estado"] == "Confirmado"])}
 
 
@app.get("/api/turnos")
def get_turnos(vista: str | None = None, u: dict = Depends(usuario_actual)):
    hoy = date.today().isoformat()
    mios = mis_turnos(u)
 
    if vista == "proximos":
        lista = [t for t in mios if t["estado"] in ("Confirmado", "Pendiente") and t["fecha"] >= hoy]
    elif vista == "historial":
        lista = [t for t in mios if t["estado"] == "Realizado"]
    elif vista == "cancelados":
        lista = [t for t in mios if t["estado"] == "Cancelado"]
    else:
        lista = mios
 
    return sorted(lista, key=lambda t: (t["fecha"], t["hora"]))
 
 
@app.get("/api/turnos/{turno_id}")
def get_turno(turno_id: int, u: dict = Depends(usuario_actual)):
    return buscar_turno(turno_id, u)
 
 
@app.post("/api/turnos", status_code=201)
def crear_turno(datos: TurnoIn, u: dict = Depends(usuario_actual)):
    if datos.hora not in horarios_libres(datos.profesional_id, datos.fecha):
        raise HTTPException(409, "Ese horario ya no está disponible")
 
    t = nuevo_turno(max([t["id"] for t in turnos_db], default=0) + 1, datos.profesional_id,
                    datos.fecha, datos.hora, "Pendiente", u["email"])
    turnos_db.append(t)
    guardar()
    return t
 
 
@app.put("/api/turnos/{turno_id}/confirmar")
def confirmar_turno(turno_id: int, u: dict = Depends(usuario_actual)):
    t = buscar_turno(turno_id, u)
    t["estado"] = "Confirmado"
    guardar()
    return t
 
 
@app.put("/api/turnos/{turno_id}/cancelar")
def cancelar_turno(turno_id: int, u: dict = Depends(usuario_actual)):
    t = buscar_turno(turno_id, u)
    t["estado"] = "Cancelado"
    guardar()
    return t
 
 
@app.put("/api/turnos/{turno_id}/reprogramar")
def reprogramar_turno(turno_id: int, datos: ReprogramarIn, u: dict = Depends(usuario_actual)):
    t = buscar_turno(turno_id, u)
    if datos.hora not in horarios_libres(t["profesional_id"], datos.fecha, turno_id):
        raise HTTPException(409, "Ese horario ya no está disponible")
 
    t["fecha"], t["hora"], t["estado"] = datos.fecha, datos.hora, "Pendiente"
    guardar()
    return t
 
 
# Sirve el frontend (HTML/CSS/JS) desde /static. Debe ir al final.
app.mount("/", StaticFiles(directory="static", html=True), name="static")