#!/bin/bash

case "$1" in
    up)
        echo "Iniciando OpenProject..."
        docker compose up -d
        ;;
    down)
        echo "Parando OpenProject..."
        docker compose down
        ;;
    logs)
        docker compose logs -f
        ;;
    *)
        echo "Uso: ./start.sh {up|down|logs}"
        exit 1
esac
