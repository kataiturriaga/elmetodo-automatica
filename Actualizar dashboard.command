#!/bin/zsh
# Doble clic en este archivo para refrescar el dashboard a mano y abrirlo.
cd "$(dirname "$0")"
/usr/bin/python3 generar_north_star.py
open north-star-dashboard.html
