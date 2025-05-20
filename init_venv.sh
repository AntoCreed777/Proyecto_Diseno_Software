#!/bin/bash

echo "Sistema operativo detectado: $(uname -s)"
if [[ "$(uname -s)" == "Linux" || "$(uname -s)" == "Darwin" ]]; then
    echo "Activando entorno virtual en Linux/macOS..."
    source venv/bin/activate || { echo "Fallo al activar el entorno virtual."; exit 1; }
elif [[ "$(uname -s)" == *"NT"* || "$(uname -s)" == *"MINGW"* || "$(uname -s)" == *"CYGWIN"* ]]; then
    echo "Activando entorno virtual en Windows..."
    . venv/Scripts/activate || { echo "Fallo al activar el entorno virtual."; exit 1; }
else
    echo "Sistema operativo no compatible."
    exit 1
fi

pip install -r requirements.txt || { echo "Fallo al instalar dependencias."; exit 1; }

echo "Entorno virtual activado y dependencias instaladas."