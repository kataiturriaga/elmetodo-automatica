# Auditoría de datos reales — desbloqueo §1 del plan

Resuelve los bloqueantes de la [§1 del plan de implementación](../plans/tareas-implementacion-puntuaciones.md#1-definiciones-previas-bloqueantes) contrastando el [spec de puntuaciones](puntaciones-entreno.md) contra la **estructura y los datos reales** de la plataforma.

**Fuentes usadas** (la BD de prod da timeout por firewall):
- **Estructura/esquema**: código de `elmetodo_api` (modelos SQLAlchemy + `app/services/marca_value.py`).
- **Datos de distribución**: dump `tests/fixtures/reference_data.sql.gz` (3.616 ejercicios, 2.553 ejercicios-de-rutina). ⚠️ Es una BD de **test**, no prod limpia (tiene 130+ "Test Objective" y programas basura). Vale para **estructura y valores posibles**, NO para conteos de prod.
- **Verificación puntual en prod**: API dashboard (token coach) → confirma que existen "Runner 10K Starter", "Atleta híbrido Pro", etc.

> Fecha auditoría: 2026-06-18.

---

## Resumen ejecutivo — semáforo de viabilidad

| Pieza del spec | ¿Existe el dato? | Veredicto |
|---|---|---|
| Filtro "solo barra/mancuerna, no máquinas" vía `equipment` | ❌ campo casi vacío en los lifts core | **Necesita curación manual** |
| 7 grupos musculares vía `muscle_group` | ❌ valores burdos + IDs legacy Firebase | **Inservible como está** |
| 7 grupos vía `category` | ⚠️ bilingüe sucio; no separa pierna | **Usable con normalización + split manual de pierna** |
| Lista de ejercicios válidos del spec por nombre exacto | ❌ los nombres del spec no existen literales | **Mapear por ID real, no por nombre** |
| Tipo de programa (Fuerza/Running/Híbrido) | ✅ vía `objective` (no hay columna `type`) | **Derivable; falta definir pesos híbrido** |
| Modelo de running por `distance`/`time` | ✅ soportado en código (`marca_value.py`) | **Viable; falta data real para calibrar** |
| Zonas de running (Z2/Z3/Z4) | ❌ no hay campo; `category` 96% NULL | **Necesita heurística por naming o flag nuevo** |
| Parseo de `logged_value` texto-libre → número | ✅ robusto (kg, mm:ss, km→m, reps) | **Listo para reutilizar** |

**Conclusión de fondo**: el sistema es viable, pero **el cuello de botella no son las tablas de estándares — es la falta de un mapeo curado ejercicio→grupo→"válido para score"**. Ni `muscle_group`, ni `equipment`, ni los nombres del spec sirven tal cual. Hay que construir una tabla de curación manual sobre IDs reales.

---

## 1. Grupos musculares — `muscle_group` es inservible, `category` es la mejor base

**`exercises.muscle_group`** (3.616 ejercicios) — valores reales:

| Conteo | Valor |
|---|---|
| 1231 | `Chest` |
| 881 | `Legs` |
| 528 | `Back` |
| 180 | `Arms` |
| 177 | `Updated Chest` (sic) |
| ~700 | `grupoMusculares/Lw5o8EhuyS9...` → **IDs legacy de Firebase sin migrar** (~30 valores distintos) |

Problemas: (a) está en inglés y burdo — `Legs` no separa **cuádriceps vs isquiotibiales**, `Arms` no separa **bíceps vs tríceps** (el spec necesita los 7 grupos por separado); (b) ~30% son referencias Firebase rotas.

**`exercises.category`** es mejor, pero sucio:

`Pecho`/`Chest`, `Espalda`/`Back`, `Pierna`/`Legs`, `Bíceps`/`Biceps`, `Tríceps`, `Hombro`, `Abdomen` — mezcla español/inglés duplicado.

→ Mapea a **6 de los 7 grupos** del spec, pero `Pierna` no distingue Cuádriceps de Isquiotibiales.

**Decisión recomendada**: usar `category` normalizada (de-duplicar ES/EN) como primer filtro, y resolver el split Cuádriceps/Isquiotibiales y el "válido para score" con una **tabla de curación manual sobre los ejercicios concretos del MVP** (son pocos: ~25-30 lifts).

---

## 2. `equipment` NO sirve para filtrar máquinas

Solo 6 valores distintos en toda la tabla:

| Conteo | Valor |
|---|---|
| 2116 | `["None"]` |
| 528 | `["Pull-up bar"]` |
| 341 | `[]` |
| 278 | `` (vacío) |
| 180 | `["Dumbbells"]` |
| 173 | `["Barbell"]` |

**El problema fatal**: los lifts que el score necesita tienen el campo **vacío**:
- `Press banca inclinado` → `equipment = []`
- `Sentadilla` → `equipment = ''`
- `Peso muerto` → `equipment = ''`
- `Curl de bíceps` → `equipment = ''`

Y **no existe ningún valor "Machine"** — incluso `Peso muerto en máquina` tiene equipment vacío. Es decir: no se puede ni filtrar barra/mancuerna *dentro*, ni excluir máquinas *fuera*, usando `equipment`.

**Decisión recomendada**: añadir un flag explícito **`valid_for_score` (bool)** curado a mano sobre los ejercicios del MVP, en vez de derivarlo de `equipment`. (Opción A del plan §1, no la derivación.)

---

## 3. Los nombres de ejercicio del spec no existen literales

Al cruzar los 26 ejercicios "válidos" del spec contra la tabla real:

- ✅ Existen genéricos: `Sentadilla`, `Press militar`, `Peso muerto`, `Remo con barra`, `Curl de bíceps`, `Curl barra Z`, `Press banca inclinado`…
- ❌ **No existen** las variantes que inventa el spec: `Sentadilla con barra`, `Press militar con barra`, `Press banca con mancuerna`, `Vuelo lateral con mancuerna`, `Estocada con mancuernas`, `Press banca cerrado`, `Skullcrusher con barra Z`, `Skullcrusher con mancuerna`, `Extensión de tríceps a un brazo`…
- ⚠️ El grupo **Tríceps** se quedó con **0 matches** — ningún ejercicio del spec existe con ese nombre.

**Decisión recomendada**: la lista de ejercicios que puntúan se construye **curando IDs reales de la tabla `exercises`**, no copiando los nombres del spec. El spec sirve como *intención* (qué patrón de movimiento por grupo), no como lista literal.

---

## 4. Tipo de programa — derivable de `objective`, sin columna nueva (o con una pequeña)

`programs` **no tiene columna de tipo** (confirmado en el modelo). Pero el **objetivo** lo codifica. Objetivos reales del dump: `Fisico`, `Atleta`, `Salud`, `Carrera`. Y en prod existen programas como:
- **"Runner 10K Starter"** → running
- **"Atleta híbrido Pro"** ("6 días de fuerza y carrera") → híbrido

**Decisión recomendada**: mapa `objective → score_type + pesos`:

| Objetivo | score_type | Peso Fuerza | Peso Running |
|---|---|---|---|
| Fisico / Salud | fuerza | 100% | — |
| Atleta (híbrido) | híbrido | 50% | 50% |
| Carrera | running | — | 100% |

Implementarlo como **tabla de mapeo** (no columna en `programs`) mantiene la flexibilidad de ajustar pesos sin tocar cada programa. Pendiente: confirmar si "Carrera" incluye runners con fuerza complementaria (peso 20/80 del spec).

---

## 5. Running — el modelo del spec SÍ es real (con un matiz)

`app/services/marca_value.py` mapea `log_type` a unidad:

```python
log_type == "time"  | "time_distance"  → tiempo
log_type == "distance"                 → metros   ("2.5km" → 2500, "800m" → 800)
else                                   → reps / kg
```

→ El modelo `plan_type`/`log_type` con `distance`/`time` del spec **existe y está soportado en código**. La alarma inicial (no aparecía `distance` en el dump) era porque **el dump de test no tiene programas de running**, no porque el modelo no exista.

**Dos matices nuevos**:
1. Aparece un tercer tipo, **`time_distance`**, que el spec no menciona. Hay que clasificarlo (probablemente "corre X tiempo y registra distancia", justo el caso de Series/Umbral del spec).
2. **No hay data real de running en el dump** → las tablas de estándares de running (pace→score) no se pueden calibrar con esta fuente. Hace falta extraer sesiones reales de los programas Runner de prod.

**Zonas (Z2/Z3/Z4)**: no hay campo. `training_day_exercises_v2.category` está **96% NULL** (2364 de 2553). → La zona habría que inferirla del **nombre de la sesión/ejercicio** o añadir un flag. Es el bloqueante de running que sigue abierto.

---

## 6. Parseo de logs — listo para reutilizar

`marca_value.py` ya parsea texto libre de forma robusta: `"50kg"`, `"15:30"` (mm:ss), `"2.5km"`/`"800m"`, reps. Funciones `parse_numeric`, `top_set_value`. Para fuerza extrae el mejor set; para running convierte a metros/segundos. → El motor de score puede apoyarse en esto directamente (plan §0 ya lo anticipaba). Pendiente: medir % de logs reales no parseables.

---

## Decisiones que necesito de producto (Kata)

1. **Curación manual del catálogo de score** (lo más importante): ¿avanzamos definiendo a mano la lista de ~25-30 ejercicios del MVP con su grupo canónico y flag `valid_for_score`? Es trabajo de producto, no de código, y desbloquea todo lo demás.
2. **Split de pierna**: ¿separamos Cuádriceps/Isquiotibiales (como pide el spec) o arrancamos el MVP con "Pierna" unificada para simplificar?
3. **Pesos de programas híbridos**: confirmar la tabla objetivo→pesos (¿"Carrera con fuerza" 20/80 existe como objetivo real?).
4. **Running en el MVP**: dado que no hay data de running para calibrar y las zonas no están estructuradas, ¿el MVP arranca **solo con Score de Fuerza** y running queda para fase 2? (Recomendado.)

---

## Apéndice — cómo reproducir esta auditoría

```bash
# 1. Estructura: modelos en elmetodo_api/app/models/{exercise,program,training_day_exercise_v2}.py
#    y unidades en elmetodo_api/app/services/marca_value.py
# 2. Datos: dump de test
cd /Users/kataiturriaga/repos/elmetodo_api
gzip -dc tests/fixtures/reference_data.sql.gz > /tmp/refdata.sql   # bloques COPY de Postgres
# 3. Prod (verificación): API dashboard con token coach
#    POST /api/coaches/auth/login  → GET /api/dashboard/programs/search?q=Runner
```
