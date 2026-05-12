# Coached App — Spec General (V2)

Especificación de la experiencia de usuario del tier **Coached** dentro de la app El Método.

---

## Contexto

La app El Método tiene 3 tiers de usuario:

```
FREE / SUSCRIPTOR          COACHED
─────────────────          ──────────────────────────────────
Home (pasos, ranking)  →   Home (progreso personal, ciclo)
Entreno (programas)    →   Entreno (rutina asignada por coach)
Explora (recetas)      →   Dieta (plan asignado por coach)
Comunidad (ranking)    →   Comunidad (ranking compartido)
                           Guías (contenido premium)
```

El usuario coached **no ve los programas genéricos** de suscripción. Su contenido es 100% asignado y gestionado desde el dashboard por su coach, bajo la marca de Inazio.

El mismo usuario puede pasar de free → suscriptor → coached sin cambiar de app. El router detecta el tier en runtime y sirve la navegación correspondiente.

---

## Arquitectura de Navegación V2

5 tabs en la barra inferior:


| Tab           | Icono    | Descripción                                                                                               |
| ------------- | -------- | --------------------------------------------------------------------------------------------------------- |
| **Home**      | casa     | Panel de visualizacion de pasos y otras metricas (calorias, racha, tiempo, distancia) diarios y semanales |
| **Entreno**   | pesas    | Rutina de la semana asignada por el coach + estadisticas                                                  |
| **Dieta**     | tenedor  | Plan de alimentación asignado por el coach                                                                |
| **Comunidad** | personas | Ranking global + grupos (compartido con V1)                                                               |
| **Perfil**    | usuario  | Ajustes, check-in, historial de progreso                                                                  |


> **Nota de diseño**: La shell de zona es visualmente diferente a subscripcion/free para que el usuario perciba que está en un nivel premium. Paleta, tipografía y tono más personales.

---

## Core Loop del Usuario Coached

El ciclo de 14 días es el motor del producto. Todo gira alrededor de él.

```
DÍA 1 ─── Coach sube rutina + dieta ─────────────────────────────────┐
           │                                                           │
           ▼                                                           │
   Usuario recibe notificación push                                    │
   "Tu coach ha actualizado tu plan"                                   │
           │                                                           │
           ▼                                                           │
   Días 1–14: Usuario entrena con su rutina                            │
              y sigue su dieta                                         │
           │                                                           │
DÍA 14 ── Ventana de check-in se abre (7 días para enviar)            │
           │                                                           │
           ▼                                                           │
   Usuario envía check-in:                                             │
   - Fotos (frente, lado, espalda)                                     │
   - Peso actual                                                       │
   - Valoraciones (entreno, dieta, rendimiento, adherencia)           │
   - Campo libre (comentarios)                                         │
           │                                                           │
           ▼                                                           │
   Coach recibe notificación en dashboard                              │
   Coach revisa y actualiza plan ──────────────────────────────────────┘
```

---

## Sección por Sección

### 1. Home

**Propósito**: Panel de actividad diaria con el anillo de pasos como protagonista. El ciclo coached vive aquí de forma contextual y no invasiva.

**La home coached es la misma que V1 en estructura** (anillo de pasos, métricas, vista diaria/semanal, actividades) con una capa adicional para el ciclo de asesoría.

**Métricas de actividad** (idénticas a V1):

- Anillo de pasos del día como elemento principal
- Tabs de métricas: Pasos / Calorías / Racha / Tiempo / Distancia
- Vista diaria y semanal (gráfico por día de la semana)
- Registro manual de actividades
- Integración con wearable (calorías sumadas si está conectado)
- Sección "Tus marcas en nuestra comunidad" (ranking, compartido con V1)

**Capa coached — estado del ciclo**:


| Momento del ciclo             | Qué aparece en Home                                           |
| ----------------------------- | ------------------------------------------------------------- |
| Días 1–7 (inicio)             | Indicador discreto: "Ciclo · Día 5 de 14"                     |
| Días 8–14 (ventana check-in)  | Card/banner prominente: "Es tu semana de check-in" + CTA      |
| Check-in enviado              | El banner desaparece. Vuelve al indicador discreto            |
| Plan actualizado por el coach | Banner puntual: "Tu coach ha actualizado tu plan" (con fecha) |


> El anillo de pasos mantiene siempre el protagonismo. El check-in aparece con urgencia solo cuando la ventana está abierta, sin interrumpir la vista de actividad diaria.

**Estado vacío (primer acceso, sin plan todavía)**:

- La capa de actividad funciona igual (pasos, métricas)
- En lugar del indicador de ciclo: "Tu coach está preparando tu plan"

**Conexión con dashboard**:

- El indicador de ciclo consume `last_review_date` / `next_review_date`
- El banner de plan actualizado se activa cuando `plan_sent_at` > última apertura del usuario

---

### 2. Entreno

**Propósito**: El usuario ve y ejecuta la rutina semanal que le ha asignado el coach.

**Vista principal — Los días de entreno**:

- La rutina se organiza por días numerados: Día 1, Día 2, Día 3... (no por día de la semana)
- El coach asigna X días de entreno; el usuario decide qué día del calendario hace cada uno
- Cada día muestra: nombre/descripción del entrenamiento (ej. "Día 1 — Tren superior")
- Indicador de días completados en el ciclo actual (ej. "3/5 días completados")

**Vista de sesión**:

- Nombre de la sesión (ej. "Tren superior — Fuerza")
- Lista de ejercicios con:
  - Nombre del ejercicio
  - Series × Repeticiones (o tiempo)
  - Técnica aplicada (RIR, TUT, etc.) si aplica
  - Video demostrativo del ejercicio (thumbnail → reproducción inline)
  - Notas del coach sobre el ejercicio si las hay
- Soporte para **supersets** (agrupados visualmente)
- Soporte para **rondas/circuits** cuando esté disponible en dashboard

**Ejecución de sesión**:

- Botón "Empezar sesión"
- Timer de descanso entre series
- Marcar serie como completada (tap)
- Al completar todos los ejercicios → pantalla de celebración + sesión marcada
- El log de la sesión queda guardado (para histórico y para el check-in)

**Estado sin plan**:

- "Tu coach está preparando tu rutina"
- No se muestran los programas genéricos de suscripción (el coached no ve eso)

---

### 3. Dieta

**Propósito**: El usuario consulta su plan de alimentación personalizado de forma clara y atractiva.

**Vista principal — El plan**:

- Organizado por comidas del día: Desayuno / Media mañana / Comida / Merienda / Cena
- Cada comida muestra:
  - Nombre de la comida / descripción
  - Ingredientes con cantidades (ej. "Avena — 60g", "Leche desnatada — 200ml")
  - Calorías estimadas de la comida
  - Opción de ver **sustituciones** por ingrediente (las que el coach ha configurado)
- Total de calorías del día (visible en header o footer)
- Macros del día: proteína / carbohidratos / grasas (visual tipo gráfico de barras o anillos)

**Navegación entre opciones calóricas**:

- Si el coach ha configurado varias opciones de calorías (déficit / mantenimiento / volumen), el usuario puede cambiar entre ellas
- Selector visual claro (ej. tabs o chips: "Déficit 1800 kcal" / "Mantenimiento 2200 kcal")

**Recetas asociadas**:

- Si alguna comida tiene receta vinculada → botón "Ver receta completa"
- Las recetas son las mismas del módulo de Explora (contenido compartido)

**Estado sin plan**:

- "Tu coach está preparando tu plan de alimentación"

---

### 4. Check-in

**Propósito**: El usuario envía su revisión quincenal al coach de forma sencilla y no intimidante.

> El check-in **no es un tab**. Se accede desde:
>
> - CTA en Home cuando la ventana está abierta
> - Perfil → "Mis check-ins"

**Flujo de envío** (cuando la ventana está abierta):

```
PASO 1 — Fotos
  3 fotos obligatorias: frente, lateral, espalda
  Cámara nativa o galería
  Preview antes de confirmar cada foto
  Indicación visual de cómo ponerse (silueta guía)

PASO 2 — Métricas
  Peso actual (kg) — campo numérico
  Opcional: cintura (cm), cadera (cm) [si el coach lo ha activado]

PASO 3 — Valoraciones
  4 sliders o escalas del 1 al 5:
  - ¿Cómo ha ido el entrenamiento?
  - ¿Has seguido la dieta?
  - ¿Cómo te has sentido de energía?
  - ¿Cómo ha sido tu descanso?

PASO 4 — Comentarios
  Campo de texto libre (opcional)
  Placeholder: "¿Algo que quieras contarle a tu coach?"

PASO 5 — Enviar
  Resumen de lo que se va a enviar
  Botón "Enviar check-in"
  Confirmación: "¡Enviado! Tu coach lo revisará pronto"
```

**Estado de la ventana**:

- Ventana cerrada (días 1–7 del ciclo, aprox): el CTA de home no aparece
- Ventana abierta (días 8–14): CTA prominente en home, badge en tab de Perfil
- Check-in enviado: estado "Enviado ✓" + fecha; el CTA desaparece
- Ventana expirada sin enviar: el coach avanzará el ciclo manualmente desde dashboard

**Histórico de check-ins**:

- Desde Perfil → "Mi progreso"
- Lista cronológica de check-ins enviados
- Vista de cada check-in: fotos (comparativa con anterior), métricas, valoraciones
- Gráfico de evolución de peso (todos los check-ins)

---

### 5. Comunidad

**Propósito**: Ranking de pasos compartido con los usuarios de V1. El usuario coached compite con toda la comunidad.

- Idéntico al de V1 en funcionalidad
- Diferencia visual: badge de tier "Coached" en el perfil del usuario dentro del ranking
- Esto refuerza que el coached es un tier premium visible socialmente

---

### 6. Guías

**Propósito**: Contenido de bienestar general (nutrición, descanso, técnica, etc.).

- Accesibles desde Home (sección "Para ti") o como sección propia (a definir si tab o desde Perfil)
- Las mismas guías del módulo Explora de suscripción (contenido compartido)
- El coached tiene acceso completo sin paywall
- El coach puede destacar guías específicas para un cliente → aparecen en Home como "Tu coach te recomienda"

---

## Estados del Plan


| Estado               | Qué ve el usuario                                                   |
| -------------------- | ------------------------------------------------------------------- |
| `sin_plan`           | Pantallas vacías con mensaje "Tu coach está preparando tu plan"     |
| `plan_activo`        | Contenido normal de entreno y dieta                                 |
| `pendiente_check_in` | CTA de check-in prominente en home                                  |
| `check_in_enviado`   | Confirmación de envío, esperando respuesta del coach                |
| `plan_actualizado`   | Banner en home "Tu coach ha actualizado tu plan"                    |
| `pausado`            | Pantalla de "Tu asesoria está pausada" con CTA de reactivación      |
| `cancelado`          | Acceso al histórico pero sin plan activo; CTA de volver a contratar |


---

## Notificaciones Push Clave


| Trigger                                 | Mensaje                                                        |
| --------------------------------------- | -------------------------------------------------------------- |
| Coach sube plan nuevo / actualiza       | "Tu coach ha preparado tu nuevo plan 💪"                       |
| Ventana de check-in se abre             | "Es hora de tu check-in quincenal. Envía tus fotos y progreso" |
| Recordatorio D+3 sin check-in enviado   | "Tu coach está esperando tu check-in. Solo tarda 2 minutos"    |
| Coach ha visto y respondido el check-in | "Tu coach ha revisado tu check-in y actualizado tu plan"       |


---

## Diferencias Clave V1 vs V2 Coached


| Aspecto              | V1 (Free/Suscriptor)             | V2 (Coached)                        |
| -------------------- | -------------------------------- | ----------------------------------- |
| Contenido de entreno | Programas genéricos del catálogo | Rutina 100% asignada por coach      |
| Nutrición            | Recetas + calculadora calórica   | Plan de dieta personalizado         |
| Seguimiento          | Automático (pasos, sesiones)     | Check-in quincenal enviado al coach |
| Relación con Inazio  | Contenido de marca               | Sensación de seguimiento personal   |
| Navegación           | 4 tabs estándar                  | 5 tabs, shell diferente             |
| Upgrade path         | → Coached (CTA post-programa)    | → Renovar o cancelar                |


---

## Pendiente de Definir

- ¿Cómo se gestiona el onboarding del usuario cuando activa el tier coached? (cuestionario inicial)
- ¿El coached puede seguir viendo y usando los programas genéricos de suscripción, o solo ve su rutina?
- ¿Hay un chat o mensajería directa coach-cliente en V1? (actualmente no existe en dashboard)
- Pricing y flujo de compra del tier coached (desde dentro de la app o solo externo)
- ¿Cómo llega el usuario al tier coached? (desde dentro de la app, desde redes, desde WhatsApp)

