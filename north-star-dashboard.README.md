# North Star Dashboard — datos reales automatizados

El dashboard (`north-star-dashboard.html`) ya **no tiene números a mano**: los saca solos
de **GA4** (eventos de la app) y de la **API de producción** (suscripciones/pagos).

## Cómo se actualiza

**Solo, cada día a las 08:00** mientras tu Mac esté encendido (si estaba apagado/dormido,
se pone al día al encenderlo). Lo hace una tarea de macOS (`launchd`).

**A mano, cuando quieras:** doble clic en **`Actualizar dashboard.command`**.
Recalcula todo y abre el dashboard en el navegador (tarda ~15 segundos).

## Qué número es cada cosa

| Sección | De dónde sale |
|---|---|
| North Star (≥2 sesiones **reales**/7 días) + tendencia + gráfico | GA4 · `training_session_complete` deduplicado |
| Entrenos: rejilla semana × día (+ popover con nombre/email al pasar el ratón) | GA4 · sesiones reales, usuarios distintos por día |
| Últimas sesiones (usuario, programa, sesión, minutos, ejercicios) | GA4 + nombres de programa y de usuario (nombre/email) vía API |
| Embudo (inició → quiz → registro → pago) | GA4 · eventos `onboarding_*` desde 11-may-2026 |
| Pasos del onboarding (dónde se cae la gente) | GA4 · `onboarding_step_viewed` |
| Palanca 1 · Activación | GA4 · 1er entreno ≤3 días del registro |
| Palanca 2 · Enganche (ranking) | GA4 · eventos de ranking sobre activos 7d |
| Palanca 3 · Compromiso (trial→paid) | API · `/dashboard/subscriptions/overview` |

## Cosas a saber

- 🐞 **Bug de la app a reportar a ingeniería:** el evento `training_session_complete` se
  dispara muchísimas veces por sesión real (10–600×). El dashboard lo **deduplica** (una
  sesión = usuario + día + programa + nombre de sesión) y solo cuenta como **real** las de
  ≥5 min (o ≥1 ejercicio si falta la duración), para descartar el "curioseo" (abrir y darle
  a terminar). Por eso la North Star es más baja que el conteo de eventos en bruto.
- **Cuenta por cuenta de usuario** (`user_id` de GA4, presente en ~100% de los entrenos);
  si faltara, cae a `user_pseudo_id` (dispositivo) y se marca como «anónimo».
- 🔒 **PRIVACIDAD:** este HTML ahora contiene **nombres y emails reales** de usuarios (PII).
  No lo subas a git ni lo compartas públicamente. Recomendado: añadir
  `north-star-dashboard.html` al `.gitignore` (el dashboard se regenera solo).
  El nombre/email se cruza con la API por `user_id` (endpoint `subscriptions/users`).
- La semana en curso aparece baja/0 hasta que GA4 ingiere los datos del día (suele tardar
  unas horas).
- Si una consulta falla, **el dashboard NO se rompe**: deja la última versión buena y
  apunta el error en el log.
- Si los números salen raros o a 0, casi siempre es que **caducó la key de GA4**
  (ver abajo cómo reemplazarla).

## Credenciales (fuera del repo, nunca se suben a git)

`~/.config/elmetodo/dashboard.json` — usuario/clave de la API y ruta de la key de GA4.
`~/.config/elmetodo/automatica-v2.json` — key de servicio de BigQuery (GA4).

> ⚠️ La key tiene que estar **fuera de `~/Downloads`**: macOS bloquea esa carpeta a las
> tareas programadas. Por eso está copiada en `~/.config/elmetodo/`.

Si Google da una key nueva: reemplaza `~/.config/elmetodo/automatica-v2.json` por la nueva.

## Mantenimiento (comandos)

```bash
# ver el log de la última ejecución
cat ~/Library/Logs/elmetodo-northstar.log

# refrescar ahora mismo desde terminal
python3 ~/repos/elmetodo_auto/generar_north_star.py

# pausar / reactivar la actualización automática
launchctl bootout   gui/$(id -u)/com.elmetodo.northstar
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.elmetodo.northstar.plist
```

Para cambiar la hora: edita `Hour`/`Minute` en
`~/Library/LaunchAgents/com.elmetodo.northstar.plist` y recarga (los dos comandos de arriba).

## Metas y umbrales

Se cambian en la cabecera de `generar_north_star.py` (`META_TRIMESTRE`, `META_ACTIVACION`,
`META_ENGANCHE`, `META_COMPROMISO`, `COHORTE`).
