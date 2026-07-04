# Puntuaciones de Entrenamiento — Arquitectura de pantallas (IA + diseño)

Documenta el **flujo de pantallas** del Score de Fuerza: cómo está hoy, qué
problema de arquitectura de información tiene la pantalla de evolución, qué
decidimos sacar ahora y cómo podría evolucionar.

> Para la **fórmula y la lógica del score** (1RM, mediana, niveles, confianza)
> ver [puntaciones-entreno.md](puntaciones-entreno.md).
> Diseño en Figma: **App-Automatica** → sección `Seguimiento`
> (`node-id 4761-64547`).

_Última actualización: 28-jun-2026._

---

## 1. Mapa del flujo (estado actual)

```
Pantalla principal (Seguimiento)
│   Hero en pager horizontal:  Puntuación total  ↔  Mapa de fuerza (radar)
│   Lista "Por grupo muscular" (medalla + barra + chevron)
│
├─ botón "Ver gráfico evolución" ──►  Pantalla de EVOLUCIÓN
│                                     (gráfico de línea del total + chips de tiempo
│                                      + lista "Por grupo muscular" repetida)
│
└─ tap en un grupo de la lista ─────►  Detalle de GRUPO
                                       (score del grupo + "para pro" + lista de
                                        ejercicios + gráfico de progresión del grupo)
                                       │
                                       └─ tap en un ejercicio ──►  Progresión de EJERCICIO
                                                                   (mejor lift + gráfico
                                                                    + "Tus mejores marcas" / PRs)
```

Hay **dos puntos de entrada** que enseñan el desglose por grupo: la pantalla
principal y la de evolución. Lo asumimos como aceptable (dos caminos distintos
hacia la misma info).

---

## 2. Inventario de pantallas

| Pantalla | Figma node | Contenido | Estados |
|---|---|---|---|
| **Principal** | `4925-118748` / `4983-48806` | Hero en pager (Puntuación total ↔ Mapa de fuerza) + lista por grupo | Completa · Provisional (`4938-37434`) · Vacío (`4938-37489`) |
| **Evolución** | `4940-44474` | "Tu fuerza total" + chips (Mes / 6 meses / 1 año / Todos) + gráfico de línea + lista "Por grupo muscular" | — |
| **Detalle de grupo** | `4940-44808` | Score del grupo + "X para pro" + barra + lista de ejercicios (con tag "Mejor") + "Tu progresión" (chips + gráfico) | — |
| **Progresión de ejercicio** | `4983-48157` | Mejor lift ("TU MEJOR LIFT") + "Tu progresión" (chips + gráfico) + "Tus mejores marcas" (PRs con 1RM estimado) | — |

### Estados de la pantalla principal
- **Completa**: score consolidado (p. ej. 112 EXPERIMENTADO) + subida semanal + roadmap de niveles.
- **Provisional**: pocos grupos medidos → chip "baja confianza · X de 7 grupos" + "tu punto de partida".
- **Vacío**: sin datos → "Descubre tu nivel de fuerza" + CTA "Empezar evaluación".

---

## 3. El problema de IA en la pantalla de Evolución

La pantalla a la que lleva el botón **"Ver gráfico evolución"** muestra:

1. Gráfico de línea de la fuerza total en el tiempo (con chips de time-frame). ✅ Coincide con la promesa.
2. Debajo, la lista **"Por grupo muscular"** — la **misma foto fija** que ya está en la principal. ⚠️

**Diagnóstico:** el problema no es tanto la *duplicación* (hay dos entradas al
flujo, es asumible), sino la **disonancia de expectativa**: el usuario pulsa un
CTA que promete *evolución* (cambio en el tiempo) y, tras el gráfico, se
encuentra una *instantánea del estado actual* que no tiene dimensión temporal.
El relato se rompe: "tiempo → foto fija".

No queremos dejar **solo** el gráfico, porque la pantalla quedaría demasiado vacía.

---

## 4. Decisión: qué sacamos ahora (✅ Idea 2)

**Para salir rápido**, vamos con el arreglo de **encuadre** (mínimo cambio, sin
rehacer pantalla):

- Ajustar la **expectativa** del CTA y/o del título para que el desglose por
  grupo deje de sentirse fuera de lugar: la pantalla pasa a ser un **"detalle /
  progreso de fuerza"** del que el gráfico es *una parte*, no *toda* la promesa.
- Se asume la duplicación del desglose como intencional:
  **principal = vistazo**, **esta pantalla = detalle**.

> Esfuerzo: casi solo *copy*. Riesgo: muy bajo. No toca lógica ni datos.

Las ideas más ambiciosas quedan documentadas abajo para una iteración futura.

---

## 5. Cómo podría evolucionar (ideas para más adelante)

Las 5 ideas que se valoraron para resolver la disonancia, de menos a más cambio:

### Idea 1 — Que todo lo de debajo también sea "evolución" *(la más recomendable a medio plazo)*
En vez de repetir la foto fija, la lista por grupo muestra el **cambio en el
periodo elegido**: "Cuádriceps 125 ▲ +8 este mes" con una mini-línea
(sparkline). Toda la pantalla cuenta la misma historia: *tu evolución, total y
por grupo*. Tocar un grupo → su evolución en detalle.
- ✅ Cumple la promesa del CTA, llena la pantalla, reaprovecha la lista existente.
- ⚠️ Requiere el dato "cuánto ha subido cada grupo" + componente sparkline.
- Riesgo: bajo-medio.

### Idea 2 — Arreglarlo con el encuadre *(la elegida para salir ya)*
Aceptar la duplicación como intencional y cambiar solo expectativas: renombrar
CTA/título a algo más amplio ("Tu progreso de fuerza") para que el gráfico sea
*una parte* del detalle.
- ✅ Esfuerzo casi cero (copy).
- ⚠️ No elimina del todo la sensación de "¿por qué me repites la foto fija?".
- Riesgo: muy bajo.

### Idea 3 — Que la lista sea el "mando" del gráfico *(la más elegante)*
Una sola pantalla, pero al tocar un grupo el **gráfico de arriba se filtra** y
dibuja la evolución *de ese grupo*. Por defecto el total; tocas "Pecho" y la
línea pasa a ser la de Pecho. La lista deja de ser decorativa: es el
selector/leyenda del gráfico.
- ✅ Unifica los dos bloques, cero duplicación conceptual.
- ⚠️ Más trabajo de interacción y de datos (una serie temporal por grupo).
- Riesgo: medio.

### Idea 4 — Bloque de "qué ha cambiado" entre el gráfico y la lista
Bajo el gráfico, un resumen tipo *"Has subido +8 este mes, sobre todo por
Cuádriceps y Pecho. Hombros lleva 3 semanas estancado."* Después, la lista se
siente como "y aquí el detalle". Narrativa: tendencia → por qué → detalle.
- ✅ Da sentido a la lista y aporta insight real.
- ⚠️ Requiere lógica para detectar quién sube / se estanca.
- Riesgo: medio. (Combina muy bien con la Idea 1.)

### Idea 5 — Quitar la lista de aquí y llenar con contenido propio de evolución
La pantalla se queda 100% sobre el tiempo: bajo el gráfico, **hitos/récords**
("Alcanzaste Experimentado el 12 may", "Récord en sentadilla: 120 kg"),
historial de subidas de nivel, semanas medidas seguidas, comparación con el
periodo anterior. El desglose por grupo vive *solo* en la principal (única
fuente de verdad).
- ✅ Separación limpia, cero duplicación.
- ⚠️ Componentes nuevos que diseñar desde cero.
- Riesgo: medio-alto.

---

## 6. Recomendación a futuro

Cuando haya margen, **Idea 1 + un toque de la 4**: convertir la lista en
"evolución por grupo" (cumple la promesa y reaprovecha lo existente) y, encima,
la frase-resumen de qué ha cambiado. Es el mejor equilibrio entre arreglar la
disonancia y no rehacer media pantalla. Si se busca la versión más "wow", la
**Idea 3** es la más bonita conceptualmente.
