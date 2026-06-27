# Aprendizajes — feedback de Carles en el primer PR (25 jun 2026)

Qué aprendí del **code review** que hizo Carles al PR #1 (modelo de datos). Enfocado a los
**conceptos** (el "qué decidimos y por qué" está en [`Decisiones Código/`](../Decisiones%20Código/2026-06-25-puntuaciones-seeding-datos-referencia.md)).

---

## 0. Qué es un "code review" (y para qué sirve)

Cuando alguien propone un cambio (un PR), otra persona del equipo lo **revisa** antes de fusionarlo.
No es una crítica personal: es una **red de seguridad** que mejora el trabajo. Carles dio dos
comentarios **"no bloqueantes"** (= "sugerencias, no hace falta para aprobar, pero piénsalo"). Los dos
eran buenos y los aplicamos. **Lección:** una review no es que algo esté "mal"; es cómo el trabajo se
hace más sólido.

## 1. Las migraciones son historial inmutable

Una migración, una vez enviada, **no se reescribe** — es como una página del diario ya escrita.
**Consecuencia que señaló Carles:** si metes ahí datos que **van a cambiar** (como los estándares v1,
que hay que recalibrar), te obligas a una migración nueva cada vez, y encima quedan "enterrados".

> **Concepto:** separa lo que **cambia** (datos) de lo que es **estructura fija**. Los datos que
> evolucionan, mejor en un sitio **a la vista y fácil de versionar**.

## 2. "Que no falle en silencio" (errores ruidosos > silenciosos)

Nuestro primer arreglo evitaba que la migración **rompiera**… pero a cambio podía dejar una tabla
**vacía sin que nadie se enterara** → un bug futuro dificilísimo de rastrear. Carles pidió un **aviso**.

> **Concepto:** un problema que **avisa** (un WARNING) es mucho mejor que uno que se **calla**. Si algo
> raro pasa, que se **vea** en el momento, no que aparezca como un misterio semanas después.

## 3. Idempotencia y "upsert"

- **Idempotente** = lo ejecutas muchas veces y el resultado es el mismo (no duplica ni rompe). Como
  darle a "Guardar" dos veces.
- **Upsert** = "**up**date + in**sert**": si la fila existe, la actualiza; si no, la crea.

> **Concepto:** dejar las cosas **re-ejecutables** sin miedo te ahorra muchos sustos.

## 4. Código revisable > datos enterrados

Mover los 84 números a un archivo propio (`strength_standards_v1.py`) hace que se puedan **leer y
revisar** de un vistazo, en vez de buscarlos dentro de un archivo técnico.

> **Concepto:** la información importante (sobre todo la que va a cambiar) debe estar **donde se vea**.

---

## Para llevarme (como PM)

- Una review **mejora** el trabajo; no temerla, buscarla.
- Distinguir **datos que cambian** vs **estructura fija** evita líos futuros.
- Preferir siempre que las cosas **avisen** antes que **fallen en silencio**.
- Si un dato es importante y volátil (como los estándares v1), pedir que esté **a la vista** y sea
  **fácil de cambiar**.

## Mini-glosario

| Palabra | En cristiano |
|---|---|
| Code review | Revisión de un cambio por otra persona antes de fusionarlo |
| No bloqueante | Sugerencia que no impide aprobar; "piénsalo" |
| Migración inmutable | Página del diario ya escrita: no se reescribe |
| Datos de referencia | Datos base (estándares, mapeos) que el sistema usa |
| Idempotente | Se puede repetir y da el mismo resultado |
| Upsert | "Si existe actualiza, si no crea" |
| Fallar en silencio | Que algo vaya mal sin avisar de ello |
