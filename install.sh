#!/usr/bin/env bash
set -euo pipefail

BASE="$HOME/.desktop-notes"
SCRIPT_DIR="$(cd -- "$(dirname -- "$0")" && pwd)"
mkdir -p "$BASE"

echo "== Instalador de Conky + Notas =="

missing_packages=()
command -v conky >/dev/null 2>&1 || missing_packages+=(conky-all)
python3 -c 'import tkinter' >/dev/null 2>&1 || missing_packages+=(python3-tk)

if ((${#missing_packages[@]})); then
  if ! command -v apt-get >/dev/null 2>&1; then
    echo "Faltan dependencias (${missing_packages[*]}) y no se encontró apt-get." >&2
    exit 1
  fi

  if [[ $EUID -eq 0 ]]; then
    apt-get update
    apt-get install -y "${missing_packages[@]}"
  elif command -v sudo >/dev/null 2>&1; then
    sudo apt-get update
    sudo apt-get install -y "${missing_packages[@]}"
  else
    echo "Faltan dependencias (${missing_packages[*]}), pero sudo no está disponible." >&2
    echo "Instálalas como root y vuelve a ejecutar este instalador." >&2
    exit 1
  fi
fi

# Copiar aplicación
cp "$SCRIPT_DIR/desktop_notes.py" "$BASE/desktop_notes.py"
chmod +x "$BASE/desktop_notes.py"

cp "$SCRIPT_DIR/conky-right.conf" "$BASE/conky-right.conf"

# Lanzador de notas
cat > "$BASE/start-notes.sh" <<EOF
#!/usr/bin/env bash
exec python3 "$BASE/desktop_notes.py"
EOF
chmod +x "$BASE/start-notes.sh"

# Lanzador de Conky
cat > "$BASE/start-conky.sh" <<EOF
#!/usr/bin/env bash
pkill -u "$(id -u)" -x conky 2>/dev/null || true
sleep 1
exec conky -c "$BASE/conky-right.conf"
EOF
chmod +x "$BASE/start-conky.sh"

AUTOSTART="$HOME/.config/autostart"
mkdir -p "$AUTOSTART"

cat > "$AUTOSTART/desktop-notes.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=Notas del escritorio
Comment=Panel de notas con doble clic para editar
Exec="$BASE/start-notes.sh"
Terminal=false
TryExec=$BASE/start-notes.sh
EOF

cat > "$AUTOSTART/conky-right.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=Conky derecha
Comment=Monitor Conky en el lado derecho
Exec="$BASE/start-conky.sh"
Terminal=false
TryExec=$BASE/start-conky.sh
EOF

# Acceso directo en el menú de aplicaciones
APPS_DIR="$HOME/.local/share/applications"
mkdir -p "$APPS_DIR"

cat > "$APPS_DIR/desktop-notes.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=Notas del escritorio
Comment=Panel de notas con doble clic para editar
Exec="$BASE/start-notes.sh"
Terminal=false
Icon=accessories-text-editor
Categories=Utility;
EOF

chmod +x "$APPS_DIR/desktop-notes.desktop"
if command -v update-desktop-database >/dev/null 2>&1; then
  update-desktop-database "$APPS_DIR" 2>/dev/null || true
fi

# Crear archivo de notas inicial si no existe
if [ ! -f "$BASE/notes.json" ]; then
  cat > "$BASE/notes.json" <<'JSON'
[
  {
    "title": "Bienvenido",
    "body": "Doble clic sobre una nota para editarla.\nUsa + Nueva nota para crear otra.",
    "x": 0,
    "y": 0
  }
]
JSON
fi

echo
echo "Instalación terminada."
echo "Notas:      $BASE"
echo "Conky:      $BASE/conky-right.conf"
echo
echo "Iniciando ambos..."
pkill -u "$(id -u)" -f -- "$BASE/desktop_notes.py" 2>/dev/null || true
nohup "$BASE/start-conky.sh" >/tmp/conky-right.log 2>&1 &
nohup "$BASE/start-notes.sh" >/tmp/desktop-notes.log 2>&1 &
echo "Listo. Cierra sesión/reinicia para probar el autoinicio."
