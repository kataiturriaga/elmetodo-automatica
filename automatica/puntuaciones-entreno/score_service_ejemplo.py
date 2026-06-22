"""
BOCETO ILUSTRATIVO de la calculadora de Score de Fuerza  —  para APRENDER, no para producción.

⚠️  Esto NO es el código final. El motor real lo hará Carles en `elmetodo_api`,
    conectado a la base de datos y con tests. Este archivo vive en el repo de DOCS
    solo para entender (y juguetear con) la lógica del Paso 3 del plan.

Cómo se relaciona con los docs:
  - El "libro de reglas" (ESTANDARES)      → estandares-fuerza.md
  - La mini-tabla EJERCICIO_A_GRUPO        → curacion-ejercicios-fuerza.md
  - Los pasos del cálculo                  → tareas-implementacion-puntuaciones.md §3

Cómo ejecutarlo (en una terminal):
    python3 score_service_ejemplo.py
Prueba a cambiar los datos de "Marta" abajo y vuelve a ejecutarlo para ver cómo cambia el score.
"""

from statistics import median

# ─────────────────────────────────────────────────────────────────────────
# 1. EL "LIBRO DE REGLAS": tablas de estándares (de estandares-fuerza.md)
#    Para cada lift ancla: qué ratio (1RM ÷ peso) hace falta para cada score.
#    Solo pongo las anclas; H = hombre, M = mujer.
# ─────────────────────────────────────────────────────────────────────────
SCORES = [50, 100, 150, 200, 250, 300]  # los niveles

ESTANDARES = {
    # grupo:            { "H": [ratios...], "M": [ratios...] }   (alineados con SCORES)
    "pectorales":   {"H": [0.50, 0.75, 1.25, 1.75, 2.00, 2.20],
                     "M": [0.25, 0.50, 0.75, 1.00, 1.50, 1.65]},
    "espalda":      {"H": [0.50, 0.75, 1.00, 1.50, 1.75, 1.95],
                     "M": [0.25, 0.40, 0.65, 0.90, 1.20, 1.30]},
    "hombros":      {"H": [0.40, 0.55, 0.80, 1.05, 1.35, 1.50],
                     "M": [0.20, 0.35, 0.55, 0.75, 1.00, 1.10]},
    "cuadriceps":   {"H": [0.75, 1.25, 1.50, 2.25, 2.75, 3.00],
                     "M": [0.50, 0.75, 1.25, 1.50, 2.00, 2.20]},
    "isquiotibiales":{"H": [1.00, 1.50, 2.00, 2.50, 3.00, 3.30],
                     "M": [0.50, 1.00, 1.25, 1.75, 2.50, 2.75]},
    "biceps":       {"H": [0.20, 0.40, 0.60, 0.85, 1.15, 1.25],
                     "M": [0.10, 0.20, 0.40, 0.60, 0.85, 0.95]},
    "triceps":      {"H": [0.20, 0.35, 0.55, 0.80, 1.10, 1.20],
                     "M": [0.10, 0.20, 0.35, 0.55, 0.75, 0.85]},
}

# Mini-tabla ejercicio → grupo (de curacion-ejercicios-fuerza.md). Aquí solo unos pocos.
EJERCICIO_A_GRUPO = {
    484: "pectorales", 193: "pectorales", 126: "pectorales",
    594: "espalda", 331: "espalda",
    292: "hombros", 98: "hombros", 596: "hombros",
    337: "cuadriceps", 259: "cuadriceps", 313: "cuadriceps",
    601: "isquiotibiales", 413: "isquiotibiales",
    406: "biceps", 242: "biceps", 471: "biceps", 422: "biceps",
    305: "triceps", 490: "triceps", 411: "triceps",
}


# ─────────────────────────────────────────────────────────────────────────
# 2. LAS CUENTAS (cada función = un paso del viaje del Paso 3)
# ─────────────────────────────────────────────────────────────────────────
def epley_1rm(peso, reps):
    """Paso 1: estimar el máximo a 1 repetición desde una serie normal."""
    return peso * (1 + reps / 30)


def factor_edad(edad):
    """Paso 4 (ajuste): empujón para comparar justo a los mayores."""
    if edad < 30:  return 1.00
    if edad < 40:  return 1.05
    if edad < 50:  return 1.12
    if edad < 60:  return 1.22
    return 1.35


def score_de_grupo(grupo, mejor_ratio, genero, edad):
    """Coge el ratio ya ajustado por edad y lo busca en la tabla del grupo."""
    umbrales = ESTANDARES[grupo][genero]
    ratio = mejor_ratio * factor_edad(edad)

    # por debajo del primer nivel → entre 0 y 50
    if ratio <= umbrales[0]:
        return round(50 * ratio / umbrales[0])
    # por encima del último → 300+
    if ratio >= umbrales[-1]:
        return 300
    # en medio → interpolar entre los dos niveles que lo rodean
    for i in range(len(umbrales) - 1):
        if umbrales[i] <= ratio < umbrales[i + 1]:
            tramo = (ratio - umbrales[i]) / (umbrales[i + 1] - umbrales[i])
            return round(SCORES[i] + tramo * (SCORES[i + 1] - SCORES[i]))


def nivel(score):
    """Paso 7: traducir el número a su nombre."""
    if score < 50:  return "Principiante"
    if score < 100: return "Novato"
    if score < 150: return "Experimentado"
    if score < 200: return "Pro"
    if score < 250: return "Atleta"
    if score < 300: return "Élite"
    return "Olímpico"


def calcular_score(genero, edad, registros):
    """
    EL MOTOR COMPLETO.
    `registros` = lista de levantamientos: (exercise_id, peso, reps, peso_corporal_ese_dia)
    """
    # agrupar el MEJOR ratio de cada grupo (Paso 5: solo cuenta tu mejor ejercicio)
    mejor_ratio_por_grupo = {}
    for ex_id, peso, reps, peso_corporal in registros:
        grupo = EJERCICIO_A_GRUPO.get(ex_id)
        if grupo is None:        # ejercicio no válido (máquina, no mapeado) → ignorar
            continue
        ratio = epley_1rm(peso, reps) / peso_corporal   # Pasos 1-3
        if ratio > mejor_ratio_por_grupo.get(grupo, 0):
            mejor_ratio_por_grupo[grupo] = ratio

    # score de cada grupo con datos
    scores_grupo = {g: score_de_grupo(g, r, genero, edad)
                    for g, r in mejor_ratio_por_grupo.items()}

    # Paso 6: total = MEDIANA de los grupos con datos
    if not scores_grupo:
        return {"total": None, "nivel": None, "grupos": {}, "cobertura": "0 de 7"}
    total = round(median(scores_grupo.values()))
    return {
        "total": total,
        "nivel": nivel(total),
        "grupos": scores_grupo,
        "cobertura": f"{len(scores_grupo)} de 7 grupos",
    }


# ─────────────────────────────────────────────────────────────────────────
# 3. EJEMPLO: Marta, mujer, 42 años
#    (exercise_id, peso, reps, peso_corporal_ese_dia)
#    👉 Cambia estos números y vuelve a ejecutar para experimentar.
# ─────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    marta = [
        (337, 70, 4, 65),   # Sentadilla 70kg x4, pesaba 65kg  → cuádriceps
        (601, 85, 5, 65),   # Peso muerto 85kg x5             → isquios
        (484, 35, 6, 65),   # Press banca 35kg x6             → pecho
        (406, 20, 8, 65),   # Curl barra 20kg x8              → bíceps
        # (no registró espalda, hombros ni tríceps → saldrán fuera)
    ]
    r = calcular_score("M", 42, marta)
    print("SCORE TOTAL:", r["total"], "→", r["nivel"])
    print("Cobertura:", r["cobertura"])
    print("Por grupo:")
    for g, s in r["grupos"].items():
        print(f"   {g:15} {s}  ({nivel(s)})")
