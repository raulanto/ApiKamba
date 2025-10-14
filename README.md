# 🚀 Kanban API - Guía Rápida

API REST para gestión de tableros Kanban con autenticación JWT.

## 📋 Requisitos

- Python 3.11+
- pip

## 🔧 Instalación y Ejecución

### 1. Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/kanban-api.git
cd kanban-api
```

### 2. Crear entorno virtual

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/Mac
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar .env y agregar tu SECRET_KEY
# Puedes generar uno con:
python -c "import secrets; print(secrets.token_hex(32))"
```

### 5. Ejecutar migraciones

```bash
alembic upgrade head
```

### 6. Iniciar servidor

```bash
uvicorn app.main:app --reload
```

La API estará disponible en: **http://localhost:8000**
