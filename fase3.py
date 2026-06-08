# main_fuzzing_colas.py
"""
Script de ejecución para la Fase 3: Fuzzing y Monte Carlo vía Colas de Trabajo.
Despacha miles de mutaciones independientes de manera asíncrona[cite: 295, 503].
"""

import numpy as np
import ipyparallel as ipp
import time

def tarea_individual_fuzzing(parametros):
    """
    Envuelve la ejecución de una simulación mutada en el motor remoto.
    """
    # SOLUCIÓN DE CONTEXTO: Importación local para el entorno aislado del motor
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
        dview = rc.load_balanced_view() # Vista con balanceo dinámico de carga [cite: 368]
    except:
        print("Error al conectar. Verifica que levantaste 'ipcluster start'")
        return

    num_sim = 5000
    np.random.seed(42)
    tareas = [(np.random.uniform(0.3, 0.6), np.random.uniform(0.15, 0.35), 
               np.random.uniform(0.04, 0.12), 100000, 200, 0.25) for _ in range(num_sim)]
    
    print(f"Enviando {num_sim} tareas asíncronas a la cola del clúster...")
    t_inf = time.time()
    
    # Despacho asíncrono sin bloqueo del cliente central [cite: 318]
    asinc_res = dview.map_async(tarea_individual_fuzzing, tareas)
    asinc_res.wait_interactive() # Renderizado interactivo de barra de progreso en terminal
    
    resultados = asinc_res.get()
    print(f"Completado en: {time.time() - t_inf:.2f} segundos.")

if __name__ == "__main__":
    orquestar()