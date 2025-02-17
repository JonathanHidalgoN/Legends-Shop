#!/bin/bash

ENV=${1:-local}
BUILD=${2:-f}

if [[ "$ENV" != "local" && "$ENV" != "docker" ]]; then
  echo "Usage: $0 [local|docker]"
  exit 1
fi

SRC=".env.$ENV"
DEST=".env"

echo "Copying ${SRC} to ${DEST}..."
cp "$SRC" "$DEST" || {
  echo "Error copying file"
  exit 1
}

if [ "$ENV" = "local" ]; then
  echo "Running docker db and frontend service (has to be named db and fronted on Dockerfile)..."
  docker compose up db frontend -d || {
    echo "Error running docker db"
    exit 1
  }
elif [ "$ENV" = "docker" ]; then
  echo "Running docker compose up..."
  docker compose up -d || {
    echo "Error running docker compose up"
    exit 1
  }
else
  echo "Unknown environment: $ENV"
  exit 1
fi
