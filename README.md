# BlackGate

**BlackGate** es un sistema web para **control de acceso en condominios**. Permite a la administración registrar Condominios → Edificios → Apartamentos y a los **residentes** crear **invitaciones de visita** que generan un **código QR** (o código alternativo) para validación rápida en el portón.

> **Desarrollado por:** *BlackSoulDev*  
> **Eslogan:** *Acceso seguro, sin complicaciones.*

---

## Tabla de contenidos
- [Objetivos](#objetivos)
- [Características (MVP)](#características-mvp)
- [Arquitectura y Apps](#arquitectura-y-apps)
- [Modelo de datos (ERD)](#modelo-de-datos-erd)
- [Stack Tecnológico](#stack-tecnológico)
- [Convenciones del proyecto](#convenciones-del-proyecto)
- [Pre-requisitos](#pre-requisitos)
- [Guía rápida (dev)](#guía-rápida-dev)
- [Configuración](#configuración)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Roadmap](#roadmap)
- [Seguridad](#seguridad)
- [Contribución](#contribución)
- [Licencia](#licencia)

---

## Objetivos
- Reducir tiempos de espera en accesos de visitantes.
- Evitar llamadas innecesarias a apartamentos.
- Mantener **trazabilidad** de entradas/salidas.
- Separar roles y responsabilidades (administración vs residente vs guardia).

---

## Características (MVP)
- **Catálogo**: Condominios, Edificios, Apartamentos.
- **Portales por rol**:
  - **Administración**: gestiona catálogo y residentes.
  - **Residente**: crea invitaciones de visita.
  - **Guardia**: escanea y valida QR/códigos (web app).
- **Invitaciones** con **QR/UUID** de un solo uso, ventana de tiempo y registro de acceso.
- **Logs** de accesos (permitido/rechazado, motivo, IP, user-agent).

---

## Arquitectura y Apps
- `catalogo` → Dominio físico: `t_condominios`, `t_edificios`, `t_apartamentos`.
- `usuarios` → Identidad, roles y perfiles: `t_residentes`, `t_residentes_apartamentos`, (`t_guardias` opcional).
- `visitas` → Flujo de negocio (invitaciones y acceso): `t_visitas`, `t_codigos_visita`, `t_accesos`.

**Dependencias (arriba → usa a ↓):**
```
visitas
  ↑
usuarios
  ↑
catalogo
```
> Las apps superiores **conocen** a las inferiores, nunca al revés. Esto mantiene el código limpio y escalable.

---

## Modelo de datos (ERD)
- ERD base (MVP) con claves, unicidades e índices:  
  - `t_condominios 1:N t_edificios 1:N t_apartamentos`
  - `t_residentes N:M t_apartamentos` (vía `t_residentes_apartamentos`, con `f_desde`/`f_hasta` y `f_es_principal`)
  - `t_visitas` (FK a residente y apartamento)
  - `t_codigos_visita` (UUID/JWT, un solo uso)
  - `t_accesos` (auditoría)
  - `t_guardias` (opcional)

> Documento de referencia (docs): **BlackGate_Modelo_BD_y_Plan.docx**  
> Imagen guía: **blackgate_erd.png**

---

## Stack Tecnológico
- **Backend:** Django (Python 3.10+)
- **ORM/DB:** Django ORM + PostgreSQL
- **Frontend:** HTML + CSS + JS (plantillas Django).  
  *(Más adelante puede añadirse lector QR con `html5-qrcode` o `@zxing/browser`)*

---

## Convenciones del proyecto
- **Tablas** con prefijo `t_` (p. ej., `t_apartamentos`).
- **Campos** con prefijo `f_` (p. ej., `f_numero`, `f_activo`).
- `unique_together`:
  - `(f_condominio, f_nombre)` en `t_edificios`.
  - `(f_edificio, f_numero)` en `t_apartamentos`.
- **Estados** con `choices`/`CheckConstraint` (p. ej., `t_visitas.f_estado`).
- **Timestamps**: `f_creado_en` (`auto_now_add`), `f_actualizado_en` (`auto_now`).
- **on_delete**:
  - Catálogo jerárquico: `CASCADE`.
  - Enlaces sensibles (historial): `PROTECT`/`SET_NULL` según el caso.

---

## Pre-requisitos
- Python 3.10+  
- PostgreSQL 13+  
- (Opcional) Git, VS Code

---

## Guía rápida (dev)

### 1) Clonar e instalar
```bash
git clone <url_del_repo> blackgate
cd blackgate

python -m venv .venv
# mac/linux:
source .venv/bin/activate
# windows:
# .venv\Scripts\activate

pip install -r requirements.txt  # o: pip install django psycopg2-binary python-dotenv
```

### 2) Configurar base de datos
Crea una BD vacía en PostgreSQL (ajusta nombre/credenciales):
```sql
CREATE DATABASE blackgate_db;
```

Copia `.env.example` a `.env` y ajusta valores (ver sección Configuración).

### 3) Migraciones y usuario admin
```bash
python manage.py migrate
python manage.py createsuperuser
```

### 4) Ejecutar servidor
```bash
python manage.py runserver
```
- Admin: `http://127.0.0.1:8000/admin/`
- Portal (landing/login): `http://127.0.0.1:8000/`

### 5) Crear grupos (roles)
- En `/admin/` → **Groups**: `condominio_admin`, `residente`, `guardia`.  
- Asigna usuarios a grupos según su rol.

---

## Configuración
Usa variables de entorno (recomendado `.env`):

**`.env.example`**
```dotenv
DEBUG=True
SECRET_KEY=pon_aqui_una_clave_segura
ALLOWED_HOSTS=127.0.0.1,localhost

DB_NAME=blackgate_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432

TIME_ZONE=America/Santo_Domingo
LANGUAGE_CODE=es-do
```

**`settings.py` (extracto de DB)**  
*(Cargar con `python-dotenv` o tu método preferido)*:
```python
import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'blackgate_db'),
        'USER': os.getenv('DB_USER', 'postgres'),
        'PASSWORD': os.getenv('DB_PASSWORD', ''),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}

LANGUAGE_CODE = os.getenv('LANGUAGE_CODE', 'es-do')
TIME_ZONE = os.getenv('TIME_ZONE', 'America/Santo_Domingo')
USE_TZ = True
```

---

## Estructura del proyecto
```
blackgate/              # paquete de configuración (settings, urls, wsgi, asgi)
catalogo/               # app: Condominios, Edificios, Apartamentos
  models.py
  views.py
  urls.py
  templates/catalogo/
  static/catalogo/
usuarios/               # app: perfiles y roles
  models.py
  views.py  # home, login/logout, paneles por rol
  urls.py
  templates/usuarios/
  static/usuarios/
visitas/                # app: invitaciones, QR y accesos (se agrega en su fase)
  models.py
  views.py
  urls.py
  templates/visitas/
  static/visitas/
static/                 # estáticos globales (opcional)
media/                  # archivos subidos (si aplica)
manage.py
README.md
docs/
  BlackGate_Modelo_BD_y_Plan.docx
  blackgate_erd.png
```

---

## Roadmap
- **F0 – Diseño (2 días):** Validar ERD, on_delete, índices.  
- **F1 – ORM & Admin (3 días):** `catalogo`, `usuarios`, migraciones, admin y datos semilla.  
- **F2 – Portales & Roles (3–4 días):** Login/Logout, grupos, panel admin y residente, protección de vistas.  
- **F3 – Visitas & QR (5–6 días):** Modelos `visitas/códigos/accesos`, generación/lectura QR en navegador, validador del portón, logs.  
- **F4 – Reportes & Notifs (3–4 días):** Reportes básicos y notificación al residente.  
- **F5 – Hardening & Deploy (3–4 días):** Pruebas, variables de entorno, guía de despliegue.

---

## Seguridad
- JWT de invitación con vida corta y **un solo uso** (se invalida al validar).
- Validación estricta de ventana de tiempo y estado (`pendiente` → `usada/expirada`).
- Minimizar datos visibles al guardia (principio de menor privilegio).
- `DEBUG=False` y `ALLOWED_HOSTS` definidos en entornos productivos.

---

## Contribución
1. Crear rama desde `main`.
2. Commits descriptivos y cambios de **mínimo dif**.
3. PR con descripción: **qué**, **por qué** y **cómo probar**.
4. Respetar convenciones `t_`/`f_` en modelos y migraciones.

---

## Licencia
Pendiente de definir. (Ejemplo: MIT/Proprietary)
