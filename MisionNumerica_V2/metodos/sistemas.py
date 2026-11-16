"""Sala 3: Sistemas de Ecuaciones Lineales (fórmulas oficiales de la Ing. Oralia Zamora)."""

from typing import List, Dict, Any, Optional


def es_diagonal_dominante(A: List[List[float]]) -> bool:
    """Verifica |a_ii| > sum_{j != i} |a_ij| en todas las filas."""
    n = len(A)
    for i in range(n):
        diag = abs(A[i][i])
        suma_fuera = sum(abs(A[i][j]) for j in range(n) if j != i)
        if diag <= suma_fuera:
            return False
    return True


def metodo_montante(A: List[List[float]], b: List[float]) -> Dict[str, Any]:
    """Método de Montante con pivote anterior p_ant = 1."""
    n = len(A)
    M = [list(map(float, A[i])) + [float(b[i])] for i in range(n)]
    pasos = []
    p_ant = 1.0
    det_sign = 1.0
    for k in range(n):
        if abs(M[k][k]) < 1e-12:
            for r in range(k + 1, n):
                if abs(M[r][k]) >= 1e-12:
                    M[k], M[r] = M[r], M[k]
                    det_sign = -det_sign
                    break
        piv = M[k][k]
        if abs(piv) < 1e-12:
            raise ValueError("Pivote nulo en el método de Montante (sistema singular).")
        nueva = [[0.0] * (n + 1) for _ in range(n)]
        for i in range(n):
            for j in range(n + 1):
                if i == k:
                    nueva[i][j] = M[i][j]
                elif j == k:
                    nueva[i][j] = 0.0
                else:
                    nueva[i][j] = (piv * M[i][j] - M[i][k] * M[k][j]) / p_ant
        M = nueva
        p_ant = piv
        pasos.append({"pivote_idx": k + 1, "pivote": piv, "matriz": [fila[:] for fila in M]})
    det_bruto = M[n - 1][n - 1]
    solucion = [M[i][n] / det_bruto for i in range(n)]
    return {"solucion": solucion, "determinante": det_bruto * det_sign, "pasos": pasos}


def metodo_gauss_jordan(A: List[List[float]], b: List[float]) -> Dict[str, Any]:
    """Gauss-Jordan: reducción completa a matriz identidad [I | x]."""
    n = len(A)
    M = [list(map(float, A[i])) + [float(b[i])] for i in range(n)]
    pasos = []
    for k in range(n):
        if abs(M[k][k]) < 1e-12:
            for r in range(k + 1, n):
                if abs(M[r][k]) > 1e-12:
                    M[k], M[r] = M[r], M[k]
                    break
        piv = M[k][k]
        if abs(piv) < 1e-12:
            raise ValueError("Sistema singular en Gauss-Jordan.")
        M[k] = [val / piv for val in M[k]]
        for i in range(n):
            if i != k:
                factor = M[i][k]
                M[i] = [M[i][j] - factor * M[k][j] for j in range(n + 1)]
        pasos.append({"columna": k + 1, "matriz": [fila[:] for fila in M]})
    solucion = [M[i][n] for i in range(n)]
    return {"solucion": solucion, "pasos": pasos}


def eliminacion_gaussiana(A: List[List[float]], b: List[float]) -> Dict[str, Any]:
    """Eliminación gaussiana hacia adelante y sustitución hacia atrás."""
    n = len(A)
    M = [list(map(float, A[i])) + [float(b[i])] for i in range(n)]
    pasos = []
    for k in range(n - 1):
        if abs(M[k][k]) < 1e-12:
            for r in range(k + 1, n):
                if abs(M[r][k]) > 1e-12:
                    M[k], M[r] = M[r], M[k]
                    break
        piv = M[k][k]
        if abs(piv) < 1e-12:
            raise ValueError("Sistema singular en Eliminación Gaussiana.")
        for i in range(k + 1, n):
            factor = M[i][k] / piv
            for j in range(k, n + 1):
                M[i][j] -= factor * M[k][j]
        pasos.append({"paso": k + 1, "matriz": [fila[:] for fila in M]})

    x = [0.0] * n
    for i in range(n - 1, -1, -1):
        if abs(M[i][i]) < 1e-12:
            raise ValueError("Pivote nulo en sustitución hacia atrás.")
        suma = sum(M[i][j] * x[j] for j in range(i + 1, n))
        x[i] = (M[i][n] - suma) / M[i][i]
    return {"solucion": x, "triangular": [fila[:] for fila in M], "pasos": pasos}


def metodo_gauss_seidel(
    A: List[List[float]],
    b: List[float],
    x0: Optional[List[float]] = None,
    tol: float = 0.001,
    max_iter: int = 100,
) -> Dict[str, Any]:
    """Gauss-Seidel: usa valores recién actualizados, x0=(0,...,0), ε_j = |x_j^(k+1) - x_j^k|."""
    n = len(A)
    diag_dom = es_diagonal_dominante(A)
    x = list(x0) if x0 is not None else [0.0] * n
    iteraciones = []
    for it in range(1, max_iter + 1):
        x_ant = list(x)
        for i in range(n):
            if abs(A[i][i]) < 1e-12:
                raise ValueError("Cero en la diagonal principal en Gauss-Seidel.")
            suma = sum(A[i][j] * x[j] for j in range(n) if j != i)
            x[i] = (b[i] - suma) / A[i][i]
        errores = [abs(x[i] - x_ant[i]) for i in range(n)]
        err_max = max(errores)
        iteraciones.append({
            "iter": it,
            "x": list(x),
            "errores": errores,
            "error_max": err_max,
        })
        if err_max <= tol:
            break
    return {
        "solucion": x,
        "diagonal_dominante": diag_dom,
        "iteraciones": iteraciones,
    }


def metodo_jacobi(
    A: List[List[float]],
    b: List[float],
    x0: Optional[List[float]] = None,
    tol: float = 0.001,
    max_iter: int = 100,
) -> Dict[str, Any]:
    """Jacobi: usa exclusivamente valores de la iteración anterior, ε_j = |x_j^(k+1) - x_j^k|."""
    n = len(A)
    diag_dom = es_diagonal_dominante(A)
    x = list(x0) if x0 is not None else [1.0] * n
    iteraciones = []
    for it in range(1, max_iter + 1):
        x_nuevo = [0.0] * n
        for i in range(n):
            if abs(A[i][i]) < 1e-12:
                raise ValueError("Cero en la diagonal principal en Jacobi.")
            suma = sum(A[i][j] * x[j] for j in range(n) if j != i)
            x_nuevo[i] = (b[i] - suma) / A[i][i]
        errores = [abs(x_nuevo[i] - x[i]) for i in range(n)]
        err_max = max(errores)
        x = x_nuevo
        iteraciones.append({
            "iter": it,
            "x": list(x),
            "errores": errores,
            "error_max": err_max,
        })
        if err_max <= tol:
            break
    return {
        "solucion": x,
        "diagonal_dominante": diag_dom,
        "iteraciones": iteraciones,
    }
