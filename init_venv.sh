#!/bin/bash

# Detectar el sistema operativo y activar el entorno virtual correctamente
if [[ "$(uname -s)" == "Linux" || "$(uname -s)" == "Darwin" ]]; then
    # Sistemas tipo Unix (Linux/macOS)
    source venv/bin/activate
elif [[ "$(uname -s)" == *"NT"* || "$(uname -s)" == *"MINGW"* || "$(uname -s)" == *"CYGWIN"* ]]; then
    # Sistemas Windows (Git Bash, Cygwin, MSYS2)
    source venv/Scripts/activate
else
    echo "No se pudo detectar el sistema operativo o no es compatible."
    exit 1
fi
pip install -r requirements.txt