# Proyecto: Diseño de Software

Este repositorio contiene el código fuente y las dependencias necesarias para el desarrollo del proyecto de Diseño de Software basado en Django.

## Integrantes del grupo
- [Antonio Jesus Benavides Puentes](https://github.com/AntoCreed777) **(2023455954)**
- [Ariel Eduardo Cisternas Bustos](https://github.com/Arcisternas) **(2023456152)**
- [Luis Ignacio Martinez Neira](https://github.com/Nachopex) **(2023427985)**
- [Esteban Andres Navarrete Mella](https://github.com/Bandido209) **()**
- [Joaquin Hernan Sandoval Reyes](https://github.com/joaqsandoval04) **(2023434493)**


## Tecnologías utilizadas en el proyecto

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

## Requisitos previos

- Python 3 instalado
- Git Bash, WSL, macOS Terminal, o cualquier terminal compatible con bash

## Instalación y configuración

1. **Clona este repositorio:**
   ```bash
   git clone https://github.com/AntoCreed777/Proyecto_Diseno_Software
   cd Proyecto_Diseno_Software
   ```

2. **Crea un entorno virtual llamado `venv`:**
   ```bash
   python3 -m venv venv
   ```

3. **Inicializa el entorno virtual e instala las dependencias:**
   ```bash
   source init_venv.sh
   ```
   El script detecta automáticamente tu sistema operativo y activa el entorno virtual correctamente en Windows, Linux o macOS.

> [!NOTE]
> - Si el script no se ejecuta por permisos (en Linux/macOS), asígnale permisos de ejecución:
>   ```bash
>   chmod +x init_venv.sh
>   ```
> - En Windows, si tienes problemas, puedes activar el entorno manualmente y luego instalar las dependencias:
>   ```powershell
>   .\venv\Scripts\Activate.ps1
>   pip install -r requirements.txt
>   ```

> [!WARNING]
> Si en linux no se ejecuta el script, intente con el siguiente comando antes de volver a intentarlo
> ``` bash
> dos2unix init_venv.sh
> ```

## Comandos previos

Antes de iniciar el servidor, es necesario aplicar las migraciones de la base de datos para asegurar que la estructura esté actualizada. 

Ejecuta el siguiente comando:

```bash
python3 manage.py migrate
```
Esto preparará la base de datos para el correcto funcionamiento del proyecto.

## Inicio de los grupos de Usuarios

Ejecuta el siguiente comando:

```bash
python3 manage.py init_grupos
```

> [!NOTE]
> Para poblar la base de datos con datos de prueba puedes ejecutar el siguiente comando:
> 
> ```bash
> python3 manage.py poblar_bd
> ```
> Esto creará automáticamente un cliente, un despachador, un conductor y un admin de ejemplo en la base de datos.

## Ejecución del proyecto

Para iniciar el servidor de desarrollo de Django, ejecuta:

```bash
python3 manage.py runserver
```

Esto levantará el servidor en `http://127.0.0.1:8000/` por defecto.

> [!NOTE]
> Si el puerto 8000 ya está en uso o tienes algún conflicto, puedes cambiar el puerto por cualquier otro disponible agregándolo al comando. Por ejemplo, para usar el puerto 8080:
> ```bash
> python3 manage.py runserver 8080
> ```
> También puedes especificar la IP y el puerto:
> ```bash
> python3 manage.py runserver 0.0.0.0:8080
> ```
