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

> **Nota de honestidad — apuesta vs métrica.** La apuesta es estratégica (diferenciación), pero "diferenciación" no se mide directo. Lo medimos por su efecto observable: si de verdad diferencia, **los usuarios que lo usan se quedan más** (sección 2). La diferenciación es el porqué; la retención es la prueba de que aterrizó.

---

## 2. Métrica de éxito

**Métrica primaria: retención.**

El éxito es que los usuarios expuestos al score **sigan activos más tiempo** que los que no lo ven. Forma concreta de medirlo:

- **Comparación de cohortes**: retención en semana N (p. ej. % activo en semana 4 y semana 8, o D30) de usuarios que **vieron/usaron el score** vs cohorte equivalente sin él (pre-lanzamiento, o vía rollout por feature flag — la API ya soporta feature flags).
- **Objetivo (hipótesis a calibrar con baseline real, no número inventado):** un *uplift* relativo de retención en la cohorte con score frente a la cohorte de control. El umbral exacto se fija al medir la baseline actual; sin esa baseline cualquier cifra sería falsa.

**Métricas secundarias (mecanismo — explican *por qué* sube o no la retención):**
- **Engagement con el score**: % de usuarios activos que abren la pantalla de score / resumen semanal cada semana. Si nadie lo mira, no puede retener.
- **Constancia de entreno**: entrenos logueados por usuario/semana. El score debería empujar a entrenar y registrar más (es su bucle de retroalimentación).

**Guardrails (señales de que estamos haciendo daño):**
- **Desmotivación**: caída de actividad en usuarios que reciben un score bajo/"Principiante" en su primer cálculo. Riesgo real (ver sección 3) — hay que vigilarlo explícitamente.
- **% de logs no puntuables**: si muchos entrenos no generan score (texto-libre no parseable, ejercicios de máquina, grupos sin datos), la feature se siente rota.

**Anti-métrica:** no optimizamos por "score medio alto". Inflar el score para que todos se sientan bien lo vacía de significado y mata la diferenciación.

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

Si la apuesta es **diferenciación medida por retención** y la deseabilidad está **sin validar en nuestros usuarios**, lo coherente NO es construir el sistema completo del spec de una vez:

- **Empezar por el segmento de mayor señal y menor complejidad**: score de **fuerza**, en **programas de fuerza pura** (donde la cobertura de datos es alta y los estándares son más sólidos). Eso valida la apuesta entera con una fracción del trabajo.
- **Dejar running, híbrido y el historial largo para fases posteriores**, una vez confirmado que la gente mira el score y retiene mejor.
- El recorte concreto a fases vive en el plan de tareas; este doc solo fija que **el MVP se justifica por validar la apuesta barato**, no por completar el spec.

---

## 5. Preguntas abiertas / decisiones pendientes

- [ ] **Integración con Ligas: sin decidir.** ¿El score alimenta el ranking (hoy por pasos) o es vista propia? Afecta a la narrativa de diferenciación pero no bloquea el MVP de score visible. Decidir tras validar el score como vista propia.
- [ ] **Baseline de retención**: medir la curva actual antes de lanzar para poder fijar el umbral de éxito real.
- [ ] **Framing anti-desmotivación**: definir con diseño cómo se presenta un score bajo sin ahuyentar al usuario.
- [ ] **¿Gated o gratis?** No decidido aquí. La apuesta es diferenciación (no monetización), lo que sugiere score visible para todos; confirmar.
