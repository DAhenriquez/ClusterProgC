# main_fuzzing_colas.py
"""
Script de ejecución para la Fase 3: Fuzzing y Monte Carlo vía Colas de Trabajo.
Despacha miles de mutaciones independientes de manera asíncrona.
"""

import numpy as np
import ipyparallel as ipp
import time
#Importación modular de telemetría para benchmarking
from utils import registrar_tiempo


def tarea_individual_fuzzing(parametros):
    """
    Envuelve la ejecución de una simulación mutada en el motor remoto.
    """
    # Importación local para el entorno aislado del motor
    import numpy as np
    from sim_solver.rk4 import modelo_seir_base
    
    beta, sigma, gamma, N, pasos, h = parametros
    Y = np.array([N - 10.0, 0.0, 10.0, 0.0])
    max_infectados = 10.0
    t = 0.0
    
    for _ in range(pasos):
        # Evaluación secuencial RK4 pura en el motor (Sin intercomunicación)
        k1 = modelo_seir_base(t, Y, beta, sigma, gamma, N)
        k2 = modelo_seir_base(t + h/2.0, Y + (h/2.0)*k1, beta, sigma, gamma, N)
        k3 = modelo_seir_base(t + h/2.0, Y + (h/2.0)*k2, beta, sigma, gamma, N)
        k4 = modelo_seir_base(t + h, Y + h*k3, beta, sigma, gamma, N)
        
        Y = Y + (h/6.0) * (k1 + 2.0*k2 + 2.0*k3 + k4)
        t += h
        if Y[2] > max_infectados:
            max_infectados = Y[2]
            
    return max_infectados

def orquestar():
    try:
        rc = ipp.Client()
        dview = rc.load_balanced_view() # Vista con balanceo dinámico de carga
        #Obtener la cantidad de núcleos reales
        size = len(rc.ids)
    except:
        print("Error al conectar. Verifica que levantaste 'ipcluster start'")
        return

    num_sim = 10000
    np.random.seed(42)
    tareas = [(np.random.uniform(0.3, 0.6), np.random.uniform(0.15, 0.35), 
               np.random.uniform(0.04, 0.12), 100000, 5000, 0.01) for _ in range(num_sim)]
    
    print(f"Enviando {num_sim} tareas asíncronas a la cola del clúster de {size} motores...")
    t_inf = time.time()
    
    # Despacho asíncrono sin bloqueo del cliente central 
    asinc_res = dview.map_async(tarea_individual_fuzzing, tareas, chunksize=100)
    asinc_res.wait_interactive() # Renderizado interactivo de barra de progreso en terminal
    
    resultados = asinc_res.get()

    t_total = time.time() - t_inf
    print(f"Completado en: {t_total:.2f} segundos.")
    #Registramos el tiempo de ejecución en el sistema de telemetría para benchmarking
    registrar_tiempo("Fase 3 (Colas)", size, t_total)

if __name__ == "__main__":
    orquestar()
