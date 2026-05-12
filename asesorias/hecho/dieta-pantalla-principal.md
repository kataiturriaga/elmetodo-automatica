# Pantalla principal de dieta — Ideación y definición

**Estado:** Dirección de diseño definida — pendiente validación con usuarios
**Fecha:** Abril 2026

---

## Contexto del problema

El 58% de los usuarios consulta la dieta antes de cada comida. La pantalla debe ser accesible y legible de un vistazo — es un flujo de consulta rápida, no de exploración.

El usuario tiene que tomar **dos decisiones** para llegar a la información que necesita:

- **Nivel 1:** ¿Qué comida es? (hasta 5 comidas por día)
- **Nivel 2:** ¿Qué opción elijo? (3 opciones por comida)

Hoy esas dos decisiones ocurren en pantallas separadas. Ese es el problema de fondo.

**Modelo de uso:** La app es puramente de consulta — no registra qué opción eligió el usuario. No hay selección explícita.

---

## Datos conocidos

| Frecuencia de uso | % usuarios |
|---|---|
| Antes de cada comida (3–5x/día) | 58% |
| Una vez al día | 35% |
| Una vez a la semana | 30% |

> Nota: los porcentajes pueden superponerse — un usuario puede consultar antes de comer Y también planear por la mañana.

---

## Soluciones evaluadas

### Solución 1 — Todo en una pantalla, mismo nivel de accesibilidad ✅ Elegida

Mostrar comidas y opciones en la pantalla principal, con navegación fluida entre ambas dimensiones al mismo tiempo.

**A favor:** Cubre los dos perfiles principales. El 58% accede a su comida actual sin fricciones. El 35% ve todas las comidas del día de un vistazo.

**En contra:** Requiere encontrar un patrón de diseño que sea legible con esa densidad de información.

---

### Solución 2 — Todo en una pantalla, comida como panel secundario

La opción es el protagonista. La comida se resuelve con contexto temporal (hora actual).

**Descartada porque:** No cubre al 35% de usuarios que planifica el día entero — ocultar las comidas en un panel secundario les perjudica directamente.

---

### Solución 3 — Dos pantallas (solución actual)

**Descartada porque:** Dos taps, dos momentos de orientación. Pierde inmediatez para el caso de uso principal.

---

## Tensión clave entre perfiles

Los dos segmentos principales tienen necesidades compatibles:

- **58% (antes de comer)** → necesita ver la comida actual + sus opciones, ya.
- **35% (una vez al día)** → necesita ver todas las comidas del día de un vistazo.

Ambas necesidades se resuelven con el mismo diseño si se prioriza bien la jerarquía visual.

---

## Patrones explorados (Solución 1)

Se exploraron 4 patrones en Figma. Los más fuertes:

**P1 — Chips horizontales + opciones verticales**
Chips scrolleables para navegar comidas. Al cambiar de chip, las 3 opciones se muestran debajo. Simple y conocido.

**P4 — Lista de comidas + bottom sheet**
El día entero visible como lista con hora. Al tocar una comida se abre un panel inferior con las opciones. Muestra contexto temporal sin configuración.

**P5 — Timeline + opciones expandidas inline**
Línea de tiempo vertical. La comida actual está expandida con sus 3 opciones. Las demás colapsadas pero visibles.

> Los exploración están en Figma, página **"Dieta — Exploración"**, sección *Exploración — Pantalla principal dieta*.

---

## Decisión de diseño — Pantalla principal

**Patrón elegido: Chips horizontales + cards con imagen (variante de P1)**

### Navegación de comidas
Chips scrolleables en la parte superior: Des. / Comida 2 / C.3 / C.4 / Cena. El chip activo en verde. Sin configuración de horarios — el usuario selecciona manualmente.

### Cards de opciones
Cada opción es una card con:
- **Imagen a la izquierda** como columna fija (cubre toda la altura de la card, incluso expandida)
- **Label** de opción (Opción A/B/C)
- **Nombre** del plato
- **Recetas asociadas** (subtexto)
- **"Ingredientes ↓"** como affordance de expansión

### Accordion de ingredientes
Al tocar la card, se expande mostrando la lista de ingredientes con cantidades en la columna derecha (la imagen permanece fija a la izquierda — esto mantiene un único eje de alineación y evita el salto visual).

Al expandir aparece también **"Ver recetas y detalle →"** como link de texto — sin peso de CTA primario, ya que la pantalla es de consulta, no de acción.

Solo una card expandida a la vez (acordeón exclusivo).

---

## Flujo completo

```
Pantalla principal
│
├── Chips → navegar entre comidas del día
│
├── Cards → ver opciones con imagen
│   │
│   └── [tap card] → accordion abre ingredientes básicos
│       │
│       └── "Ver recetas y detalle →" → Pantalla de detalle
│
Pantalla de detalle
│
├── Tabs (Opción 1 / Opción 2 / Opción 3) → navegar opciones en profundidad
├── Imagen grande
├── Toggle Raciones / Unidades
├── Lista completa de ingredientes con cantidades
└── Recetas asociadas (cards horizontales)
```

**Estado de entrada al detalle:** el tab activo debe corresponder a la opción desde la que se navegó.

---

## Perfiles de usuario

> ⚠️ **Estos perfiles son hipótesis.** Solo tenemos dato de frecuencia de apertura — el contexto, motivación y momento de uso son inferidos, no validados.

---

**Perfil 1 — La consultora frecuente**
*58% de usuarios*

Abre la app entre 3 y 5 veces al día, justo antes de cada comida. No recuerda qué toca — abre, mira, elige y cierra. El tiempo entre abrir la app y tomar una decisión debe ser mínimo. No explora, no planea: ejecuta.

- **Momento de uso:** Segundos antes de preparar o pedir la comida
- **Necesita ver:** La comida que toca ahora + las 3 opciones disponibles
- **Cómo lo resuelve el diseño:** Abre → chip de comida activo → ve 3 cards → decide. Sin necesidad de expandir ni navegar al detalle.

*Hipótesis alternativa: podría abrir, mirar y luego comer algo diferente de todos modos — en ese caso el problema no es velocidad sino relevancia o adherencia.*

---

**Perfil 2 — La planificadora diaria**
*35% de usuarios*

Abre la app una vez al día, normalmente a la mañana. Quiere tener el día claro: saber qué va a comer en cada momento.

- **Momento de uso:** Mañana, antes de salir o al despertarse
- **Necesita ver:** Todas las comidas del día de un vistazo, con sus opciones
- **Cómo lo resuelve el diseño:** Navega chip a chip para ver cada comida. La estructura es rápida de explorar.

*Hipótesis alternativa: podría abrir a mediodía para ver qué queda del día, no necesariamente a la mañana.*

---

**Perfil 3 — La planificadora semanal**
*30% de usuarios*

Abre la app una vez a la semana a principios de semana para hacer la compra y organizarse.

- **Decisión:** No diseñar la pantalla principal para este perfil. Comportamiento demasiado diferente. Cubrir con funcionalidad secundaria (vista semanal, compartir menú) sin comprometer el diseño principal.

---

## Próximos pasos

- [ ] Validar hipótesis de perfiles — hablar con 3–4 clientes antes de que los perfiles se conviertan en verdad de diseño
- [ ] Definir comportamiento del chip activo al abrir la app — ¿siempre Comida 1, o la comida más cercana en el tiempo?
- [ ] Definir máximo de opciones por comida (actualmente asumimos 3)
- [ ] Diseñar estado vacío — ¿qué ve el usuario si una comida no tiene opciones asignadas?
- [ ] Revisar cómo se comporta la pantalla si el nombre de la opción es muy largo (wrapping en la card)
