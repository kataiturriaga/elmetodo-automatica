# Embudo actualizado — Automática

> Embudo de conversión vigente (mayo 2026 en adelante). Sustituye al modelo antiguo basado en `Installs → activación` con entrada sin registro.
> Relacionado: [north-star.md](north-star.md) · [08-UPDATES-MAYO/nuevo-onboarding.md](08-UPDATES-MAYO/nuevo-onboarding.md)

---

## El embudo nuevo

```
   CUESTIONARIO  →  REGISTRO  →  PRUEBA  →  PAGO
   (6 preguntas)    (cuenta)     (trial)    (suscripción)
```

A diferencia del modelo antiguo, **ya no se entra a la app sin registrarse**. Todo el mundo pasa primero por el cuestionario de 6 preguntas (inversión cognitiva / efecto IKEA), y el registro ocurre tras la metodología y el pricing. Los antiguos "invitados" (`zone0_guest`) son población heredada y **no forman parte de este flujo**.

---

## Etapas, definición y fuente del dato

El onboarding nuevo está instrumentado en GA4 con una familia de eventos `onboarding_*` (activo desde **11-may-2026**).

| Etapa | Qué mide | Evento GA4 | Fuente |
|-------|----------|------------|--------|
| **1. Inició** | Abre el onboarding | `onboarding_started` | GA4 |
| **2. Cuestionario** | Responde / completa las 6 preguntas y recibe programa | `onboarding_answer_selected` · `onboarding_recommendation_fetched` | GA4 |
| **3. Paywall** | Ve el pricing | `onboarding_paywall_viewed` | GA4 |
| **4. Registro** | Crea cuenta | `onboarding_register_success` | GA4 (flujo) · API (stock) |
| **5. Pago** | Paga / inicia trial | `onboarding_purchase_completed` | GA4 (flujo) · API (stock) |

> GA4 mide el **flujo** (conversión de cada cohorte que entra al onboarding). La API mide el **stock** acumulado (cuántos hay registrados / han pagado en total). Son dos lentes distintas — no cuadran porque miden cosas distintas.

---

## Foto de datos reales

### A) Flujo del onboarding nuevo — GA4, cohorte desde 11-may-2026 (n=193)

| Etapa | Usuarios | % de los que inician |
|-------|----------|----------------------|
| Inició onboarding | 193 | 100% |
| Respondió cuestionario | 78 | 40% |
| Completó cuestionario (recibió programa) | 60 | 31% |
| Vio el paywall | 50 | 26% |
| **Se registró** | **51** | **26%** |
| **Pagó / inició trial** | **16** | **8,3%** |

**Conversiones clave:** cuestionario→registro **26%** · registro→pago **31%** · inicio→pago **8,3%**.

### Drop-off por paso (los 15 pasos, base welcome=196)

Eventos y orden según [onboarding_flow.md](onboarding_flow.md) (fuente canónica).

| Paso | Usuarios | % | Caída |
|------|----------|---|-------|
| 1 Welcome | 196 | 100% | |
| **2 Vídeo intro** | 105 | 54% | **🔴 −46%** |
| 3 Datos personales | 98 | 50% | −7% |
| **4 Objetivo** | 61 | 31% | **🔴 −38%** |
| 5–12 (resto quiz + registro) | ~62 | ~32% | estable |
| 13 Salud | 53 | 27% | −15% |
| 14 Paywall | 52 | 27% | |
| → Pago | 18 | 9% | −65% |

🔴 **Toda la sangría está en los pasos 1–4.** Pasado el Objetivo (step 4), casi todos completan el cuestionario y se registran. Los dos tapones a atacar primero:
1. **Welcome → Vídeo intro: −46%** (casi la mitad se va en la primera pantalla).
2. **Datos personales → Objetivo: −38%** (dan género+edad y abandonan).

> Muestra pequeña (n≈196). Tratar como señal direccional, no como cifra cerrada.

### B) Stock acumulado — API `/dashboard/subscriptions/overview` (18-jun-2026)

| | Valor |
|-------|-------|
| Registrados (histórico) | 542 |
| Pagaron alguna vez (`has_ever_subscribed`) | 38 (≈7,0%) |
| Pagando ahora | 7 · **MRR 69,98 €** |

Aparte (no parte del embudo nuevo): **2.113 "invitados"** (`zone0_guest`) heredados del embudo antiguo.

---

## El campo que distingue Automática

Cada usuario de Automática trae, en el endpoint de suscripciones:

- **`access_level`** → `zone0_guest` (heredado) · `zone1_trial` · `zone2_subscriber`
- **`dashboard_cohort`** → `guest` · `registered_no_activity` · `trial_active` · `blocked_recent` · `blocked_stale` · `subscriber`
- **`has_ever_subscribed`** → booleano = "alguna vez pagó"
- **`is_guest`**, **`created_at`** (permite excluir cohortes por fecha, p. ej. el sorteo del coche de abril 2026)

En **asesorías** el modelo es distinto (`subscription_status` active/paused/cancelled + coach). Ese es el campo que separa los dos productos.

---

## Pendiente

- [x] ~~Conectar en GA4 la conversión cuestionario → registro~~ → hecho: instrumentado con eventos `onboarding_*`.
- [ ] **Atacar la fuga bienvenida → 1ª pregunta** (−60%): es la mayor pérdida del embudo.
- [ ] Esperar a más volumen (n=193 es muestra pequeña) antes de fijar metas sobre estas conversiones.
- [ ] Decidir si excluir la cohorte del sorteo (abril 2026) del stock de la API, vía `created_at`.
