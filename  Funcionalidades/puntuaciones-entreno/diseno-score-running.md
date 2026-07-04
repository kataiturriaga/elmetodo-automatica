# Diseño — Score de Running

> **Estado: BORRADOR EN PROGRESO** (brainstorming con Kata, 2026-07-02). Documento vivo: se actualiza a medida que se validan secciones. Al cerrarlo pasa a plan de implementación.

**Objetivo:** construir el Score de Running y su integración en el Score Total para programas híbridos (Atleta), lanzando **fuerza + running juntos**. Hyrox queda aparcado.

---

## Decisiones cerradas

| # | Decisión | Detalle |
|---|---|---|
| D1 | **Misma escala que fuerza** | Running en 0–300, mismos 7 niveles (Principiante→Olímpico). |
| D2 | **Score único desde el día 1** | Baja confianza al principio; el desglose por zonas aparece según haya datos de cada tipo de sesión. |
| D3 | **Motor Opción 1: por zonas + VDOT** | Las 3 zonas funcionan como los grupos musculares (reutiliza el motor de fuerza). Tablas pace→nivel construidas con equivalencias VDOT + curva motivadora (como fuerza). |
| D4 | **Híbrido/Atleta: Total = media ponderada** | Pero **los dos sub-scores (Fuerza y Running) siempre visibles**. El Total es la síntesis, no el único número. |
| D5 | **Hyrox / programas por bloques: sin score** | Se entrenan igual; en puntuaciones muestran "no disponible para este programa". No se toca el catálogo. |
| D6 | **Zona se lee del nombre del ejercicio** | Los ejercicios de running siempre nombran la zona ("Zona 2", "Zona 3"…) → clasificación fiable, sin clasificador frágil. |
| D7 | **Número único = zonas ponderadas por calidad** | VO2max/Umbral pesan más que Base (un Z2 suave es la señal más ruidosa). No es promedio simple. Pesos exactos a calibrar. |
| D8 | **Test = ancla del número global + rellena huecos del desglose** | Si hay Test válido en la ventana, ancla el Score Running (alta confianza). En el desglose, cada zona muestra su sesión real; si una zona no tiene dato real, se rellena con la estimación VDOT del Test **marcada "~ estimado"**. |

## Arquitectura

```
Score Total
├── Score Fuerza    (motor actual: 7 grupos → mediana)
└── Score Running   (motor NUEVO: 3 zonas → combinación)
        ↑ ambos en 0–300, mismos niveles

Tipo de programa (vía objective_score_types, ya existe) decide qué se muestra:
  fuerza puro    → solo Score Fuerza
  running puro   → solo Score Running
  híbrido/Atleta → Total = media ponderada(Fuerza, Running) + ambos sub-scores visibles
  hyrox/bloques  → sin score
```

## Datos de entrada por zona

- Cada sesión de carrera = un `UserExerciseLog` (tiempo↔distancia). Mejor registro de los **últimos 90 días** (misma ventana que fuerza).
- **Zona: se lee del nombre del ejercicio** (Zona 1/2/3/4).
- `pace = tiempo_total / distancia` [min/km] por sesión → mejor pace por zona.

**Mapeo de zonas del programa → zonas de score:**

| Zona del programa | → Zona de score |
|---|---|
| Zona 1 (recuperación) | **se ignora** (no puntúa) |
| Zona 2 (rodaje fácil) | **Base aeróbica** |
| Zona 3 (umbral) | **Umbral** |
| Zona 4 (VO2max / series) | **Velocidad / VO2max** |
| (Zona 5 no existe) | — |

**Fuente especial:** sesión **Test** (distancia prescrita → registras tiempo) = máxima calidad; da un VDOT directo que ancla la lectura. Sesiones muy cortas (strides) o sin clasificar → no puntúan.

## Motor de cálculo (4 pasos)

1. **Pace por zona**: mejor pace de los últimos 90 días por zona (zona leída del nombre). `pace = tiempo / distancia`.
2. **Pace → nivel de zona (0–300)**: vía VDOT, con tabla por género/edad y curva motivadora (como fuerza).
3. **Score Running (número único) = zonas ponderadas por calidad** (D7): VO2max/Umbral > Base. Con 1 zona → esa (baja confianza). Test → ancla (D8).
4. **Híbrido (Atleta): Score Total = media ponderada(Fuerza, Running)** (D4), pesos de `objective_score_types`. Dos sub-scores siempre visibles.

## Qué necesita el motor para calcular

1. Pace de la sesión (tiempo + distancia del registro). ✅ disponible.
2. Género + edad del usuario. ✅ disponible (perfil/cuestionario).
3. **Tablas de estándares de running** (pace → nivel 0–300, por zona/género/edad), construidas con equivalencias VDOT. ← **dependencia principal a construir** (equivalente a StrengthLevel en fuerza).
4. Mapeo zonas 1–4 → 3 zonas de score. ✅ definido arriba.

---

## Cold-start y confianza

- **Cuándo aparece el número:** mínimo 1 sesión clasificable con pace válido (tiempo + distancia). Por debajo → "aún sin datos de carrera".
- **Nivel de confianza** (independiente del número):

  | Confianza | Cuándo |
  |---|---|
  | Baja | 1 sola zona con datos (arranque: solo Base/Z2) |
  | Media | 2 zonas con datos (incluye Umbral) |
  | Alta | Hay Test válido, **o** las 3 zonas con datos |

  Baja confianza → indicador visible ("provisional"/"~"; forma exacta en pantallas).
- **Caducidad:** solo cuentan registros de los últimos 90 días (como fuerza). Todo caducado → "sin datos recientes"; al volver a correr reaparece en baja confianza.

## Puntos abiertos / pendientes

- [x] ~~Sección 3 — motor de cálculo~~ (D7, D8).
- [x] ~~Cold-start / confianza~~ (arriba).
- [x] ~~Caducidad de registros~~ (90 días).
- [ ] **Sección 5 — tablas de estándares** VDOT por zona/género/edad (fuente + calibración motivadora). *(en discusión — ver "Dónde lo dejamos")*
- [ ] **Diseño de pantallas** — incl. cómo mostrar los dos sub-scores en híbrido/Atleta (D4) y el "~ estimado" del Test (D8).
- [ ] **Testing**.

---

## Dónde lo dejamos (para retomar)

**Parqueado el 2026-07-02** para atender un fix del estado vacío del Score de Fuerza. Retomar por aquí:

**Cerrado:** Secciones 1–4 (alcance, arquitectura, datos por zona, motor de cálculo, cold-start/confianza) → decisiones D1–D8.

**En discusión — Sección 5 (tablas de estándares).** Presentada, faltan 2 respuestas de Kata:
1. **¿Ajustar las tablas por género y edad** (como fuerza, usando age-grading del running)? — recomendación mía: **sí**.
2. **Alcance MVP de las tablas:** ¿las 3 zonas desde el inicio, o arrancar con Base + Umbral y añadir VO2max/Test después? — recomendación mía: **las 3 desde el inicio** (el trabajo grande es montar el método VDOT+age-grading una vez).

**Aún sin empezar:** diseño de pantallas (incl. mostrar los 2 sub-scores en híbrido y el "~ estimado" del Test) y testing. Después: cerrar diseño → `writing-plans` → implementación.
