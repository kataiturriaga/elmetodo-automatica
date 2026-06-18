# Curación del catálogo de fuerza — ejercicios que puntúan (MVP)

Mapeo de los **26 ejercicios del spec** ([puntaciones-entreno.md](puntaciones-entreno.md)) a los **IDs reales de ejercicios en prod** (catálogo de 717 ejercicios, vía API `/api/exercises/`, 18-jun-2026).

**Alcance MVP**: solo **Score de Fuerza** (running → fase 2, decidido con Kata 18-jun).

Esta tabla alimenta dos cosas en la implementación: la columna nueva **`valid_for_score`** y el **`grupo_muscular_canonico`** de cada ejercicio.

---

## ⚠️ Cosas que descubrí al curar (importantes)

1. **"Skullcrusher" no existe con ese nombre — en la BD se llama "Press francés"** (es el mismo ejercicio). Por eso daban "sin match".
2. **"Estocada" = "Zancada"** y **"Vuelo lateral" = "Elevación lateral"** en la BD.
3. **`equipment` está vacío (`[]`) en absolutamente todos** → no se puede automatizar; la curación manual es la única vía.
4. Categoría **"Hyrox"** = duplicados de otro programa (saco, wallball, kettlebell). Los evito; prefiero la librería de fuerza canónica (`Pecho/Espalda/Hombro/Pierna/Bíceps/Tríceps`).
5. **Insight de diseño clave**: la fórmula del spec usa `max(fuerza_relativa)` por grupo → **solo cuenta el mejor lift de cada grupo**. Eso significa que lo crítico es tener bien el **compuesto principal de barra** por grupo; las variantes con mancuerna son secundarias (suben datos pero rara vez son el máximo). → Podemos arrancar el MVP con **1 compuesto principal por grupo** y añadir variantes después.

---

## Tabla de curación (propuesta)

✅ = match limpio · ⚠️ = necesita tu decisión · ⭐ = compuesto principal del grupo (el que más pesa en el score)

### Pectorales
| Spec | ID real propuesto | Nombre real | Nota |
|---|---|---|---|
| Press banca ⭐ | **484** | Press banca plano | ✅ |
| Press banca inclinado | **193** | Press banca inclinado | ✅ |
| Press banca con mancuerna | **126** | Press plano con mancuernas | ✅ |
| Press banca inclinado con mancuernas | **495** | Press inclinado 1 mano | ⚠️ no hay "inclinado con mancuernas" exacto; esto es a 1 mano |

### Espalda
| Spec | ID real propuesto | Nombre real | Nota |
|---|---|---|---|
| Remo con barra ⭐ | **594** | Remo con barra | ✅ |
| Remo con barra agarre supino | **513** | Remo en polea agarre supino | ⚠️ no hay con barra libre; este es en polea |
| Remo con mancuerna | **331** | Remo 1 mano mancuerna | ✅ |
| Remo con mancuerna inclinado | **339** | Remo con mancuernas de pie | ⚠️ no hay variante "inclinado" |

### Hombros
| Spec | ID real propuesto | Nombre real | Nota |
|---|---|---|---|
| Press militar con barra ⭐ | **292** | Press militar barra | ✅ |
| Press militar con barra sentado | **98** | Press militar sentado | ✅ (no especifica barra, pero es el de barra) |
| Vuelo lateral con mancuerna | **596** | Elevación lateral 1 mano | ✅ (vuelo = elevación) |
| Press de hombro con mancuerna | **41** | Press militar 1 mano | ⚠️ los de mancuerna sentado están en cat. Hyrox (650) |

### Cuádriceps
| Spec | ID real propuesto | Nombre real | Nota |
|---|---|---|---|
| Sentadilla con barra ⭐ | **337** | Sentadilla trasera con barra | ✅ |
| Sentadilla frontal | **259** | Sentadilla frontal | ✅ |
| Sentadilla búlgara con mancuernas | **313** | Zancada búlgara | ✅ (búlgara; sin peso especificado) |
| Estocada con mancuernas | **239** | Zancada hacia adelante | ⚠️ no hay "con mancuernas" en cat. Pierna (sí en Hyrox: 705) |

### Isquiotibiales
| Spec | ID real propuesto | Nombre real | Nota |
|---|---|---|---|
| Peso muerto ⭐ | **601** | Peso muerto con barra | ✅ |
| Peso muerto con piernas rígidas | **413** | Peso muerto piernas rígidas | ✅ |
| Peso muerto rumano con mancuerna | **137** | Peso muerto mancuernas | ⚠️ no hay "rumano con mancuerna"; el rumano (677) está en Hyrox |

### Bíceps
| Spec | ID real propuesto | Nombre real | Nota |
|---|---|---|---|
| Curl de bíceps con barra ⭐ | **406** | Curl barra recta | ✅ |
| Curl barra Z | **242** | Curl barra Z | ✅ |
| Curl de bíceps con mancuerna | **471** | Curl de bíceps mancuernas | ✅ |
| Curl de bíceps sentado | **422** | Curl de bíceps sentado | ✅ |

### Tríceps
| Spec | ID real propuesto | Nombre real | Nota |
|---|---|---|---|
| Press banca cerrado ⭐ | **—** | (no existe) | ⚠️ **no hay press banca cerrado**; ver decisión abajo |
| Skullcrusher con barra Z | **305** | Press francés barra Z | ✅ (skullcrusher = press francés) |
| Skullcrusher con mancuerna | **490** | Press francés con mancuernas | ✅ |
| Extensión de tríceps con mancuerna a un brazo | **343** | Press francés 1 mano | ✅ (o 411 Patada tríceps con mancuerna) |

---

---

## ✅ CATÁLOGO FINAL `valid_for_score` — los de TU lista que ya existen en la BD

**Decisión (18-jun-2026)**: de los 26 ejercicios de tu lista, coger **solo los que ya existen en la BD** (no crear ninguno nuevo). Resultado: **20 de 26 existen**.

⭐ = compuesto principal del grupo (ancla del score).

| Grupo | Ejercicio (tu lista) | ¿En BD? | ID real | Nombre real en la app |
|---|---|---|---|---|
| **Pectorales** | Press banca ⭐ | ✅ | **484** | Press banca plano |
| | Press banca inclinado | ✅ | **193** | Press banca inclinado |
| | Press banca con mancuerna | ✅ | **126** | Press plano con mancuernas |
| | Press banca inclinado con mancuernas | ❌ | — | no existe |
| **Espalda** | Remo con barra ⭐ | ✅ | **594** | Remo con barra |
| | Remo con barra agarre supino | ❌ | — | solo existe en polea (513), no con barra libre |
| | Remo con mancuerna | ✅ | **331** | Remo 1 mano mancuerna |
| | Remo con mancuerna inclinado | ❌ | — | no existe |
| **Hombros** | Press militar con barra ⭐ | ✅ | **292** | Press militar barra |
| | Press militar con barra sentado | ✅ | **98** | Press militar sentado |
| | Vuelo lateral con mancuerna | ✅ | **596** | Elevación lateral 1 mano |
| | Press de hombro con mancuerna | ✅ | **98** | = Press militar sentado (mismo que arriba) |
| **Cuádriceps** | Sentadilla con barra ⭐ | ✅ | **337** | Sentadilla trasera con barra |
| | Sentadilla frontal | ✅ | **259** | Sentadilla frontal |
| | Sentadilla búlgara con mancuernas | ✅ | **313** | Zancada búlgara |
| | Estocada con mancuernas | ❌ | — | no existe (en Hyrox sí: 705) |
| **Isquiotibiales** | Peso muerto ⭐ | ✅ | **601** | Peso muerto con barra |
| | Peso muerto con piernas rígidas | ✅ | **413** | Peso muerto piernas rígidas |
| | Peso muerto rumano con mancuerna | ❌ | — | no existe (rumano solo en Hyrox: 677) |
| **Bíceps** | Curl de bíceps con barra ⭐ | ✅ | **406** | Curl barra recta |
| | Curl barra Z | ✅ | **242** | Curl barra Z |
| | Curl de bíceps con mancuerna | ✅ | **471** | Curl de bíceps mancuernas |
| | Curl de bíceps sentado | ✅ | **422** | Curl de bíceps sentado |
| **Tríceps** | Press banca cerrado ⭐ | ❌ | — | no existe → ancla pasa a Press francés barra Z (305) |
| | Skullcrusher con barra Z | ✅ | **305** | Press francés barra Z |
| | Skullcrusher con mancuerna | ✅ | **490** | Press francés con mancuernas |
| | Extensión de tríceps con mancuerna a un brazo | ✅ | **411** | Patada tríceps con mancuerna |

### Lista limpia de IDs `valid_for_score` (20)

- **Pectorales**: `484`⭐, `193`, `126`
- **Espalda**: `594`⭐, `331`
- **Hombros**: `292`⭐, `98`, `596`  _(Press de hombro con mancuerna = 98, ya incluido)_
- **Cuádriceps**: `337`⭐, `259`, `313`
- **Isquiotibiales**: `601`⭐, `413`
- **Bíceps**: `406`⭐, `242`, `471`, `422`
- **Tríceps**: `305`⭐, `490`, `411`

### Anclas del score (compuesto principal por grupo)
| Grupo | Lift | ID |
|---|---|---|
| Pectorales | Press banca plano | 484 |
| Espalda | Remo con barra | 594 |
| Hombros | Press militar barra | 292 |
| Cuádriceps | Sentadilla trasera con barra | 337 |
| Isquiotibiales | Peso muerto con barra | 601 |
| Bíceps | Curl barra recta | 406 |
| Tríceps | Press francés barra Z | 305 |

---

## Notas para implementación

- Estos 20 IDs se marcan con **`valid_for_score = true`** + su **`grupo_muscular_canonico`** (los 7 grupos) en la tabla de curación/columna nueva (plan §2).
- **6 ejercicios de tu lista NO existen** en la BD y NO se crean (decisión MVP): Press banca inclinado con mancuernas, Remo con barra agarre supino, Remo con mancuerna inclinado, Estocada con mancuernas, Peso muerto rumano con mancuerna, Press banca cerrado.
- **Las tablas de estándares** (siguiente bloqueante, plan §1) se calibran contra los **7 compuestos principales** — son los que definen los rangos fuerza-relativa → score.
