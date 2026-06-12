# Tarea: Auditar TODOS los programas de producción y planificar las "sesiones de evaluación" del sistema de puntuación

> Prompt para un agente en chat paralelo. Trabaja sobre `elmetodo_api` (DB de producción + modelos) y lee la doc de la feature en `elmetodo_auto/automatica/puntuaciones-entreno/`.

## Tu rol y límite (IMPORTANTE)
Eres un agente de planificación. Tu trabajo es **auditar** las rutinas/programas reales en la base de datos de **producción** y **proponer un plan** para introducir "sesiones de evaluación" al inicio de **cada** programa.
- **NO ejecutes nada**: no modifiques la DB, no escribas migraciones, no cambies contenido de programas, no hagas commits.
- Necesitas acceso de **SOLO LECTURA** a la base de producción. Los datos de conexión están en la memoria de usuario / `.env` del repo `elmetodo_api`. Si no los tienes, **pídelos antes de empezar** — no asumas ni inventes credenciales.
- Entregable = un **documento markdown** con el plan y los cambios propuestos, programa por programa. Nada más.

## Contexto del producto (por qué existe esto)
El Metodo (app de fitness, repo API `elmetodo_api` = FastAPI/SQLAlchemy/Postgres; app `elmetodo_app` = Flutter) va a lanzar un **sistema de puntuación de entrenamiento**: un score 0–300+ que mide cómo de fuerte/en forma está el usuario, calculado desde sus logs de entreno. La apuesta es **diferenciación competitiva**, y la métrica de éxito es **conversión trial→pago** (el free trial dura **7 días**).

Problema a resolver: el score nace **vacío**. Si el usuario tiene que acumular semanas de datos para ver algo, el score no llega a tiempo para influir en la conversión del trial.

Solución (lo que vienes a planificar): las **primeras sesiones de cada programa son sesiones de evaluación** diseñadas para poblar el score desde el día 1. Esto aplica a **todos los tipos de programa** (fuerza, running e híbrido), no solo a uno.

## Cómo se calcula el score (lo que condiciona el diseño de las sesiones)

**Fuerza** (los 7 grupos musculares):
- Por cada ejercicio válido: `1RM proyectado = peso × (1 + reps/30)` (fórmula de Epley) sobre la mejor serie.
- `fuerza_relativa = 1RM / peso_corporal` → tabla de estándares por grupo/género/edad → score del grupo.
- Score total = promedio de los grupos con datos. Grupos sin datos → "—" (no cuentan).
- **No requiere test de 1RM máximo**: Epley funciona con **series de trabajo submáximas** (ej. 8–10 reps con peso moderado). La sesión de evaluación NO debe ser un max-out a fallo (riesgo de lesión y datos basura en principiantes).
- **Solo cuentan ejercicios de barra o mancuerna** (NO máquinas: varían entre marcas, no comparables).

**Los 7 grupos musculares y sus ejercicios válidos** (del spec):
| Grupo | Ejercicios válidos |
|---|---|
| Pectorales | Press banca, Press banca inclinado, Press banca con mancuerna, Press banca inclinado con mancuernas |
| Espalda | Remo con barra, Remo con barra agarre supino, Remo con mancuerna, Remo con mancuerna inclinado |
| Hombros | Press militar con barra, Press militar con barra sentado, Vuelo lateral con mancuerna, Press de hombro con mancuerna |
| Cuádriceps | Sentadilla con barra, Sentadilla frontal, Sentadilla búlgara con mancuernas, Estocada con mancuernas |
| Isquiotibiales | Peso muerto, Peso muerto con piernas rígidas, Peso muerto rumano con mancuerna |
| Bíceps | Curl de bíceps con barra, Curl barra Z, Curl de bíceps con mancuernas, Curl de bíceps sentado |
| Tríceps | Press banca cerrado, Skullcrusher con barra Z, Skullcrusher con mancuerna, Extensión de tríceps con mancuerna a un brazo |

**Running**: el pace se saca de sesiones tipo Test / Series Largas (Z4) / Umbral (Z3) / Z2. Los campos clave son `plan_type` (lo que prescribe el programa: `time` o `distance`) y `log_type` (lo que registra el atleta). Un Test de carrera completa solo aparece al final de los programas. Para baseline temprano se necesita un **test ligero escalado al nivel del programa** (time-trial corto), no un 10K el día 1.

**Híbrido**: combina fuerza + running, así que su sesión de evaluación debe cubrir **ambas** partes (los grupos musculares relevantes + el test ligero de running).

## Modelo de datos (en `elmetodo_api`, valida el esquema real tú mismo)
Programas V2 se estructuran aprox. así (confirma joins exactos leyendo los modelos en `app/models/`):
- `programs` (`Program`): título, `zones`, `objective_id`/`sub_objective_id`, `training_location`, `experience_level`, `days_per_week`, `gender`, `program_group_id`. **No hay campo de "tipo" (fuerza/running/híbrido)** → tendrás que inferirlo.
- `program_phases` (`ProgramPhase`) → semanas → `training_days_v2` (`TrainingDayV2`: `name`, `day_order`).
- Dentro de un día: `bloques_v2`, `supersets_v2`, `rondas_v2` (`RondaV2.mode`), y los ejercicios en `training_day_exercises_v2` (`TrainingDayExerciseV2`: `exercise_id`, `plan_type`, `log_type`, `sets` JSON, `position`, `category`, `place`).
- `exercises` (`Exercise`): `name`, `muscle_group`, `equipment`, `category`. **Audita qué valores reales tienen `muscle_group` y `equipment` en prod** — hay que mapearlos a los 7 grupos y al filtro barra/mancuerna vs máquina.

Archivos clave a leer en `elmetodo_api`: `app/models/{program,program_phase,training_day_v2,training_day_exercise_v2,exercise,ronda_v2}.py`, y `app/services/marca_value.py` (ya parsea logs y mapea log_type→unidad).

Documentación de la feature (en el repo `elmetodo_auto`, carpeta `automatica/puntuaciones-entreno/`): `puntaciones-entreno.md` (spec del score), `vision-producto-puntuaciones.md` (§5 = solución cold-start), `tareas-implementacion-puntuaciones.md`.

## Lo que tienes que entregar (el plan)
Audita **todos los programas activos de producción**, sin excepción y sin priorizar un tipo sobre otro:

1. **Inventario completo de programas**: lista todos los programas activos, clasificados por tipo inferido (fuerza / running / híbrido / otro) con el criterio que uses para clasificarlos.
2. **Auditoría de cobertura actual por programa**:
   - *Fuerza/híbrido*: qué grupos musculares (de los 7) tocan sus primeras sesiones con ejercicios **válidos** (barra/mancuerna), y en cuántas sesiones se tardaría hoy en cubrir los 7. Señala los huecos.
   - *Running/híbrido*: qué tipos de sesión (`plan_type`/`log_type`) aparecen al inicio y cuándo llegaría hoy el primer dato puntuable; si hace falta añadir un test ligero de arranque.
3. **Estado de los datos**: valores reales de `muscle_group`/`equipment`, % de ejercicios mapeables a los 7 grupos, y ejercicios válidos que falten o estén mal etiquetados.
4. **Propuesta de cambios por programa** (concreta, sin ejecutar): para CADA programa, qué sesión(es) de evaluación añadir o cómo modificar las primeras sesiones para que el score se pueble pronto — cubriendo los 7 grupos con series submáximas en fuerza, y/o el test ligero en running. Indica si conviene **añadir** un bloque de evaluación o **modificar** las sesiones existentes, y el impacto en la duración del programa.
5. **Decisiones abiertas y riesgos** que detectes (ej. programas sin ejercicios válidos suficientes, conflictos con la progresión del programa, programas que no encajen en el sistema de score).

Empieza confirmando acceso de solo lectura a la DB de producción y leyendo los modelos + el spec antes de consultar datos.
