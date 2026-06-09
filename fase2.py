# main_mpi_vlan.py
"""
Script de ejecución para la Fase 2: Redes Acopladas y Overhead vía MPI.
Utiliza el paradigma SPMD para simular VLANs interconectadas.
"""

import numpy as np
from mpi4py import MPI
# Importación modular del solver abstracto 
from sim_solver.rk4 import modelo_seir_base
# Importación modular de telemetría para benchmarking
from utils import registrar_tiempo

def paso_rk4_distribuido(comm, rank, size, t, Y, h, beta, sigma, gamma, N):
    """
    Calcula el avance temporal RK4 coordinando zonas de halo mediante MPI.
    """
    vecino_izq = (rank - 1) % size
    vecino_der = (rank + 1) % size
    I_recibido = np.array(0.0, dtype='d')

    # --- EVALUACIÓN K1 ---
    # Barrera de sincronización punto a punto para intercambiar estado K1
    comm.Sendrecv(sendbuf=np.array(Y[2], dtype='d'), dest=vecino_der, sendtag=11,
                  recvbuf=I_recibido, source=vecino_izq, recvtag=11)
    k1 = modelo_seir_base(t, Y, beta, sigma, gamma, N, float(I_recibido))

    # --- EVALUACIÓN K2 ---
    Y2 = Y + (h / 2.0) * k1 
    # Intercambio síncrono de la zona de halo para la pendiente intermedia K2
    comm.Sendrecv(sendbuf=np.array(Y2[2], dtype='d'), dest=vecino_der, sendtag=12,
                  recvbuf=I_recibido, source=vecino_izq, recvtag=12)
    k2 = modelo_seir_base(t + h/2.0, Y2, beta, sigma, gamma, N, float(I_recibido))

    # --- EVALUACIÓN K3 ---
    Y3 = Y + (h / 2.0) * k2 
    # CRÍTICO: Sincronización de datos de frontera para el cálculo de K3
    comm.Sendrecv(sendbuf=np.array(Y3[2], dtype='d'), dest=vecino_der, sendtag=13,
                  recvbuf=I_recibido, source=vecino_izq, recvtag=13) 
    k3 = modelo_seir_base(t + h/2.0, Y3, beta, sigma, gamma, N, float(I_recibido)) 

    # --- EVALUACIÓN K4 ---
    Y4 = Y + h * k3 
    # Último intercambio de datos de frontera síncronos para cerrar el paso RK4
    comm.Sendrecv(sendbuf=np.array(Y4[2], dtype='d'), dest=vecino_der, sendtag=14,
                  recvbuf=I_recibido, source=vecino_izq, recvtag=14) 
    k4 = modelo_seir_base(t + h, Y4, beta, sigma, gamma, N, float(I_recibido)) 

    return Y + (h / 6.0) * (k1 + 2.0*k2 + 2.0*k3 + k4)

def ejecutar():
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank() 
    size = comm.Get_size() 
    
    # Inicialización local de datos por proceso (VLAN de red)
    N_vlan = 25000
    Y = np.array([N_vlan - 50, 0, 50, 0], dtype='d') if rank == 0 else np.array([N_vlan, 0, 0, 0], dtype='d')
    t, h, pasos = 0.0, 0.1, 100
    historial = np.zeros((pasos + 1, 4))
    historial[0] = Y

    # Barrera global para sincronizar el inicio del cronómetro de rendimiento
    comm.Barrier()
    t_inicio = MPI.Wtime()

    for n in range(pasos):
        Y = paso_rk4_distribuido(comm, rank, size, t, Y, h, 0.4, 0.2, 0.05, N_vlan)
        t += h
        historial[n+1] = Y

    # Barrera global para detener el tiempo de cómputo unificadamente
    comm.Barrier()
    t_total = MPI.Wtime() - t_inicio

    # Barrera global para consolidar los resultados en el nodo raíz (Rank 0)
    todos_datos = comm.gather(historial, root=0)
    
    if rank == 0:
        print(f"Simulación finalizada en {t_total:.4f} segundos con {size} procesos.")
        registrar_tiempo("Fase 2 (MPI)", size, t_total)

if __name__ == "__main__":
    ejecutar()