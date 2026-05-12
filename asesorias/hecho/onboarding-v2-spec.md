# Onboarding Asesorías — Spec v2

## Contexto

Rediseño completo del flujo de onboarding/cuestionario de asesorías. Se parte de la v1 (22 pantallas) con los siguientes problemas críticos resueltos:

| Issue | Severidad |
|-------|-----------|
| Contador de pasos inconsistente ("1 de 11" → "2 de 13") | P0 |
| Imágenes AI-generated para género, tipo de cuerpo y objetivo | P0 |
| Banner amarillo fuera del DS en pantalla de revisión | P0 |
| Pantallas con 60%+ espacio vacío (radio buttons sin agrupar) | P1 |
| Inconsistencia visual entre pantallas de cards y radio buttons | P1 |

**Referencia de calidad:** App automática (suscripción V1)
**Design system:** EMP DS Library — dark theme, verde neón `#00ee00`, Open Sans

---

## Flujo completo: 22 pantallas → ~15

### A. Registro

- Email + Contraseña
- Social login: **Google + Apple**
- Tab: Iniciar sesión / Registrarse
- Links: Políticas de privacidad · Términos de uso *(sin "EULA")*

---

### B. Datos Físicos

**B1 — Género**
- Opciones: Hombre / Mujer
- Visual: iconografía neutral del DS (sin fotos ni imágenes AI)

**B2 — Edad + Altura + Peso**
- Campos agrupados en una pantalla: Fecha de nacimiento + Altura (cm) + Peso (kg)

**B3 — Tipo de cuerpo**
- Pregunta: *"¿Cómo describirías tu estado físico actual?"*
- 5 opciones de texto (sin fotos):
  1. Estoy delgado/a, me falta músculo
  2. Me siento bien pero quiero definir
  3. Tengo algo de barriga que quiero bajar
  4. Quiero perder bastante peso
  5. Tengo sobrepeso notable
- Visual: cards de texto — surface-2 `#1d1f23`, R-8, borde activo verde `#00ee00` + glow

---

### C. Bloque Dieta

**C0 — Intro**
- Copy: *"Ahora cuéntanos sobre tu dieta"*
- Subtítulo: *"Para personalizar tus macros y plan alimenticio"*
- Solo CTA "Continuar"

**C1 — Objetivo físico** *(pantalla propia)*
- Opciones: Definición · Definición extrema · Volumen · Mantenimiento
- Visual: cards con icono o ilustración (no AI-generated)

**C2 — Comidas + Intolerancias** *(una pantalla)*
- Sección 1: ¿Cuántas comidas al día? → 2 / 3 / 4 / 5
- Divisor visual
- Sección 2: Intolerancias (multi-select, máx. 3) → Ninguna / Gluten / Lactosa / Huevos / Pescado / Frutos secos / Aguacate / Claras / Verdura

**C3 — Especificaciones dieta** *(pantalla propia)*
- Copy: *"¿Algo más que deba saber tu coach sobre tu dieta?"*
- Textarea opcional

---

### D. Bloque Entreno

**D0 — Intro**
- Copy: *"Ahora cuéntanos sobre tu entreno"*
- Solo CTA "Continuar"

**D1 — Tipo de entreno + Subvariante** *(pantalla propia, condicional)*
- Opciones: Físico · Carrera · Híbrido · Hyrox
- Lógica condicional:
  - **Físico** → sin subvariante adicional (usa objetivo de C1)
  - **Carrera** → subvariante: 5 km / 10 km / 21 km / 42 km
  - **Híbrido** → seleccionable, subvariante TBD
  - **Hyrox** → seleccionable, subvariante TBD

**D2 — Lugar + Días + Nivel** *(una pantalla)*
- Sección 1: ¿Dónde entrenas? → Gimnasio / Casa / Casa con material
- Sección 2: ¿Cuántos días/semana? → 2 / 3 / 4 / 5
- Sección 3: Nivel → Principiante / Avanzado

**D3 — Lesiones + Especificaciones** *(una pantalla)*
- Sección 1: Lesiones (multi-select) → Ninguna / Lumbar, espalda / Rodilla, pierna / Hombro, rotadores
- Sección 2: *"¿Algo más que deba saber tu coach sobre tu entreno?"* → Textarea opcional

---

### E. Transición "Calculando..."

- Animación de procesamiento (círculos concéntricos verdes)
- Micro-texto dinámico: "Calculando tu metabolismo..." → "Definiendo tu objetivo..."

---

### F. Pantalla "¡Listo!"

- 3 checks verdes: Datos físicos ✓ · Dieta ✓ · Entreno ✓
- Copy: *"Tu coach tiene todo lo que necesita para crear tu plan personalizado"*
- CTA: "Revisar información"

---

### G. Revisión Final

- Header: texto en surface-2 con texto secondary (sin banner amarillo)
- Secciones: Datos físicos / Dieta / Entreno — cada campo editable con flecha
- Formato fecha: "14 nov 2000" (no ISO)
- Formato peso: "60 kg" (sin decimal)
- CTA: "Enviar información" (title case)

---

## Progreso y numeración

- Indicador de progreso por bloque (no global)
- Numeración fija y consistente desde el paso 1 hasta el final
- El total no cambia mid-flow

---

## Fuera de scope (esta fase)

- Pantallas de intro/story (4 slides previos al registro) — se define en fase posterior
- Subvariantes de Híbrido y Hyrox — se añaden cuando estén confirmadas
