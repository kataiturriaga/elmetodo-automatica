# Cómo compilar y ver la app en local (elmetodo_app)

Guía para arrancar la app Flutter (**`elmetodo_app`**, la automática) en el **simulador de
iPhone** del Mac y verla en vivo. Probado el 25-jun-2026.

> **Resumen rápido:** solo iOS (simulador de iPhone); Android no hace falta. La app arranca
> sin configuración especial. El único muro fue **CocoaPods** (el gestor de librerías de
> iOS) — una vez arreglado (abajo), no hay que repetirlo.

---

## 1. Setup de una sola vez (los arreglos que costaron)

Esto solo se hace **una vez**. Abre la Terminal y ejecuta:

```bash
# (a) CocoaPods necesita el idioma en UTF-8 (si no, falla)
export LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8

# (b) Reinstalar CocoaPods (arregla una librería interna rota, 'ffi')
brew reinstall cocoapods

# (c) Re-resolver las librerías de iOS de la app
cd ~/repos/elmetodo_app/ios
pod update
```

---

## 2. Cada vez que quieras ver la app

```bash
cd ~/repos/elmetodo_app
export LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8

# (solo si cambiaron las dependencias de Flutter)
flutter pub get

# arrancar la app en el simulador (entorno de desarrollo, no producción)
flutter run --dart-define=APP_ENV=development
```

- Si no hay simulador abierto, se abre solo. (O ábrelo a mano: `open -a Simulator`.)
- **La primera compilación tarda varios minutos**; las siguientes son rápidas.
- Cuando aparezca `Flutter run key commands`, la app ya está corriendo. 🎉

---

## 3. Ver tus cambios al instante (hot reload 🔥)

Con `flutter run` corriendo, en esa misma terminal:

| Tecla | Qué hace |
|---|---|
| **`r`** | **Recarga en caliente** — aplica tus cambios al instante (~1 seg) |
| **`R`** | **Reinicio en caliente** — reinicia la app (vuelve a la pantalla inicial) |
| **`q`** | Salir |

Flujo para iterar pantallas: **editas el código → pulsas `r` → lo ves cambiar en el
simulador**, sin recompilar de cero.

Captura de pantalla del simulador (para guardar o compartir):
```bash
xcrun simctl io booted screenshot foto.png
```

---

## 4. Si algo falla (errores que ya vimos)

| Error | Solución |
|---|---|
| `CocoaPods requires your terminal to be using UTF-8 encoding` | Te falta `export LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8` antes de `pod`/`flutter` |
| `Ignoring ffi... extensions are not built` / `specs repository is too out-of-date` | `brew reinstall cocoapods` |
| `could not find compatible versions for pod ...` | `cd ~/repos/elmetodo_app/ios && pod update` |
| `Android toolchain ... Unable to locate Android SDK` (en `flutter doctor`) | Ignóralo — no usamos Android |

---

## Notas

- `pod update` modifica `ios/Podfile.lock` (cambio **local**). No hace falta commitearlo
  salvo que quieras actualizar versiones a propósito.
- La app, por defecto, apunta a **producción**. Con `--dart-define=APP_ENV=development`
  apunta al backend de **desarrollo** (recomendado para probar).
- Esta misma info, resumida, está en la memoria de Claude (`reference_run_app_local`).
