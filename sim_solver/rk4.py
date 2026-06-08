# sim_solver/rk4.py
"""
Módulo especializado en la integración numérica de modelos epidemiológicos.
Provee las funciones abstractas para el modelo SEIR y el avance discreto RK4.
"""

import numpy as np

def modelo_seir_base(t, Y, beta, sigma, gamma, N, I_vecino=0.0):
    """
    Calcula las derivadas temporales del modelo epidémico SEIR.

    Parameters
    ----------
    t : float
        Instante de tiempo actual.
    Y : ndarray
        Vector de estado local [S, E, I, P].
    beta : float
        Tasa de propagación del malware.
    sigma : float
        Tasa de latencia de la vulnerabilidad.
    gamma : float
        Velocidad de distribución de parches.
    N : int
        Número total de equipos en el dominio local.
    I_vecino : float, optional
        Población infectada contigua para acoplamiento de red (Fase 2).

    Returns
    -------
    ndarray
        Derivadas instantáneas [dS/dt, dE/dt, dI/dt, dP/dt].
    """
    S, E, I, P = Y
    
    # Incorporación del impacto de infección cruzada entre fronteras (VLANs)
    I_efectivo = I + 0.1 * I_vecino
    
    dS_dt = -beta * (S * I_efectivo) / N 
    dE_dt = beta * (S * I_efectivo) / N - sigma * E 
    dI_dt = sigma * E - gamma * I 
    dP_dt = gamma * I 
    
    return np.array([dS_dt, dE_dt, dI_dt, dP_dt])