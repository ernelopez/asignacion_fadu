import streamlit as st
import numpy as np
from scipy.optimize import milp, LinearConstraint, Bounds
import pandas as pd

st.title("Asignación de letras a docentes")

# --- INPUTS ---

st.subheader("Cantidades por letra")
default_letras = {
    'A':35 , 'B':35, 'C':47, 'D':19, 'E':5, 'F':26, 'G':47,
    'H':12 , 'I':1, 'J':5, 'K':2, 'L':25, 'M':48, 'N':8,
    'O':11 , 'P':38, 'Q':7, 'R':41, 'S':32, 'T':12, 'U':7,
    'V':14 , 'W':1, 'X':0, 'Y':5, 'Z':5
}

dicc_letras = {}
cols = st.columns(6)
for i, (k, v) in enumerate(default_letras.items()):
    dicc_letras[k] = cols[i % 6].number_input(k, min_value=0, value=v)

st.subheader("Docentes")
docentes_text = st.text_area(
    "Ingresar nombres (uno por línea)",
    "ADRIANA\nADRIAN\nFLORENCIA\nGUIDO\nJUAN\nJUAN PABLO\nMIJAL\nROSA\nSANDRA\nVIRGINIA"
)
docentes = [d.strip() for d in docentes_text.split("\n") if d.strip()]

eps = st.number_input("Tolerancia (eps)", min_value=0, value=1)

# --- BOTÓN ---
if st.button("Resolver"):

    # limpiar ceros
    dicc_letras = {k: v for k, v in dicc_letras.items() if v != 0}

    letras = list(dicc_letras.keys())
    pesos = list(dicc_letras.values())

    N = sum(pesos)
    M = len(docentes)
    n = len(letras)
    K = round(N / M)

    c = np.zeros(n * M)

    # Restricción 1
    A1 = np.zeros((n, n * M))
    for i in range(n):
        for j in range(M):
            A1[i, i * M + j] = 1

    # Restricción 2
    A2 = np.zeros((M, n * M))
    for j in range(M):
        for i in range(n):
            A2[j, i * M + j] = pesos[i]

    A = np.vstack([A1, A2])

    lb = np.concatenate([
        np.ones(n),
        np.full(M, K - eps)
    ])

    ub = np.concatenate([
        np.ones(n),
        np.full(M, K + eps)
    ])

    constraints = LinearConstraint(A, lb, ub)
    bounds = Bounds(0, 1)
    integrality = np.ones(n * M)

    res = milp(
        c=c,
        constraints=constraints,
        bounds=bounds,
        integrality=integrality
    )
    
    if res.success:
        sol = res.x.reshape((n, M))
    
        filas = []
    
        for j in range(M):
            letras_doc = []
            for i in range(n):
                if sol[i, j] > 0.5:
                    letras_doc.append(letras[i])
    
            total = sum(pesos[i] * sol[i, j] for i in range(n))
    
            filas.append({
                "Docente": docentes[j],
                "Cantidad": int(total),
                "Letras": ", ".join(letras_doc)
            })
    
        df = pd.DataFrame(filas)
    
        st.subheader("Resultado")
        st.dataframe(df, use_container_width=True)
        st.text(f"Total estudiantes: {N}")
    
    else:
        st.error("No se encontró solución")
