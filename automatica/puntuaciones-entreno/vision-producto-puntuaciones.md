# Puntuación de Entrenamiento — Visión de producto

One-pager que vive por encima del spec técnico. Responde *por qué* construimos esto, *cómo sabremos si funcionó* y *qué tan seguros estamos de que el usuario lo quiere*, antes de entrar en el *cómo* ([puntaciones-entreno.md](puntaciones-entreno.md)) y el plan de tareas ([tareas-implementacion-puntuaciones.md](tareas-implementacion-puntuaciones.md)).

Fecha: 2026-06-12 · Alcance: app automática (sin coaches, sin dashboard).

---

## 1. Por qué — la apuesta

**Apuesta principal: diferenciación competitiva.**

El Metodo compite con un mar de apps de programas de entrenamiento que, en esencia, ofrecen lo mismo: un calendario de rutinas y vídeos. Loguear series es tedioso y, una vez hecho, el dato **muere ahí** — no devuelve nada al usuario. El producto no tiene una razón propia para existir frente a la competencia genérica.

La puntuación convierte el entrenamiento en un **número con significado, propio de El Metodo**: una medida objetiva de "cómo de fuerte / en forma estás" que evoluciona con cada entreno y se compara contra estándares poblacionales (no contra ti mismo de forma vaga). Es la diferencia entre *"registraste 100kg en banca"* y *"estás en nivel Experimentado, top de tu franja de edad"*.

Esto posiciona al producto como **una herramienta seria de progreso medible**, no un reproductor de rutinas. Es el tipo de feature que la competencia genérica no tiene y que da un argumento de marketing y de identidad de marca.

**Por qué ahora:** la infraestructura ya soporta el 80% del trabajo invisible — ya capturamos logs de entreno, peso corporal con histórico, y demografía; y el feature "Tus marcas" ya parsea esos logs a números. Construir el score es explotar datos que **ya estamos recogiendo y hoy desperdiciamos**, no montar una tubería nueva.

> **Nota de honestidad — apuesta vs métrica.** La apuesta es estratégica (diferenciación), pero "diferenciación" no se mide directo. Lo medimos por su efecto sobre el negocio: si de verdad diferencia, la gente **percibe valor suficiente para pagar y no cancelar tras el trial** (sección 2). La diferenciación es el porqué; la conversión trial→pago es la prueba de que aterrizó.

---

## 2. Métrica de éxito

**Métrica primaria: conversión trial → pago (suscriptores que no cancelan tras el trial).**

El éxito es que el score haga que más usuarios **paguen y se queden** tras el free trial. Dos formas equivalentes de leerlo, ambas medibles con datos que la API ya guarda (`free_trial_started_at` / `free_trial_expires_at` / `subscription_tier` / `has_ever_subscribed`):

- **Tasa de conversión trial→pago**: % de usuarios que entran al trial y acaban como suscriptores activos al expirar (no cancelan). Es la métrica más directa.
- **Crecimiento neto de suscriptores**: altas de pago menos cancelaciones. Mismo fenómeno visto a nivel agregado.

**Cómo se atribuye al score (no basta con mirar la cifra global):**
- **Comparación de cohortes vía feature flag** (la API ya soporta feature flags): conversión trial→pago de la cohorte que **ve el score durante el trial** vs cohorte de control sin él.
- **Objetivo (hipótesis a calibrar con baseline real, no número inventado):** *uplift* relativo de la conversión en la cohorte con score. El umbral se fija al medir la baseline de conversión actual; sin esa baseline cualquier cifra sería falsa.

> **Restricción de diseño crítica — la ventana del trial son 7 días.** Si la conversión es la métrica, el score tiene que **entregar valor percibido dentro del trial** (`free_trial_expires_at` = inicio + 7). Esto choca con el spec: el running necesita ~3 meses de datos y la fuerza necesita varios logs para estabilizarse. Un score que solo brilla a los 2 meses **no mueve la conversión**. Implicación: en el MVP el score debe dar una **primera lectura útil con muy pocos datos** (ej: estimar nivel desde el primer entreno de fuerza logueado, aunque sea con baja confianza), priorizando el "momento ajá" temprano sobre la precisión total.

**Métricas secundarias (mecanismo — explican *por qué* convierte o no):**
- **Engagement con el score durante el trial**: % de usuarios en trial que abren la pantalla de score. Si no lo miran antes de que expire el trial, no puede influir en la decisión de pago.
- **Time-to-first-score**: cuántos días/entrenos tarda un usuario nuevo en ver su primer score real. Cuanto antes dentro del trial, mejor.
- **Constancia de entreno**: entrenos logueados por usuario/semana (alimenta el score y es señal de hábito).

**Guardrails (señales de que estamos haciendo daño):**
- **Desmotivación**: cancelación más alta en usuarios que reciben un score bajo/"Principiante" en su primer cálculo. Riesgo real (ver sección 3) — vigilar explícitamente, porque iría justo en contra de la métrica.
- **% de logs no puntuables**: si muchos entrenos no generan score (texto-libre no parseable, máquinas, grupos sin datos), la feature se siente rota durante el trial.

**Anti-métrica:** no optimizamos por "score medio alto". Inflar el score para que todos se sientan bien lo vacía de significado y mata la diferenciación que justifica el pago.

---

## 3. Deseabilidad — ¿lo quiere el usuario?

**Evidencia actual: datos de competidores (Gravl y similares).** El sistema está inspirado en que esta mecánica funciona en otras apps de fitness. Es una señal válida pero **indirecta**: demuestra que el patrón puede funcionar, no que *nuestros* usuarios lo pidan.

> **Tratamos la deseabilidad como hipótesis, no como hecho.** No tenemos aún feedback directo de usuarios de El Metodo pidiendo esto. Es la pata más débil de la apuesta y la que más barato sale validar antes de construirlo entero.

**Validación barata antes de comprometerse al sistema completo:**
- Señal interna que ya tenemos al alcance: **uso real de "Tus marcas"** (records + progresión). Si la gente ya entra a ver su progreso ahí, hay apetito por el dato cuantificado. Medirlo es gratis y es de *nuestros* usuarios.
- El éxito de las **Ligas por pasos** existentes indica apetito por gamificación/comparación.
- Opcional: una encuesta corta o un fake-door (pantalla de "tu nivel de fuerza" detrás de un tap) para medir interés antes de calcular nada real.

**Riesgos de deseabilidad (lo que puede hacer que NO lo quieran):**
1. **Un número que juzga puede desmotivar.** Alguien constante que sale "Principiante" puede sentirse mal y abandonar — justo lo contrario de la métrica de retención. Mitigación: enfatizar **progreso personal** (delta vs ti mismo) por encima del nivel absoluto, framing de coaching, no de ranking frío.
2. **Score poco fiable = pérdida de confianza.** Si el número salta de forma rara (por logs sucios o estándares mal calibrados), el usuario deja de creérselo. El spec ya prevé indicadores de baja confianza en running; hay que aplicar el mismo cuidado en fuerza.
3. **Cobertura parcial frustra.** Programas con pocos ejercicios válidos (máquinas, running básico) dan scores con muchos `—`. Para esos segmentos quizá v1 no deba mostrar score.

---

## 4. Implicaciones para el alcance (de la apuesta al MVP)

Si la apuesta es **diferenciación medida por conversión trial→pago**, la deseabilidad está **sin validar en nuestros usuarios**, y la ventana de decisión son **7 días**, lo coherente NO es construir el sistema completo del spec de una vez:

- **Empezar por el segmento de mayor señal y menor complejidad**: score de **fuerza**, en **programas de fuerza pura** (cobertura de datos alta, estándares sólidos, y — clave — produce un número desde el **primer entreno logueado**, dentro del trial). Eso valida la apuesta entera con una fracción del trabajo.
- **Dejar running, híbrido y el historial largo para fases posteriores**: dependen de meses de datos, así que no pueden influir en la conversión del trial — su valor es de retención a largo plazo, otra fase.
- **Diseñar para el "momento ajá" temprano**: una primera estimación de nivel con pocos datos (marcada como provisional) pesa más para la conversión que un score perfecto a los 3 meses.
- El recorte concreto a fases vive en el plan de tareas; este doc solo fija que **el MVP se justifica por mover la conversión dentro del trial**, no por completar el spec.

---

## 5. Solución al cold-start — sesiones de evaluación

**Problema:** el score nace vacío. Si el usuario tiene que acumular semanas de entrenos para ver algo, el score no llega a tiempo para influir en la conversión del trial (7 días) y el tab de Puntuaciones se siente roto al abrirlo.

**Solución:** las **primeras sesiones de cada programa son sesiones de evaluación** diseñadas para poblar el score desde el día 1.

- **Fuerza — bloque de evaluación**: una o dos sesiones iniciales que incluyen, a propósito, al menos un ejercicio válido **por cada uno de los 7 grupos musculares**. Probablemente no cabe en una sola sesión → bloque de ~2 sesiones (ej. tren superior + tren inferior) en la primera semana.
  - **No es un test de 1RM máximo.** La fórmula es Epley sobre cualquier serie (`1RM = peso × (1 + reps/30)`), así que basta con **series de trabajo submáximas** (ej. 8–10 reps con peso moderado, bien calentado). Esto evita riesgo de lesión en día 1 y evita baselines basura de un principiante asustado ante peso pesado.
- **Running — test ligero de inicio**: en vez del Test de carrera completa (que el spec deja al final), un **proxy corto escalado al nivel del programa** (time-trial de 1–2 km o test de 12 min tipo Cooper) para tener un pace de arranque sin pedirle un 10K a un principiante el día 1. El Test completo sigue al final como dice el spec.

**Por qué esto es bueno más allá del cold-start:**
- Da una **baseline limpia** → el delta "+X pts este mes" mide progreso real desde un punto fijo, no ruido de datos que entran a cuentagotas.
- El usuario entiende desde el día 1 **para qué** loguea: "esta sesión calcula tu nivel".

**Implicaciones (no es solo UI):**
- Es **trabajo de contenido**: hay que diseñar las sesiones de evaluación y garantizar que contienen los ejercicios que puntúan por grupo. Se conecta con la auditoría de `muscle_group`/`equipment` ya planificada.
- Necesita un **flag de "sesión de evaluación"** en `training_day_v2` (o ejercicio), que encaja con el tipo de sesión "Test" del running.
- **Empty state previo**: antes de completar la evaluación, el tab de Puntuaciones muestra un onboarding ("Completa tu sesión de evaluación para ver tu nivel"), no un score en cero.

**Riesgo:** una baseline que sale "Principiante" puede desmotivar en pleno trial. Mitigación: framing de punto de partida ("mira cómo sube"), primer delta rápido, y evaluación con series submáximas bien calentadas (baseline más justa que un test a fallo).

---

## 6. Preguntas abiertas / decisiones pendientes

- [ ] **Integración con Ligas: sin decidir.** ¿El score alimenta el ranking (hoy por pasos) o es vista propia? Afecta a la narrativa de diferenciación pero no bloquea el MVP de score visible. Decidir tras validar el score como vista propia.
- [ ] **Baseline de conversión trial→pago**: medir la tasa actual antes de lanzar para poder fijar el umbral de éxito real (uplift).
- [ ] **Mínimo de datos para un primer score** dentro del trial: ¿con cuántos entrenos/ejercicios logueados mostramos una primera lectura, y cómo la marcamos como provisional? Decisión que condiciona si el score puede mover la conversión.
- [ ] **Framing anti-desmotivación**: definir con diseño cómo se presenta un score bajo sin ahuyentar al usuario (y sin disparar cancelación en el trial).
- [ ] **¿Visible en el trial o solo tras pagar?** Si la métrica es conversión, el score debe verse **durante** el trial (es la palanca). Confirmar que no queda detrás del paywall.
