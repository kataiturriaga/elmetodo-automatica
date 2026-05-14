# Brief para prototipar pantallas — Sistema de Puntuación

Este documento recoge todo el contexto necesario para prototipar las pantallas del sistema de puntuación de entrenamiento. No es un spec técnico — es un brief de diseño.

---

## Qué es el sistema

Un score numérico que refleja el rendimiento del atleta a lo largo del tiempo. Tiene dos dimensiones: **fuerza** y **running**. Todos los programas generan ambas dimensiones, pero con distinta cobertura según el tipo de programa.

Tiene dos audiencias:
- **Atleta**: motivación, progreso personal, comparativa en el tiempo
- **Coach**: señal de calidad de entrenamiento de cada cliente sin revisar set a set

---

## Estructura del score

```
Score Total
├── Score Fuerza
│     └── por grupo muscular → por ejercicio
└── Score Running
      └── por zona de esfuerzo (VO2max, Umbral, Base aeróbica)
```

El Score Total es el promedio ponderado de los dos sub-scores. La ponderación depende del programa:

| Programa | Peso Fuerza | Peso Running |
|---|---|---|
| Fuerza pura | 100% | — |
| Runner 10K / 21K | ~20% | ~80% |
| Atleta Híbrido | 50% | 50% |

---

## Regla de datos faltantes

Si un grupo muscular o zona de running no tiene registros en los últimos 3 meses:
- Muestra `—` en el desglose
- **No entra al cálculo** del promedio
- El score total lleva `*` con nota: "basado en X de 7 grupos" o "X de 3 zonas"

---

## Niveles

Los mismos para fuerza y running:

| Nivel | Rango | Color |
|---|---|---|
| Principiante | 0–49 | Verde |
| Novato | 50–99 | Naranja |
| Experimentado | 100–149 | Azul |
| Pro | 150–199 | Morado |
| Atleta | 200–249 | Rojo |
| Élite | 250–299 | Negro |
| Olímpico | 300+ | Dorado |

---

## Cobertura por tipo de programa

Qué grupos/zonas tienen datos según el programa que sigue el atleta:

### Fuerza pura (Cuerpo definido, Cuerpo construido)
```
Score Total = Score Fuerza (100%)

Score Fuerza:
  Pectorales       ✓
  Espalda          ✓
  Hombros          ✓
  Cuádriceps       ✓
  Isquiotibiales   ✓
  Bíceps           ✓
  Tríceps          ✓

Score Running:     — (no aplica)
```

### Runner 10K Pro
```
Score Total = Fuerza 20% + Running 80%

Score Fuerza (complementaria):
  Cuádriceps       ✓   (días de fuerza del programa)
  Isquiotibiales   ✓
  Espalda          ✓
  Resto            —

Score Running:
  VO2max           —   (strides de 20s insuficientes)
  Umbral           ✓   (Ritmo Umbral Z3, 18 min)
  Base aeróbica    ✓   (Zona 2 + Fondo Largo)
  
  ⚠️ Score running de baja confianza hasta completar Test 10K
```

### Runner 21K Pro
```
Score Total = Fuerza 20% + Running 80%

Score Fuerza (complementaria):
  Cuádriceps       ✓
  Isquiotibiales   ✓
  Espalda          ✓
  Resto            —

Score Running:
  VO2max           ✓   (Series Largas Z4, ~13 min)
  Umbral           ✓   (Ritmo Umbral Z3, 30 min)
  Base aeróbica    ✓   (Fondo Largo Z2, 125 min)
  
  ✓ Score running fiable desde Fase 2
```

### Atleta Híbrido
```
Score Total = Fuerza 50% + Running 50%

Score Fuerza:
  Pectorales       ✓
  Espalda          ✓
  Hombros          ✓
  Cuádriceps       ✓
  Isquiotibiales   ✓
  Bíceps           ~ (depende del programa)
  Tríceps          ~ (depende del programa)

Score Running:
  VO2max           ✓
  Umbral           ✓
  Base aeróbica    ✓
```

---

## Ejemplos de desglose por programa

### Ejemplo — Fuerza pura

```
Score Total: 187 (Pro)
├── Pectorales    142
│     Press banca         142
│     Press inclinado     118
├── Espalda       201
│     Remo con barra      201
│     Remo mancuerna      189
├── Hombros        —
├── Cuádriceps    165
├── Isquiotibiales 190
├── Bíceps        143
└── Tríceps        —
* Score basado en 5 de 7 grupos
```

### Ejemplo — Runner 21K Pro

```
Score Total: 162
├── Score Fuerza: 148*
│     Cuádriceps      165
│     Isquiotibiales  159
│     Espalda         141
│     Resto            —
│     * 3 de 7 grupos
└── Score Running: 176
      VO2max        180   (Series Largas Z4)
      Umbral        178   (Ritmo Umbral Z3)
      Base aeróbica 170   (Fondo Largo Z2)
```

### Ejemplo — Atleta Híbrido

```
Score Total: 171
├── Score Fuerza: 165
│     Pectorales      142
│     Espalda         201
│     Hombros         158
│     Cuádriceps      165
│     Isquiotibiales  190
│     Bíceps          143
│     Tríceps          —
└── Score Running: 178
      VO2max        180
      Umbral        182
      Base aeróbica 171
```

---

## Pantallas a prototipar

### 1. Pantalla principal del atleta
- Score Total grande + nivel (chip de color)
- Dos bloques: Score Fuerza y Score Running (o solo Fuerza si es programa de fuerza pura)
- Acceso al historial (1 mes / 6 meses / 1 año / Todo)
- CTA para ver desglose completo

### 2. Desglose de Fuerza
- Lista de los 7 grupos musculares con su score (o `—`)
- Toca un grupo → expande los ejercicios con su score individual y el 1RM
- Nota al pie si hay `*`

### 3. Desglose de Running
- Las 3 zonas: VO2max, Umbral, Base aeróbica con su score (o `—`)
- Toca una zona → muestra el dato fuente (tipo de sesión, pace, fecha del mejor registro)
- Nota al pie si hay `*` o advertencia de baja confianza

### 4. Historial
- Gráfico de línea del Score Total a lo largo del tiempo
- Filtro de período: 1 mes / 6 meses / 1 año / Todo
- Posibilidad de ver Fuerza y Running por separado

### 5. Vista coach (dashboard)
- Tabla o lista de clientes con su Score Total
- Indicador de tendencia (↑ mejorando / → estancado / ↓ bajando)
- Drill a cualquier cliente → misma pantalla de desglose del atleta

---

## Datos técnicos clave para el diseño

- **Ventana temporal**: siempre últimos 3 meses. Registros más antiguos no cuentan.
- **1RM**: calculado automáticamente del historial de pesos y reps (fórmula Epley). El atleta no lo introduce.
- **Pace running**: calculado automáticamente de los logs de distancia/tiempo.
- **El atleta no ve fórmulas** — solo ve el número, el nivel y el desglose por grupo/zona.
- **El score es dinámico**: si el atleta deja de entrenar un grupo, su score baja gradualmente conforme los registros salen de la ventana de 3 meses.
