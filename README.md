
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
- Inicio de sesión con credenciales registradas.
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

Luego, abrir una terminal y ubicarse en la carpeta principal del proyecto, donde se encuentra el archivo `main.py`.

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
2. Ingresar a la carpeta `static`.
3. Abrir el archivo `index.html` utilizando la extensión **Live Server**.
4. El navegador abrirá la aplicación en una dirección local, generalmente `http://127.0.0.1:5500`.
5. Mantener activa la terminal donde se está ejecutando FastAPI.

El frontend se comunica con el backend mediante solicitudes HTTP a la API.

**Importante:** si se modifica la dirección o el puerto del servidor, también se deberá verificar la configuración de conexión a la API en JavaScript.

## Datos de prueba

### Registro de pacientes

Para utilizar el sistema por primera vez, es necesario crear una cuenta desde la opción **Registrarse** de la pantalla de inicio.

Se debe completar el formulario con los datos solicitados. Una vez realizado el registro, el paciente podrá iniciar sesión utilizando el correo electrónico y la contraseña que ingresó al crear su cuenta.

### Inicio de sesión

Para ingresar al sistema:

- **Correo electrónico:** utilizar el correo registrado previamente.
- **Contraseña:** utilizar la contraseña ingresada durante el registro.

El sistema verifica que el paciente se encuentre registrado antes de permitir el acceso.

### Prueba de gestión de turnos

Una vez registrado e iniciada la sesión, se puede realizar el siguiente recorrido:

1. Crear una cuenta desde la opción de registro.
2. Iniciar sesión con las credenciales registradas.
3. Ingresar a la sección de solicitud de turnos.
4. Seleccionar una especialidad médica.
5. Elegir un profesional.
6. Seleccionar una fecha disponible.
7. Elegir un horario.
8. Confirmar la solicitud.
9. Consultar el turno desde la sección "Mis turnos".
10. Probar las opciones de cancelación o reprogramación.

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
├── requirements.txt
├── README.md
│
└── static/
    ├── index.html
    ├── registro.html
    ├── panel.html
    ├── perfil.html
    ├── mis-turnos.html
    ├── nuevo-turno.html
    ├── confirmar.html
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

## Logo

El logo de AXIS se encuentra en `static/img/logo.png`.

Para reemplazarlo, colocar la nueva imagen en esa misma ubicación, conservando el nombre `logo.png`.

## Consideraciones

- AXIS es un proyecto académico con un backend simulado.
- Los datos se almacenan localmente en un archivo JSON.
- No se utiliza una base de datos SQL.
- El inicio de sesión requiere que el paciente se encuentre previamente registrado.
- La autenticación está simplificada y no implementa todos los mecanismos de seguridad necesarios para un entorno de producción.
- No se deben utilizar datos personales reales ni contraseñas reales para las pruebas.
- El servidor se ejecuta en un entorno local y está destinado a demostración y aprendizaje.

---

**AXIS – Sistema de turnos médicos**

Proyecto académico – Analista de Sistemas.
