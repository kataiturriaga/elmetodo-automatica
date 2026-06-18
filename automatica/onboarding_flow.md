# Onboarding — Flujo actual y eventos

> **Fuente:** rama `feat/new-onboarding-flow` (nuevo onboarding de Automática, 15 pantallas).
> En `main` todavía vive el embudo v1 (welcome + home preview); este documento describe el flujo **nuevo**.
> Implementación: `lib/features/onboarding/presentation/screens/onboarding_stepN_*.dart`.

---

## 1. Flujo de navegación

Cada pantalla usa `context.go(...)` (reemplaza, no apila). El flujo es lineal con botón "atrás" entre los pasos del cuestionario.

```
Cold start (primer arranque)
        │
   1. Welcome ───────(“Ya tengo cuenta”)──────────────► /login
        │ CTA
   2. Vídeo intro
        │
   3. Datos personales (género + edad)
        │
   4. Objetivo ◄────────────┐
        │                   │ (atrás)
   5. Prueba social ◄───────┤
        │                   │
   6. Tipo de entreno ◄─────┤
        │                   │
   7. Dónde entrenas ◄──────┤
        │                   │
   8. Nivel ◄───────────────┤
        │                   │
   9. Días por semana ◄─────┤
        │                   │
  10. Programa recomendado ─┘  (llamada al backend de recomendación)
        │
  11. Metodología (“El Método no es solo entrenar”)
        │
  12. Registro (Google / Apple / Email)
        │
  13. Permisos de salud (“Activa tu cuentapasos”)
        │
  14. Paywall (PaywallScreen, entryPoint=onboarding)
        │
  15. Notificaciones ──────► Home  (dispara onboarding_completed)
```

- **Steps 1–9:** locales (recogen respuestas del cuestionario, persistidas en `OnboardingState`).
- **Step 10:** consulta al backend (`program_recommendation_request/response`) para recomendar programa.
- **Step 14:** reutiliza `PaywallScreen` con `PaywallEntryPoint.onboarding` (no es una pantalla propia).
- **Resume:** si la app se cierra a media, el router reanuda en el step guardado y dispara `onboarding_resumed` ([app_router.dart](../lib/core/router/app_router.dart)).

---

## 2. Eventos genéricos (presentes en casi todos los pasos)

| Evento | Cuándo | Parámetros clave |
|---|---|---|
| `onboarding_started` | Solo en step 1, al montar | `entry_point` (`cold_start`) |
| `onboarding_step_viewed` | Al montar cada pantalla | `step` (nº), `step_name` |
| `onboarding_step_completed` | Al pulsar el CTA / avanzar | `step`, `step_name`, `time_on_screen_ms` |
| `onboarding_step_skipped` | Al saltar (login, omitir permiso) | `step`, `step_name` |
| `onboarding_answer_selected` | Al elegir respuesta del cuestionario | `field`, `value` |
| `onboarding_completed` | Al terminar (desde step 15) | `total_time_ms`, `health_granted`, `notifications_granted`, `program_selected` |
| `onboarding_resumed` | Al reanudar tras cierre | `step` |

> Todos los nombres se emiten en `snake_case` (la conversión la hace `AnalyticsEventExtension.analyticsName`).

---

## 3. Eventos por paso

| # | Pantalla (`step_name`) | Archivo | Eventos disparados | Parámetros / notas |
|---|---|---|---|---|
| 1 | Welcome (`welcome`) | `onboarding_step1_welcome_screen.dart` | `onboarding_started`, `onboarding_step_viewed`, `onboarding_step_completed`, `onboarding_step_skipped` | `step_skipped` → va a `/login`; `started` con `entry_point: cold_start` |
| 2 | Vídeo intro (`video`) | `onboarding_step2_video_screen.dart` | `onboarding_step_viewed`, `onboarding_step_completed` | CTA "Vamos" |
| 3 | Datos personales (`personal_info`) | `onboarding_step3_personal_info_screen.dart` | `onboarding_step_viewed`, `onboarding_answer_selected` ×2, `onboarding_step_completed` | `answer_selected` con `field: gender` (`value`=nombre) y `field` edad (`value`=edad) |
| 4 | Objetivo (`goal`) | `onboarding_step4_goal_screen.dart` | `onboarding_step_viewed`, `onboarding_answer_selected`, `onboarding_step_completed` | `field: goal`, `value/goal: goal.id` |
| 5 | Prueba social (`social_proof`) | `onboarding_step5_social_proof_screen.dart` | `onboarding_step_viewed`, `onboarding_step_completed` | Testimonios por género/edad |
| 6 | Tipo de entreno (`objective`) | `onboarding_step6_objective_screen.dart` | `onboarding_step_viewed`, `onboarding_answer_selected`, `onboarding_step_completed` | `field: objective` (objetivo y sub-objetivo) |
| 7 | Dónde entrenas (`training_place`) | `onboarding_step7_training_place_screen.dart` | `onboarding_step_viewed`, `onboarding_answer_selected`, `onboarding_step_completed` | `answer_selected` por cada card |
| 8 | Nivel (`experience`) | `onboarding_step8_experience_screen.dart` | `onboarding_step_viewed`, `onboarding_answer_selected`, `onboarding_step_completed` | Principiante / Avanzado |
| 9 | Días por semana (`days`) | `onboarding_step9_days_screen.dart` | `onboarding_step_viewed`, `onboarding_answer_selected`, `onboarding_step_completed` | 2 / 3 / 4 / 5 |
| 10 | Programa recomendado (`program`) | `onboarding_step10_program_screen.dart` | `onboarding_step_viewed`, `onboarding_recommendation_fetched`, `onboarding_program_selected`, `onboarding_step_completed`, `onboarding_step_skipped` | `recommendation_fetched`: `primary_program_id`, `alternative_program_id`, `latency_ms`, `had_error`. `program_selected`: `program_id`, `is_alternative` |
| 11 | Metodología (`methodology`) | `onboarding_step11_methodology_screen.dart` | `onboarding_step_viewed`, `onboarding_step_completed` | "El Método no es solo entrenar" |
| 12 | Registro (`register`) | `onboarding_step12_register_screen.dart` | `onboarding_step_viewed`, `onboarding_register_attempt`, `onboarding_register_success`, `onboarding_register_failed` | `attempt/success/failed` con `method` (`google`/`apple`/`email`); `success` añade `time_on_screen_ms`; `failed` añade `error_message` |
| 13 | Permisos de salud (`health`) | `onboarding_step13_health_screen.dart` | `onboarding_step_viewed`, `onboarding_health_granted`, `onboarding_health_skipped`, `onboarding_step_skipped` | "Activa tu cuentapasos" |
| 14 | Paywall (`onboarding`) | `onboarding_step14_paywall_screen.dart` → `PaywallScreen` | `onboarding_paywall_viewed`, `onboarding_purchase_completed`, `onboarding_purchase_cancelled`, `onboarding_purchase_failed` | Eventos disparados dentro de [paywall_screen.dart](../lib/features/subscription/presentation/screens/paywall_screen.dart) cuando `entryPoint == onboarding` |
| 15 | Notificaciones (`notifications`) | `onboarding_step15_notifications_screen.dart` | `onboarding_step_viewed`, `onboarding_notifications_granted`, `onboarding_notifications_skipped`, `onboarding_step_skipped` | Al terminar → `completeOnboarding()` dispara `onboarding_completed` y navega a Home |

---

## 4. Catálogo completo de eventos (enum `AnalyticsEvent`, sección "New Onboarding Flow")

```
onboarding_started
onboarding_step_viewed
onboarding_step_completed
onboarding_step_skipped
onboarding_answer_selected
onboarding_recommendation_fetched
onboarding_program_selected
onboarding_register_attempt
onboarding_register_success
onboarding_register_failed
onboarding_paywall_viewed
onboarding_purchase_completed
onboarding_purchase_failed
onboarding_purchase_cancelled
onboarding_health_granted
onboarding_health_skipped
onboarding_notifications_granted
onboarding_notifications_skipped
onboarding_completed
onboarding_resumed
```

Definidos en [analytics_service.dart](../lib/core/analytics/analytics_service.dart). Son un set **nuevo e independiente** del embudo v1 (`onboarding_start/complete/skip` y `training_onboarding_*`), que siguen existiendo para el flujo viejo.

---

## 5. Embudo de conversión (resumen para análisis)

Secuencia esperada de un usuario que convierte:

```
onboarding_started
  → onboarding_step_viewed (×15)
  → onboarding_answer_selected (steps 3,4,6,7,8,9)
  → onboarding_recommendation_fetched + onboarding_program_selected (step 10)
  → onboarding_register_attempt → onboarding_register_success (step 12)
  → onboarding_health_granted (step 13)
  → onboarding_paywall_viewed → onboarding_purchase_completed (step 14)
  → onboarding_notifications_granted (step 15)
  → onboarding_completed
```

Puntos de caída clave a vigilar: salto en step 1 (`onboarding_step_skipped` → login), error de recomendación (`had_error: true` en step 10), fallo de registro (step 12) y abandono del paywall (`onboarding_purchase_cancelled`, step 14).
```
