# Reunión con Ignacio — 16 marzo 2026
**El Método App · V2 Asesorías**

---

## Contexto

Estamos diseñando la segunda versión de la app de asesorías. El objetivo es acercarla a la experiencia de la app automática: más contenido, más interacción y más visibilidad del progreso del cliente. La V1 sigue en producción mientras diseñamos V2.

---

## Novedades principales acordadas con Jorge

**1. Tres líneas de entrenamiento**
En V1 todos los clientes siguen la misma línea. En V2 habrá tres:
- Fuerza
- HIIT / cardio (hi-docs)
- Híbrido


El cliente elige su línea al empezar. Si quiere cambiarla, se lo comunica al coach (por WhatsApp) y el coach lo gestiona desde el dashboard.

**2. Dashboard del coach — más datos**
El dashboard web recibirá nuevas secciones para que el coach tenga mejor visibilidad de lo que hace el cliente:
- Pasos diarios
- Calorías quemadas
- Actividades registradas
- Días de entreno (con calendario)

**3. Calendario en la app del cliente**
El cliente podrá ver y planificar sus días de entreno. El coach podrá consultar ese calendario desde el dashboard para saber cuándo está entrenando cada cliente.

**4. Lista de la compra**
Desde la sección de Dieta, el cliente podrá generar una lista de la compra basada en su plan semanal. Como el plan ya tiene opciones de sustitución por comida, la lista se personalizará según las opciones que haya elegido. Opción de descarga incluida.

**5. Muro / canal de comunidad**
Se quiere añadir una sección de comunidad dentro de la app. Hay dos modelos posibles:

- **Modelo A — Canal de difusión:** solo Ignacio publica (vídeos, posts, tips). Los clientes pueden reaccionar y quizás comentar.
- **Modelo B — Muro abierto:** los clientes interactúan entre ellos además de con Ignacio.

Jorge tiene dudas sobre el modelo B a escala (3.000+ clientes activos). La decisión está abierta.

**6. Definición del objetivo de pasos por los coaches**
Que los coaches puedan definir el objetivo de pasos de cada cliente

---

## Arquitectura propuesta — 5 tabs

Con todo el contenido nuevo, proponemos reorganizar la navegación en 5 tabs:

| Tab | Qué incluye |
|---|---|
| **Home** | Estado del ciclo, pasos, acceso al check-in, acceso rápido a progreso |
| **Entreno** | Sesiones asignadas, calendario de planificación e historial |
| **Dieta** | Plan del día, detalle de comidas, lista de la compra |
| **Comunidad** | Ranking + Muro |
| **Perfil** | Progreso (gráfica de peso + fotos check-in), datos personales, configuración |

> **Cambio relevante:** Progreso actualmente tiene tab propia. La propuesta es integrarlo dentro de Perfil para liberar espacio de navegación. Necesitamos la opinión de Ignacio sobre esto.

---

## Decisiones abiertas para esta reunión

| # | Decisión | Opciones |
|---|---|---|
| 1 | Modelo del muro | Canal de difusión vs. comunidad abierta |
| 2 | Progreso | Tab propia vs. dentro de Perfil |
| 3 | Calendario | Solo historial vs. historial + planificación del cliente |
| 4 | Lista de la compra | Prioridad respecto al resto de funcionalidades |

---

## Preguntas para la reunión

### Sobre el negocio y los clientes
- ¿Cuál es el perfil de cliente que más usa la app hoy? ¿Hay diferencias entre los que entrenan fuerza vs cardio?
- ¿Qué es lo que más te piden los clientes que la app no tiene ahora mismo?
- ¿Hay algo en V1 que los clientes usen poco o que sientas que no funciona?

### Sobre el muro
- ¿Con qué frecuencia publicarías contenido si hubiera un canal? ¿Tienes ya ese contenido (vídeos, posts) o habría que producirlo?
- ¿Los clientes se conocen entre ellos o la comunidad es muy fragmentada?
- ¿Te preocupa moderar comentarios entre clientes a escala?

### Sobre el entrenamiento
- ¿Los clientes de hi-docs o híbrido son muy diferentes a los de fuerza en motivación o uso de la app?
- ¿Cómo funciona hoy el proceso de cambio de línea — ocurre con frecuencia?

### Sobre el check-in y el progreso
- ¿Los clientes consultan su progreso frecuentemente o solo en el momento del check-in?
- ¿Las fotos del check-in son algo que los clientes valoran ver o les genera inseguridad?

### Sobre la navegación
- ¿Usas tú mismo la app? ¿Qué tabs usas más como coach?
- ¿Qué es lo primero que debería ver un cliente nuevo nada más entrar?

---

## Notas de la reunión

_Completar durante / después de la reunión_

### Decisiones tomadas
-

### Pendientes
-

### Próximos pasos
-
