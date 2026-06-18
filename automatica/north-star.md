# North Star — Automática

> App de entrenamiento para usuarios finales (free + paid). Modelo económico: % sobre resultados.
> Alineado con el reposicionamiento de junio 2026: **Sistema de Consistencia Deportiva**.
> Ver: `automatica/estrategia-posicionamiento-jun2026.md`

---

## El juego que jugamos

Juego de **hábito / consistencia**. El producto entrega valor cuando el usuario **vuelve y es constante**, porque eso es lo que rompe el ciclo `inicio → abandono → culpa`. Como el modelo es **% sobre resultados**, el valor del usuario y el ingreso apuntan al mismo sitio: que la persona sea constante de verdad.

Por eso el North Star mide **consistencia**, no actividad ni dinero.

---

## ⭐ North Star Metric

> ### Usuarios Semanalmente Consistentes (USC)
> **Número de usuarios que completan ≥ 3 sesiones de bienestar en una ventana de 7 días.**
> (sesión = entreno de fuerza **o** día de pasos que suma XP — la "moneda unificada")

El umbral de **3 sesiones/semana** coincide con la definición de consistencia ya existente (*6 sesiones en 14 días*). No es una métrica nueva, es la que ya definimos como éxito.

### Por qué cumple los 7 criterios

| Criterio | Cómo lo cumple |
|---|---|
| Fácil de entender | "Cuánta gente está siendo constante esta semana" |
| Centrado en el cliente | Mide **su** constancia, no la facturación |
| Valor sostenible | Hábito repetido, no un pico puntual |
| Alineado con la visión | Es "Sistema de Consistencia" hecho número |
| Cuantitativo | Conteo limpio de usuarios |
| Accionable | Onboarding, ligas, racha y paywall lo mueven directo |
| Indicador adelantado | La constancia predice retención → trial-to-paid → ingreso |

### Qué NO es el North Star
Descargas, registros, MAU o ingresos. Todas se pueden inflar sin que nadie mejore su vida — y rompen el modelo de negocio.

---

## Las palancas (input metrics)

Las 4 que más directamente mueven el USC. Son más fáciles de mover a corto plazo; cada una corresponde a una fase del embudo y a una palanca estratégica.

| # | Palanca (qué mides) | Fase | Estrategia que la mueve | KPI objetivo |
|---|---|---|---|---|
| 1 | **Activación temprana** — % de instaladores que hacen su 1er entreno en los 3 primeros días | Entrada | Onboarding / cuestionario, cargador de algoritmo (efecto IKEA) | >35% activación D0 · >60% con programa D0–D3 |
| 2 | **Enganche social** — % de usuarios en liga (≤30 pers.) que abren ranking ≥3 días/semana | Vuelta diaria | Ligas, XP unificado, democión, friend quests | — (definir con datos) |
| 3 | **Protección de racha** — racha media activa / % que usa el *streak freeze* | Continuidad | Seguro de racha (+48–62% de duración según datos) | — (definir con datos) |
| 4 | **Compromiso por pago** — trial-to-paid (D7–D8) | Skin in the game | Paywall como dispositivo de compromiso | >25% trial-to-paid |

### El árbol

```
                    ⭐ Usuarios Semanalmente Consistentes (≥3 sesiones/7d)
                                        ▲
        ┌───────────────┬──────────────┴──────────────┬───────────────┐
   1. Activación    2. Enganche        3. Protección       4. Compromiso
      temprana         social             de racha            por pago
   (1er entreno     (ranking ≥3d/sem)  (streak freeze)     (trial→paid)
    en 3 días)
        │                │                   │                  │
   Onboarding /      Ligas /            Seguro de          Paywall como
   cuestionario      XP unificado       racha              dispositivo
   (efecto IKEA)     / democión                            de compromiso
```

Para subir el USC no se ataca la estrella directamente: se ataca **una de las 4 palancas** y eso la empuja.

---

## ✅ Ya es medible — y los datos reales (jun 2026)

La telemetría está conectada (GA4/BigQuery + API). Snapshot real:

| Métrica | Real | Meta |
|---------|------|------|
| ⭐ USC (≥3 días bienestar/sem) | **71** (cayó ~60% desde may) | 3.000 |
| P1 · 1er entreno ≤3 días | 1,3% | >35% |
| P2 · abren ranking (7d) | 22% (4 con ≥3 días/sem) | >55% |
| P3 · racha | sin datos (aparcado) | — |
| P4 · trial → paid | 11,3% | >25% |

## 🔴 Riesgo crítico real: el core no se está usando

1. **La consistencia es casi 100% pasos.** De 71 consistentes, **solo 1** entrenó ≥3 veces/sem; ~6 usuarios entrenaron en 30 días. La parte de *entrenar* del producto apenas ocurre.
2. **El USC se desplomó ~60% al lanzar el onboarding nuevo (11-may)**, que obliga a registrarse antes de entrar. Correlación, no causa probada → **investigar**.

Detalle del embudo de conversión en [embudo-actualizado.md](embudo-actualizado.md). Dashboard visual en [north-star-dashboard.html](north-star-dashboard.html).
