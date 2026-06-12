# Auditoría de programas de producción y plan de "sesiones de evaluación"

**Fecha:** 2026-06-12 · **Alcance:** todos los programas activos en producción · **Autor:** agente de planificación (solo lectura).
Documento de **planificación**. No se modificó la base de datos, ni contenido de programas, ni se escribió migración alguna.

Relacionado: [puntaciones-entreno.md](puntaciones-entreno.md) (spec del score) · [vision-producto-puntuaciones.md](vision-producto-puntuaciones.md) §5 (cold-start) · [tareas-implementacion-puntuaciones.md](tareas-implementacion-puntuaciones.md).

---

## 0. Método, acceso y límites de la auditoría

**Acceso a producción (solo lectura).** El puerto de la BD gestionada (DigitalOcean, `:25060`) está **filtrado por allowlist de IPs de confianza** y esta máquina no está en la lista, así que `psql` directo **no fue posible** (TCP timeout; DNS resuelve y el resto de internet funciona). Las credenciales de memoria son de **superusuario** (`doadmin`), no de un rol de solo lectura.

En su lugar se auditó vía la **API de producción** (`https://api.apps.elmetodoapp.com`), que sí es alcanzable, usando **solo endpoints de lectura** (`GET`) del dashboard de coach. Esto cubre exactamente la misma estructura de datos (programas → fases → rutinas → días → ejercicios) leyendo los modelos en `elmetodo_api/app/models/`. Ningún `POST/PATCH/DELETE` fue invocado.

> **Si se prefiere auditar contra la BD directa** (consultas agregadas más exactas), basta con **añadir la IP `212.115.166.76`** a las *trusted sources* del clúster en DigitalOcean; con eso reproduzco todo esto en SQL puro. No fue necesario para este informe.

**Unidad de análisis = "primeras sesiones".** Para cada programa se auditó el **primer microciclo real** que ve un usuario nuevo: la primera fase (`phase_order` mínimo) → su primera rutina (`routine_order` mínimo) → todos sus `training_days` (en `day_order`). Ahí es donde el score tiene que poblarse dentro del trial de 7 días.

**Clasificador de ejercicios (heurístico, conservador).** Los campos del esquema no bastan para puntuar (ver §3), así que se mapeó cada ejercicio a los 7 grupos **por nombre** y se aplicó un filtro barra/mancuerna **por nombre**. Es deliberadamente estricto: **las cifras de cobertura son una cota inferior** — la cobertura real puede ser algo mayor si se decide que ejercicios de equipo ambiguo (ej. "Peso muerto" sin sufijo) cuentan como barra.

**Esquema real confirmado** (difiere del brief: los días cuelgan de `routines_v2`, no de las fases directamente):
```
programs → program_phases → program_phase_routines (junction, duration_weeks)
         → routines_v2 → training_days_v2 (day_order, training_type)
         → bloques_v2 / supersets_v2 → rondas_v2
         → training_day_exercises_v2 (exercise_id, plan_type, log_type, sets[])
         → exercises (name, muscle_group, equipment, category)
```

---

## 1. Inventario completo de programas

**191 programas activos** (ninguno con `deleted_at`), **69 títulos distintos**, **717 ejercicios** en catálogo.

| Dimensión | Reparto |
|---|---|
| **Zona** | `subscription` 110 · `free` 29 · `consultancy` 52 |
| **Tipo inferido** | **Fuerza** 114 · **Running** 44 · **Híbrido** 33 · *otro* 0 |
| **Nivel** | intermediate 89 · beginner 51 · advanced 51 |
| **Agrupación** | 50 `program_group_id` (variantes género/ubicación) + 52 sin grupo (consultancy, 1×) |

**Criterio de clasificación de tipo** (no hay campo de tipo en `programs`; se infiere del título, validado con la composición real de ejercicios de la primera rutina):
- **Running** → título contiene `Runner`. Composición: 100% sesiones `Zona N` (categoría `Running`/`Cardio`), 0 fuerza.
- **Híbrido** → título contiene `híbrido` o `Hyrox`. Composición: mezcla días de fuerza + días `Zona N`.
- **Fuerza** → resto (`Cuerpo construido/definido`, `recomposicion-*`, `chicos-gym-*`). Composición: días de fuerza, sin running (salvo Starters, que meten cardio).
- **otro** → ninguno.

### 1.1 Catálogo (subscription / free) — 87 programas
| Título | Tipo | Variantes | Días 1ª rutina |
|---|---|---|---|
| Cuerpo construido Pro | Fuerza | 18 | 3 |
| Cuerpo construido Starter | Fuerza | 4 | 4 |
| Cuerpo definido Pro | Fuerza | 18 | 3 |
| Cuerpo definido Elite | Fuerza | 18 | 3 |
| Cuerpo definido Starter | Fuerza | 4 | 4 |
| Atleta híbrido Pro | Híbrido | 14 | 3 |
| Atleta híbrido Starter | Híbrido | 4 | 4 |
| Hyrox Elite / Pro Oro / Pro Plata | Híbrido | 3+3+3 | 4–5 |
| Tu primera Hyrox Pro / Starter | Híbrido | 3+3 | 4 |
| Runner 5K Pro / 10K Pro / 21K Pro | Running | 12+12+12 | 5–6 |
| Runner 5K Starter / 10K Starter | Running | 4+4 | 4 |

Las variantes son combinaciones **género × ubicación** (`gym` / `home` / `home_with_material`) del mismo programa-grupo. **Comparten la plantilla de sesión pero NO los ejercicios** — y eso cambia radicalmente la puntuabilidad (un mismo programa en `gym` usa barra; en `home_with_material` usa gomas → 0 puntuable).

### 1.2 Consultancy (asesorías, zona `consultancy`) — 52 programas, IDs 149–200
- `recomposicion-{chicos,chicas}-{gimnasio, mancuernas y gomas, solo gomas}-{principiante,avanzado}-{2..5} dias` (48)
- `chicos-gym-principiante-{2..5} dias` (4)

Son 1× cada uno (sin grupo) y wrappean rutinas para el tier de asesorías. Su puntuabilidad depende fuertísimamente del material (gimnasio vs gomas).

---

## 2. Auditoría de cobertura actual (primer microciclo)

**Resultado titular: ningún programa de los 191 cubre los 7 grupos musculares en su primera rutina.** El mejor caso llega a **5/7** (recomposicion gimnasio avanzado 4–5 días). La distribución entre los 147 programas de fuerza+híbrido:

| Grupos cubiertos en 1ª rutina | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
|---|---|---|---|---|---|---|---|---|
| nº de programas | 23 | 43 | 32 | 23 | 19 | 7 | 0 | 0 |

**Frecuencia con que cada grupo FALTA** (entre 147 fuerza+híbrido):

| Grupo | % que NO lo cubre en 1ª rutina |
|---|---|
| Tríceps | **97%** |
| Bíceps | 77% |
| Pectorales | 74% |
| Isquiotibiales | 73% |
| Cuádriceps | 70% |
| Hombros | 69% |
| Espalda | 42% (el mejor cubierto) |

→ **Tríceps y bíceps casi nunca puntúan al inicio**: cuando aparecen, es con press en máquina, jalón, fondos, contractora o curl en polea — nada de barra/mancuerna en compuestos. Espalda es el único grupo razonablemente cubierto (remo con barra/mancuerna es común).

### 2.1 Fuerza/híbrido — cobertura por título (rango entre variantes)

`cov = grupos puntuables cubiertos / 7` · `str = días con algún ejercicio puntuable` · números = cota inferior conservadora.

| Título | Var. | Días | cov /7 | Lectura |
|---|---|---|---|---|
| Cuerpo construido Pro | 18 | 3 | **0–4** | gym cubre 3–4; home_with_material → 0 |
| Cuerpo definido Pro | 18 | 3 | **0–4** | **muy machine-heavy**; varias variantes gym a 0 |
| Cuerpo definido Elite | 18 | 3 | 0–5 | idem, isolación en máquina |
| recompo chicos gimnasio avanzado 4–5d | 1+1 | 4–5 | **5** | mejor caso del catálogo |
| recompo *gimnasio* (resto) | varios | 2–5 | 1–5 | sube con los días/semana |
| recompo *mancuernas y gomas* | 16 | 2–5 | **0–2** | gomas no puntúan; solo mancuernas sueltas |
| recompo *solo gomas* | 16 | 2–5 | **0–2** | **score-blind de facto** |
| Atleta híbrido Pro | 14 | 3 | 0–5 | día de fuerza global; gym ok, casa 0 |
| Hyrox (todas) | 15 | 4–5 | 1–4 | movimientos funcionales no mapean a los 7 grupos |

**23 programas de fuerza/híbrido son score-blind** (0 grupos puntuables en su primera rutina). No son solo los de casa: incluyen **Cuerpo definido Pro en `gym`** (IDs 12, 19) — 100% máquina/polea/multipower por diseño (objetivo "definición" → isolación en máquina). Lista completa en §5.3.

> Ejemplo validado (id=19, *Cuerpo definido Pro*, gym/male): Press vertical **en máquina**, Remo **máquina**, Jalón, Elevaciones laterales **en máquina**, Curl scott **máquina**, Prensa, Femoral sentado, Extensión de cuádriceps, Hip thrust **en máquina**… → **cero** ejercicios de barra/mancuerna.

### 2.2 Running/híbrido — qué hay al inicio y cuándo llega el primer dato puntuable

Las sesiones de running se modelan como ejercicios `Zona 1/2/3/4` (categoría `Running`/`Cardio`); la **zona va en el nombre** y el `plan_value` de cada serie son **segundos**. Tipos vistos en primeras rutinas:

| `plan_type → log_type` | Significado | Puntuable |
|---|---|---|
| `time → distance` | prescribe segundos, loguea distancia (Z2/Z3/Z4 series) | Sí, da pace |
| `distance → time` | prescribe metros, loguea tiempo (test/intervalo) | Sí, VDOT directo |

| Programa | Sesiones puntuables en 1ª rutina | Primer dato fiable |
|---|---|---|
| **Runner 21K Pro** | **Sí**: Z4 series (Day "Series Cortas") + Z3 umbral 15min (Day "Ritmo Umbral") | Semana 1 ✓ (coincide con "Alta" del spec) |
| Runner 10K Pro | Parcial: Z2 + algún umbral; series cortas | Media — pace base, sin VO2max fiable hasta umbral |
| Runner 5K Pro | Casi todo Z2 + strides | Baja — sin sesión de umbral/series larga temprana |
| **Runner 5K/10K Starter** | **No**: solo Z2 y rodajes suaves (4 días) | **Solo al Test final** del programa |
| Atleta híbrido / Hyrox | Z2 + Z4 cortos desde Day 2 | Pace base sí; calidad depende del nivel |

→ Para **Starters y 5K** el running **no puntúa dentro del trial**: el único dato fiable es el Test, que el spec deja al final del programa. Necesitan un **test ligero de arranque** (§4).

---

## 3. Estado de los datos (lo que condiciona todo)

Auditados los 717 ejercicios del catálogo:

| Campo | Estado real | Implicación |
|---|---|---|
| **`equipment`** | **Inutilizable**: 1 único valor en los 717 ejercicios → `"[]"` (vacío) | El filtro barra/mancuerna vs máquina **no puede** usar este campo. Hay que inferir por nombre. |
| **`muscle_group`** | 29 referencias Firebase opacas (`grupoMusculares/wuQk8a3…`) + 98 a `None` | No legible. Cada ref mapea a una sola `category`, pero no separa los 7 grupos del spec. |
| **`category`** | Limpio y legible (11 valores) pero **grueso** | `Pierna` agrupa Cuádriceps **+** Isquiotibiales **+** glúteo/gemelo → no distingue 2 de los 7 grupos. Útil solo como filtro de primer nivel. |
| **`name`** | Única clave fiable, pero con ruido | Es lo que usa el clasificador. ~30% de nombres no declaran el equipo. |

**Categorías:** Pierna 153 · Hombro 118 · Espalda 92 · Hyrox 76 · Bíceps 76 · Tríceps 63 · Abdomen 61 · Pecho 56 · Movilidad 8 · Running 8 · Cardio 6.

### 3.1 % de ejercicios mapeables al score

| Cubeta | nº | % | Comentario |
|---|---|---|---|
| **Puntuable** (grupo + barra/mancuerna por nombre) | **95** | **13%** | Lo único que hoy alimenta el score con seguridad |
| Máquina/polea/multipower (excluido correctamente) | 113 | 16% | No comparable entre marcas (spec) |
| **Equipo AMBIGUO** (grupo conocido, equipo no declarado) | **211** | **29%** | "Peso muerto", "Press militar", "Curl de bíceps", "Elevaciones laterales", "Sentadilla goblet"… podrían ser barra/mancuerna **o** no |
| No mapea a ninguno de los 7 grupos | 298 | 42% | Hyrox, abdomen, cardio, running, glúteo/gemelo aislado, etc. |

→ **El 29% ambiguo es el mayor problema de datos.** Con `equipment` vacío, casi un tercio del catálogo no se puede clasificar barra/mancuerna sin revisión manual. **Sin arreglar `equipment`, el filtro del score es poco fiable** y la cobertura real queda indeterminada entre la cota baja (95) y la alta (95+211).

### 3.2 Ejercicios del spec mal etiquetados / con nombre distinto

Los nombres del spec **no coinciden** con producción (match exacto: ~6/26). Producción usa "Press banca plano/con barra", "Sentadilla trasera con barra", "Press Militar 1 mano", "Press francés barra Z", "Curl barra recta", "Remo con barra"… El mapeo del score **debe construirse contra los nombres reales de prod**, no contra los literales del spec. (Se detectó además un ejercicio basura: `Test1` en categoría Espalda.)

---

## 4. Propuesta de cambios por programa (sin ejecutar)

**Principio rector** (de §5 visión): la evaluación es **series de trabajo submáximas** (8–10 reps, peso moderado, bien calentado), NO un max-out a fallo. Y se necesita un **flag `is_evaluation`** en `training_days_v2` (o por ejercicio) para que la app sepa qué sesión puebla el score y muestre el onboarding correcto.

### 4.1 Bloque de evaluación de FUERZA (estándar para fuerza + parte de fuerza de híbrido)

Diseñar **2 sesiones de evaluación** al inicio de la primera fase que, juntas, toquen **1 ejercicio puntuable por cada uno de los 7 grupos** (no cabe en 1 sola sesión de forma sensata):

- **Eval A — Tren superior** (Pectorales, Espalda, Hombros, Bíceps, Tríceps): Press banca / Remo con barra / Press militar / Curl barra / Press francés barra Z.
- **Eval B — Tren inferior + posterior** (Cuádriceps, Isquiotibiales): Sentadilla trasera con barra / Peso muerto con barra. (+ opcional repetir 1 empuje para redundancia.)

Todos con nombres **que ya existen en prod** y caen en la cubeta "puntuable". Decisión por variante:

| Variante de programa | Acción recomendada | Impacto en duración |
|---|---|---|
| **gym** (barra disponible) | **Modificar** los primeros 2 días para garantizar los 7 grupos con compuestos de barra/mancuerna (muchos ya están a 3–5/7; faltan tríceps/bíceps/un empuje) | ~0 (se reordena, no se alarga) |
| **home_with_material** (mancuernas) | **Modificar** usando variantes con mancuerna (Press plano con mancuernas, Remo 1 mano, Sentadilla con mancuerna, Peso muerto mancuernas, Curl mancuernas, Press francés con mancuernas) | ~0 |
| **solo gomas / mancuernas y gomas** | **No forzar score.** Las gomas no son puntuables (no hay carga absoluta comparable). Ver §5.1 | n/a |
| **Cuerpo definido (machine-heavy)** | **Añadir** 1 bloque de evaluación con barra/mancuerna al arranque, porque el cuerpo del programa es isolación en máquina y nunca generará dato | +1 sesión la primera semana |

**Cobertura objetivo:** pasar de 0–5/7 a **7/7 en ≤2 sesiones** para toda variante con barra o mancuerna.

### 4.2 RUNNING — test ligero de arranque

Para los programas donde el primer dato puntuable llega tarde (5K, Starters, y reforzar 10K):

- **Añadir** una **sesión de evaluación de carrera** en la semana 1: un *time-trial* corto escalado al nivel (p.ej. **test de 12 min tipo Cooper** o **1–2 km a ritmo controlado**), modelado como `plan_type: distance → log_type: time` (la estructura "test" que el score prioriza como VDOT directo). El Test de carrera completa **se mantiene al final** como dice el spec.
- **Programas Pro de 21K**: ya tienen Z3/Z4 puntuable en semana 1 → **no requieren** test extra; basta con marcar esas sesiones para el score.

| Programa | Acción | Impacto |
|---|---|---|
| Runner 5K/10K Starter | **Añadir** test ligero (Cooper 12') semana 1 | +1 sesión corta |
| Runner 5K Pro | **Añadir** test ligero o adelantar una sesión de umbral corto | +1 sesión |
| Runner 10K Pro | **Marcar** umbral existente como evaluación; opcional test ligero | ~0 |
| Runner 21K Pro | **Solo marcar** Z3/Z4 de semana 1 como fuente de score | 0 |

### 4.3 HÍBRIDO (Atleta híbrido, Hyrox)

Cubrir **ambas patas**: bloque de evaluación de fuerza (§4.1, versión reducida — el peso fuerza del híbrido es menor) **+** test ligero de running (§4.2). Ponderación de score según spec (Atleta híbrido 50/50). Hyrox usa mucho movimiento funcional que no mapea a los 7 grupos → su score de fuerza será parcial por diseño; conviene apoyarse más en la pata running y avisar de baja confianza en fuerza.

---

## 5. Decisiones abiertas y riesgos

### 5.1 Programas de solo-gomas / casa sin material puntuable
~16 programas consultancy (`solo gomas`, parte de `mancuernas y gomas`) y varias variantes `home_with_material` del catálogo **no pueden generar score de fuerza** (las gomas no dan carga absoluta comparable; mancuernas ligeras dan poco). **Decisión necesaria:** ¿se les muestra score con muchos `—` y baja confianza, se les oculta el tab (como sugiere §3 de la visión para cobertura parcial), o se les da un score basado solo en lo poco que haya? Recomendación: **no mostrar score de fuerza** en variantes sin barra/mancuerna; empty-state explicativo.

### 5.2 Arreglar `equipment` es prerequisito, no opcional
El 29% de ejercicios ambiguos hace que el filtro barra/mancuerna sea heurístico y discutible. **Antes de calcular scores en producción** hay que poblar `equipment` (o un flag `scoreable`/`equipment_class`) en los ~211 ejercicios ambiguos + los 95 ya claros. Es trabajo de **contenido/datos**, no de código, y bloquea la fiabilidad del score. (Esto encaja con "la auditoría de `muscle_group`/`equipment` ya planificada" de la visión §5.)

### 5.3 Programas score-blind a vigilar (0 grupos puntuables hoy en 1ª rutina)
23 programas fuerza/híbrido, incluyendo varios **de gimnasio** (no solo de casa):
`Cuerpo definido Pro` gym IDs **12, 19**; `Cuerpo definido Elite` id 5; múltiples `Cuerpo construido/definido` en `home_with_material`; `Atleta híbrido Pro` casa IDs 102–104; `chicos-gym-principiante-2 dias` id 197; varias recompo gomas (IDs 158, 162, 166, 170). Todos requieren **añadir** bloque de evaluación, no solo reordenar.

### 5.4 Conflicto con la progresión / intención del programa
"Cuerpo definido" es machine-heavy **a propósito** (objetivo de definición/hipertrofia con isolación). Meterle compuestos de barra al inicio cambia el carácter del programa. **Decisión:** ¿se acepta 1 sesión de evaluación "fuera de estilo" al arranque a cambio de poblar el score, o se asume que estos programas muestran score parcial? Trade-off score-vs-fidelidad del programa.

### 5.5 Riesgo de desmotivación (de la visión)
Baseline "Principiante" en pleno trial puede disparar cancelación. Mitigación ya prevista: framing de punto de partida, primer delta rápido, evaluación submáxima bien calentada (más justa que un test a fallo). Aplica especialmente a los Starters/principiantes.

### 5.6 Programas que no encajan limpio
- **Hyrox**: 76 ejercicios categoría Hyrox no mapean a los 7 grupos → score de fuerza estructuralmente parcial.
- **Híbrido/Runner con día de fuerza de nombres ambiguos** ("Peso muerto", "Press militar sentado", "Remo 2 manos" sin sufijo de equipo): hoy quedan fuera del score por el filtro estricto aunque probablemente sean puntuables. Se resuelve con §5.2.

---

## Anexo — Reproducibilidad
- Datos extraídos vía API de prod (solo `GET`), cacheados en `/tmp/em_programs.json` (191), `/tmp/em_exercises.json` (717), `/tmp/em_audit.json` (primer microciclo de cada programa).
- Clasificador y agregados: scripts heurísticos por nombre (mapeo a 7 grupos + filtro barra/mancuerna). Cifras de cobertura = **cota inferior conservadora**.
- Para una auditoría en SQL directo contra la BD: allowlistar IP `212.115.166.76` en DigitalOcean (trusted sources del clúster `dbaas-db-6439710`).
</content>
</invoke>
