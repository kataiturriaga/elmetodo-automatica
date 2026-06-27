# Puntuación de Entrenamiento — Diseño del sistema

Inspirado en el sistema de Gravl, adaptado a la estructura real de programas de El Metodo.

---

## Tipos de programa y sus scores

| Tipo de programa | Score visible |
|---|---|
| Fuerza | Score Total + desglose por grupo muscular + desglose por ejercicio |
| Running / Atleta | Score Total → Score Fuerza + Score Running (con sus propios desgloses) |
| Híbrido | Igual que Running/Atleta |

---

## Score de Fuerza

### Fórmula

**Paso 1 — 1RM proyectado por ejercicio** (mejor registro últimos 3 meses)
```
1RM = peso × (1 + reps / 30)   [fórmula de Epley]
```

**Paso 2 — Fuerza relativa**
```
fuerza_relativa = 1RM / peso_corporal
```

**Paso 3 — Score por grupo muscular**
```
score_grupo = tabla_estandar(max(fuerza_relativa), género, edad)
```
Solo se consideran ejercicios con barra o mancuerna (no máquinas — varían entre marcas y no son comparables).

**Paso 4 — Score total**
```
score_total = mediana(grupos_con_datos)
```
> Actualizado 18-jun-2026: **mediana** (no promedio), igual que Gravl. Ver [estandares-fuerza.md](estandares-fuerza.md).
Si algún grupo no tiene datos → muestra `—` en el desglose, no entra al cálculo.
El score total lleva un `*` si hay grupos sin datos, con nota: "basado en X de 7 grupos musculares".

**Confianza del score (decidido 23-jun-2026, con Kata):** se muestra el chip **"baja confianza"** mientras hay **1–3 grupos** con datos; **a partir de 4 grupos** (mayoría de 7) el score se considera fiable y se quita la etiqueta. El `*` "basado en X de 7" se mantiene hasta completar los 7. Razón: el total es la **mediana** de los grupos, que se estabiliza con mayoría. (Umbral antes indefinido.)

### Ajustes
- **Género**: estándares separados para comparaciones justas
- **Edad**: los estándares ajustan con la edad
- **Ventana temporal**: solo el mejor registro de los **últimos 3 meses** (score dinámico y actual)

### Grupos musculares y ejercicios válidos

| Grupo | Ejercicios |
|---|---|
| Pectorales | Press banca, Press banca inclinado, Press banca con mancuerna, Press banca inclinado con mancuernas |
| Espalda | Remo con barra, Remo con barra agarre supino, Remo con mancuerna, Remo con mancuerna inclinado |
| Hombros | Press militar con barra, Press militar con barra sentado, Vuelo lateral con mancuerna, Press de hombro con mancuerna |
| Cuádriceps | Sentadilla con barra, Sentadilla frontal, Sentadilla búlgara con mancuernas, Estocada con mancuernas |
| Isquiotibiales | Peso muerto, Peso muerto con piernas rígidas, Peso muerto rumano con mancuerna |
| Bíceps | Curl de bíceps con barra, Curl barra Z, Curl de bíceps con mancuernas, Curl de bíceps sentado |
| Tríceps | Press banca cerrado, Skullcrusher con barra Z, Skullcrusher con mancuerna, Extensión de tríceps con mancuerna a un brazo |

### Niveles

| Nivel | Rango |
|---|---|
| Principiante | 0–49 |
| Novato | 50–99 |
| Experimentado | 100–149 |
| Pro | 150–199 |
| Atleta | 200–249 |
| Élite | 250–299 |
| Olímpico | 300+ |

---

## Score de Running

### Estructura de datos real en los programas

Los ejercicios de running tienen dos campos clave:
- `plan_type`: lo que el programa prescribe (`time` o `distance`)
- `log_type`: lo que el atleta registra (`distance` o `time`)

Los tipos de sesión identificados en los programas reales y su utilidad para scoring:

| Sesión | Estructura | Duración típica | Utilidad para score |
|---|---|---|---|
| Test 10K / Test Media | `distance → log time` | carrera completa | ★★★ VDOT directo |
| Series Largas (Z4) | `time → log distance` | 800s (~13 min) × 5 | ★★★ proxy VO2max |
| Ritmo Umbral (Z3) | `time → log distance` | 1080–1800s (18–30 min) | ★★ umbral de lactato |
| Fondo Progresivo (Z2+Z3) | `time → log distance` | 45 min Z2 + 15 min Z3 | ★★ eficiencia aeróbica |
| Zona Dos (Z2) | `time → log distance` | 35–125 min | ★ referencia base |
| Strides (Z4 cortos) | `time → log distance` | 15–20s | ★ velocidad neuromuscular |

### Fuente de datos por tipo de programa

| Programa | Datos disponibles | Fiabilidad del score |
|---|---|---|
| Runner 5K / 10K Starter | Z2 + strides 20s + Test final | Baja — score solo al final del programa |
| Runner 10K Pro | Z2 + strides 20s + umbral 18min + Test 10K | Media |
| Runner 21K Pro | Z2 + Series Largas Z4 13min + umbral 30min + Test Media | Alta |

> **Implicación de diseño**: el score de running solo es fiable a partir de programas de nivel Pro con sesiones de umbral y series largas. Para programas Starter o 10K básico, mostrar el score con indicador de baja confianza o activarlo solo cuando hay Test disponible.

### Fórmula

**Dato principal — pace por tipo de esfuerzo** (mejor registro últimos 3 meses)
```
pace = tiempo_total / distancia_logueada   [min/km]
```

**Prioridad de fuentes para el score:**
1. Test session (`plan_type: distance, log_type: time`) → VDOT directo con tiempo real de carrera
2. Series Largas Z4 (≥ 5 min) → pace a intensidad VO2max
3. Ritmo Umbral Z3 (≥ 15 min) → pace de umbral
4. Zona 2 larga → eficiencia aeróbica base

**Conversión a score:**
```
score_running = tabla_estandar(pace_mejor_fuente_disponible, género, edad, distancia_referencia)
```

### Desglose del Score Running

```
Score Running
├── Velocidad / VO2max   →  Series Largas Z4 (o Test)
├── Umbral               →  Ritmo Umbral Z3
└── Base aeróbica        →  Zona 2 larga
```

Mismo comportamiento que fuerza: si una zona no tiene dato → `—`, no entra al promedio.

---

## Score Híbrido (programas con fuerza + running)

```
Score Total = promedio ponderado(Score Fuerza, Score Running)
```

La ponderación la define el tipo de programa:

| Programa | Peso Fuerza | Peso Running |
|---|---|---|
| Fuerza pura | 100% | — |
| Atleta Híbrido | 50% | 50% |
| Runner con fuerza complementaria | 20% | 80% |
| Running puro | — | 100% |

En la pantalla siempre se muestran los **dos sub-scores** visibles — el Score Total es la síntesis, no el único número.

---

## Vista del atleta

- **Pantalla principal**: Score Total (con `*` si hay grupos/zonas sin datos)
- **Historial**: progreso en 1 mes / 6 meses / 1 año / Todo el tiempo
- **Desglose fuerza**: por grupo muscular → por ejercicio
- **Desglose running**: por zona de esfuerzo (VO2max, umbral, base)
- **Resumen semanal**: comparación vs semana anterior, grupos/zonas que mejoraron o bajaron, si hay registros expirados (>3 meses)

## Vista del coach

- Score de cada cliente en el dashboard
- Velocidad de progreso (mejorando rápido / estancado / bajando)
- Signal de calidad de entrenamiento sin revisar set por set
