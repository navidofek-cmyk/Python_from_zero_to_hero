#!/usr/bin/env bash
set -e

PROJEKT="$(cd "$(dirname "$0")" && pwd)"
VENV="$PROJEKT/.venv"

cd "$PROJEKT"

if [ ! -d "$VENV" ]; then
    echo "[*] Vytvářím virtuální prostředí..."
    python3 -m venv "$VENV"
fi

source "$VENV/bin/activate"

if ! python -c "import mkdocs_material" 2>/dev/null; then
    echo "[*] Instaluji mkdocs-material..."
    pip install --quiet mkdocs-material
fi

echo "[*] Spouštím kurz na http://127.0.0.1:9999"
mkdocs serve
