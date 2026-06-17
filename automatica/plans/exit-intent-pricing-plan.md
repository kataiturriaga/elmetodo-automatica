# Plan de implementación — Exit-Intent Pricing

**Autora:** Kata · **Revisa:** Carles
**Basado en:** [exit-intent-pricing-spec.md](../exit-intent-pricing-spec.md)
**Fecha:** 2026-06-16 (actualizado)
**Repos que se tocan:** `elmetodo_api` (backend) · `elmetodo_app` (Flutter) · App Store Connect

> Este documento es el plan. El código va en los otros dos repos. Aquí solo planificamos.

## ✅ Estado actual (al 2026-06-16)

- **Tiendas:** producto iOS **enviado a revisión** de Apple ⏳ · oferta Android **creada y activada** ✅
- **Backend:** rama `feature/exit-intent-pricing` creada; productos de oferta (iOS + Android) registrados en `PRODUCT_TIER_MAP`. **Sin commit** (pendiente revisión de Carles).
- **Llave `.p8`** (solo iOS "ya pagaron"): **pedida a Carles** ⏳.
- **Pendiente Kata:** pasar el **Base plan ID** y el **Offer ID** (`exit-intent`) de Google Play.
- **Siguiente:** Flutter (botón "De momento no" + modal + compras), iOS y Android.

---

## Idea central

Cuando el usuario cierra el paywall, mostramos un modal con una oferta del trimestral. **El descuento es exclusivo del modal** (no aparece en ningún otro sitio). Para que sea exclusivo de verdad y respete las reglas de Apple, usamos **dos mecanismos según el usuario**:

| Usuario | Mecanismo | ¿Necesita firma del backend? | Producto |
|---------|-----------|------------------------------|----------|
| **Nunca pagó** (`has_ever_subscribed = false`) | **Introductory offer** (Apple la aplica sola) | ❌ No | **`trimestral-oferta`** (producto NUEVO) |
| **Ya pagó alguna vez** (`has_ever_subscribed = true`) | **Promotional offer** (la del spec) | ✅ Sí (llave `.p8`) | Trimestral normal |

**Por qué dos productos / dos vías:** Apple solo deja **una** introductory offer por usuario en todo el grupo de suscripción, y solo a quien **nunca** ha pagado. Por eso:
- A los nuevos les creamos un producto aparte (`trimestral-oferta`) con su intro de 9,99€, que solo ven en el modal → exclusivo y sin firma.
- A los que ya pagaron, Apple no les deja intro → se usa la oferta promocional (que sí firma el backend).

---

## Decisiones tomadas

| Decisión | Elección |
|----------|----------|
| Rama de trabajo (ambos repos) | `feature/exit-intent-pricing` |
| Plataformas | **iOS y Android, juntas en la misma v1** (en paralelo) |
| La oferta | **9,99€ el primer trimestre, luego 19,99€. SIN prueba gratis.** Igual en iOS y Android |
| Copy del modal | **Quitar** el "7 días de prueba gratuita" (la oferta 9,99 NO lleva trial) |
| Usuarios nuevos | iOS: producto `trimestraloffer` + introductory offer (sin firma) · Android: oferta sobre el plan trimestral (sin firma) |
| Usuarios que ya pagaron | iOS: oferta promocional (con firma `.p8`) · Android: oferta con elegibilidad determinada (sin firma) |
| Orden interno (dentro de iOS) | Primero la vía de usuarios nuevos (no depende de la llave), luego la de los que ya pagaron |

---

## Niveles de riesgo (leyenda)

- 🟢 **Bajo** — añade algo nuevo, no toca lo existente. Fácil de deshacer.
- 🟡 **Medio** — zona sensible, depende de algo externo (Apple), o no se prueba del todo en local.
- 🔴 **Alto** — afecta a una pantalla que ven usuarios reales y/o maneja pagos de verdad.

---

## FASE 0 — Configuración en las tiendas (Apple + Google) 🟡

Lo de las tiendas tarda en aprobarse, así que se empieza primero aunque no haya código.

- [x] **Producto creado y enviado a revisión en App Store Connect** ⏳ (esperando aprobación de Apple) — grupo "El Método Premium" (ID `21962380`):
  - **Product ID (CONFIRMADO, escribir EXACTO):** `com.elmetodo.subscription.trimestraloffer`
  - Nombre interno: "Premium Trimestral Oferta"
  - Duración: 3 meses · **Precio normal: 19,99€**
  - Añadirle una **Introductory Offer** tipo *Pay up front* = **9,99€ los 3 primeros meses**
  - Enviar a revisión (Apple lo tiene que aprobar → ⏳ puede tardar). 🟡
  - *Lo hace Kata / quien tenga acceso a App Store Connect.*
- [x] **Oferta Android creada y ACTIVADA en Google Play** ✅ — Product ID `elmetodo_subscription_trimestraloffer`, plan base 3 meses a **19,99€**, oferta **9,99€ primer ciclo** (pago único), eligibility **Developer determined**. ⏳ Falta que Kata pase el **Base plan ID** y el **Offer ID** (`exit-intent`).
- [x] **Precio normal del trimestral: 19,99€** (confirmado por Kata). 9,99€ = 50% real → copy honesto.
- [~] **Llave `.p8` de Apple** (solo para la vía iOS de "ya pagaron"): **ya pedida a Carles** ⏳. Recordar: una `.p8` solo se descarga una vez → mejor recuperar la que el backend ya usa, no crear una nueva. *No bloquea el resto.*
- [x] **Gesto disparador (decidido):** se añade un **botón "De momento no"** explícito en el paywall (Flutter). Al pulsarlo se evalúa `has_ever_subscribed` y se muestra el modal que corresponda.

---

## FASE 1 — Vía "usuarios nuevos" (la rápida, sin firma)

### Backend (`elmetodo_api`) 🟢
1. [x] **Rama `feature/exit-intent-pricing` creada** desde `main`. ✅
2. [x] **Productos registrados** (iOS `com.elmetodo.subscription.trimestraloffer` **y** Android `elmetodo_subscription_trimestraloffer`) → tier `quarterly` en `PRODUCT_TIER_MAP` ([subscription.py:169](../elmetodo_api/app/api/routes/mobile/subscription.py#L169)). ✅ Hecho a propósito **solo** en el mapa interno, NO en `IAP_PRODUCTS`, para que el paywall normal no los muestre (quedan exclusivos del modal). Sin commit aún (pendiente de revisión).
   - Riesgo 🟢 bajo: solo añade un producto reconocido; no toca flujos existentes.

### Flutter (`elmetodo_app`) 🔴
3. Crear rama `feature/exit-intent-pricing` desde `main`.
4. **Construir el modal** `ExitIntentSheet` siguiendo Figma (badge, headline, card, botones). 🟡
5. **Interceptar el cierre del paywall:** si `hasEverSubscribed == false` → mostrar el modal con el producto `trimestral-oferta`. 🔴
6. **"Activar oferta"** → lanzar la compra del producto con el **flujo de compra que ya existe** (`purchaseStream` → `verify-iap`). Apple aplica la intro sola. 🔴
7. **"No gracias"** → cerrar modal + cerrar paywall (flujo normal). 🟢
8. **Analítica:** los 6 eventos del spec. 🟢

> ✅ Esta vía **no necesita** el endpoint de firma ni la llave `.p8`. Se puede probar y lanzar sin Carles.

### Riesgo a vigilar 🟡
Que enseñemos "9,99€" a alguien no elegible y Apple le cobre 19,99€. Mitigación: mostrar el modal **solo a `has_ever_subscribed = false`**, e idealmente comprobar la elegibilidad real con Apple antes de pintar el precio (para eso sí conviene el paquete `in_app_purchase_storekit`, solo para *leer* el precio).

---

## FASE 2 — Vía "usuarios que ya pagaron" (la del spec, con firma)

> Se hace después, cuando tengamos la llave `.p8`. Misma rama.

### Backend (`elmetodo_api`) 🟡
1. **Endpoint** `POST /api/v2/subscription/promotional-offer-signature` en `subscription.py`: firma la oferta con la llave `.p8`. Aislado, no toca lo existente.
2. Probar (necesita la llave). 🟡

### Flutter (`elmetodo_app`) 🔴
3. **Añadir paquete** `in_app_purchase_storekit` al `pubspec.yaml` (necesario para compras con descuento firmado). 🟢
4. Si `hasEverSubscribed == true` → en el modal, "Activar oferta" pide la firma al backend → compra con `SKPaymentDiscountWrapper`. 🔴
5. El `verify-iap` existente recoge la transacción (ya gestiona `offerType = 2` correctamente — verificado en [apple_store_service.py:220](../elmetodo_api/app/services/apple_store_service.py#L220)). 🟢

### Riesgo
🔴 Alto (pantalla real + pagos). Mitigación: todo en **sandbox** primero (`APPLE_IAP_ENVIRONMENT=sandbox`, ya existe) y review de Carles antes de mezclar a `main`.

---

## Probar (en sandbox, antes de publicar)

- [ ] Backend nuevos: el producto `trimestral-oferta` se reconoce en `verify-iap`.
- [ ] App, usuario **nuevo**: cerrar paywall → modal → comprar → entra con trimestral a 9,99€ aplicado.
- [ ] App, usuario **que ya pagó**: cerrar paywall → modal → comprar con oferta promocional → entra.
- [ ] App, "No gracias": cierra y va al app sin cambios.
- [ ] Los 6 eventos de analítica se registran.

---

## Seguridad / cómo deshacer

- Todo vive en la rama `feature/exit-intent-pricing`. **Mientras no se mezcle a `main`, los usuarios reales no ven nada.**
- Si algo falla tras publicar, se revierte la mezcla (Carles) y se vuelve atrás.
- Ningún paso borra ni modifica datos de usuarios existentes.
- El producto nuevo de Apple no afecta a los planes actuales (es uno más en el grupo).

---

## Android / Google Play (DENTRO del scope — añadido 2026-06-16)

> El spec lo dejaba fuera, pero Kata lo metió en scope. Mecánica distinta a iOS, pero **no es el doble de trabajo**.

**Ya montado (verificado):**
- Backend `app/services/google_play_service.py`: ya verifica compras Android, lee ofertas (`offerDetails`/`offerTags`/`basePlanId`) y hace el acknowledge obligatorio. El trimestral Android ya está mapeado (`elmetodo_subscription_quarterly` → quarterly). → Probablemente **sin cambios** para el exit-intent (confirmar al implementar). 🟢
- Flutter: el plugin `in_app_purchase` ya compra productos Android (`purchase_service.dart:18`).

**Falta (nuevo):**
- Google Play Console: crear una **oferta** sobre el plan trimestral existente (en Google la oferta cuelga del plan; NO se crea un producto nuevo como el `trimestraloffer` de iOS), con su elegibilidad (cliente nuevo / determinada por nosotros) y sus fases. 🟡
- Flutter: lanzar esa oferta requiere pasar su **offer token** (`GooglePlayPurchaseParam`) — hoy no se hace. 🔴 (pagos reales → probar en pruebas de Google)

**Diferencias con iOS (a favor de Android):** sin firma `.p8`, sin producto duplicado, y Google permite **combinar** prueba gratis + descuento en una misma oferta.

---

## Fuera de scope (por ahora)

- Lógica de frecuencia (mostrar X veces cada Y días).
- A/B test de precio o copy.
- Sacar a los usuarios nuevos a una web de pago (alternativa más potente pero otro proyecto).
