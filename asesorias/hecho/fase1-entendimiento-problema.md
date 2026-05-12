# FASE 1 — Entendimiento del Problema

> Esta fase ocurre **antes de abrir Figma en modo diseño**. Su único objetivo es que el equipo tenga claridad sobre qué están construyendo, para quién, y por qué — antes de invertir tiempo en cualquier pantalla.

---

## 01 — PROBLEM STATEMENT

### ¿Qué problema estamos resolviendo?

**Qué busca definir**
El problema central en 1-2 oraciones que cualquier persona del equipo pueda entender. Responde cuatro preguntas a la vez: ¿quién tiene el problema?, ¿cuál es exactamente?, ¿por qué importa resolverlo ahora?, ¿cómo sabremos que lo resolvimos?

**Por qué importa**
Sin problem statement claro, cada persona del equipo resuelve un problema diferente sin saberlo. El diseñador diseña para una cosa, el dev construye otra, el coach espera una tercera. Es el norte que hace coherentes todas las decisiones posteriores.

Regla: si no podés escribirlo en dos oraciones, todavía no lo entendés bien.

**Para tu rol**

- 🎨 Diseñadora → lo usás para justificar cada decisión de UI. Cuando alguien diga "agreguemos esto", volvés al problem statement para evaluar si suma o distrae.
- 📋 PM → es tu escudo contra el scope creep. Prioriza lo que resuelve el problema definido, rechaza lo que no.
- ⭐ Para crecer → aprendé a escribirlo sola, sin que nadie te lo dicte. Ese salto — de recibir instrucciones a definir el problema — es el que separa un rol ejecutor de uno estratégico.

**Framework / Plantilla**

> *"El usuario [tipo] necesita [necesidad] porque [razón], pero hoy [problema actual], lo que genera [consecuencia negativa]."*

**En este proyecto — Asesorías V2**

**Problem statement (cerrado):**

> "El coached paga un precio premium por tener estructura y acompañamiento real en su entrenamiento y alimentación, pero la app V1 es tan deficiente en UX que no cumple esa promesa — el coach sigue en WhatsApp (intencionalmente, por la cercanía humana) sin una app que le dé soporte estructural al coached —, lo que genera abandono antes de los 90 días y una percepción de que el servicio no vale lo que cuesta."

**Notas de contexto:**

- WhatsApp = canal humano intencional. La app V2 no lo reemplaza, lo complementa.
- Scope diferencial vs Automatica: entrenamiento + dieta + funciones en definición (ej. lista de compra).
- El coach opera desde el dashboard. La app es la experiencia exclusiva del coached.

---

## 02 — ¿PARA QUIÉN?

### Perfil del usuario — proto-persona

**Qué busca definir**
Quién es la persona concreta que va a usar la app. No un promedio estadístico — una persona con contexto de vida real, motivaciones reales y frustraciones específicas. La proto-persona es una herramienta para tomar decisiones: cuando tenés dudas de diseño, le hacés la pregunta al personaje.

**Por qué importa**
Si diseñás para "todos", diseñás para nadie. Las decisiones se vuelven defensibles cuando podés decir "este usuario necesita esto porque está en esta situación". Sin usuario definido, las discusiones del equipo son debates de opinión sin resolución.

También es la base de los JTBDs (sección siguiente): no podés saber qué trabajo contrata el usuario si no sabés quién es.

**Para tu rol**

- 🎨 Diseñadora → la proto-persona te da el contexto de uso. "¿Esta pantalla tiene demasiada info?" depende de si tu usuario está en el gym con las manos sucias o sentado en casa tranquila.
- 📋 PM → los PMs piensan en segmentos, los diseñadores en personas. Saber hacer ambas cosas te hace más valiosa en cualquier equipo.
- ⭐ Para crecer → una proto-persona honesta incluye frustraciones reales, no solo datos de marketing. Las frustraciones son las que generan oportunidades de diseño.

**Cómo construirla**
No necesitás research exhaustivo. Usá lo que ya sabés + hipótesis marcadas como tal. Una proto-persona imperfecta es infinitamente mejor que ninguna.

**Proto-persona — Usuario Coached, Asesorías V2**


| Dimensión           | Contenido                                                                                                                          |
| ------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| Quién               | Padre o madre trabajador/a, 30-60 años, ingresos medios-bajos. 70€/mes es un esfuerzo real, no un gasto casual                     |
| Contexto            | Poco tiempo, muchas responsabilidades. Le cuesta sacar hueco para el gym o para comer bien. No busca una vida healthy de Instagram |
| Motivación profunda | No compra un plan de entreno — compra coger las riendas de su vida. El punch psicológico es tan importante como la dieta           |
| Por qué Inazio      | Inazio es un tío normal, bajito, calvo, cercano. No es un influencer perfecto. Eso genera confianza: "si él puede, yo también"     |
| Relación con coach  | No percibe a un coach individual — percibe a Inazio. El equipo opera en su nombre. La marca es la figura, no la persona detrás     |
| Dieta               | Sin pijadas healthy. Come hamburguesas y pizzas si toca — pero con calorías y macros controlados. Eso es lo que engancha           |
| Frustración hoy     | La app V1 no le ayuda. No tiene estructura clara. No sabe si lo que hace está bien sin preguntar por WhatsApp                      |
| Comportamiento      | Poco tiempo para pensar. Necesita saber QUÉ hacer hoy, no elegir ni interpretar                                                    |


---

## 03 — JOBS-TO-BE-DONE

### ¿Qué trabajo le contrata el usuario al producto?

**Qué busca definir**
Los JTBDs no son features ni funcionalidades — son necesidades funcionales, emocionales y sociales. La diferencia es crucial: "ver mi plan de entreno" es una feature; "saber exactamente qué hacer hoy sin tener que pensar" es un JTBD.

**Por qué importa**
"La gente no compra un taladro, compra un agujero en la pared." Los JTBDs sobreviven a los pivots de producto. Si mañana cambiás la tecnología o el formato, los jobs del usuario siguen siendo los mismos. Diseñar para el job te protege de construir cosas que nadie usa.

**Para tu rol**

- 🎨 Diseñadora → cada JTBD principal se traduce en una pantalla o flujo central. 3 JTBDs críticos = al menos 3 pantallas principales. El JTBD define QUÉ; el diseño define CÓMO.
- 📋 PM → los JTBDs te dicen qué priorizar en el roadmap. "Construimos esto primero porque resuelve el job más frecuente y de mayor valor."
- ⭐ Para crecer → aprendé a distinguir JTBDs funcionales (hacer algo) de los emocionales (sentir algo). Los emocionales son los que generan retención real.

**Framework**

> *"Cuando [situación concreta], quiero [motivación], para [resultado esperado]."*
>
> Tipos: Funcional · Emocional · Social

**JTBDs — Asesorías V2 (priorizados)**


| Prioridad     | Tipo      | JTBD                                                                                                                                                                                                                          |
| ------------- | --------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 🔴 Crítico    | Funcional | Saber qué hacer hoy: *"Cuando abro la app antes de entrenar, quiero ver mi plan del día de un vistazo, para no tener que pensar ni preguntar"*                                                                                |
| 🔴 Crítico    | Funcional | Consultar mi plan de dieta: *"Cuando toca comer, quiero ver qué me toca sin buscar ni decidir, para no improvisar y tirar por la borda el esfuerzo del gym"* ✅ *Validado por encuesta: 58% consulta antes de cada comida*    |
| 🔴 Crítico    | Emocional | Sentir que Inazio me sigue: *"Cuando mando mi check-in, quiero saber que alguien lo va a ver y ajustar mi plan, para no sentir que estoy solo en esto"*                                                                       |
| 🔴 Crítico    | Emocional | No complicarme la vida: *"Cuando abro la app con poco tiempo y cabeza llena, quiero que todo sea claro y rápido, para que la app sea un alivio y no una tarea más"*                                                           |
| 🟡 Importante | Emocional | Sentirme capaz: *"Cuando completo un entreno o una semana, quiero ver que lo estoy haciendo, para no tirar la toalla como otras veces"*                                                                                       |
| 🟡 Importante | Funcional | Registrar lo que hice: *"Cuando termino un entreno, quiero anotar el peso que levanté y cómo me fue, para que Inazio pueda ajustar la carga y yo pueda ver mi progreso"* ✅ *Subido de Secundario — peso levantado y RPE son las dos opciones más votadas en encuesta (12 y 11 votos)* |
| 🟡 Importante | Funcional | Adaptar el plan cuando algo no encaja: *"Cuando no tengo un alimento o la máquina del gym está ocupada, quiero una alternativa dentro del plan para no improvisar ni saltarme el día"* ✅ *JTBD nuevo — validado por encuesta: equivalencias de dieta fue la petición más recurrente (3 menciones independientes) y alternativas de ejercicio también aparece* |
| 🟡 Importante | Funcional | Hacer el check-in cuando toca: *"Cuando la app me avisa de que es momento de check-in, quiero mandar mis fotos y métricas fácil, para que Inazio pueda ajustar mi plan al siguiente ciclo"*                                   |
| 🟡 Importante | Funcional | Ver que mi inversión vale: *"Cuando llevo semanas en esto, quiero ver cómo evoluciono, para saber que los 70€ tienen sentido"*                                                                                                |
| 🟢 Secundario | Funcional | Lista de la compra: *"Cuando tengo que hacer la compra, quiero saber qué necesito esta semana, para no improvisar y comer mal por falta de planificación"* — generada automáticamente por la app                              |


**Notas de contexto:**

- La dieta varía cada 4 semanas (ciclo propio, distinto al ciclo de entreno + check-in de 14 días).
- La lista de la compra la genera la app automáticamente a partir del plan de dieta.
- La dieta no es igualmente relevante para todos los usuarios (58% la consulta antes de cada comida, 19% solo una vez a la semana) — la UI debe dar acceso fácil sin imponerla en primer plano.
- El JTBD de adaptar el plan (equivalencias + alternativas) es el que más aparece en las sugerencias abiertas. No es un problema de vez en cuando — es fricción cotidiana.

---

## 04 — CONTEXTO DE NEGOCIO

### ¿Qué necesita el negocio de este producto?

**Qué busca definir**
Los objetivos del negocio que el producto debe cumplir, las restricciones que no podés ignorar, las métricas de éxito, y los stakeholders cuya aprobación importa. El diseño no existe en el vacío.

**Por qué importa**
Un diseño brillante que ignora las restricciones del negocio no sirve. Si el pago es externo y no hay IAP, no podés proponer un checkout dentro de la app. Si el coach es el canal de adquisición principal, la app tiene que hacerle la vida más fácil al coach — no solo al usuario.

Esto diferencia al diseñador/PM junior del senior: el junior propone lo ideal, el senior propone lo posible dentro de las restricciones reales.

**Para tu rol**

- 🎨 Diseñadora → el contexto te protege de proponer soluciones imposibles o que contradigan la estrategia.
- 📋 PM → sos responsable de que el producto cumpla los objetivos de negocio. Definís las métricas antes de empezar a construir.
- ⭐ Para crecer → acostumbrate a preguntar "¿cuál es la métrica de éxito de esto?" en cada decisión. Esa pregunta sola te diferencia.

**Nota crítica — Stakeholder olvidado**
El usuario final es el coached. Pero el stakeholder más crítico para el negocio es el **coach**: si la app no le ahorra tiempo o le complica la vida, no la recomendará a sus clientes. Diseñar solo para el coached sin considerar la experiencia del coach es un error estratégico.

**Contexto — Asesorías V2**


| Dimensión           | Detalle                                                                 |
| ------------------- | ----------------------------------------------------------------------- |
| Objetivo            | Tier coached con mayor retención a 30/60/90 días que free y suscripción |
| Restricción dura    | Pago externo, sin IAP. La app no gestiona cobros                        |
| Métrica principal   | Retención del coached. Secundaria: NPS                                  |
| Stakeholder crítico | Los coaches — si no les ahorra trabajo, no recomendarán                 |
| Restricción técnica | Una sola app para 3 tiers, shell diferente en runtime                   |
| Estado actual       | Cero pantallas V2 implementadas                                         |


**Prioridades de producto — validadas por el equipo**

El equipo lleva acumulando feedback de ~600k–1M interacciones con usuarios (vía Paule + reuniones con Jorge). Las prioridades ya están definidas sin necesidad de encuesta:


| Prioridad | Área                   | Justificación                                                                          |
| --------- | ---------------------- | -------------------------------------------------------------------------------------- |
| 🔴 Alta   | **Wearables**          | ~50-60% de España tiene wearable; sin integración, esos usuarios no usan la app        |
| 🔴 Alta   | **Entrenamientos**     | Ver peso anterior + gráficos de progreso = adherencia. La UI nueva ya es más intuitiva |
| 🔴 Alta   | **Diseño**             | Desequilibrio visual actual detectado                                                  |
| 🟡 Media  | **Lista de la compra** | Muy pedida, pero no es must-have — puede ir después                                    |


---

## 05 — SUPOSICIONES Y RIESGOS

### ¿Qué asumimos como verdadero sin haberlo validado?

**Qué busca definir**
Todo lo que el equipo asume como verdadero pero no ha verificado. Se ordenan por dos ejes: impacto si estamos equivocados, y certeza que tenemos. Las más peligrosas: alto impacto + baja certeza.

**Por qué importa**
Las suposiciones no identificadas se convierten en bugs de producto. Mejor descubrirlas en papel que después de meses de desarrollo. La diferencia entre un diseñador/PM bueno y uno mediocre es la capacidad de nombrar las propias suposiciones antes de que fallen.

**Para tu rol**

- 🎨 Diseñadora → las suposiciones de UX se validan con prototipos y tests de usabilidad. Sin código.
- 📋 PM → las suposiciones de negocio se validan con entrevistas y datos.
- ⭐ Para crecer → antes de diseñar cualquier pantalla, preguntate: *"¿Qué tendría que ser verdad para que esto funcione?"*

**Cómo priorizarlas**

```
Impacto ALTO + Certeza BAJA  → validar antes de construir cualquier cosa
Impacto ALTO + Certeza ALTA  → son hechos, documentar
Impacto BAJO + Certeza BAJA  → monitorear, no bloquear
Impacto BAJO + Certeza ALTA  → ignorar
```

**Suposiciones — Asesorías V2**


| Riesgo     | Suposición                                                                                                    | Estado                                                                |
| ---------- | ------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------- |
| 🔴 Alto    | El coach quiere y puede gestionar clientes desde la app                                                       | Abierta                                                               |
| 🔴 Alto    | El usuario llega con expectativas alineadas a lo que la app ofrece                                            | Abierta                                                               |
| 🟡 Medio   | La comunicación coach-usuario puede ser asíncrona (no tiempo real)                                            | Abierta                                                               |
| 🟡 Medio   | El coach genera el plan manualmente y lo carga en el sistema                                                  | Abierta                                                               |
| 🟢 Bajo    | El usuario tiene smartphone moderno y conexión estable                                                        | Abierta                                                               |
| 🟢 Bajo    | El usuario tiene experiencia previa en fitness                                                                | Abierta                                                               |
| ✅ Validada | El usuario quiere ver el peso anterior y gráficos de progreso — es el principal motor de adherencia           | Confirmada por feedback acumulado                                     |
| ✅ Validada | La integración con wearables es un bloqueante real: usuarios con wearable no usan la app porque no se conecta | Confirmada por quejas recurrentes                                     |
| ✅ Validada | La nueva UI de entrenamientos es más intuitiva que la anterior                                                | Confirmada por feedback cualitativo (usuarios no afiliados al equipo) |


---

## 06 — PREGUNTAS A RESOLVER ANTES DE FASE 2

### ¿Qué debe estar claro antes de wireframear?

**Qué busca definir**
Las preguntas que DEBEN tener respuesta antes de empezar la arquitectura de información. Esta lista define cuándo estás lista para avanzar. Es tu *Definition of Ready*.

**Por qué importa**
Una pregunta sin respuesta en Fase 1 se convierte en retrabajo en Fase 3, 4 o 5. El patrón más costoso en producto: diseñar pantallas hermosas para un flujo que hay que tirar porque nadie preguntó algo básico al principio.

**Para tu rol**

- 🎨 Diseñadora → te protegen de diseñar el flujo equivocado.
- 📋 PM → sos responsable de conseguir las respuestas: hablar con el coach, tech, usuarios piloto.
- ⭐ Para crecer → aprendé a distinguir qué podés asumir provisionalmente y qué bloquea el diseño. No todas las preguntas son bloqueantes.

**Preguntas — Asesorías V2**


| Urgencia      | Pregunta                                                                               |
| ------------- | -------------------------------------------------------------------------------------- |
| 🚫 Bloqueante | ¿El coach gestiona clientes en esta app o tiene dashboard separado?                    |
| 🚫 Bloqueante | ¿Cómo se comunica el usuario con el coach? ¿Chat, notas asíncronas, WhatsApp externo?  |
| 🚫 Bloqueante | ¿Qué pasa si el usuario activa el tier coached pero todavía no tiene plan asignado?    |
| ❓ Importante  | ¿Quién genera el plan — el coach manualmente o el sistema automáticamente?             |
| ❓ Importante  | ¿Hay check-ins periódicos? ¿Con qué frecuencia, quién los inicia, qué formato tienen?  |
| ❓ Importante  | ¿El usuario coached puede ver su historial de V1 si ya era usuario antes del upgrade?  |
| 💡 A explorar | ¿Qué métricas registra el usuario? ¿Peso, fotos, RPE? ¿Obligatorio u opcional?         |
| 💡 A explorar | ¿Las notificaciones del tier coached son diferentes a las de V1? ¿Quién las configura? |


---

## 07 — ENCUESTA DE USUARIO

### Validar hipótesis con datos reales antes de diseñar

**Cuándo hacerla**
Después de completar las secciones 02 a 06 — no antes. Las secciones anteriores definen exactamente qué no sabés y qué necesitás validar. Si mandás la encuesta sin haberlas hecho, no sabés qué preguntar y terminás con datos que no podés usar.

```
02 Proto-persona     → genera hipótesis sobre quién es el usuario
03 JTBDs             → genera hipótesis sobre qué necesita
05 Suposiciones      → lista lo que no sabés
06 Preguntas         → lista lo que necesitás saber
         ↓
07 ENCUESTA          ← cada pregunta resuelve una suposición o cierra una pregunta abierta
         ↓
   Analizar resultados → actualizar proto-persona y JTBDs → cerrar checklist → pasar a Fase 2
```

**Nota de contexto — conocimiento acumulado del equipo**
El equipo ya lleva ~600k–1M interacciones con usuarios reales (conversaciones vía Paule, reuniones con Jorge, feedback de clientes potenciales). Las prioridades principales ya están validadas sin necesidad de encuesta formal. La encuesta en este proyecto **complementa** ese conocimiento — no lo reemplaza ni lo bloquea. Su valor está en cuantificar lo que ya se sabe cualitativamente y en detectar matices que el feedback informal puede haber perdido.

**Por qué importa**
La encuesta convierte hipótesis en datos. Sin ella, la proto-persona y los JTBDs son suposiciones propias del equipo — con ella, son decisiones respaldadas por usuarios reales. Es especialmente crítica en este proyecto porque el usuario coached todavía no existe en volumen: hay que entender al usuario actual (free/suscripción) y su disposición a pagar por coaching.

**Para tu rol**

- 🎨 Diseñadora → los resultados ajustan la proto-persona y pueden cambiar qué pantallas son prioritarias.
- 📋 PM → los resultados validan (o invalidan) las suposiciones de negocio antes de comprometer recursos de desarrollo.
- ⭐ Para crecer → aprendé a diseñar encuestas con intención. Cada pregunta debe tener un objetivo claro: "si la respuesta es X, entonces tomamos la decisión Y".

**Cómo diseñarla bien**


| Criterio              | Guía                                                                                 |
| --------------------- | ------------------------------------------------------------------------------------ |
| Longitud              | Máximo 8-10 preguntas — más de eso, la gente abandona                                |
| Tipos de pregunta     | 2-3 abiertas (cualitativas) + el resto cerradas (cuantitativas)                      |
| Orden                 | Empezar con preguntas fáciles y contextuales, las más sensibles al final             |
| Objetivo por pregunta | Cada pregunta debe resolver UNA suposición o pregunta de las secciones 05/06         |
| A quién mandar        | Usuarios de distintos tiers si es posible: free, suscripción y coached si ya existen |


**Preguntas sugeridas — Asesorías V2**

> Encuesta dirigida exclusivamente a usuarios del tier coached (ya tienen coach asignado y están pagando el servicio).

| #   | Pregunta                                                                                                                                                                          | Tipo        | Qué valida                                          |
| --- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------- | --------------------------------------------------- |
| 1   | ¿Con qué frecuencia usas la app? (varias veces al día / 1 vez al día / cada 2 días / 1 vez a la semana / menos)                                                                   | Cerrada     | Engagement base                                     |
| 2   | ¿Cuándo consultas la pantalla de dieta? (antes de cada comida / 1 vez al día y me planeo el menú / cada 3 días / 1 vez a la semana)                                               | Cerrada     | Patrón de uso de dieta → decisiones de UI           |
| 3   | Cuando tienes una duda sobre tu entreno o dieta, ¿qué haces? (escribo por WhatsApp / busco en la app / espero al check-in / lo resuelvo solo)                                     | Cerrada     | Comportamiento real — por qué salen de la app       |
| 4   | ¿Qué es lo que más te falta en la app ahora mismo?                                                                                                                                | Abierta     | Frustraciones directas del coached                  |
| 5   | Después de un entreno, ¿qué te gustaría poder registrar? (peso levantado / fotos de progreso / cómo me fue la serie / esfuerzo percibido / nada, ya lo hace el wearable)          | Multiselect | Métricas a implementar y orden de prioridad         |
| 6   | ¿Qué información sobre tu progreso querrías que Inazio pueda ver?                                                                                                                 | Abierta     | Métricas para el dashboard del coach                |
| 7   | ¿Qué te haría sentir que Inazio realmente te está siguiendo?                                                                                                                      | Abierta     | JTBD emocional — sentir acompañamiento              |


**Cómo analizar los resultados**

1. Buscar patrones en las respuestas abiertas — agrupar por tema
2. Para cada suposición de la sección 05: ¿los datos la confirman o la refutan?
3. Para cada pregunta de la sección 06: ¿tenés ahora una respuesta?
4. Actualizar la proto-persona con lo que aprendiste
5. Ajustar la priorización de JTBDs si alguno cambió
6. Documentar qué suposiciones siguen abiertas y decidir si bloquean el avance a Fase 2

---

### Resultados — Encuesta enviada (n=29)

Encuesta enviada a usuarios coached activos. 29 respuestas recibidas.

**Pregunta 1: ¿Con qué frecuencia usas la app?**

- Varias veces al día: 23 (79%)
- 1 vez al día: 4 (14%)
- Cada dos días: 1 (3%)
- 1 vez a la semana: 0
- Otro (para las revisiones): 1 (3%)

**Pregunta 2: ¿Cuándo consultas la pantalla de dieta?**

- Antes de cada comida: 15 (58%)
- 1 vez al día (me planeo el menú): 6 (23%)
- Cada 3 días: 0
- 1 vez a la semana: 5 (19%)
- Otro: 0

**Pregunta 3: Cuando tienes una duda sobre tu entreno o dieta, ¿qué haces?**

- Escribo por WhatsApp: 15
- Busco en la app: 14
- Espero a la revisión: 0
- Lo resuelvo solo: 5

**Pregunta 4 (multiselect): ¿Qué te gustaría poder registrar después de un entreno?**

- Peso levantado: 12
- Esfuerzo percibido (RPE): 11
- Que lo registre todo un wearable automáticamente: 8
- Cómo fue la serie: 5
- Fotos de progreso: 1

**Sugerencias y peticiones abiertas (agrupadas por tema):**

Dieta (tema más recurrente):
- Equivalencias para sustituir alimentos por otros (mencionado 3 veces de forma independiente)
- Más alimentos disponibles en la opción de equivalencias
- Añadir recetas para hacer varios platos con los mismos productos y que no sea monótono
- El apartado de dieta podría ofrecer más variedad y un sistema para sustituir alimentos
- Poder imprimir las dietas

Entrenamiento:
- Pesos de la última sesión visibles desde la pantalla del entreno, sin tener que salir a buscarlos
- Indicar el peso que debería levantar en las siguientes sesiones según la evolución del usuario
- Alternativas a ejercicios cuando el gimnasio está petado y no se puede usar la máquina
- Poner ejercicios de cardio con más variedad (solo aparece cinta, sin configurar elevación)

Revisiones / check-in:
- Medir zonas del cuerpo en las revisiones (medidas corporales)
- Añadir porcentaje graso a las revisiones
- Añadir sensaciones y emociones a las revisiones
- Notificación para avisar cuándo toca la revisión

Wearables:
- Integración con wearable (mencionado explícitamente)
- Poder sincronizar o registrar los pasos reales del día, porque muchos días no llevan el móvil encima y el recuento difiere

---

### Análisis — ¿Qué aprendemos?

**Engagement muy alto confirmado.** El 79% usa la app varias veces al día. No es una app que se abre una vez y se olvida — es una herramienta de consulta constante. Cualquier fricción se nota inmediatamente.

**La dieta se consulta en el momento de comer.** El 58% la abre antes de cada comida. Esto tiene una implicación de diseño directa: la pantalla de dieta tiene que ser extremadamente rápida de acceder y legible de un vistazo, desde el estado que sea (pantalla bloqueada, desde el home). No puede requerir navegar varios niveles.

**WhatsApp y la app como canales de dudas casi igualados (15 vs 14).** Esto refuta la suposición de que "el usuario usa WhatsApp por defecto para todo". Casi la mitad ya busca en la app primero. Si la app tiene mejor información (equivalencias, peso sugerido, alternativas de ejercicio), parte de ese tráfico de WhatsApp se puede absorber. Es una oportunidad clara.

**Registro post-entreno: peso y RPE son lo que importa, no las fotos.** Peso levantado (12) y esfuerzo percibido (11) están prácticamente empatados en primera posición. Las fotos de progreso tienen solo 1 voto — confirma que son para el check-in periódico, no para el registro diario. El wearable automático (8 votos) también es relevante.

**El sistema de equivalencias de dieta es la petición más recurrente.** Aparece mencionada de forma independiente por al menos 3 usuarios distintos, más referencias indirectas en otras respuestas. No es un nice-to-have — es una fricción activa que la gente está experimentando hoy.

**El check-in necesita más campos de los previstos.** Los usuarios piden medidas corporales, porcentaje graso y sensaciones/emociones además del peso y las fotos. Esto expande el scope del flujo de check-in.

**Wearables: confirmado como prioridad crítica por los propios usuarios.** Aparece tanto en las respuestas cuantitativas (8 votos en "que lo registre el wearable") como en comentarios abiertos.

---

### Impacto en la arquitectura — cambios sobre las hipótesis iniciales

Estos resultados obligan a actualizar tres cosas antes de wireframear:

1. La pantalla de dieta necesita un subsistema de equivalencias. Era una pantalla simple; ahora tiene una capa de interacción adicional.
2. El flujo de check-in se expande: medidas corporales + % graso + sensaciones son campos que hay que incluir o al menos contemplar.
3. En entrenamiento, el peso anterior tiene que ser visible in-line en la pantalla de sesión, sin navegación adicional. Es la petición más concreta y directa de toda la encuesta.

Estos cambios están incorporados en el documento de Fase 2.

---

## Checklist de salida — ¿Cuándo paso a Fase 2?

- Problem statement escrito en 1-2 oraciones y validado con el equipo
- Proto-persona definida con motivaciones y frustraciones reales
- JTBDs priorizados — top 3 críticos identificados
- Contexto de negocio documentado: objetivo, restricciones, métricas
- Suposiciones ordenadas por riesgo
- Preguntas bloqueantes resueltas (las 3 marcadas como 🚫)
- Encuesta enviada, resultados analizados y proto-persona actualizada

