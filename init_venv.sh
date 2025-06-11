#!/bin/bash

echo "Sistema operativo detectado: $(uname -s)"
OS_NAME="$(uname -s)"

if [[ "$OS_NAME" == "Linux" || "$OS_NAME" == "Darwin" ]]; then
    echo "Activando entorno virtual en Linux/macOS..."
    source venv/bin/activate || { echo "Fallo al activar el entorno virtual."; exit 1; }
elif [[ "$OS_NAME" == *"NT"* || "$OS_NAME" == *"MINGW"* || "$OS_NAME" == *"CYGWIN"* ]]; then
    echo "Activando entorno virtual en Windows..."
    source venv/Scripts/activate || { echo "Fallo al activar el entorno virtual."; exit 1; }
else
    echo "Sistema operativo no compatible."
    exit 1
fi

echo "Instalando dependencias necesarias..."
if ! pip install -r requirements.txt; then
    echo "Fallo al instalar dependencias."
    exit 1
fi

echo "Entorno virtual activado y dependencias instaladas."
