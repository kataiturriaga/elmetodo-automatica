# Por decidir / cambiar — Ranking sobre puntuación de entreno

> Documento de trabajo sobre **evolucionar las Ligas** para que rankeen por la puntuación de entreno, en vez de por pasos.
> Conecta con: [visión §6](vision-producto-puntuaciones.md) y [tareas §9](../plans/tareas-implementacion-puntuaciones.md) — ambas dejaron esta integración "sin decidir, decisión de producto".
> Estado: **dirección acordada, construcción aplazada** (ver riesgo de liquidez). Fecha: 2026-06-22.

---

## Contexto: cómo es el ranking hoy

- Sistema de Ligas existente (`RankingGroup`): grupos NATO de ~100 usuarios, con niveles, **rankeados por pasos**.
- App: `lib/features/ranking` (podium, badges, summary).
- Insignia actual: **escudo con una letra del alfabeto militar** (Alfa, Bravo, Charlie…). Todos los grupos comparten la misma forma y solo cambia la letra.
- Problema: los **pasos no dicen nada del entrenamiento**. El ranking no está conectado con lo que el producto hace de verdad → se siente como un feature pegado, no cohesionado.

## La apuesta

Hacer que el ranking se base en la **puntuación de entreno** (fuerza ahora; running e híbrido después). Así score y liga se retroalimentan y el producto se siente como un todo.

---

## Decisiones tomadas (22-jun-2026, con Kata)

1. **El ranking pasa a basarse en la puntuación de entreno**, no solo en los pasos.
2. **Agrupación** de las ligas por:
   - **Nivel de fuerza** (Principiante → Olímpico): compites contra gente de tu fuerza, no contra todo el mundo.
   - **Tipo de programa**: ligas separadas por tipo de entreno, porque fuerza y running no son comparables en la misma escala.
3. **Métrica de ranking dentro de cada liga = velocidad de progreso** (cuánto sube tu score en el periodo), **no** el score absoluto.
   - *Por qué:* es justo para todos los niveles (un principiante constante puede ganar a un fuerte estancado), alinea con el anti-job de "no desmotivar", y premia el hábito.
4. **Insignias: libres de rediseñar.** No hace falta que recuerden a las actuales (escudo + letra), porque hoy solo hay ~1 usuario activo y no hay base instalada que confundir. La insignia que se está explorando para el héroe del score puede ser la semilla del nuevo sistema de ligas.

---

## Mecánica de diseño que esto habilita

- **Ascenso / descenso de liga:** al subir de nivel de fuerza, "asciendes" de liga. Es uno de los loops de retención más potentes (modelo Duolingo / rank de videojuegos). Sale casi gratis al agrupar por nivel.
- **Insignia compartida:** la misma insignia del score (nivel + puntuación) sirve como insignia de liga → un único lenguaje visual.

---

## Riesgos

- ⚠️ **Liquidez (estructural):** una liga competitiva con ~1 usuario activo está **vacía** y se siente rota. → **Diseñar el concepto ahora, construir después** de que el MVP de score demuestre que la gente convierte. No lanzar una "liga de una persona".
- **Comparabilidad cruzada:** fuerza vs running no están en la misma escala → resuelto agrupando por tipo de programa (decisión 2).

## Complejidad técnica (nota, a confirmar por Carles)

- **Riesgo técnico: bajo-medio.** La velocidad de progreso = restar dos *snapshots* de score (hoy vs inicio del periodo). Esos snapshots **ya se guardan** para la gráfica de historial → no es una tubería de datos nueva, es una resta + ordenación.
- La complejidad real es de **producto/reglas**, no de ingeniería (ver decisiones abiertas).

---

## Decisiones abiertas (resolver al construir, no urge hoy)

- [ ] **Temporadas:** ¿el ranking es por semana / mes? ¿Cuándo se resetea?
- [ ] **Usuarios nuevos:** cómo entra alguien que aún no tiene dos snapshots para medir progreso (sin baseline).
- [ ] **Score que baja solo:** qué pasa en el ranking cuando tu score baja porque una marca caducó (>3 meses) sin que tú dejes de entrenar.
- [ ] **Empates** y cómo se desempata.
- [ ] **¿Se mantiene también el ranking por pasos** en paralelo, o se sustituye del todo?
- [ ] **Tamaño y nomenclatura** de las ligas (¿se mantiene el alfabeto militar como nombres, aunque cambien las insignias?).

---

## Secuencia recomendada

1. **Ahora:** MVP de score de fuerza (en curso) + diseño del concepto de ranking-sobre-score (este doc).
2. **Después (cuando el score MVP demuestre valor y haya más usuarios):** construir la liga sobre velocidad de progreso, resolviendo las reglas abiertas.
