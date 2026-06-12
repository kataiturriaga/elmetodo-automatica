# Puntuación de Entrenamiento — Resumen de sesión

Fecha: 2026-06-12 · Estado: Planificación avanzada, listo para auditoría y ejecución.

---

## El problema

Los programas de entrenamiento genéricos compiten solo en contenido (rutinas + vídeos). Una vez que el usuario loguea entrenamientos, ese dato **muere** — no retorna valor al usuario, no diferencia el producto.

**Síntomas:**
- Churn en el free trial (7 días) porque el usuario no ve valor medible de su esfuerzo.
- Sin palanca de diferenciación vs apps genéricas.
- Datos de logs (fuerza, peso, running) se recogen pero se desperdician.

---

## Qué hicimos en esta sesión

### 1. **Visión de producto** (no solo tech)
Escribimos [vision-producto-puntuaciones.md](vision-producto-puntuaciones.md) anclado en tres pilares:
- **Por qué:** diferenciación competitiva (un score serio tipo Gravl que la competencia no tiene).
- **Métrica de éxito:** conversión trial→pago (no genérica retención). Dentro de 7 días.
- **Deseabilidad:** hipótesis basada en datos de competidores (Gravl); sin validación en nuestros usuarios aún.

### 2. **Solución al cold-start**
El score nace vacío, pero **no tiene por qué**: 
- **Sesiones de evaluación** al inicio de cada programa, diseñadas para poblar el score desde el día 1.
- Fuerza: bloque que cubre los 7 grupos musculares con series submáximas (Epley desde la primera sesión).
- Running: test ligero escalado al nivel del programa (no un 10K el día 1).
- Esto hace que el score sea una palanca real para la conversión, no un promedio a los 3 meses.

### 3. **Spec técnico completo** ([puntaciones-entreno.md](puntaciones-entreno.md))
- 7 grupos musculares, 28 ejercicios válidos (barra/mancuerna solo).
- Fórmula Epley, fuerza relativa, tabla de estándares por grupo/género/edad.
- Score de running (pace → estándares VDOT-like), desglose por zona (VO2max / Umbral / Base).
- Árboles de score híbrido y cálculo de cobertura (basado en X de 7 grupos).

### 4. **Plan de implementación** ([tareas-implementacion-puntuaciones.md](tareas-implementacion-puntuaciones.md))
- Desde modelo de datos (estándares, ejercicios válidos) hasta Flutter UI (dos tabs en Entreno: Programa / Puntuaciones).
- Reutilización masiva de lo que ya existe: `marca_value.py` (parsing), `marcas_service.py` (series), `Progress` (peso histórico), `Questionnaire` (demografía).
- Motor de cálculo nuevo (`score_service.py`), endpoints API, Figma specs.

### 5. **Scope al MVP (decisión de producto)**
No construimos el spec entero. Empezamos por:
- **Score de fuerza** (running e híbrido son fase 2).
- **Programas de fuerza pura** (máxima señal, mínima complejidad).
- **Con sesiones de evaluación** para que el score se pueble en el trial.

Esto valida la hipótesis (¿el score mueve la conversión?) con ~40% del trabajo.

### 6. **Prompt para auditoría paralela** ([prompt-auditoria-rutinas.md](prompt-auditoria-rutinas.md))
Agente dedicado (otro chat) está auditando **todos los programas en producción**:
- Qué ejercicios válidos tienen en las primeras sesiones (cobertura de grupos).
- Dónde caben las sesiones de evaluación sin desbaratar la progresión.
- Propuesta de cambios programa por programa.

Este trabajo es crítico: determina si la solución es escalar a todos los programas o si hay conflictos.

### 7. **Bonus: claridad sobre usuarios activos**
Descubrimos cómo rastrear usuarios activos entrenando (via `user_pseudo_id` de GA4 → `firebase_analytics_instance_id` en Postgres):
- Query BigQuery deduplicada para saber cuántos entrenan realmente (había un bug de doble-disparo; un usuario con 228 "sesiones" eran ~50 reales).
- Mapeo a programa + última sesión + nombre/email en la DB.

---

## Siguientes pasos (abiertos)

### Corto plazo (bloqueantes)
- [ ] **Conseguir / construir las tablas de estándares** (fuerza + running). Fuente: Symmetric Strength, Gravl inversa, o datos propios.
- [ ] **Auditoría de programas en prod** (en otro chat): qué ejercicios válidos hay, dónde caben los tests.
- [ ] **Calibrado anti-desmotivación**: framing visual/textual si el primer score es bajo ("punto de partida", progreso rápido).
- [ ] **Decidir sobre bloque de evaluación vs modificar sesiones**: ¿añadimos contenido al inicio o reemplazamos las primeras sesiones?

### Mediano plazo (durante ejecución)
- [ ] Normalizar `muscle_group`/`equipment` en ejercicios (mapeo a los 7 grupos).
- [ ] Flag de "sesión de evaluación" en `training_day_v2`.
- [ ] Motor de cálculo (`score_service.py`, Epley, fuerza relativa, lookup estándares).
- [ ] Endpoints API (`GET /score`, `GET /score/history`).
- [ ] Flutter: dos tabs, Freezed models, Riverpod providers, UI (pantalla principal + desgloses + historial).
- [ ] Figma: specs visuales (mockup actual es reference, hay que validar con diseño real).

### Largo plazo (validación + fases 2)
- [ ] A/B test: cohorte con score vs sin score (metric: conversión trial→pago). Baseline primero.
- [ ] Integración con Ligas (¿el score alimenta el ranking o es vista propia?).
- [ ] Running + híbrido (fase 2, después de validar fuerza).
- [ ] Historial largo (1 mes / 6 meses / 1 año / todo).

---

## Documentación versionada

Todos los docs viven en `automatica/puntuaciones-entreno/`:

| Archivo | Propósito |
|---|---|
| `vision-producto-puntuaciones.md` | Por qué, métrica, deseabilidad, cold-start. |
| `puntaciones-entreno.md` | Spec técnico completo (fórmulas, grupos, algoritmo). |
| `tareas-implementacion-puntuaciones.md` | Desglose end-to-end de tareas (modelos, servicios, API, Flutter, Figma). |
| `prompt-auditoria-rutinas.md` | Prompt para agente paralelo: auditar programas. |
| `RESUMEN-SESION.md` | Este archivo. |

---

## Estado para la próxima sesión

✅ **Decisiones tomadas:** apuesta, métrica, MVP scope, solución cold-start.  
✅ **Documentación lista:** vision, spec, tareas, prompt.  
🔄 **En progreso:** auditoría de programas.  
⏳ **Bloqueantes pendientes:** estándares reales, decisión de contenido.  

**Puedes arrancar ejecución** tan pronto como:
1. La auditoría de programas devuelva insights sobre dónde caben los tests.
2. Se confirme la fuente de estándares (o la decida el equipo).
3. Se resuelva el framing anti-desmotivación con diseño.

El código está listo para escribir. Los bloqueantes son de producto/contenido.
