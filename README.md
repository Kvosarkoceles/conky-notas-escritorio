# Conky + Notas del escritorio

## Instalación

```bash
chmod +x install.sh
./install.sh
```

El instalador funciona con los escritorios Debian que respetan el estándar
de autoinicio de freedesktop, incluidos GNOME, KDE Plasma, XFCE, Cinnamon,
MATE y LXQt. Comprueba `conky` y Tkinter antes de instalar; si falta alguno,
los instala mediante `apt` usando `sudo` cuando es necesario.

Conky y Tkinter necesitan una sesión gráfica X11 o XWayland. En una sesión
Wayland pura, activa XWayland para que ambas aplicaciones puedan mostrar sus
ventanas.

## Guardar notas

En el editor ahora hay un botón grande:

**💾 GUARDAR CAMBIOS**

También funciona:

```text
Ctrl + S
```

Las notas se guardan en:

`~/.desktop-notes/notes.json`

## Uso

- `+` crea una nota.
- Doble clic sobre una nota la abre para editar.
- `💾 GUARDAR CAMBIOS` guarda título y contenido.
- `Ctrl + S` también guarda.
- `🗑 Eliminar` elimina la nota.
- `Cancelar` cierra sin guardar.
- Puedes arrastrar el panel desde su cabecera.
