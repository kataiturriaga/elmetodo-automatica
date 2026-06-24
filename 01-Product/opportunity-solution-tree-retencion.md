# Opportunity Solution Tree — Retención / Consistencia

> **Outcome:** aumentar el % de usuarios que entrenan **≥2 veces/semana** y la **retención a 30 días**.
> **Método:** OST (Teresa Torres). Oportunidades ancladas en **1.424 reseñas reales** de competidores de fuerza/gym usados en España.
> **Fecha:** junio 2026. Relacionado: [north-star.md](north-star.md) · [estrategia-posicionamiento-jun2026.md](estrategia-posicionamiento-jun2026.md) · [gravl-analisis-competitivo.md](gravl-analisis-competitivo.md)

---

## 0. Evidencia y su método (trazabilidad)

| App | Reseñas | Fuente | Por qué la elegimos |
|-----|--------:|--------|---------------------|
| Hevy | 500 | App Store ES (RSS) | Logger de gym top en España, eje racha/social |
| AimHarder 🇪🇸 | 690 | App Store ES + Google Play ES | App española de programación de entrenos |
| Symmetry | 172 | App Store ES | "Workout log con IA", racha estilo Duolingo |
| Fitbod | 62 | App Store ES | Rutinas por IA (competidor directo tipo Gravl) |
| **TOTAL** | **1.424** | `country=es` → reseñas del mercado español | |

**Caveat honesto (leer antes de usar el árbol):**
- Las reseñas de store están **sesgadas a positivo**. La lente literal de abandono (*"lo dejé porque…"*) solo cazó **4/1.424**: quien abandona borra la app sin reseñar. → La señal de retención es **indirecta**: medimos qué hace *volver* (pull) y qué frustra *al empezar*.
- Los **bugs** (112 menciones, casi todas de AimHarder: crashes, cierre de sesión) son **ruido** según la regla del teardown de Gravl: son parcheables y específicos de esa app, no un hueco de producto. Se excluyen del árbol salvo donde rompen el hábito.
- Solo App Store ES (+ Google Play AimHarder). Señal direccional, no cifra cerrada.

### Temas detectados (nº de reseñas que los tocan)

| Tema | Reseñas | Reparto |
|------|--------:|---------|
| Progreso visible | 246 | Hevy 120 · AimHarder 97 · Symmetry 21 · Fitbod 8 |
| Facilidad de empezar/usar | 184 | AimHarder 90 · Hevy 77 · Symmetry 15 |
| (Bugs — ruido) | 112 | AimHarder 81 · Symmetry 20 |
| Muro de pago | 91 | Hevy 54 · Symmetry 18 · AimHarder 12 |
| Social / competición | 88 | Hevy 39 · AimHarder 35 · Symmetry 11 |
| Motivación / enganche | 56 | Hevy 40 · Symmetry 7 |
| Racha / constancia | 54 | Hevy 23 · AimHarder 21 · Symmetry 7 |
| Rigidez / culpa | 27 | Hevy 10 · AimHarder 8 |
| Aburrimiento / variedad | 16 | Hevy 11 |

---

## 1. Oportunidades (en lenguaje del usuario)

Cada una sale de citas reales. Priorización con **Opportunity Score = Importancia × (1 − Satisfacción)** (0–1).

| # | Oportunidad (cómo lo vive el usuario) | Imp. | Satisf. | **Score** | Evidencia (citas) |
|---|----------------------------------------|-----:|--------:|----------:|-------------------|
| **O1** | *"Quiero que se premie mi constancia con una racha — pero sin sentirme castigado/culpable cuando fallo un día."* | 0.85 | 0.30 | **0.60** | *"la motivación de la racha estilo duolingo"* (Symmetry 5★) · *"me obliga a subir resultados cuando no quiero"* (AimHarder 1★) · *"recomendada para quienes se exigen más cada día"* |
| **O2** | *"No quiero entrenar solo: ver a mis amigos y compararme me empuja a volver."* | 0.80 | 0.30 | **0.56** | *"falta que puedas agregar amigos y ver sus actividades, como en Strava"* (Symmetry 3★) · *"su apartado social y mensajes motivacionales han hecho que vuelva al ejercicio"* (Hevy 5★) · *"poder compararte con otra gente da mucha motivación y ganas de seguir"* |
| **O3** | *"Necesito VER que progreso — si no veo avance, pierdo la razón de volver."* | 0.90 | 0.50 | **0.45** | *"ver las mejoras al momento"* (Hevy 5★) · *"a parte de ver tu progreso te motiva a subir de rango"* (Symmetry 4★) · *"la funcionalidad de ver el histórico es muy mejorable"* (AimHarder 2★) |
| **O4** | *"Quiero poder retomar y empezar sin fricción ni mil opciones."* | 0.70 | 0.50 | **0.35** | *"demasiadas opciones en cada pantalla, poco intuitiva"* (AimHarder 3★) · *"intuitiva y fácil, se hace fácil"* (Hevy 5★) |
| **O5** | *"No quiero chocar con un muro de pago antes de sentir el valor."* | 0.60 | 0.40 | **0.36** | *"típica app que o pagas o no puedes ni abrirla para ojear"* (Fitbod 1★) · *"está en la lista de gratis y te cobran un plan, mentirosos"* (Symmetry 1★) · *(contraste)* *"impresionante todo lo que da GRATIS"* (Hevy 5★) |

> *Importancia* = cuánto mueve el outcome de retención. *Satisfacción* = qué bien lo resuelve hoy el mercado/El Método para nuestro usuario.

**Validación estratégica:** las 3 oportunidades top (**O1 racha sin culpa, O2 social, O3 progreso**) coinciden casi 1:1 con tu apuesta del *Sistema de Consistencia Deportiva* (anti-culpa, ligas, XP). El mercado confirma el ángulo: la gente **pide** estas cosas en las reseñas.

---

## 2. El árbol (foco en las 3 oportunidades top)

```
                      ⭐ OUTCOME
        ↑ % usuarios entrenando ≥2×/sem  +  retención 30 días
                          │
      ┌───────────────────┼───────────────────────┐
   O1 Racha SIN culpa   O2 No entrenar solo    O3 Ver que progreso
   (score 0.60)         (score 0.56)           (score 0.45)
      │                    │                       │
   ┌──┴──┐            ┌────┴────┐             ┌─────┴─────┐
  S1a S1b S1c       S2a S2b S2c             S3a S3b S3c
```

---

## 3. Soluciones (3+ por oportunidad — trío PM / Diseño / Ingeniería)

### O1 · Racha que premia constancia sin castigar el fallo
- **S1a — Streak freeze / "día de descanso" automático** *(PM):* 1–2 congeladores de racha al mes; si fallas, no pierdes la racha, la "proteges". Datos de tu propio research: +48–62% duración de racha. Anti-culpa por diseño.
- **S1b — Racha por semana, no por día** *(Diseño):* el objetivo es "≥2 entrenos esta semana", no "todos los días". La barra es semanal → fallar un día no rompe nada. Encaja con el outcome (≥2×/sem).
- **S1c — Mensaje de re-enganche empático, no culpabilizador** *(PM/Copy):* tras 1 día perdido, push tipo *"un día menos no borra tu progreso, ¿seguimos?"* en vez de *"¡has roto tu racha!"*.
- **S1d — Nunca forzar acciones** *(Ing):* quitar obligaciones tipo "tienes que subir resultados" (queja real de AimHarder). Registrar es opcional, no un peaje.

### O2 · No entrenar solo (social / comparación)
- **S2a — Liga/grupo cerrado de ≤30 personas con nivel similar** *(PM):* modelo Duolingo de tu estrategia. Ranking semanal con democión como disparador de cierre de semana.
- **S2b — Añadir amigos + ver su actividad (estilo Strava)** *(Diseño):* lo piden literalmente ("como en Strava"). Feed simple de "tu amigo entrenó hoy".
- **S2c — Retos colectivos (friend quests)** *(PM):* desafío semanal de grupo donde el éxito depende de todos → corresponsabilidad.
- **S2d — Rangos/insignias comparables** *(Ing):* "subir de rango" sale citado como motivador puro. Rango por músculo o global.

### O3 · Ver que progreso (el motor que ya domina Hevy)
- **S3a — Resumen visual de progreso post-entreno** *(Diseño):* al cerrar la sesión, "esta semana levantaste X% más / 2/2 entrenos hechos". Refuerzo inmediato.
- **S3b — PRs y récords personales con celebración** *(PM):* "te aviso cuando rompes una marca" es de las cosas más alabadas de Hevy. Notificación de PR = chute de dopamina que hace volver.
- **S3c — Histórico fiable y a un toque** *(Ing):* la queja de AimHarder es histórico "muy mejorable". Es higiene: si el progreso no se ve fácil, no retiene.
- **S3d — Progreso de *consistencia*, no solo de pesos** *(PM):* gráfico de "semanas consistentes seguidas" → alinea el progreso visible con tu North Star (USC).

---

## 4. Experimentos (para las soluciones más prometedoras)

> Preferir experimentos con *skin in the game* sobre opiniones. Cada uno: hipótesis · método · métrica · umbral.

### E1 — Racha semanal con freeze (valida O1 · S1a+S1b)
- **Hipótesis:** una racha *semanal* con 1 freeze/mes sube la proporción de usuarios que entrenan ≥2×/sem vs. una racha diaria clásica.
- **Método:** A/B en un segmento de usuarios activos durante 4 semanas. A = racha diaria; B = racha semanal + freeze.
- **Métrica:** % de usuarios con ≥2 entrenos/sem sostenido 3 de 4 semanas.
- **Umbral de éxito:** B supera a A en ≥10 pp (relativo) sin caída de satisfacción.

### E2 — Liga de ≤30 personas (valida O2 · S2a)
- **Hipótesis:** meter a usuarios nuevos en una liga semanal pequeña sube la retención D30 vs. sin liga.
- **Método:** pintar el ranking como núcleo del Home para una cohorte; cohorte de control sin liga. (Hoy "el ranking está enterrado bajo el anillo de pasos" — *estrategia jun 2026*.)
- **Métrica:** retención D30 + % que abren ranking ≥3 días/sem (palanca P2 del North Star).
- **Umbral:** retención D30 de la cohorte con liga ≥ +8 pp.

### E3 — Notificación de PR / récord (valida O3 · S3b) — *barato, primero*
- **Hipótesis:** una notificación celebrando un récord personal aumenta el regreso a la siguiente sesión.
- **Método:** activar push de PR a la mitad de los usuarios; medir vuelta en 72 h. Experimento de bajo coste → empezar por aquí.
- **Métrica:** % que abre la app y entrena dentro de 72 h tras el PR.
- **Umbral:** grupo con push ≥ +15% (relativo) de retorno a sesión.

---

## 5. Qué NO atacar (decisiones explícitas)
- **Bugs/estabilidad como estrategia:** ruido parcheable (era el 80% de las quejas de AimHarder). Higiene de ingeniería, no oportunidad de discovery.
- **Muro de pago agresivo temprano (O5):** importa, pero es palanca de *activación/conversión*, no el corazón de la retención post-activación. Vive mejor en el árbol del embudo ([embudo-actualizado.md](embudo-actualizado.md)). Aquí queda registrada, no priorizada.
- **Variedad de ejercicios (16 menciones):** señal débil; table-stakes, no diferenciador.

---

## 6. Próximos pasos (discovery es continuo, no lineal)
- [ ] Empezar por **E3** (notificación de PR): el más barato, valida O3.
- [ ] Conseguir señal de churn *real* (la que las reseñas no dan): encuesta de 1 pregunta al desinstalar o a usuarios inactivos 14 días → *"¿por qué dejaste de entrenar?"*.
- [ ] Revisar el árbol cada semana con datos de los experimentos; matar soluciones que no validen.
- [ ] Datos crudos de las reseñas: `reviews_appstore_es.csv` (1.024) + `reviews_gplay_es.csv` (400). *(Hoy en scratchpad temporal — decidir si se versionan en el repo.)*
