# Decisión: cómo se siembran y mantienen los datos del Score de Entreno

**Fecha:** 25-jun-2026 · **Contexto:** PR #1 del Score de Entrenamiento (modelo de datos, ya fusionado a `main`).
**Quién decidió:** Kata (PM) + Carles (review de código).

> Registro en cristiano de las decisiones **técnicas** que tomamos. El "cómo aprende" / conceptos
> está en [`aprendizajes/`](../aprendizajes/sesion-2026-06-24-aprendizajes-implementacion.md). La versión
> para devs vive en el repo de la API: `docs/plans/training-score.md`.

---

## El contexto

Nuestra migración es la **primera del repo de la API que siembra datos** (mete filas, no solo crea
tablas). Como no había un patrón previo, **inventamos una convención** — y por eso conviene tenerla
escrita. Carles la revisó y pidió un par de mejoras; estas son las decisiones finales.

## Las decisiones (y por qué)

**1. Los datos van sembrados en la migración (no un panel/admin en runtime).**
Porque son **datos de dev: pocos, técnicos y de cambio raro** (estándares de fuerza, mapeos). Montar
un sistema recargable en caliente sería sobreingeniería hasta que alguien no-técnico lo necesite.

**2. Los 84 números de estándares viven en un archivo de código aparte y revisable**
(`app/data/strength_standards_v1.py`), no enterrados dentro de la migración.
Porque son **v1 a recalibrar** (el mayor riesgo abierto del feature) → tienen que estar **a la vista**
para revisarlos y cambiarlos fácil. Ver [estandares-fuerza.md](../%20Funcionalidades/puntuaciones-entreno/estandares-fuerza.md).

**3. La siembra es "idempotente" (upsert).**
*Idempotente* = se puede ejecutar muchas veces y da el mismo resultado, sin duplicar ni romper.
*Upsert* = "si existe, actualiza; si no, crea". Así el seed es **re-ejecutable** sin miedo.

**4. Recalibrar = versión nueva, NUNCA editar la migración ya enviada.**
Las migraciones son **historial inmutable**. Para cambiar los números (v2): archivo nuevo
`strength_standards_v2.py` + una **migración de datos nueva** que hace upsert. La vieja no se toca.

**5. Los mapeos con dependencia (ejercicio/objetivo) se siembran "a la defensiva" + avisan.**
Esos mapeos apuntan a tablas de referencia (`exercises`, `objectives`) que **existen en producción pero
no en una base de datos vacía** (tests/CI). Decisión: sembrar **solo lo que exista**, y soltar un
**WARNING** con lo que falte. Así **no rompe** en vacío y **no falla en silencio** (si no, el motor de
score se quedaría sin datos sin que nadie se enterara).

## De dónde salió cada mejora

- Puntos 1–2 (números fuera de la migración) y 3–4 (upsert + versionado) → **feedback de Carles** en el PR.
- Punto 5 (defensivo + warning) → lo cazamos **probando en local de verdad** (la prueba en vivo pilló
  un fallo que la validación "en seco" no veía).

## Dónde vive en el código (repo `elmetodo_api`)

- Migración: `migrations/versions/create_score_tables.py`
- Números v1: `app/data/strength_standards_v1.py`
- Doc para devs: `docs/plans/training-score.md`
