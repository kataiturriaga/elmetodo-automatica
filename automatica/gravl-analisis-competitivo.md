# Teardown competitivo: Gravl → decisión de producto (modelo híbrido)

> **Para qué es este doc:** marco de referencia para decisiones de producto frente a nuestro
> competidor más directo (Gravl). Antes de priorizar una feature, contrasta aquí: *¿esto
> compite donde Gravl ya gana, o refuerza nuestra apuesta diferencial?*
>
> **Cómo encaja con la estrategia viva:** complementa `estrategia-posicionamiento-jun2026.md`.
> Aquel define el marco ("Sistema de Consistencia Deportiva", gamificación = retención).
> Este aterriza el **eje de producto/método** frente a Gravl. No se contradicen: el híbrido de
> aquí es el "qué hacer cuando el usuario llega" (punto 7 de aquel doc), afinado.
>
> **Fecha:** junio 2026.

---

## 1. Qué es Gravl y por qué lo analizamos

Gravl (Personal Trainer) — app de fitness con IA. App Store `id6450921637` · Google Play `com.liteup.getgains`. Es el competidor cuyo enfoque (rutinas generadas por IA al momento) choca de frente con el nuestro (programas diseñados por entrenador). Capturas de su UI en `gravl-puntuacion/`.

## 2. Método y evidencia (trazabilidad)

- **259 reseñas reales** scrapeadas de fuentes públicas (App Store RSS + Google Play). 54 negativas (1-2★), 16 neutras, **189 positivas (4-5★)**.
- Evidencia cruda y análisis detallado en el repo `repeat`: `gravl_reseñas.csv`, `gravl_analisis_IA.md`, `1.3.pildora.md`.
- **Caveat de datos:** geografía fiable solo en App Store (US/UY); Google Play no segmenta país → "español mezclado". No hay corte limpio España vs LATAM.

## 3. Qué hace bien Gravl → REPLICAR, no competir aquí

> Regla: si todos sus fans lo alaban, no es donde nos diferenciamos. Lo igualamos y punto.

| Fortaleza de Gravl | Evidencia |
|---|---|
| **Autopilot "no pensar"** (la IA decide la rutina) | *"No thinking just work!"* · *"removes the guesswork"* — adorado por **principiantes** |
| **Progresión automática de pesos** (lo más alabado, 31 menciones) | *"te empuja a aumentar pesos de manera progresiva"* · *"I have put on 4 lbs of muscle"* |
| **Adaptación al equipo del gym/casa** | *"colocó las máquinas de mi sucursal y la app hizo el resto"* — **paridad, no diferencial nuestro** |
| Variedad de rutinas · Videos con personas reales · Soporte que responde | 25 / 11 / 6 menciones positivas |

## 4. Dónde falla → pero ojo, separa ruido de huecos

- **Ruido (no es hueco):** lo más ruidoso de las 1-2★ son **bugs** (crashes, no guarda) y **precio/"no es gratis"**. Gravl los parchea. No construir estrategia sobre esto.
- **Huecos reales (viven en los 4★ "me encanta PERO…"):**
  - **Criterio de la IA** desconfiado por usuarios que saben entrenar (EXP): *"the AI doesn't understand you can't always increase weight"* · *"me recomendó patada de mula… contraproducente para la hipertrofia"* · *"el chatgpt es mejor"*. Pocas (~6) pero intensas.
  - **Cuerpo real ignorado:** la IA no pregunta por lesiones ni condiciones: *"poner la opción de agregar lesiones"* · *"no hace ajustes según el ciclo femenino"* · *"no preguntan si tienes alguna anomalía, y eso lo tienen otras apps"*.
  - **Pesos imposibles / mal calibrados:** *"pone pesos imposibles solo para mostrar progreso"*.

## 5. Jobs to be Done (3 niveles)

| Nivel | Job |
|---|---|
| **Funcional** | "Que me armen la rutina y me digan exactamente qué hacer" · seguir mi progreso · adaptar al equipo que tengo |
| **Emocional** | Quitar la ansiedad del principiante ("no sé qué hacer en el gym") · sentirme seguro · **confiar en que detrás hay criterio** |
| **Social** | Competir con amigos · mostrar mi rutina al profe |

## 6. Segmento ignorado (identificado, NO es la apuesta)

Usuarios con **lesiones / condiciones físicas** (~5/259). Gravl no les pregunta por su cuerpo al programar; otras apps sí. **Decisión consciente:** lo detectamos, pero **no basamos el producto nuevo en él** — es demasiado nicho para un producto recién lanzado que necesita pesca de arrastre. Se integra como un **flujo** dentro del producto (ver §8) y se reserva como expansión futura, no como diferenciación de marca.

## 7. Nuestra diferenciación (la decisión)

> **"El humano diseña el plan. El algoritmo afina los pesos. Tú solo entrenas."**

No competimos en "otra app de rutinas con IA". Diferenciamos en el eje donde el autopilot de Gravl no puede: **el criterio humano / la confianza**. Es una palanca de **posicionamiento ancho** (le habla a todos, no a un nicho) y coherente con nuestro "Sistema de Consistencia Deportiva".

**Honestidad estratégica:** el grueso del mercado (principiantes) *adora* el autopilot de Gravl — no desconfía de la IA. Por tanto "experto vs IA" funciona como **señal de confianza/marca** para captar y retener, no como una queja masiva contra Gravl. Es legítimo (muchas marcas fitness ganan así), pero sabemos que es un juego de posicionamiento, no de "Gravl le falla a las masas".

## 8. Concepto de producto: el modelo híbrido

| Pieza | Quién manda | Qué resuelve |
|---|---|---|
| **Estructura del programa** | El **entrenador** (programa cerrado) | Criterio y confianza. Evita ejercicios basura ("patada de mula") que critican de Gravl |
| **Progresión de pesos** | **Algoritmo**, según lo que el usuario registra | No cedemos el eje fuerte de Gravl. Arregla los "pesos imposibles" |
| **Cambio de ejercicio** (modal con 2 flujos) | Sistema guiado | El usuario elige por qué cambia → recomendación adecuada |

**El modal de swap, dos flujos:**
1. **Por lesión** → cuestionario corto / recomendación directa de un ejercicio alternativo seguro. *(Es el flujo diferencial: Gravl no lo tiene.)*
2. **Por falta de material** → pregunta qué equipo falta/hay y sugiere reemplazo. *(Paridad: Gravl ya lo hace bien; lo igualamos, no lo vendemos como ventaja.)*

## 9. Decisiones explícitas (qué NO hacemos)

- **No** diferenciamos por "app para lesiones" (nicho para producto nuevo → diferido a expansión).
- **No** vendemos la adaptación al equipo como ventaja (Gravl ya la clava → es table-stakes).
- **No** confiamos en Instagram como foso: es un **canal** (Gravl también anuncia ahí), no una diferenciación.
- **No** competimos en bugs ni en "ser más barato/gratis": es el ruido de Gravl, lo parchearán.

## 10. Preguntas abiertas / próximos pasos

- **Alcance MVP:** ¿qué entra en v1 (programa cerrado + progresión algorítmica + swap por equipamiento) y qué se difiere a v2 (cuestionario de lesiones)?
- **Promesa de Instagram:** clavar el claim de pesca de arrastre ("tu plan lo diseña un entrenador, no lo adivina un robot") y testearlo.
- **Validación:** ¿la progresión algorítmica nuestra es de verdad mejor que la de Gravl, o solo distinta? (Si no es mejor, el diferencial recae 100% en marca/criterio.)

---

*Fuente del análisis: 259 reseñas reales de Gravl (jun 2026). Trazabilidad completa en repo `repeat`.*
