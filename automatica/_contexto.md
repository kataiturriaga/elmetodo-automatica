# Contexto de trabajo — Automática

> Actualizar al final de cada sesión. Es el punto de partida para la siguiente.

---

## Qué es este proyecto

**Automática** — app de entrenamiento para usuarios finales (free + paid tiers). Modelo económico: % sobre resultados → interés directo en mejorar conversión y retención.

Archivo Figma activo: `App Automatica` — file key `629ryw0MF7hzDxIFiZJ5Un`

---

## Dirección estratégica (junio 2026)

El Método se reposiciona como **Sistema de Consistencia Deportiva** — deja de competir como app de rutinas para combatir el ciclo inicio→abandono→culpa del mercado hispanohablante. Tres palancas: telemetría para medir el embudo, onboarding con inversión cognitiva progresiva, y ligas sociales como motor principal de retención diaria.

Ver: `automatica/estrategia-posicionamiento-jun2026.md` — contexto completo
Ver: `tareas.md` (raíz) — tareas organizadas en 3 fases

---

## Estado actual (mayo → junio 2026)

### Track 1: Nuevo onboarding (en curso)
Rediseño completo del embudo de conversión. V1 tenía 22 pantallas con problemas graves. V2 tiene 12 pantallas.

**Página Figma:** `auto-onboarding-exploracion` → Section 2

| # | Pantalla | Node ID | Estado |
|---|----------|---------|--------|
| 1 | Hero — "Llega a resultados reales" | `4016:79595` | ✅ |
| 2–7 | Cuestionario 6 preguntas | `4020:79720`+ | ✅ |
| 8 | Tu programa recomendado | `4038:369` | ✅ |
| 9 | Metodología | `4108:31985` | ✅ |
| 10 | Health permissions | `4110:31990` | ✅ |
| 11 | Pricing — 7 días prueba + 3 tiers | `4096:32487` | ✅ |
| 12 | Registration | `4108:31922` | ✅ |

Estado global: **diseñado, pendiente de revisión/validación con Carles**

### Track 2: UX improvements (pausado / según feedback)
Lista completa en `automatica/ux_improvements.md`. Se atacan según feedback real de usuarios, no como lista fija.

Priorizados en su momento (pueden haber cambiado): E3, E4, H9, H10

### Track 3: Analytics / Ranking
- Grupos de ranking: `automatica/08-UPDATES-MAYO/grupos-ranking.md`
- Looker Studio + GA4: 23 eventos pendientes de conexión (estado desconocido, verificar)

---

## Decisiones tomadas
- Notificaciones: **cerradas**, no se trabajan ahora
- UX improvements: se priorizan por feedback real, no por criterio interno
- Onboarding: el registro va **después** del cuestionario (post-sesión), no al inicio

---

## Pendiente
- [ ] Validar nuevo onboarding con Carles
- [ ] Revisar estado analytics / GA4
- [ ] Definir siguiente ronda de UX improvements según feedback recibido

---

## Archivos de referencia
- `automatica/ux_improvements.md` — análisis UX completo (Home + flujo Entreno)
- `automatica/08-UPDATES-MAYO/nuevo-onboarding.md` — spec del nuevo flujo
- `automatica/08-UPDATES-MAYO/grupos-ranking.md` — propuesta grupos ranking
- `plan-trabajo-abr-mayo.md` (raíz) — plan general de los dos tracks
