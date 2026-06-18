# Tablas de estándares de fuerza (v1) — fuerza relativa → score

Resuelve el bloqueante más crítico de la [§1 del plan](../plans/tareas-implementacion-puntuaciones.md): convertir **fuerza relativa (1RM ÷ peso corporal)** en un **score 0–300+** por grupo muscular, género y edad.

**Modelo**: igual que Gravl ([su artículo](https://help.gravl.ai/en/articles/9953877-gravl-strength-score-how-does-it-work)), pero como Gravl **no publica sus números** (son propietarios), construimos la tabla sobre **estándares públicos de fuerza relativa de [StrengthLevel](https://strengthlevel.com)** — la misma base que usan estas apps. Calibración elegida: **motivadora** (se sube rápido al principio; Élite/Olímpico reservado a gente realmente fuerte).

> Fecha: 2026-06-18. Estado: **v1 para validar** contra datos reales de usuarios de El Metodo.

---

## Cómo se calcula un score (en cristiano)

1. Coge el **mejor 1RM de los últimos 3 meses** del *lift ancla* del grupo (Epley: `peso × (1 + reps/30)`).
2. Divídelo por el **peso corporal** vigente → `ratio` (ej. 100 kg ÷ 80 kg = 1.25×).
3. Aplica el **ajuste de edad** (abajo).
4. Busca el `ratio` en la **columna de tu género** → te da un número 0–300 (interpolando entre niveles).
5. **Score del grupo** = ese número. **Score total** = mediana de los grupos con datos.

> ✅ **DECIDIDO (18-jun-2026): mediana.** El score total = **mediana** de los grupos con datos (no promedio). Igual que Gravl ("median score across all muscle groups") y más justo: un grupo flojo no te hunde el total. *(El spec original decía "promedio" — queda obsoleto.)*

---

## Mapeo de niveles (calibración motivadora)

Cada nivel nuestro = un nivel de StrengthLevel, con nombre más generoso:

| Nuestro nivel | Score | = StrengthLevel | Quién es |
|---|---|---|---|
| Principiante | 0–49 | (por debajo de Beginner) | acaba de empezar |
| Novato | 50 | Beginner | primeras semanas |
| Experimentado | 100 | Novice | unos meses entrenando |
| Pro | 150 | Intermediate | gimrata regular (~1-2 años) |
| Atleta | 200 | Advanced | fuerte de verdad |
| Élite | 250 | Elite | top ~5% |
| Olímpico | 300 | más allá de Elite | nivel competición |

Dentro de cada tramo el score **interpola lineal** entre los dos ratios.

---

## Tablas por lift ancla (ratio = 1RM ÷ peso corporal)

Score → ratio necesario. **H** = hombre, **M** = mujer.

### Pectorales — Press banca plano (id 484)
| | 50 Novato | 100 Exp. | 150 Pro | 200 Atleta | 250 Élite | 300 Olímpico |
|---|---|---|---|---|---|---|
| H | 0.50× | 0.75× | 1.25× | 1.75× | 2.00× | 2.20× |
| M | 0.25× | 0.50× | 0.75× | 1.00× | 1.50× | 1.65× |

### Espalda — Remo con barra (id 594)
| | 50 | 100 | 150 | 200 | 250 | 300 |
|---|---|---|---|---|---|---|
| H | 0.50× | 0.75× | 1.00× | 1.50× | 1.75× | 1.95× |
| M | 0.25× | 0.40× | 0.65× | 0.90× | 1.20× | 1.30× |

### Hombros — Press militar barra (id 292)
| | 50 | 100 | 150 | 200 | 250 | 300 |
|---|---|---|---|---|---|---|
| H | 0.40× | 0.55× | 0.80× | 1.05× | 1.35× | 1.50× |
| M | 0.20× | 0.35× | 0.55× | 0.75× | 1.00× | 1.10× |

### Cuádriceps — Sentadilla trasera con barra (id 337)
| | 50 | 100 | 150 | 200 | 250 | 300 |
|---|---|---|---|---|---|---|
| H | 0.75× | 1.25× | 1.50× | 2.25× | 2.75× | 3.00× |
| M | 0.50× | 0.75× | 1.25× | 1.50× | 2.00× | 2.20× |

### Isquiotibiales — Peso muerto con barra (id 601)
| | 50 | 100 | 150 | 200 | 250 | 300 |
|---|---|---|---|---|---|---|
| H | 1.00× | 1.50× | 2.00× | 2.50× | 3.00× | 3.30× |
| M | 0.50× | 1.00× | 1.25× | 1.75× | 2.50× | 2.75× |

### Bíceps — Curl barra recta (id 406)
| | 50 | 100 | 150 | 200 | 250 | 300 |
|---|---|---|---|---|---|---|
| H | 0.20× | 0.40× | 0.60× | 0.85× | 1.15× | 1.25× |
| M | 0.10× | 0.20× | 0.40× | 0.60× | 0.85× | 0.95× |

### Tríceps — Press francés barra Z (id 305)
| | 50 | 100 | 150 | 200 | 250 | 300 |
|---|---|---|---|---|---|---|
| H | 0.20× | 0.35× | 0.55× | 0.80× | 1.10× | 1.20× |
| M | 0.10× | 0.20× | 0.35× | 0.55× | 0.75× | 0.85× |

> Las **variantes** de cada grupo (las otras del catálogo curado) usan el mismo cuadro que su ancla en el MVP. Afinar coeficientes por variante es trabajo de fase 2 (con `max` por grupo casi no cambia el resultado).

---

## Ajuste por edad (v1)

La fuerza baja con la edad. Se multiplica la `ratio` del usuario por un **coeficiente** antes de buscarla en la tabla, para compararlo de forma justa contra el estándar de adulto joven:

| Edad | Coeficiente | Efecto |
|---|---|---|
| 18–29 | 1.00 | referencia (pico) |
| 30–39 | 1.05 | +5% |
| 40–49 | 1.12 | +12% |
| 50–59 | 1.22 | +22% |
| 60+ | 1.35 | +35% |

Ej.: un hombre de 55 años con press banca 1.0× → 1.0 × 1.22 = **1.22× efectivo** → puntúa como un joven a 1.22×. Coeficientes basados en curvas de Masters; **es la parte que más hay que validar**.

---

## Notas de implementación

- Estas tablas van a la **tabla de estándares** de la API (plan §2): `(lift_id | grupo, género, score_nivel, ratio_umbral)` + interpolación lineal entre umbrales.
- El score por grupo se calcula contra el **lift ancla**; si el usuario solo registró una variante, se usa esa con el mismo cuadro.
- **Pendiente de validar** con datos reales: (1) que los ratios no salgan ni absurdamente fáciles ni imposibles para la base de usuarios de El Metodo; (2) los coeficientes de edad. *(Media vs mediana → ya decidido: **mediana**.)*
- Fuente de ratios: StrengthLevel (bench, squat, deadlift, military press, bent-over row, barbell curl, lying tricep extension), kg, junio 2026.
