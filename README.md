
# AXIS – Sistema de turnos médicos

AXIS es una aplicación web para la gestión de turnos médicos. Permite a los pacientes registrarse, iniciar sesión, consultar especialidades y profesionales disponibles, solicitar turnos y administrar sus reservas.

El proyecto fue desarrollado como una simulación de un sistema de turnos médicos, utilizando HTML, CSS y JavaScript para el frontend, y FastAPI para el backend.

## Tecnologías utilizadas

### Frontend
- HTML5
- CSS3
- JavaScript

### Backend
- Python
- FastAPI
- Uvicorn
- Pydantic

### Almacenamiento
- Archivo JSON (`datos.json`) para guardar los datos de manera local.

## Funcionalidades principales

- Registro de pacientes.
- Inicio de sesión.
- Consulta de especialidades médicas.
- Consulta de profesionales.
- Visualización de días y horarios disponibles.
- Solicitud de turnos médicos.
- Consulta de próximos turnos e historial.
- Cancelación y reprogramación de turnos.
- Visualización y edición de datos del perfil del paciente.

## Requisitos previos

Antes de ejecutar el proyecto, es necesario tener instalado:

- Python 3.10 o superior.
- pip (administrador de paquetes de Python).
- Un navegador web.
- Visual Studio Code (recomendado).

Para comprobar que Python y pip están instalados, abrir una terminal y ejecutar:

```bash
python --version
pip --version
```

## Instalación y ejecución del backend

Seguir estos pasos para iniciar el servidor de FastAPI.

### 1. Abrir el proyecto

Abrir la carpeta del proyecto AXIS desde Visual Studio Code.

Luego, abrir una terminal y ubicarse en la carpeta donde se encuentra el archivo `main.py`.

Es importante ejecutar los siguientes comandos desde esa ubicación.

### 2. Crear un entorno virtual (recomendado)

El entorno virtual permite instalar las dependencias del proyecto sin afectar otros proyectos de Python.

En Windows:

```bash
python -m venv venv
```

Activarlo con:

```bash
venv\Scripts\activate
```

Si se utiliza PowerShell y aparece un error relacionado con la ejecución de scripts, se puede utilizar la terminal CMD o configurar los permisos correspondientes.

### 3. Instalar las dependencias

Con el entorno virtual activado, ejecutar:

```bash
pip install "fastapi[all]"
```

Este comando instala FastAPI y sus dependencias adicionales, incluyendo Uvicorn, necesario para ejecutar el servidor.

### 4. Iniciar el servidor

Ejecutar el siguiente comando:

```bash
uvicorn main:app --reload
```

Donde:
- `main` hace referencia al archivo `main.py`.
- `app` es la instancia de FastAPI definida dentro de ese archivo.
- `--reload` permite reiniciar automáticamente el servidor cuando se realizan cambios en el código.

Si el servidor inicia correctamente, aparecerá un mensaje indicando que está ejecutándose en:

```text
http://127.0.0.1:8000
```

**Importante:** no cerrar la terminal mientras se esté utilizando la aplicación, ya que el servidor debe permanecer activo.

### 5. Acceder a la documentación de la API

FastAPI genera automáticamente una documentación interactiva de los endpoints.

Abrir en el navegador:

[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

Desde allí se pueden consultar los endpoints disponibles, visualizar los parámetros que recibe cada uno y realizar pruebas de las solicitudes directamente.

## Ejecución del frontend

Con el backend en funcionamiento, se debe abrir el frontend para utilizar la aplicación.

1. Abrir la carpeta del proyecto en Visual Studio Code.
2. Abrir el archivo `index.html` utilizando la extensión **Live Server**.
3. El navegador abrirá la aplicación en una dirección local, generalmente `http://127.0.0.1:5500`.
4. Mantener activa la terminal donde se está ejecutando FastAPI.

El frontend se comunica con el backend mediante solicitudes HTTP a la API.

**Importante:** si se modifica la dirección o el puerto del servidor, también se deberá verificar la configuración de conexión a la API en JavaScript.

## Datos de prueba

### Inicio de sesión

Para probar el acceso al sistema:

- **Correo electrónico:** cualquier correo no vacío.
- **Contraseña:** cualquier contraseña no vacía.

El inicio de sesión está simplificado para esta demostración y no realiza una autenticación real con credenciales previamente registradas.

### Registro de pacientes

También se puede ingresar desde la opción de crear cuenta y completar el formulario con datos de prueba.

Se deben completar los campos obligatorios para realizar el registro.

Una vez creada la cuenta, se puede utilizar el correo ingresado para acceder al sistema.

### Prueba de gestión de turnos

Una vez dentro de la aplicación, se puede realizar el siguiente recorrido:

1. Iniciar sesión.
2. Ingresar a la sección de solicitud de turnos.
3. Seleccionar una especialidad médica.
4. Elegir un profesional.
5. Seleccionar una fecha disponible.
6. Elegir un horario.
7. Confirmar la solicitud.
8. Consultar el turno desde la sección "Mis turnos".
9. Probar las opciones de cancelación o reprogramación.

## Almacenamiento de datos

El backend utiliza un archivo local llamado `datos.json` para conservar los datos de los pacientes y los turnos.

- Si el archivo existe, el sistema carga la información almacenada.
- Si no existe, se inicializan los datos de prueba.
- Cuando se realizan operaciones que modifican la información, los cambios se guardan en el archivo.

Esto permite conservar los datos entre ejecuciones del servidor, sin necesidad de configurar una base de datos externa.

## Estructura general del proyecto

```text
AXIS/
│
├── main.py
├── datos.json
│
├── index.html
├── registro.html
├── panel.html
├── perfil.html
├── mis-turnos.html
├── nuevo-turno.html
│
├── css/
│   └── styles.css
│
├── js/
│   └── app.js
│
└── img/
    └── logo.png
```

*La estructura es orientativa y puede variar según la organización final de los archivos.*

## Logo

El logo de AXIS se encuentra en `img/logo.png`.

Para reemplazarlo, colocar la nueva imagen en esa misma ubicación, conservando el nombre `logo.png`.

## Consideraciones

- AXIS es un proyecto académico con un backend simulado.
- Los datos se almacenan localmente en un archivo JSON.
- No se utiliza una base de datos SQL.
- La autenticación está simplificada y no implementa mecanismos de seguridad reales.
- No se deben utilizar datos personales reales ni contraseñas reales para las pruebas.
- El servidor se ejecuta en un entorno local y está destinado a demostración y aprendizaje.

---

**AXIS – Sistema de turnos médicos**

Proyecto académico – Analista de Sistemas.
