#!/bin/sh
set -e

# Ensure storage directory structure exists (useful if mounting empty volume)
STORAGE="${STORAGE_DIR:-/app/storage}"
mkdir -p "${STORAGE}/data" \
         "${STORAGE}/media/images" \
         "${STORAGE}/media/thumbnails" \
         "${STORAGE}/media/books" \
         "${STORAGE}/media/videos" \
         "${STORAGE}/media/repository"

exec "$@"
