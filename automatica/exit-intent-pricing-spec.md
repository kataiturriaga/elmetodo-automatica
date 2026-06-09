# Exit-Intent Pricing — Spec de implementación

**Para:** Carles  
**Feature:** Exit-intent con descuento al pulsar "De momento no" en el pricing screen  
**Fecha:** 2026-06-09

---

## Qué hay que hacer

Cuando el usuario pulsa **"De momento no"** en la PricingScreen, en vez de ir directo al app, se muestra un bottom sheet con una oferta exclusiva del plan trimestral al 50% el primer trimestre.

Si acepta → compra el trimestral con el descuento aplicado y entra al app.  
Si rechaza → entra al app sin descuento.

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
| Producto | Premium Trimestral |

La **Subscription Key (.p8)** para firmar está en:  
App Store Connect → Users & Access → Keys → Subscriptions  
→ Hay que descargarla y guardarla en el backend de forma segura (no en el repo).

---

## Backend — nuevo endpoint

### `POST /payments/promotional-offer-signature`

El backend tiene que generar una firma usando la Subscription Key para que Apple valide que el descuento es legítimo.

**Request (desde la app):**
```json
{
  "product_id": "com.elmetodo.premium.trimestral",
  "offer_id": "001"
}
```

**Lógica del backend:**
1. Generar un `nonce` (UUID v4 aleatorio)
2. Obtener el `timestamp` actual en milisegundos (Unix)
3. Construir el payload a firmar (concatenar con `\n`):
   ```
   <app_bundle_id>\n
   <key_identifier>\n
   <product_id>\n
   <offer_id>\n
   <application_username>\n
   <nonce>\n
   <timestamp>
   ```
4. Firmar con ECDSA + SHA-256 usando la Subscription Key (.p8)
5. Devolver la firma en Base64

**Response:**
```json
{
  "key_identifier": "XXXXXXXXXX",
  "nonce": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "timestamp": 1749470000000,
  "signature": "base64encodedSignature=="
}
```

Referencia Apple: [Generating a Promotional Offer Signature](https://developer.apple.com/documentation/storekit/in-app_purchase/subscriptions_and_offers/generating_a_promotional_offer_signature)

---

## Flutter — implementación

### 1. Interceptar "De momento no"

En `PricingScreen`, el botón "De momento no" actualmente navega al app. Cambiar para que llame a `_showExitIntentSheet(context)`.

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

Crear `ExitIntentSheet` como widget separado con el diseño descrito arriba.

### 3. Al pulsar "Activar oferta"

```dart
Future<void> _activateOffer() async {
  // 1. Pedir firma al backend
  final sig = await api.getPromotionalOfferSignature(
    productId: 'com.elmetodo.premium.trimestral',
    offerId: '001',
  );

  // 2. Lanzar compra con el descuento
  await iap.purchaseWithPromotionalOffer(
    productId: 'com.elmetodo.premium.trimestral',
    offerId: '001',
    keyIdentifier: sig.keyIdentifier,
    nonce: sig.nonce,
    timestamp: sig.timestamp,
    signature: sig.signature,
  );
}
```

Adaptar a la implementación de StoreKit/IAP que ya esté en el proyecto.

### 4. Al pulsar "No gracias. Salir sin descuento"

Cerrar el bottom sheet y navegar al app (flujo normal).

```dart
Navigator.of(context).pop();
// navegar a home
```

---

## Condiciones de elegibilidad

Apple solo permite aplicar Promotional Offers a usuarios que **han tenido o tienen una suscripción activa** con la app. Para usuarios completamente nuevos (nunca han suscrito), usar Introductory Offers en su lugar.

Antes de mostrar el exit-intent, verificar si el usuario es elegible para el Promotional Offer. Si no lo es, o bien no mostrar el bottom sheet, o mostrar el Introductory Offer equivalente.

---

## Analytics

Registrar estos eventos:

| Evento | Cuándo |
|--------|--------|
| `paywall_skipped` | Usuario pulsa "De momento no" |
| `exit_intent_shown` | Bottom sheet aparece |
| `exit_intent_offer_accepted` | Pulsa "Activar oferta" |
| `exit_intent_offer_declined` | Pulsa "No gracias. Salir sin descuento" |
| `exit_intent_purchase_success` | Compra completada con éxito |
| `exit_intent_purchase_error` | Error en la compra |

---

## Fuera de scope (por ahora)

- Android / Google Play (mismo concepto, diferente implementación)
- Lógica de frecuencia (mostrar X veces, cada Y días)
- A/B test del precio o copy
