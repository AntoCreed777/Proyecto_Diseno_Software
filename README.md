# 🚛 Proyecto: Diseño de Software

<div align="center">

![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)

Sistema de gestión de transporte desarrollado con Django y SQLite

</div>

## 👥 Integrantes del Equipo

| Nombre | GitHub | Matrícula |
|--------|--------|-----------|
| Antonio Jesus Benavides Puentes | [@AntoCreed777](https://github.com/AntoCreed777) | 2023455954 |
| Ariel Eduardo Cisternas Bustos | [@Arcisternas](https://github.com/Arcisternas) | 2023456152 |
| Luis Ignacio Martinez Neira | [@Nachopex](https://github.com/Nachopex) | 2023427985 |
| Esteban Andres Navarrete Mella | [@Bandido209](https://github.com/Bandido209) | 2023455547 |
| Joaquin Hernan Sandoval Reyes | [@joaqsandoval04](https://github.com/joaqsandoval04) | 2023434493 |

## 📋 Tabla de Contenidos

- [🚀 Inicio Rápido](#-inicio-rápido)
- [📋 Requisitos Previos](#-requisitos-previos)
- [⚙️ Instalación](#️-instalación)
- [🔧 Configuración](#-configuración)
- [🗄️ Base de Datos](#️-base-de-datos)
- [▶️ Ejecución](#️-ejecución)
- [🛠️ Solución de Problemas](#️-solución-de-problemas)
- [🤝 Contribuir](#-contribuir)

## 🚀 Inicio Rápido

```bash
# Clonar el repositorio
git clone https://github.com/AntoCreed777/Proyecto_Diseno_Software
cd Proyecto_Diseno_Software

# Configurar entorno virtual
source init_venv.sh

# Preparar base de datos
python3 manage.py migrate
python3 manage.py init_grupos
python3 manage.py poblar_bd

# Ejecutar servidor
python3 manage.py runserver
```

## 🛠️ Tecnologías Utilizadas

<div align="center">

### Herramientas de desarrollo y control de versiones
<a href="https://skillicons.dev">
  <img src="https://skillicons.dev/icons?i=git,github,vscode&perline=5" />
</a>

### Base de datos y lenguaje de programación
<a href="https://skillicons.dev">
  <img src="https://skillicons.dev/icons?i=python,sqlite&perline=5" />
</a>

### Framework utilizado
<a href="https://skillicons.dev">
  <img src="https://skillicons.dev/icons?i=django&perline=5" />
</a>

</div>

## 📋 Requisitos Previos

- **Python 3.8+**
- **Git**
- Terminal compatible con bash (Git Bash, WSL, Terminal de macOS/Linux)

## ⚙️ Instalación

### 1️⃣ Clonar el Repositorio

```bash
git clone https://github.com/AntoCreed777/Proyecto_Diseno_Software
cd Proyecto_Diseno_Software
```

### 2️⃣ Configurar Entorno Virtual

```bash
# Crear entorno virtual
python3 -m venv venv

# Activar e instalar dependencias automáticamente
source init_venv.sh
```

<details>
<summary>🔧 Activación manual del entorno</summary>

**Linux/macOS:**
```bash
source venv/bin/activate
pip install -r requirements.txt
```

**Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**Windows (CMD):**
```cmd
venv\Scripts\activate.bat
pip install -r requirements.txt
```

</details>

> [!WARNING]
> Si en Linux no se ejecuta el script, intente con el siguiente comando antes de volver a intentarlo:
> ```bash
> dos2unix init_venv.sh
> ```

## 🔧 Configuración

El script `init_venv.sh` detecta automáticamente tu sistema operativo y activa el entorno virtual correctamente en Windows, Linux o macOS.

### Configuraciones importantes

En el archivo `Proyecto_Diseño_Software/settings.py` puedes encontrar configuraciones como:

```python
# Configuración regional
TIME_ZONE = 'America/Santiago'
LANGUAGE_CODE = 'es-cl'

# Para desarrollo local
DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']
```

> ⚠️ **Importante:** Para producción, asegúrate de cambiar `DEBUG = False` y configurar `ALLOWED_HOSTS` apropiadamente.

## 🗄️ Base de Datos

Este proyecto utiliza **SQLite** como base de datos por defecto, lo que simplifica la configuración y desarrollo.

### Preparar la Base de Datos

```bash
# Aplicar migraciones de la base de datos
python3 manage.py migrate
```

### Inicializar Grupos de Usuarios

```bash
# Crear grupos de usuarios del sistema
python3 manage.py init_grupos
```

### Poblar con Datos de Prueba

```bash
# Crear datos de ejemplo para testing
python3 manage.py poblar_bd
```

> 📝 **Nota:** Este comando creará automáticamente un cliente, un despachador, un conductor y un admin de ejemplo en la base de datos.

### Comandos Útiles

```bash
# Crear superusuario para el panel de administración
python3 manage.py createsuperuser

# Reiniciar la base de datos (si existe el script)
./reiniciar_bd.sh
```

## ▶️ Ejecución

```bash
# Iniciar servidor de desarrollo
python3 manage.py runserver
```

El servidor estará disponible en: **http://127.0.0.1:8000/**

### Opciones Adicionales

```bash
# Usar puerto personalizado
python3 manage.py runserver 8080

# Permitir acceso desde cualquier IP
python3 manage.py runserver 0.0.0.0:8000
```

## 🛠️ Solución de Problemas

<details>
<summary>🐧 Script no ejecuta en Linux</summary>

### Problema
El script `init_venv.sh` no se ejecuta por permisos o formato de líneas.

### Solución
```bash
# Corregir formato de líneas
dos2unix init_venv.sh

# Dar permisos de ejecución
chmod +x init_venv.sh

# Ejecutar
source init_venv.sh
```

</details>

<details>
<summary>🐍 Error con el entorno virtual en Windows</summary>

### Problema
El entorno virtual no se activa correctamente en Windows.

### Solución
```powershell
# Activar manualmente en PowerShell
.\venv\Scripts\Activate.ps1

# O en CMD
venv\Scripts\activate.bat

# Luego instalar dependencias
pip install -r requirements.txt
```

</details>

<details>
<summary>🔌 Error de migraciones</summary>

### Problema
Django no puede aplicar las migraciones correctamente.

### Verificaciones
1. **Verificar que el entorno virtual esté activo:**
   ```bash
   which python3  # Debe mostrar la ruta del venv
   ```

2. **Crear migraciones si es necesario:**
   ```bash
   python3 manage.py makemigrations
   python3 manage.py migrate
   ```

3. **Reiniciar la base de datos (desarrollo):**
   ```bash
   rm db.sqlite3
   python3 manage.py migrate
   python3 manage.py init_grupos
   python3 manage.py poblar_bd
   ```

</details>

<details>
<summary>🚫 Puerto ya en uso</summary>

### Problema
El puerto 8000 ya está siendo utilizado por otro proceso.

### Solución
```bash
# Usar un puerto diferente
python3 manage.py runserver 8080

# O encontrar y terminar el proceso que usa el puerto
# Linux/macOS
lsof -ti:8000 | xargs kill -9

# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

</details>

---

<div align="center">

**Desarrollado con ❤️ por el equipo de Diseño de Software**

</div>
