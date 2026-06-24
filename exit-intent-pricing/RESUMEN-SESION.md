# RESUMEN DE SESIÓN — Exit-Intent Pricing

**Fecha:** 2026-06-16
**Quién:** Kata (PM/diseñadora, no técnica) + Claude
**Contexto:** Carles dio a Kata libertad para pushear código de la feature exit-intent. En esta sesión hemos hecho el plan, tomado decisiones y dejado el primer cambio de código (de bajo riesgo) listo en una rama.

**Documentos relacionados:**
- Spec original: [../exit-intent-pricing-spec.md](../exit-intent-pricing-spec.md)
- Plan de implementación (vivo): [../plans/exit-intent-pricing-plan.md](../plans/exit-intent-pricing-plan.md)
- Diseño Figma: [App Automatica — Section 3](https://www.figma.com/design/629ryw0MF7hzDxIFiZJ5Un/App-Automatica?node-id=4596-116145)

> ⚠️ Este resumen es el punto de retorno. Si retomas en otra sesión, **empieza leyendo esto** y luego el plan.

---

## 1. La feature en una frase

Cuando el usuario cierra el paywall (pulsando un botón nuevo **"De momento no"**), en vez de irse directo al app, le aparece un **modal (bottom sheet)** con una oferta exclusiva del **plan trimestral a 9,99€ el primer trimestre** (luego 19,99€). Si acepta, compra con descuento; si no, entra al app normal.

---

## 2. Estado de un vistazo

| Cosa | Estado |
|---|---|
| Plan escrito y actualizado | ✅ Hecho |
| Decisiones de producto/diseño | ✅ Cerradas (ver sección 3) |
| Backend: rama creada | ✅ `feature/exit-intent-pricing` en `elmetodo_api` |
| Backend: registrar producto nuevo | ✅ Hecho (1 cambio, **SIN commit**) |
| Producto iOS en App Store Connect | ✅ Creado y **enviado a revisión** de Apple ⏳ |
| Oferta Android en Google Play | ✅ **Creada y activada** (eligibility: Developer determined) |
| Llave `.p8` | ✅ Colocada en `elmetodo_api/secrets/` (git la ignora). Es la del servidor (la pasó Carles) → config OK |
| Flutter: botón + modal + compra | 🔜 **No empezado** |
| Backend: endpoint de firma (2ª vía) | 🔜 **No empezado** |
| Android / Google Play | 🆕 **Añadido al scope 2026-06-16** (ver sección 11) |

---

## 3. Decisiones tomadas (con el porqué)

1. **Rama de trabajo:** `feature/exit-intent-pricing` (mismo nombre en los dos repos). *Buena práctica: la rama describe el trabajo, no a la persona. Nunca tocar `main` directamente.*

2. **Enfoque de DOS vías según el usuario** (esto es lo más importante de la sesión):
   - **Usuario que NUNCA pagó** (`has_ever_subscribed = false`) → se le ofrece un **producto nuevo `trimestraloffer`** con una **introductory offer** (Apple le aplica el descuento solo). **NO necesita firma del backend ni la llave `.p8`.**
   - **Usuario que YA pagó alguna vez** (`has_ever_subscribed = true`) → se le ofrece una **oferta promocional** sobre el trimestral normal. **SÍ necesita firma del backend con la llave `.p8`** (es lo que describía el spec original).

3. **Alcance v1:** cubrimos **a los dos** tipos de usuario.

4. **Orden de trabajo:** primero la vía de **usuarios nuevos** (no depende de la llave de Carles, así no nos bloqueamos), luego la de **usuarios que ya pagaron**.

5. **Disparador:** se añade un **botón explícito "De momento no"** en el paywall (hoy NO existe; solo hay una flecha de cerrar). Al pulsarlo se mira `has_ever_subscribed` y se muestra el modal que toque.

6. **Precio:** trimestral normal = **19,99€** (confirmado por Kata). Oferta = **9,99€ el primer trimestre, luego 19,99€**. Así el "Ahorra 50%" es verdad.

7. **Product ID del producto nuevo:** `com.elmetodo.subscription.trimestraloffer` (sigue el patrón de los existentes). **Tiene que ser idéntico, carácter por carácter, en Apple + backend + app.**

8. **El producto nuevo NO se anuncia en el paywall:** se registra solo en el mapa interno del backend, no en la lista de productos pública, para que **solo exista dentro del modal** (exclusividad real).

9. **Plataformas:** iOS **y** Android, **juntas en la misma v1** (en paralelo). *(Android añadido al scope — ver sección 11.)*

10. **La oferta (definitiva):** **9,99€ el primer trimestre, luego 19,99€, SIN prueba gratis**, igual en iOS y Android. Es un gancho de precio (tachado 19,99 → 9,99 = "Ahorra 50%").

11. **Copy del modal:** hay que **quitar** el "7 días de prueba gratuita" que ponía el spec — esa oferta NO lleva prueba gratis (se pagan 9,99€ ya). Texto correcto sugerido: *"Pago único de 9,99€ por los 3 primeros meses · Luego 19,99€/trim. · Cancela cuando quieras"*.

---

## 4. El "por qué técnico" (para no re-descubrirlo en la próxima sesión)

**La regla de Apple que manda todo:** las *introductory offers* son **una por GRUPO de suscripción y de un solo uso por usuario**, y solo para quien **nunca** ha pagado en ese grupo.

- Por eso a los **nuevos** sí les vale: creamos un producto aparte (`trimestraloffer`) con su propia intro de 9,99€, que **solo ven en el modal** → exclusivo y sin firma. Como nunca han pagado, Apple les aplica el descuento.
- Por eso a los que **ya pagaron** NO les vale la intro (Apple no se la aplica → les cobraría 19,99€ del tirón). Para ellos hace falta una **oferta promocional**, que el backend tiene que **firmar** con la llave `.p8`.

**Otras formas que usan otras apps** (descartadas o fuera de scope):
- Mandar al usuario a una **web de pago** (fuera de Apple, máxima libertad, pero es otro proyecto). Fuera de scope.
- Un **producto más barato a precio plano** (sin volver a subir). Descartado porque queremos "9,99 solo el primer trimestre y luego 19,99".

**Lo que YA funcionaba en el backend (verificado, no hay que tocar):** el endpoint `verify-iap` ya distingue las compras promocionales — recibe `offerType = 2` de Apple y marca la compra como "no es prueba gratis" correctamente.

---

## 5. Cambios de código hechos en esta sesión

### Repo `elmetodo_api` (backend) — rama `feature/exit-intent-pricing`

**Archivo:** `app/api/routes/mobile/subscription.py` (después de la línea ~175, junto al mapa de productos)

**Qué hace:** registra el producto nuevo para que, cuando llegue una compra de `com.elmetodo.subscription.trimestraloffer`, el backend la trate como una suscripción **trimestral**. Sin esto, Apple cobraría al usuario pero el backend rechazaría la compra como "producto desconocido" y no daría acceso.

**Diff exacto:**
```diff
 # Also map Android-style IDs
 PRODUCT_TIER_MAP.update({
     "elmetodo_subscription_monthly": "monthly",
     "elmetodo_subscription_quarterly": "quarterly",
     "elmetodo_subscription_yearly": "yearly",
 })
+# Exit-intent offer product: a separate quarterly SKU shown ONLY in the exit-intent
+# modal (com.elmetodo.subscription.trimestraloffer). Grants the quarterly tier just
+# like the regular quarterly. Deliberately NOT added to IAP_PRODUCTS so the /products
+# endpoint (and the normal paywall) never advertises it — it stays exclusive to the modal.
+PRODUCT_TIER_MAP.update({
+    "com.elmetodo.subscription.trimestraloffer": "quarterly",
+})
```

**Estado:** el cambio está en la rama, en el árbol de trabajo, **SIN commit y SIN push**. Falta que Kata/Carles lo revisen antes de commitear.

> Nota: en esa rama también aparecen como modificados `app/api/routes/dashboard/ai_tester.py` y `app/schemas/ai_body_fat.py` — **NO son de esta feature**, son cambios previos de otra persona. No tocarlos ni subirlos.

### Repo `elmetodo_app` (Flutter)
**Sin cambios todavía.** No se ha creado la rama aún (se creará al empezar la parte de Flutter).

---

## 6. Datos clave (para copiar/pegar sin equivocarse)

**App Store Connect:**
- Grupo de suscripción: **"El Método Premium"**, ID `21962380`
- Productos existentes (patrón `com.elmetodo.subscription.X`): `...yearly`, `...quarterly`, `...monthly`
- **Producto a CREAR:**
  - Product ID (exacto): `com.elmetodo.subscription.trimestraloffer`
  - Nombre interno sugerido: "Premium Trimestral Oferta"
  - Duración: 3 meses · Precio normal: **19,99€**
  - Introductory Offer: tipo **Pay up front** = **9,99€ los 3 primeros meses**
  - Enviar a revisión de Apple
- **Oferta promocional (del spec, para la 2ª vía, ya creada en Apple):** reference name `exit-intent`, offer id `001`, producto `com.elmetodo.subscription.quarterly`, 9,99€, tipo "Pay up front for the first 3 months"

**Backend (`elmetodo_api`) — ficheros relevantes:**
- Endpoint de verificación de compras: `app/api/routes/mobile/subscription.py` → `verify-iap` (línea ~178)
- Mapa de productos (donde hicimos el cambio): `subscription.py` líneas ~169-182
- Manejo de `offerType` de Apple: `app/services/apple_store_service.py` (línea ~220)
- Variables de entorno Apple ya configuradas: `app/config/settings.py` (líneas ~156-160): `APPLE_IAP_KEY_ID`, `APPLE_IAP_ISSUER_ID`, `APPLE_IAP_PRIVATE_KEY_PATH` (por defecto `secrets/apple_iap_key.p8`), `APPLE_IAP_ENVIRONMENT` (sandbox/production)
- Campo en BD: `app/models/user.py` → `has_ever_subscribed` (línea ~123)
- ✅ La llave `.p8` está colocada en `elmetodo_api/secrets/apple_iap_key.p8` (git la ignora). Es la misma que el servidor (la pasó Carles) → `APPLE_IAP_KEY_ID` ya coincide, sin cambios.

**Flutter (`elmetodo_app`) — ficheros relevantes:**
- Paywall: `lib/features/subscription/presentation/screens/paywall_screen.dart` (el cierre es un `CircularBackButton` con `context.pop()`, línea ~122)
- Providers / stream de compras: `lib/features/subscription/presentation/providers/subscription_providers.dart` (escucha de compras, línea ~233)
- Servicio de compra: `lib/features/subscription/data/services/purchase_service.dart` (`buyNonConsumable`, línea ~104)
- Datasource remoto (donde añadir la llamada de firma): `lib/features/subscription/data/datasources/subscription_remote_datasource.dart`
- `hasEverSubscribed` ya disponible en la app: `lib/features/subscription/data/models/iap_subscription_status_model.dart` (línea ~20)
- `pubspec.yaml`: `in_app_purchase: ^3.2.0` (línea ~121). **Falta añadir** `in_app_purchase_storekit` (para la 2ª vía y para leer el precio de la intro).
- ⚠️ Histórico: la app fuerza **StoreKit 1** (commits `de60d1a`, `2af2017`). La API de ofertas (`SKPaymentDiscountWrapper`) es de StoreKit 1, así que encaja — confirmarlo al probar.

**Eventos de analítica a registrar (6):** `paywall_skipped`, `exit_intent_shown`, `exit_intent_offer_accepted`, `exit_intent_offer_declined`, `exit_intent_purchase_success`, `exit_intent_purchase_error`.

---

## 7. Qué falta por hacer (pendientes con responsable)

| # | Tarea | Quién | Bloquea a |
|---|-------|-------|-----------|
| 1 | Crear producto `trimestraloffer` + intro offer en App Store Connect y enviar a revisión | **Kata** (acceso Apple) | Probar la vía de nuevos |
| 2 | Conseguir la llave `secrets/apple_iap_key.p8` | **Carles** | Vía "ya pagaron" (firma) |
| 3 | Revisar y commitear el cambio del backend (mapa de producto) | Kata/Carles | — |
| 4 | Flutter: crear rama + botón "De momento no" + modal `ExitIntentSheet` | Próxima sesión | — |
| 5 | Flutter: conectar compra de `trimestraloffer` (vía nuevos) al flujo existente | Próxima sesión | Producto aprobado en Apple |
| 6 | Backend: endpoint `POST /api/v2/subscription/promotional-offer-signature` (firma) | Próxima sesión | Llave `.p8` |
| 7 | Flutter: añadir `in_app_purchase_storekit` + compra con `SKPaymentDiscountWrapper` (vía ya pagaron) | Próxima sesión | Endpoint de firma |
| 8 | Añadir los 6 eventos de analítica | Próxima sesión | — |
| 9 | Probar TODO en sandbox (`APPLE_IAP_ENVIRONMENT=sandbox`) | Próxima sesión | Lo anterior |

---

## 8. Próximos pasos concretos al retomar

1. Comprobar si el producto de Apple ya está **aprobado**.
2. Comprobar si Carles ya pasó la **llave `.p8`**.
3. Si el producto está listo → empezar la **vía de usuarios nuevos en Flutter**: mirar el paywall actual y el Figma juntos, crear la rama en `elmetodo_app`, añadir el botón "De momento no" y construir el modal.
4. Recordar gatear el modal por `has_ever_subscribed` para no enseñar 9,99€ a quien no es elegible.

---

## 9. Riesgos a recordar

- 🔴 **Mismatch del Product ID:** si el ID no es idéntico en Apple/backend/app, la compra se cobra pero no da acceso. Verificar siempre que sea `com.elmetodo.subscription.trimestraloffer`.
- 🟡 **Elegibilidad de la intro:** si se enseña 9,99€ a un usuario no elegible, Apple le cobra 19,99€. Mitigar mostrando el modal solo a `has_ever_subscribed = false` y, a poder ser, comprobando elegibilidad real con Apple.
- 🔴 **El paywall es pantalla real con pagos:** todo el código de Flutter se prueba en **sandbox** antes de mezclar a `main`. Nada se publica hasta que Carles revise.
- 🟡 **Dependencias externas:** aprobación de Apple (tarda) y llave de Carles. Por eso vamos por fases.

---

## 10. Notas guardadas en memoria (persisten entre sesiones)

- `user_kata_non_technical` — Kata es PM/diseñadora, no técnica.
- `feedback_explain_and_flag_risk` — explicar en cristiano, preguntar mucho, avisar del nivel de riesgo.
- `feedback_always_feature_branch` — al pushear código, trabajar siempre en rama aparte.

---

## 11. Android / Google Play — AÑADIDO AL SCOPE (2026-06-16)

> ⚠️ **Cambio de scope:** el spec tenía Android fuera, pero Kata lo metió **dentro**. Añade trabajo (otra plataforma, mecánica distinta), pero NO es "el doble": el backend de Android ya está muy montado y Android se ahorra la complejidad de la firma de iOS.

**Ya montado (verificado):**
- Backend `app/services/google_play_service.py`: verifica compras Android, lee ofertas (`offerDetails`/`offerTags`/`basePlanId`), hace el acknowledge obligatorio y decodifica notificaciones de Google. El trimestral Android ya está mapeado (`elmetodo_subscription_quarterly` → quarterly). → Probablemente **sin cambios** para el exit-intent (confirmar al implementar).
- Flutter: `in_app_purchase` ya compra productos Android (`purchase_service.dart:18`).

**Falta (nuevo):**
- Google Play Console: crear una **oferta** sobre el plan trimestral (en Google la oferta cuelga del plan; NO se crea un producto nuevo como el `trimestraloffer` de iOS).
- Flutter: lanzar esa oferta requiere pasar su **offer token** (`GooglePlayPurchaseParam`) — hoy no se hace.

**Diferencias con iOS (a favor de Android):** sin firma `.p8`; sin producto duplicado (oferta sobre el plan existente); Google permite **combinar prueba gratis + descuento** en una misma oferta (en iOS es "uno u otro").

**Decisiones de producto (YA TOMADAS):**
1. Oferta: **9,99€ primer trimestre, luego 19,99€, SIN prueba gratis**, igual en iOS y Android.
2. **Android va en la misma v1 que iOS** (en paralelo).

**Datos de Google Play (CREADA Y ACTIVADA):**
- **Product ID:** `elmetodo_subscription_trimestraloffer` → ya mapeado en el backend (→ quarterly), junto al de iOS, en la misma rama.
- Plan base: 3 meses, **19,99€** (precio normal). Oferta encima: **9,99€ el primer ciclo** (pago único), luego vuelve a 19,99€.
- **Eligibility: Developer determined** (la app decide quién la ve). → Probablemente esta misma oferta sirva para **nuevos Y para los que ya pagaron** en Android (a confirmar al programar).
- **Base plan ID:** `trimestral` · **Offer ID:** `exit-intent` ✅ (los 3 IDs que necesita Flutter para Android: producto `elmetodo_subscription_trimestraloffer` + base plan `trimestral` + oferta `exit-intent`)
- Falta en Flutter: manejo del *offer token* (`GooglePlayPurchaseParam`).
