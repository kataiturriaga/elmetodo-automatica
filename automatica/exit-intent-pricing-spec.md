# Exit-Intent Pricing — Spec de implementación

**Para:** Carles  
**Feature:** Exit-intent con descuento al pulsar "De momento no" en el pricing screen  
**Fecha:** 2026-06-09

---

## Qué hay que hacer

Cuando el usuario pulsa **"De momento no"** en la PricingScreen, en vez de ir directo al app, se muestra un bottom sheet con una oferta exclusiva del plan trimestral al 50% el primer trimestre.

- Si acepta → compra el trimestral con el descuento → llama al verify-iap existente → entra al app
- Si rechaza → entra al app sin descuento

---

## Diseño

El bottom sheet replica esta pantalla de Figma:  
[App Automatica — Section 3](https://www.figma.com/design/629ryw0MF7hzDxIFiZJ5Un/App-Automatica?node-id=4596-116145)

Elementos:
- Badge verde: "⚡ OFERTA EXCLUSIVA"
- Headline: "¡Espera un momento!"
- Subtítulo: "Solo por hoy, accede al plan trimestral a mitad de precio en tu primer trimestre."
- Card del plan:
  - Label "Trimestral" + badge "Más popular"
  - Precio tachado: 19,99€/trim.
  - Precio destacado: **9,99€** + badge "Ahorra 50%"
  - Texto pequeño: "Primer trimestre · Luego 19,99€/trim. · Cancela cuando quieras"
- Botón primario: "Activar oferta"
- Botón secundario (texto): "No gracias. Salir sin descuento"
- Pie: "7 días de prueba gratuita. Cancela cuando quieras"

---

## Configuración en App Store Connect (ya hecho)

El Promotional Offer ya está creado en App Store Connect:

| Campo | Valor |
|-------|-------|
| Reference name | exit-intent |
| Offer identifier | `001` |
| Offer type | Pay up front for the first 3 months |
| Precio | 9,99€ |
| Producto | `com.elmetodo.subscription.quarterly` |

La **Subscription Key (.p8)** ya existe en el backend:  
→ Es la misma key que se usa para el App Store Server API: `secrets/apple_iap_key.p8`  
→ Las env vars ya están configuradas: `APPLE_IAP_KEY_ID`, `APPLE_IAP_ISSUER_ID`  
→ No hace falta descargar nada nuevo.

---

## Backend — nuevo endpoint

Añadir en `app/api/routes/mobile/subscription.py`, junto al resto de endpoints de suscripción.

### `POST /api/v2/subscription/promotional-offer-signature`

Autenticado (usuario logueado). El backend firma los parámetros de la oferta para que Apple valide que el descuento es legítimo.

**Request:**
```json
{
  "product_id": "com.elmetodo.subscription.quarterly",
  "offer_id": "001"
}
```

**Lógica:**

```python
import uuid
import time
import hashlib
import hmac
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec

def generate_promotional_offer_signature(
    app_bundle_id: str,       # "com.elmetodo.app"
    key_identifier: str,      # settings.APPLE_IAP_KEY_ID
    product_id: str,          # "com.elmetodo.subscription.quarterly"
    offer_id: str,            # "001"
    application_username: str, # str(user_id)
    private_key_path: str,    # settings.APPLE_IAP_PRIVATE_KEY_PATH
) -> dict:
    nonce = str(uuid.uuid4()).lower()
    timestamp = int(time.time() * 1000)  # milisegundos

    payload = "\n".join([
        app_bundle_id,
        key_identifier,
        product_id,
        offer_id,
        application_username,
        nonce,
        str(timestamp),
    ])

    with open(private_key_path, "rb") as f:
        private_key = serialization.load_pem_private_key(f.read(), password=None)

    signature = private_key.sign(payload.encode("utf-8"), ec.ECDSA(hashes.SHA256()))

    return {
        "key_identifier": key_identifier,
        "nonce": nonce,
        "timestamp": timestamp,
        "signature": signature.hex(),  # la app lo convierte a Data
    }
```

**Response:**
```json
{
  "key_identifier": "XXXXXXXXXX",
  "nonce": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "timestamp": 1749470000000,
  "signature": "3045022100..."
}
```

Referencia Apple: [Generating a Promotional Offer Signature](https://developer.apple.com/documentation/storekit/in-app_purchase/subscriptions_and_offers/generating_a_promotional_offer_signature)

---

## Condición de elegibilidad

Los Promotional Offers de Apple solo funcionan para usuarios que **ya han tenido una suscripción** (activa o expirada). Para usuarios nuevos que nunca han pagado, Apple rechaza la compra.

Usar el campo existente `user.has_ever_subscribed` (bool en `app/models/user.py`):

- `has_ever_subscribed = True` → mostrar exit-intent con Promotional Offer
- `has_ever_subscribed = False` → mostrar exit-intent con Introductory Offer (o no mostrar exit-intent)

**Decisión pendiente:** ¿qué hacemos con usuarios que nunca han suscrito? Opciones:
1. No mostrar el exit-intent (ir directo al app)
2. Mostrar el exit-intent con el Introductory Offer (si está configurado)

---

## Flutter — implementación

Archivos relevantes en `elmetodo_app`:
- Paywall actual: `lib/features/subscription/presentation/screens/paywall_screen.dart`
- Lógica de compra: `lib/features/subscription/presentation/providers/subscription_providers.dart`
- Servicio IAP: `lib/features/subscription/data/services/purchase_service.dart`

### 0. Añadir paquete (pubspec.yaml)

El paquete actual `in_app_purchase: ^3.2.0` no soporta Promotional Offers. Hay que añadir la extensión iOS:

```yaml
in_app_purchase_storekit: ^0.3.13
```

### 1. Interceptar "De momento no"

En `paywall_screen.dart`, el cierre actual es un `CircularBackButton` con `context.pop()`. Hay que buscar si existe un botón "De momento no" explícito o si es ese back button, e interceptarlo así:

```dart
// Reemplazar context.pop() por:
final canUsePromo = user.hasEverSubscribed;

if (canUsePromo) {
  _showExitIntentSheet(context);
} else {
  context.pop(); // flujo normal, sin exit-intent
}
```

### 2. Bottom sheet del exit-intent

```dart
void _showExitIntentSheet(BuildContext context) {
  showModalBottomSheet(
    context: context,
    isScrollControlled: true,
    backgroundColor: Colors.transparent,
    builder: (_) => const ExitIntentSheet(),
  );
}
```

Crear `ExitIntentSheet` como widget nuevo en:
`lib/features/subscription/presentation/screens/exit_intent_sheet.dart`

### 3. Al pulsar "Activar oferta"

La compra con Promotional Offer NO pasa por el `purchaseManagerProvider` existente — requiere usar `in_app_purchase_storekit` directamente con la firma del backend:

```dart
Future<void> _activateOffer() async {
  // 1. Pedir firma al backend
  final sig = await subscriptionRemoteDatasource
      .getPromotionalOfferSignature(
        productId: SubscriptionProductIds.quarterlyIos,
        offerId: '001',
      );

  // 2. Construir el discount con StoreKit
  final paymentDiscount = SKPaymentDiscountWrapper(
    identifier: '001',
    keyIdentifier: sig.keyIdentifier,
    nonce: sig.nonce,
    signature: sig.signature,
    timestamp: sig.timestamp,
  );

  // 3. Lanzar compra con descuento
  final iapStoreKit = InAppPurchaseStoreKitPlatform.instance;
  await iapStoreKit.buyNonConsumable(
    purchaseParam: PurchaseParam(
      productDetails: quarterlyProductDetails,
    ),
    // + paymentDiscount (ver docs de in_app_purchase_storekit)
  );

  // 4. El stream de compras existente en subscription_providers.dart
  //    recoge la transacción y llama a verify-iap automáticamente
}
```

El backend recibe `offerType = 2` en la transacción de Apple, que ya gestiona correctamente (marca `is_trial_period = False`, crea el `UserSubscription` con tier `quarterly`).

### 4. Al pulsar "No gracias. Salir sin descuento"

```dart
Navigator.of(context).pop(); // cierra el bottom sheet
context.pop(); // cierra el paywall → va al app (flujo normal)
```

---

## Analytics

Registrar estos eventos (usando el sistema de tracking que ya esté en el proyecto):

| Evento | Cuándo |
|--------|--------|
| `paywall_skipped` | Usuario pulsa "De momento no" |
| `exit_intent_shown` | Bottom sheet aparece |
| `exit_intent_offer_accepted` | Pulsa "Activar oferta" |
| `exit_intent_offer_declined` | Pulsa "No gracias. Salir sin descuento" |
| `exit_intent_purchase_success` | Compra completada con éxito |
| `exit_intent_purchase_error` | Error en la compra |

---

## Resumen de tareas

| # | Tarea | Quién | Notas |
|---|-------|-------|-------|
| 1 | Decidir qué hacer con usuarios `has_ever_subscribed = False` | Kata | Antes de que Carles empiece |
| 2 | Añadir endpoint `POST /v2/subscription/promotional-offer-signature` en `app/api/routes/mobile/subscription.py` | Carles (backend) | La key .p8 ya está en `secrets/apple_iap_key.p8` |
| 3 | Añadir `in_app_purchase_storekit` a `pubspec.yaml` | Carles (Flutter) | Extensión iOS del paquete IAP actual |
| 4 | Localizar el botón "De momento no" en `paywall_screen.dart` e interceptarlo | Carles (Flutter) | Comprobar `has_ever_subscribed` |
| 5 | Construir `ExitIntentSheet` en `lib/features/subscription/presentation/screens/` | Carles (Flutter) | Ver diseño en Figma |
| 6 | Conectar "Activar oferta" → firma del backend → `SKPaymentDiscountWrapper` → compra | Carles (Flutter) | El stream existente en `subscription_providers.dart` recoge la transacción |
| 7 | Manejar "No gracias" → cerrar sheet + cerrar paywall | Carles (Flutter) | |
| 8 | Añadir eventos de analytics | Carles | |
| 9 | Probar en sandbox con cuenta de test de Apple | Carles | `APPLE_IAP_ENVIRONMENT=sandbox` ya existe |

---

## Fuera de scope (por ahora)

- Android / Google Play (mismo concepto, diferente implementación)
- Lógica de frecuencia (mostrar X veces, cada Y días)
- A/B test del precio o copy
