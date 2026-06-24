# Análisis de competencia — Reseñas (extracción de datos)

> **Naturaleza de este documento:** extracción de datos cualitativos, **sin interpretación ni propuestas de diseño**. Todos los textos son *verbatims literales* (copiados tal cual, con sus erratas).
> **Corpus:** 1.424 reseñas reales · App Store España (`country=es`) + Google Play ES (AimHarder). Datos crudos en [reviews-raw.csv](reviews-raw.csv).
> **Apps:** Hevy (500) · AimHarder (690) · Symmetry (172) · Fitbod (62).
> **Fecha de scrape:** junio 2026.

## Nota metodológica (leer antes de los conteos)
- **Reparto por nota:** POSITIVAS (4-5★) = 1.167 · NEGATIVAS (1-3★) = 257.
- **Distribución por app:** Hevy `{5★:454, 4★:42, 3★:3, 2★:1, 1★:0}` · AimHarder `{5★:426, 4★:89, 3★:43, 2★:30, 1★:102}` · Symmetry `{5★:88, 4★:27, 3★:16, 2★:10, 1★:31}` · Fitbod `{5★:28, 4★:13, 3★:9, 2★:4, 1★:8}`.
- Los conteos por categoría son **"nº de reseñas que mencionan X"** mediante coincidencia de palabras clave; **las categorías solapan** (una reseña puede contar en varias). No son particiones excluyentes.
- En **AimHarder** hay reseñas con **nota ≠ sentimiento del texto** (p. ej. 5★ cuyo texto es una queja de cierre de sesión). Se conserva el verbatim tal cual.

---

## 1. CONTEXTOS DE USO mencionados

| # | Contexto de uso (verbatim) | App | Nota |
|---|----------------------------|-----|------|
| C1 | *"La mejor app para llevar mi seguimiento continuo en el gym y ver mis progresos y estadísticas, diarias, semanales, mensuales y anuales"* | Hevy | 5★ |
| C2 | *"Muy fácil de usar y cómoda para el gym! Yo la uso todos los días"* | Hevy | 5★ |
| C3 | *"Ideal para el primer día en el gimnasio porque te propone ejercicios, te dice cómo hacerlos y te felicita cuando te superas"* | Hevy | 5★ |
| C4 | *"Llevaba 15 años sin entrar al gym y 55 años de edad, me ha resultado fácil e intuitiva"* | Hevy | 5★ |
| C5 | *"Me ha encantado y me ha devuelto la motivación después de dejar el CrossFit"* | Hevy | 5★ |
| C6 | *"te ayuda… sobre todo en hacer una guía, para no estar inventando qué hacer todos los días"* | Hevy | 5★ |
| C7 | *"De lo mejor que he probado para gym en casa con tu propio equipo"* | Fitbod | 5★ |
| C8 | *"He conseguido adherencia a hacer ejercicios de fuerza solo en el gimnasio. Sin experiencia previa usando app ni controlando sala"* | Fitbod | 5★ |
| C9 | *"puedo registrar mis entrenamientos del box muy bien"* | AimHarder | 5★ |
| C10 | *"no me carga ni las reservas, ni los wod, ni el perfil"* (uso: reservar clases + ver WOD del box) | AimHarder | 1★ |
| C11 | *"empecé apuntando en papel, luego en el móvil en notas… pero mucho mejor con esta app"* | Hevy | 5★ |
| C12 | *"Se acabó el excel y entrenar mirando el pantallazo en el móvil!"* | Hevy | 5★ |
| C13 | *"se sincroniza con Apple Watch"* / *"ya no tengo que andar pendiente del móvil"* (uso con wearable durante el entreno) | Hevy | 5★ |
| C14 | *"para apuntarse a las clases y subir resultados"* | AimHarder | 5★ |

---

## 2. JOBS TO BE DONE revelados (por contexto)

> Clasificación pedida por la plantilla (Funcional / Emocional / Social), cada una respaldada por verbatim. Sin inferencias añadidas.

| Contexto | Tipo | Job (qué contrata) | Verbatim de respaldo |
|----------|------|--------------------|----------------------|
| C1, C2 (gym, a diario) | **Funcional** | Llevar registro de pesos/series y ver estadísticas | *"para no olvidarme de los pesos que utilizo o ver las mejoras al momento"* (Hevy 5★) |
| C1 (gym, a diario) | **Emocional** | Sentir superación / ilusión continuada | *"después de 25 entrenamientos todavía tengo ilusión de seguir superándome"* (Hevy 5★) |
| C1 (gym) | **Social** | Compararse/competir con otros | *"poder compararte con otra gente y ver tu rango… da mucha motivación y ganas de seguir"* (Hevy 5★) · *"I miss having the opportunity to compete with my friends"* (Hevy 4★) |
| C3, C8 (primer día / principiante) | **Funcional** | Que le digan qué ejercicios hacer y cómo | *"te propone ejercicios, te dice cómo hacerlos"* (Hevy 5★) |
| C3, C8 (principiante) | **Emocional** | Quitar la inseguridad de no saber en el gym | *"Sin experiencia previa usando app ni controlando sala, la recomiendo mucho"* (Fitbod 5★) |
| C5, C4 (retomar tras parón) | **Emocional** | Recuperar la motivación / volver | *"me ha devuelto la motivación después de dejar el CrossFit"* (Hevy 5★) |
| C6 (no improvisar) | **Funcional** | Tener una guía para no decidir cada día | *"para no estar inventando qué hacer todos los días"* (Hevy 5★) |
| C7 (gym en casa) | **Funcional** | Rutina adaptada al equipo disponible | *"para gym en casa con tu propio equipo"* (Fitbod 5★) |
| C9, C10, C14 (box / CrossFit) | **Funcional** | Reservar clase y registrar el WOD | *"registrar mis entrenamientos del box"* (AimHarder 5★) |
| C9, C14 (box) | **Social** | Subir/compartir resultados y ranking del box | *"a veces no puedo… ni compartir resultados"* (AimHarder 1★) · *"ver el ranking del box"* (AimHarder 1★) |
| C11, C12 (sustituir papel/excel) | **Funcional** | Reemplazar libreta/Excel por registro digital | *"Se acabó el excel"* (Hevy 5★) · *"empecé apuntando en papel… mucho mejor con esta app"* (Hevy 5★) |
| C1, C5 (constancia) | **Emocional** | Sentir disciplina / gamificación del hábito | *"esta app ha conseguido motivarme y gamificar el ir al gym"* (Hevy 5★) · *"la motivación de la racha estilo duolingo"* (Symmetry 5★) |

---

## 3. QUEJAS RECURRENTES (reseñas 1-3★, base 257)

> Conteo = reseñas negativas que mencionan la categoría (solapan).

| Categoría | Frecuencia | Verbatims literales |
|-----------|-----------:|---------------------|
| **Rendimiento** | **101** | *"Se cierra continuamente, no carga y se queda pillada"* (AimHarder 2★) · *"it constantly freezes and doesn't store the reps properly when you use your Apple Watch"* (Fitbod 1★) · *"Tengo que desinstalar y volver a instalar todas las semanas, porque si no no puedo ni subir entrenamientos"* (AimHarder 1★) · *"Every time I'm doing a workout and I want to log an exercise is swiching me to the next exercise"* (Fitbod 3★) |
| **Funcionalidad Faltante** | **48** | *"falta idioma español sincronización a todos"* (Fitbod 3★) · *"Me encantaría que se pudiera sincronizar con apple fitness o health"* (AimHarder 3★) · *"Falta un método de pago como Apple Pay"* (AimHarder 2★) · *"Keeps asking to use an amount of weight way above the equipment limit… Waiting for this fix for over a year"* (Fitbod 1★) |
| **Precio** | **31** | *"Típica app que después de hacer el test y pedirte tus datos, o pagas o no puedes ni abrirla para ojear"* (Fitbod 1★) · *"La app no es gratis te hacen la mentira para poder cobrarte un plan… están en la lista de apps gratis. Mentirosos"* (Symmetry 1★) · *"Más caro que el gym"* (Fitbod 1★) · *"para apuntar el peso hay que pagar el plan pro… Me vuelvo a la aplicación de notas del móvil"* (Symmetry 1★) |
| **Usabilidad** | **26** | *"Muy poco intuitiva, demasiada info"* (AimHarder 1★) · *"Me cuesta encontrar las cosas, demasiadas opciones en cada pantalla"* (AimHarder 3★) · *"las pantallas son feas feas, demasiadas opciones… no se ve en horizontal en el iPad"* (AimHarder 2★) · *"lo de poner en fav los ejercicios es más molestia que buscarlo, poco intuitivo"* (AimHarder 3★) |
| **Atención al cliente** | **4** | *"Correos enviados a soporte y no sirven de nada"* (Symmetry 1★) · *"who is the it support if any?!"* (AimHarder 1★) |
| **Otros / sin categoría** | **88** | *"Keeps asking to use an amount of weight way above the equipment limit. For example 10 reps with 200lb. The max load on the machine is 150"* (Fitbod 1★) · *"Me obliga a subir los resultados cuando no quiero"* (AimHarder 1★) |

---

## 4. ELOGIOS RECURRENTES (reseñas 4-5★, base 1.167)

> Conteo = reseñas positivas que mencionan la categoría (solapan). 916 positivas no caen en ninguna categoría específica (elogio genérico).

| Categoría | Frecuencia | Verbatims literales |
|-----------|-----------:|---------------------|
| **Usabilidad** | **100** | *"súper fácil de usar… Súper intuitiva y muy completa"* (Hevy 5★) · *"Llevaba 15 años sin entrar al gym y 55 años de edad, me ha resultado fácil e intuitiva"* (Hevy 5★) · *"Todo funciona bien y es super intuitiva. 100% recomendable"* (Hevy 5★) |
| **Funcionalidad Faltante** *(elogio "me encanta PERO falta…")* | **92** | *"lo único que creo que falta es algo de rangos para cada músculo, poder compararte con otra gente"* (Hevy 5★) · *"Solo echo en falta las calorías… Si las contase, tendría mis 5 estrellas"* (Hevy 4★) · *"quizás le faltan más actividades y mejor conectivas con garmin y Apple Health"* (Hevy 5★) |
| **Precio** *(elogio al gratis)* | **48** | *"No es necesaria la versión de pago, muy buena aplicación"* (Hevy 5★) · *"se puede usar con mucha efectividad sin pagar nada, gracias por tanto hevy"* (Hevy 5★) · *"no quieren cobrarte todo el tiempo"* (Hevy 5★) |
| **Rendimiento** *(elogio a la estabilidad)* | **43** | *"Funciona perfecto, la base de datos es muy buena y nunca da fallos"* (Hevy 5★) · *"no da errores y no tiene publicidad"* (Hevy 5★) |
| **Atención al cliente** | **1** | *"escribí a Aimharder y me lo dijeron ellos"* (AimHarder 5★) |
| **Otros / elogio genérico** | **916** | *"La mejor app para el gym. Práctica, sin complicaciones, fácil de usar… Llevo usándola 4 años"* (Hevy 5★) · *"esta app ha conseguido motivarme y gamificar el ir al gym. Un 10/10"* (Hevy 5★) · *"Gracias hevy, por hacer de un entrenamiento una diversión"* (Hevy 5★) |

---

## 5. COMPETIDORES O ALTERNATIVAS mencionados

> Apps/herramientas/métodos que los usuarios dicen usar, comparar o sustituir. (Las auto-menciones del propio nombre de la app no se cuentan como alternativa.)

| Alternativa | Menciones | Verbatim literal |
|-------------|----------:|------------------|
| **Strava** | 6 | *"it connects with Strava automatically and the statistics results quite useful"* (Hevy 5★) · *"Es como strava pero del gym"* (Hevy 5★) · *"me gustaría poder vincularla con Strava"* (AimHarder 5★) |
| **Symmetry** *(comparada vs Hevy)* | 12 | *"Mejor que symmetry. Muchas más opciones gratis y te muestra el progreso real"* (Hevy 5★) · *"While it is better than Symmetry and Lyfta, I miss… compete with my friends"* (Hevy 4★) |
| **Lyfta** | (en cita de Symmetry) | *"it is better than Symmetry and Lyfta"* (Hevy 4★) |
| **Notas del móvil** | 3 | *"empecé apuntando en papel, luego en el móvil en notas… pero mucho mejor con esta app"* (Hevy 5★) · *"Me vuelvo a la aplicación de notas del móvil que es gratis"* (Symmetry 1★) |
| **Libreta / papel** | 2-3 | *"Ideal para llevar tus entrenamientos y no usar libreta"* (Hevy 5★) · *"empecé apuntando en papel"* (Hevy 5★) |
| **Excel** | 2 | *"Se acabó el excel y entrenar mirando el pantallazo en el móvil!"* (Hevy 5★) · *"Es como un Excel, todo tienes todas tus marcas"* (Hevy 5★) |
| **ChatGPT / GPT** | 1 | *"la combinación con el GPT que tiene desde ChatGPT es muy potente"* (Hevy 5★) |
| **Strong** | 1 | *(mención en comparativa de apps de gym)* |
| **Apple Health / Apple Watch / Garmin / Fitbit** *(sincronización pedida)* | varias | *"sería un puntazo sincronizar con apple fitness o health"* (AimHarder 3★) · *"mejor conectivas con garmin y Apple Health"* (Hevy 5★) · *"sincronizarse con Fitbit"* (Fitbod 3★) |
| **"Otras apps de CrossFit"** | 2 | *"muy lenta a la hora de escribir los wods en comparación con otras apps de crossfit"* (AimHarder 4★) |

---

*Fin de la extracción. Sin interpretación. Para el análisis interpretado (oportunidades, soluciones, experimentos) ver [opportunity-solution-tree-retencion.md](../opportunity-solution-tree-retencion.md).*
