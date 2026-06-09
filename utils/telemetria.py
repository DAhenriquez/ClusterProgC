# utils/telemetria.py
"""
Módulo de benchmarking automatizado.
Gestiona el registro I/O de tiempos de ejecución y la generación de gráficas HPC.
"""

import json
import os
import matplotlib.pyplot as plt
import numpy as np

ARCHIVO_METRICAS = 'resultados_benchmarking.json'

def inicializar_registro():
    """Crea un JSON vacío si no existe para evitar errores de lectura."""
    if not os.path.exists(ARCHIVO_METRICAS):
        base = {"Fase 2 (MPI)": {}, "Fase 3 (Colas)": {}}
        with open(ARCHIVO_METRICAS, 'w') as f:
            json.dump(base, f, indent=4)

def registrar_tiempo(fase, nucleos, tiempo):
    """
    Persiste el tiempo de ejecución en disco agregándolo a un historial. 
    En entornos MPI, debe invocarse exclusivamente desde el Rank 0.
    """
    inicializar_registro()
    
    with open(ARCHIVO_METRICAS, 'r') as f:
        datos = json.load(f)
        
    # Si es la primera vez que probamos esta cantidad de núcleos, creamos una lista vacía
    if str(nucleos) not in datos[fase]:
        datos[fase][str(nucleos)] = []
        
    # Agregamos el nuevo tiempo a la lista de corridas
    datos[fase][str(nucleos)].append(tiempo)
    
    with open(ARCHIVO_METRICAS, 'w') as f:
        json.dump(datos, f, indent=4)
        
    print(f"--> [Telemetría] {fase} | Nodos: {nucleos} | Tiempo registrado: {tiempo:.4f}s")

def generar_graficas_desde_json():
    """
    Lee el archivo de métricas, promedia las ejecuciones y genera automáticamente 
    el análisis de Speedup y Eficiencia Paralela utilizando Matplotlib.
    """
    if not os.path.exists(ARCHIVO_METRICAS):
        print("Error: No hay métricas registradas aún. Ejecuta las simulaciones primero.")
        return
        
    with open(ARCHIVO_METRICAS, 'r') as f:
        datos = json.load(f)
        
    # Extraer las llaves de los núcleos que se hayan registrado (ej. "1", "2", "4")
    nucleos_str = sorted(datos["Fase 3 (Colas)"].keys(), key=int)
    
    if not nucleos_str:
        print("Error: Faltan datos en el JSON para graficar.")
        return
        
    nucleos = np.array([int(n) for n in nucleos_str])
    
    # Extraer tiempos calculando el PROMEDIO de la lista de corridas
    # Si no hay datos, se usa una lista con infinito para evitar divisiones por cero
    tiempos_mpi = np.array([np.mean(datos["Fase 2 (MPI)"].get(n, [float('inf')])) for n in nucleos_str])
    tiempos_colas = np.array([np.mean(datos["Fase 3 (Colas)"].get(n, [float('inf')])) for n in nucleos_str])
    
    # Calcular Speedup (Tiempo promedio con 1 núcleo / Tiempo promedio con p núcleos)
    speedup_mpi = tiempos_mpi[0] / tiempos_mpi
    speedup_colas = tiempos_colas[0] / tiempos_colas
    speedup_ideal = nucleos
    
    # Calcular Eficiencia Paralela (Speedup / p)
    eficiencia_mpi = speedup_mpi / nucleos
    eficiencia_colas = speedup_colas / nucleos
    eficiencia_ideal = np.ones(len(nucleos))
    
    # --- CONFIGURACIÓN DE GRÁFICOS MATPLOTLIB ---
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Gráfica 1: Curvas de Speedup
    ax1.plot(nucleos, speedup_ideal, 'k--', label='Speedup Ideal (Lineal)')
    ax1.plot(nucleos, speedup_colas, 'go-', linewidth=2, label='Fase 3: Colas (ipyparallel)')
    ax1.plot(nucleos, speedup_mpi, 'ro-', linewidth=2, label='Fase 2: MPI Acoplado')
    
    ax1.set_title('Análisis de Escalabilidad: Curvas de Speedup', fontsize=14)
    ax1.set_xlabel('Número de Procesadores (Nodos)', fontsize=12)
    ax1.set_ylabel('Speedup', fontsize=12)
    ax1.set_xticks(nucleos)
    ax1.grid(True, linestyle='--', alpha=0.7)
    ax1.legend()

    # Gráfica 2: Eficiencia Paralela
    ax2.plot(nucleos, eficiencia_ideal, 'k--', label='Eficiencia Ideal (100%)')
    ax2.plot(nucleos, eficiencia_colas, 'go-', linewidth=2, label='Fase 3: Colas')
    ax2.plot(nucleos, eficiencia_mpi, 'ro-', linewidth=2, label='Fase 2: MPI')

    ax2.set_title('Eficiencia Paralela', fontsize=14)
    ax2.set_xlabel('Número de Procesadores (Nodos)', fontsize=12)
    ax2.set_ylabel('Eficiencia (0 a 1)', fontsize=12)
    ax2.set_xticks(nucleos)
    ax2.set_ylim(0, 1.1)
    ax2.grid(True, linestyle='--', alpha=0.7)
    ax2.legend()

    # Guardar en disco
    plt.tight_layout()
    plt.savefig('benchmarking_hpc.png', dpi=300, bbox_inches='tight')
    print("--> ¡Éxito! Gráficas exportadas como 'benchmarking_hpc.png' usando tiempos promediados.")

if __name__ == "__main__":
    generar_graficas_desde_json()