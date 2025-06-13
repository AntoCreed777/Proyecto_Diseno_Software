#!/bin/bash

echo "Eliminando base de datos anterior..."
rm -f db.sqlite3

echo "Aplicando migraciones..."
python3 manage.py migrate

echo "Inicializando grupos de usuarios..."
python3 manage.py init_grupos

echo "Base de datos reiniciada correctamente."