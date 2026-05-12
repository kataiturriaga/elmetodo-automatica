# Pantalla de Revisión — UX Strategy

**Estado:** En progreso — pendiente de respuestas antes de diseñar  
**Fecha inicio:** 2026-05-12  
**Próximo paso:** Responder las 4 preguntas de abajo → diseñar cuestionario → diseñar pantalla de progreso

---

## Contexto

Rediseño de la pantalla de revisión periódica del cliente de asesoría. La pantalla actual (`Progreso`) tiene problemas de jerarquía, solo muestra peso, y las fotos tienen un UX confuso.

Screenshots de referencia: pantalla actual de Diego Martínez (usuario de prueba).

---

## Qué debe mostrar la pantalla

1. Progreso de peso corporal
2. Progreso de % de grasa corporal
3. Fotos de las revisiones (histórico)
4. Cómo cumplió las semanas previas a cada revisión (autopuntuación)
5. Score de actividad calculado por el sistema (entrenos + pasos)

---

## Modelo de datos de una revisión

| Dato | Fuente | Periodicidad |
|------|--------|-------------|
| Peso corporal | Usuario (input manual) | Por revisión |
| % grasa corporal | IA (análisis de fotos) | Por revisión |
| Fotos (3 ángulos) | Usuario (cámara) | Por revisión |
| Autopuntuación de semanas | Usuario (escala 1-5) | Por revisión |
| Score de actividad | Sistema (entrenos + pasos) | Calculado automático |

---

## Orden de diseño decidido

```
1. Definir modelo de datos  ← HECHO (arriba)
      ↓
2. Diseñar cuestionario de revisión  ← PENDIENTE
      ↓
3. Diseñar pantalla de progreso  ← PENDIENTE
```

**Razón:** El cuestionario y la pantalla son dos vistas del mismo modelo de datos. Diseñar la pantalla sin tener el cuestionario cerrado obliga a rediseñarla al añadir body fat % y activity score.

---

## Problemas críticos de la pantalla actual

1. **Gráfica plana** — visualmente comunica "nada ha pasado". Hay que gestionar el estado de datos escasos (pocas revisiones, sin variación).
2. **Fotos con memes encima** — entretenido pero confunde el objetivo de la sección.
3. **Sin jerarquía** — el gráfico, las fotos y el header compiten igual.
4. **Solo peso** — si se añade % grasa corporal, el peso puede estancarse mientras la composición mejora. Mostrar solo peso es potencialmente desmotivante y engañoso.

---

## Preguntas pendientes (responder antes de diseñar)

1. **¿Con qué frecuencia se hace la revisión?** — ¿semanal, quincenal, mensual? Afecta cómo mostrar el historial y los estados de "datos escasos".

2. **¿El cliente ve todas sus revisiones pasadas o solo la última?** — Define si la pantalla es "progreso histórico" o "estado actual".

3. **El activity score del sistema** — ¿sería una nota (ej. 7.5/10) o un cumplimiento porcentual (ej. "completaste 4/5 entrenos")? Cambia cómo visualizarlo y cómo el usuario lo interpreta.

4. **¿El flow de revisión y la pantalla de progreso son la misma sección o separadas?** — ¿El modal/flow de captura empieza desde el botón "TOCA REVISIÓN" y la pantalla es solo visualización, o están integradas?

---

## UX Context

**Usuario objetivo:** Cliente de asesoría — estado emocional mixto: esperanzado pero ansioso. Quiere ver si su esfuerzo está dando resultados.  
**Contexto de uso:** Móvil, en casa, ritual periódico.  
**Insight central:** La revisión es el momento de verdad del coaching. Un mal UX aquí erosiona la confianza en el método aunque los resultados sean buenos.
