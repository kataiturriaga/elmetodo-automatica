# Tareas de implementación — Puntuación de Entrenamiento

Plan end-to-end para implementar el sistema descrito en [puntaciones-entreno.md](puntaciones-entreno.md).

**Alcance**: solo **app automática** (sin coaches, sin dashboard). Toda la info es visible para el usuario final.

**Decisión MVP (18-jun-2026)**: el MVP arranca **solo con Score de Fuerza**. Running (§4) y híbrido (§5) → **fase 2** (no hay data de running para calibrar ni zonas estructuradas — ver [auditoría §5](../../archived/auditoria-datos-reales.md#5-running--el-modelo-del-spec-sí-es-real-con-un-matiz)). Catálogo de fuerza curado en [curacion-ejercicios-fuerza.md](../puntuaciones-entreno/curacion-ejercicios-fuerza.md).

**Stack real**:
- **API** `elmetodo_api`: FastAPI · SQLAlchemy 2.x · Alembic (forward-only) · Celery + Redis · Postgres. Capas: routes → services → repositories.
- **App** `elmetodo_app`: Flutter · Riverpod · Freezed. Carpetas `lib/features/{training,ranking}/{data,domain,presentation}`.

---

## 0. Lo que YA existe (reutilizar, no construir)

| Pieza | Dónde | Para qué sirve |
|---|---|---|
| Demografía (género, edad/`birthdate`, altura) | `Questionnaire` (`gender`, `age`, `birthdate`, `height`) | Ajustes de estándares fuerza/running |
| **Histórico de peso corporal** | `Progress(weight, date)` | Emparejar cada 1RM con el peso vigente en esa fecha |
| **Parsing de logs → número** | `app/services/marca_value.py` (`parse_numeric`, `top_set_value`, unidades kg/seg/m/reps) | Convertir `logged_value` texto-libre a float comparable |
| **Series de progresión por ejercicio** | `app/services/marcas_service.py` + `ExerciseLogRepository.get_history_for_exercise` | Base para el historial de score y las ventanas temporales |
| Logs de fuerza | `UserExerciseLog.logged_sets` (JSON, scoped enrollment+semana) | 1RM proyectado |
| Tipos plan/log de running | `training_day_exercise_v2.plan_type` / `log_type` | Clasificar sesiones de running |
| Logs de circuitos/rondas | `UserRoundLog` (rounds/amrap/for_time/emom) | (Posible) input de running por tiempo |
| Metadata de ejercicio | `exercise.muscle_group`, `equipment`, `category` | Mapeo a grupo muscular y filtro máquina |
| **Sistema de ligas** | `RankingGroup` (grupos NATO ~100u, niveles) + `lib/features/ranking` (podium, badges, summary) | Hoy rankea por **pasos** — el score de entreno podría alimentarlo |

> El score **no requiere almacenamiento nuevo de raw data**: se deriva del histórico existente de `UserExerciseLog` / `UserRoundLog` + `Progress` (mismo patrón que `marcas`).

---

## 1. Definiciones previas (bloqueantes)

> 📋 **Auditoría de datos reales hecha (18-jun-2026)** → ver [auditoria-datos-reales.md](../../archived/auditoria-datos-reales.md). Resuelve casi todos estos puntos; abajo el estado actualizado.

- [x] **Tablas de estándares de fuerza** (fuerza relativa → score 0–300+) por grupo × género × edad → HECHO (v1): construidas sobre ratios reales de **StrengthLevel** (Gravl no publica los suyos), calibración **motivadora**, ajuste de edad incluido. Ver [estandares-fuerza.md](../puntuaciones-entreno/estandares-fuerza.md). Pendiente: validar contra datos reales + decisión media vs **mediana** para el total.
- [ ] **Tabla de estándares de running** (pace → score) por género, edad y distancia de referencia (VDOT-like). **No existe.** ⚠️ Auditoría: no hay data de running en el dump de test → calibrar con sesiones reales de los programas Runner de prod.
- [x] **Auditar `exercise.muscle_group` y `exercise.equipment`** → HECHO. `muscle_group` **inservible** (valores burdos `Chest/Legs/Back/Arms` + ~30% IDs legacy Firebase; no separa cuádriceps/isquio ni bíceps/tríceps). `category` es mejor base pero bilingüe sucio y no separa pierna. **Los nombres de ejercicio del spec no existen literales** → mapear por ID real. Conclusión: **se necesita tabla de curación manual ejercicio→grupo** (no normalización automática). [detalle](../../archived/auditoria-datos-reales.md#1-grupos-musculares--muscle_group-es-inservible-category-es-la-mejor-base)
- [x] **Catálogo curado de fuerza** → HECHO: de los 26 ejercicios del spec, **20 ya existen en la BD** (decisión Kata: no crear los 6 que faltan) → van en la mini-tabla `exercise_id → grupo`, con 7 compuestos principales como anclas. Ver [curacion-ejercicios-fuerza.md](../puntuaciones-entreno/curacion-ejercicios-fuerza.md).
- [x] **Qué ejercicios cuentan** → DECIDIDO: `equipment` **no sirve** (vacío en los lifts core; no existe valor "Machine"). → **Mini-tabla de mapeo aparte** (`exercise_id → grupo_canonico`) con solo los 20 ejercicios curados. **Estar en la tabla = cuenta** → NO se añade columna `valid_for_score` ni se toca la tabla `exercises`. [detalle](../../archived/auditoria-datos-reales.md#2-equipment-no-sirve-para-filtrar-máquinas)
- [x] **Tipo de programa** → DECIDIDO: `Program` no tiene columna tipo (confirmado), se deriva del **`objective_id`**. Mapeo real de prod (confirmado 18-jun por API `/api/dashboard/objectives`):

  | `objective_id` | Nombre (prod) | score_type | Peso Fuerza | Peso Running |
  |---|---|---|---|---|
  | 1 | Físico | fuerza | 100% | — |
  | 2 | Carrera | running | — | 100% |
  | 3 | Hyrox | híbrido | 50% | 50% *(ajustable fase 2)* |
  | 4 | Atleta | híbrido | 50% | 50% |

  Implementar como **tabla de mapeo `objective_id → score_type + pesos`**, no columna en `programs`. (No existe "Salud" en prod; era data de test.) Pesos solo relevantes en fase 2 (MVP = solo fuerza).
- [~] **Clasificación de sesión de running** → PARCIAL: el modelo `plan_type`/`log_type` con `distance`/`time` **sí existe** en código (`marca_value.py`), + un tercer tipo `time_distance` no documentado. **Pero las zonas (Z2/Z3/Z4) NO tienen campo** (`category` 96% NULL) → inferir por naming de sesión o flag nuevo. Bloqueante de running que sigue abierto. [detalle](../../archived/auditoria-datos-reales.md#5-running--el-modelo-del-spec-sí-es-real-con-un-matiz)
- [x] **Texto-libre en `logged_value`** → CONFIRMADO viable: `marca_value.py` parsea robusto kg / mm:ss / km→m / reps. Pendiente solo medir % no parseable en logs reales.

## 2. Modelo de datos (API)

- [ ] Migración Alembic: tabla **estándares de fuerza** (grupo, género, rango edad, umbrales por nivel).
- [ ] Migración Alembic: tabla **estándares de running**.
- [ ] **Mini-tabla de mapeo** `exercise_id → grupo_muscular_canonico` con los 20 ejercicios curados (ver [curacion-ejercicios-fuerza.md](../puntuaciones-entreno/curacion-ejercicios-fuerza.md)). Estar en la tabla = cuenta para el score; sin flag booleano, sin tocar la tabla `exercises`.
- [ ] **Tabla de mapeo `objective_id → score_type + pesos`** (Físico=1→fuerza, Carrera=2→running, Hyrox=3→híbrido 50/50, Atleta=4→híbrido 50/50). Ver tabla en §1. No columna en `programs`.
- [ ] Tabla de **snapshots de score** (`user_id`, total, sub-scores, desglose por grupo/zona/ejercicio, `computed_at`) para el historial y para no recalcular en cada request. Refrescar snapshot de `reference_data.sql.gz` si las tablas de estándares son reference data.

## 3. Motor de cálculo — Fuerza (service nuevo, p. ej. `score_service.py`)

- [ ] **1RM proyectado (Epley)** `peso × (1 + reps/30)` por ejercicio, mejor registro de **últimos 3 meses**. Reutilizar `top_set_value`/`parse_numeric` para extraer peso y reps de `logged_sets`.
- [ ] **Emparejar peso corporal por fecha** del registro contra `Progress.weight` (fallback a `Questionnaire.weight` si no hay histórico).
- [ ] **Fuerza relativa** = 1RM / peso_corporal.
- [ ] **Score por grupo muscular** = lookup estándar con `max(fuerza_relativa)` del grupo, ajustado por género y edad.
- [ ] **Score total fuerza** = **mediana** de grupos con datos (decisión 18-jun, igual que Gravl); grupos sin datos → `—`, fuera del cálculo.
- [ ] `*` + nota *"basado en X de 7 grupos musculares"* cuando faltan grupos.
- [ ] Filtrar ejercicios de **máquina** y los no mapeados a grupo.
- [ ] Mapear score → **nivel** (Principiante → Olímpico).

## 4. Motor de cálculo — Running

- [ ] **Pace** = tiempo_total / distancia_logueada por sesión (mejor registro 3 meses), parseando `logged_sets` según `plan_type`/`log_type`.
- [ ] **Prioridad de fuentes**: Test > Series Largas Z4 (≥5 min) > Umbral Z3 (≥15 min) > Z2 larga.
- [ ] Conversión **pace → score** (estándar por género, edad, distancia referencia).
- [ ] **Desglose** por zona: Velocidad/VO2max, Umbral, Base aeróbica; zona sin dato → `—`.
- [ ] **Indicador de confianza** (baja/media/alta) por programa; en Starter/10K básico mostrar baja confianza o activar solo con Test disponible.

## 5. Motor — Híbrido + orquestación

- [ ] **Score total** = promedio ponderado(Fuerza, Running) según pesos del programa; exponer siempre los **dos sub-scores**.
- [ ] **Registros expirados** (>3 meses) y su efecto.
- [ ] **Recálculo**: tarea Celery (batch diario) y/o trigger al completar entreno / registrar peso. Persistir snapshot (sección 2).
- [ ] Tests unitarios de fórmulas (Epley, fuerza relativa, paces, ponderaciones, promedios con grupos vacíos) — sin mocks de DB en integración (convención del repo).

## 6. Sesiones de evaluación — solución cold-start

> Ver [vision-producto-puntuaciones.md](vision-producto-puntuaciones.md) §5. Lo que hace que el score se pueble dentro del trial.

- [ ] **Diseñar el bloque de evaluación de fuerza** (contenido): 1–2 sesiones iniciales que incluyan ≥1 ejercicio válido por cada uno de los 7 grupos musculares, con **series de trabajo submáximas** (no 1RM a fallo). Insertarlo al inicio de los programas de fuerza del MVP.
- [ ] **Test ligero de running de inicio** (contenido): proxy corto escalado al nivel del programa (time-trial 1–2 km o test 12 min) que dé un pace de arranque. El Test completo del spec se mantiene al final.
- [ ] **Flag de "sesión de evaluación"** en `training_day_v2` (o ejercicio) que marque qué sesiones cuentan como baseline. Alinear con el tipo de sesión "Test" del running.
- [ ] **Empty state de onboarding** en el tab Puntuaciones: antes de completar la evaluación, mostrar "Completa tu sesión de evaluación para ver tu nivel" en vez de score en cero.
- [ ] Medir **time-to-first-score** como métrica secundaria (ver visión §2).

## 7. API — Endpoints (mobile)

- [ ] `GET /score` (o dentro de training): Score Total + sub-scores + desglose + nota de cobertura + nivel.
- [ ] `GET /score/history` con ventanas 1 mes / 6 meses / 1 año / Todo.
- [ ] Schemas Pydantic (mismo patrón que `app/schemas/marcas.py`).
- [ ] Tests de integración (DB real, auth real, header `X-Client-ID`).

## 8. App Flutter (`lib/features/...`)

- [ ] **Dos tabs en la pantalla de Entreno**: *Programa* (lo actual) y *Puntuaciones* (este feature). El tab Puntuaciones aloja score + desgloses + historial.
- [ ] Capa data/domain (Freezed models + provider Riverpod) consumiendo los endpoints de score.
- [ ] **Pantalla principal**: Score Total con `*` y nota de cobertura + nivel.
- [ ] **Historial**: 1 mes / 6 meses / 1 año / Todo (gráfica — reutilizar el chart de marcas si encaja).
- [ ] **Desglose fuerza**: grupo muscular → ejercicio.
- [ ] **Desglose running**: por zona (VO2max, umbral, base).
- [ ] **Resumen semanal**: vs semana anterior, grupos/zonas que subieron/bajaron, aviso de registros expirados.
- [ ] Estados vacíos / baja confianza / "aún no hay datos suficientes".
- [ ] Strings en `l10n` (`app_localizations_es/en`).

## 9. Integración con Ligas (opcional, decisión de producto)

- [ ] Decidir si el **score de entreno alimenta el ranking** (hoy es por pasos en `RankingGroup`) o vive como vista propia. Si alimenta ligas: definir métrica de ranking (score absoluto vs velocidad de progreso) y ajustar el job de asignación de grupos.

## 10. Diseño (Figma)

- [ ] Specs de pantalla principal, historial, desgloses y resumen semanal (loop Figma del repo: execute → screenshot → iterar).
