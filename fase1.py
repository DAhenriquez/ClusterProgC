# main_secuencial.py
"""
Script de ejecución para la Fase 1: Baseline Secuencial.
Valida la corrección matemática de la curva SEIR en un único hilo de ejecución.
"""

import numpy as np
import matplotlib.pyplot as plt
# Importación modular del solver abstracto 
from sim_solver.rk4 import modelo_seir_base

def paso_rk4_secuencial(t, Y, h, beta, sigma, gamma, N):
    """
    Calcula el avance discreto de un paso temporal usando RK4 clásico.
    """
    k1 = modelo_seir_base(t, Y, beta, sigma, gamma, N)
    k2 = modelo_seir_base(t + h/2.0, Y + (h/2.0) * k1, beta, sigma, gamma, N)
    k3 = modelo_seir_base(t + h/2.0, Y + (h/2.0) * k2, beta, sigma, gamma, N)
    k4 = modelo_seir_base(t + h, Y + h * k3, beta, sigma, gamma, N)
    
    return Y + (h/6.0) * (k1 + 2.0*k2 + 2.0*k3 + k4)

def ejecutar_baseline():
    """
    Configura y corre la simulación secuencial base para generar las curvas.
    """
    # Configuración de la población global de la red
    N_total = 100000
    I0 = 10.0         # Brote inicial silencioso
    E0, P0 = 0.0, 0.0
    S0 = N_total - I0
    Y = np.array([S0, E0, I0, P0])
    
    # Parámetros temporales y epidemiológicos
    t, t_fin = 0.0, 100.0
    pasos = 1200
    h = (t_fin - t) / pasos
    
    # Historiales para almacenar la curva temporal
    tiempo = np.linspace(t, t_fin, pasos + 1)
    historial = np.zeros((pasos + 1, 4))
    historial[0] = Y
    
    # Integración numérica pura (sin sobrecarga de comunicación)
    for n in range(pasos):
        Y = paso_rk4_secuencial(t, Y, h, 1.5, 0.6, 0.15, N_total)
        t += h
        historial[n+1] = Y
        
    # Grafico (Validación matemática inicial)
    plt.figure(figsize=(10, 6))
    plt.plot(tiempo, historial[:, 0], label='Susceptibles (S)', color='blue')
    plt.plot(tiempo, historial[:, 1], label='Expuestos (E)', color='orange')
    plt.plot(tiempo, historial[:, 2], label='Infectados (I)', color='red')
    plt.plot(tiempo, historial[:, 3], label='Parcheados (P)', color='green')
    plt.xlabel('Tiempo (s)')
    plt.ylabel('Equipos en la Infraestructura')
    plt.title('Fase 1: Validación de Curva Epidemiológica SEIR Secuencial')
    plt.legend()
    plt.grid(True)
    #Exportar gráfico con alta resolución
    plt.savefig('curva_seir_fase1.png', dpi=300, bbox_inches='tight')
    print("--> Gráfico exportado exitosamente como 'curva_seir_fase1.png'")
    #Mostrar gráfico en pantalla
    plt.show()

if __name__ == "__main__":
    ejecutar_baseline()
