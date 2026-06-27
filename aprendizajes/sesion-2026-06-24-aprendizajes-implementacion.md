# Aprendizajes — primera sesión de implementación (24 jun 2026)

Resumen en cristiano de qué hicimos y qué aprendí sobre código, bases de datos y tests.
Pensado para releer antes de las siguientes sesiones. (Kata = PM/diseñadora, no técnica.)

---

## 1. Qué estamos construyendo

El **PR #1** de las Puntuaciones de Entrenamiento: el **modelo de datos** (las tablas
donde vivirá la info). Carles aprobó el plan; vamos **muy poco a poco**, paso a paso,
y cada paso será un Pull Request que Carles revisa y aprueba.

Este primer PR crea **4 tablas** (en el repo `elmetodo_api`, el backend):

| Tabla | Para qué | Datos |
|---|---|---|
| `strength_standards` | Convertir "cuánto levantas ÷ tu peso" → score 0–300 | 84 filas |
| `score_exercise_muscle_groups` | Qué 20 ejercicios cuentan y a qué grupo van | 20 filas |
| `objective_score_types` | Qué tipo de score tiene cada objetivo (fuerza/running/híbrido) | 4 filas |
| `score_snapshots` | El historial de "fotos" del score de cada usuario | vacía (se llena con el uso) |

> La de **running** queda para **fase 2** (no hay datos para calibrarla). Por eso 4 y no 5.

---

## 2. El flujo de trabajo seguro (cómo trabajamos)

```
1. Rama aparte  →  2. Cambios en local  →  3. Probar en local  →  4. PR  →  5. Carles revisa y aprueba  →  6. Se fusiona
```

- **Nunca se trabaja sobre `main`** (la rama "buena"). Cada cambio va en una **rama aislada**.
- **Nunca hago `git push` sin que Kata lo diga explícitamente.**
- Subir a una **rama aparte** ≠ subir a `main`: lo primero es seguro (es solo dejar la
  propuesta a la vista para el PR); a `main` no se toca nunca a mano.
- Cada PR es **pequeño** para que Carles lo revise fácil y Kata lo entienda.

---

## 3. Conceptos técnicos aprendidos (en cristiano)

### Repos
El trabajo vive en **repos** (carpetas de proyecto). El código de la API está en
`elmetodo_api`; la documentación (esto) en `elmetodo_auto`. Son sitios distintos.

### Migración = receta que cambia la base de datos
Una **migración** es un archivo (un script de Python) con instrucciones para **cambiar
la estructura** de la base de datos: añadir/editar/borrar tablas o columnas, o meter datos.
- **No se ejecuta sola.** Es un papel guardado; la BD solo cambia cuando alguien lanza
  a propósito el comando *"aplicar"* (`alembic upgrade`).
- Cada cambio = **un archivo nuevo** (nunca se reescribe uno viejo). Quedan en fila,
  como **vagones de un tren**.
- Tiene dos partes: `upgrade` (**aplicar**) y `downgrade` (**deshacer**, por si hay marcha atrás).

### "Cabeza" (head) del tren de migraciones
La **cabeza** = el último vagón (el cambio más reciente). Nuestra migración se **engancha
al final** del tren. La cabeza anterior se llamaba `add_feedback_source_app` (un cambio
ajeno, sobre el feedback de usuarios); el nombre es solo una etiqueta.

### Ficha (modelo) vs receta (migración)
- Las **fichas** (modelos) describen *cómo es* cada tabla y sus columnas.
- La **receta** (migración) es la que *la construye de verdad* al aplicarse.
- El **índice** (`__init__.py`) es una lista para que el sistema sepa que las fichas existen.

### Clave foránea (foreign key) = "no puedes apuntar a algo que no existe"
Regla de seguridad de la BD. Ej.: nuestra tabla dice *"objetivo 1 → fuerza"*. Para meterlo,
la BD comprueba que el **objetivo 1 exista** en la tabla maestra `objectives`. Si no existe,
lo **rechaza** (evita datos basura).

### Crear una tabla ≠ llenarla de datos
Las tablas **nacen vacías** (estanterías). Los datos solo aparecen si **alguien los mete**.
Hay datos llamados **"de referencia"** (objetivos, ejercicios) que viven en **producción**
desde siempre, pero **no los crea ninguna migración** → una BD nueva no los tiene.

### Tests automáticos + por qué usan bases de datos vacías
Carles tiene un **"robot revisor"**: pruebas que corren **solas** cada vez que se propone
un cambio, para cazar fallos antes de que lleguen a usuarios. Para ser fiables, **montan
una BD limpia y nueva cada vez** (privacidad, repetible, aislada, rápida). La montan
**ejecutando todas las migraciones sobre una BD vacía**.

### El "dump" (la foto)
Para no partir de cero, los tests cargan una **foto** de una BD: el archivo
`tests/metodo_db_test.dump` (del 23 abr 2026). Esa foto trae **ejercicios** pero **no
objetivos** (cuando se tomó, la tabla de objetivos aún no existía). Por eso:
- Ejercicios → presentes ✅
- Objetivos → vacíos ❌

---

## 4. El problema que cazamos (y por qué importa)

Al probar nuestra migración en local sobre esa foto vacía de objetivos, **reventó**: intentó
sembrar *"objetivo 1 → fuerza"* y no había objetivo 1 → la BD lo rechazó → migración cancelada.

- En **producción** funcionaría (los objetivos existen).
- Pero en los **tests de Carles** (BD vacía) fallaría → PR en rojo.

La validación "en seco" (sin BD) **no podía detectar esto**. Solo lo cazó la **prueba en vivo**.
Por eso instalamos PostgreSQL y lo probamos de verdad.

---

## 5. El arreglo

Hicimos la siembra **a prueba de balas**: antes de meter cada mapeo, comprueba si el
ejercicio/objetivo **existe**. Si existe lo mete (producción), si no lo **salta sin romper**
(tests vacíos). Probado en los dos escenarios → **ambos en verde**.

Idea de Kata para Carles (anotada en el PR): **el dump de test está desactualizado**;
quizá convenga refrescarlo (decisión suya, porque afecta a todos los tests).

---

## 6. Estado actual y siguiente paso

- **Hecho:** código de las 4 tablas + arreglo, **en local**, en la rama
  `feat/puntuaciones-modelo-datos`. **Nada subido** todavía.
- **Probado:** las 4 tablas se crean con sus datos correctos en una BD real local.
- **Siguiente:** preparar el **PR para Carles** (cuando Kata lo diga — implica el primer
  `push`, siempre a la rama, nunca a `main`, y solo con su OK explícito).

---

## 7. Mini-glosario

| Palabra | En cristiano |
|---|---|
| Repo | Carpeta de un proyecto de código |
| Rama (branch) | Copia aislada para trabajar sin tocar lo bueno (`main`) |
| Commit | Guardar un cambio con su etiqueta |
| Push | Subir la rama a la nube (GitHub) |
| PR (Pull Request) | Propuesta de cambio para que la revisen y aprueben |
| Migración | Receta que cambia la estructura de la BD |
| Modelo | Ficha que describe una tabla |
| Foreign key | Regla: no apuntar a algo que no existe |
| Datos de referencia | Datos base (objetivos, ejercicios) que viven en producción |
| Dump | Foto/copia de una BD guardada en un archivo |
| Test automático | Prueba que corre sola para cazar fallos |
