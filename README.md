# Modelado Numérico Epidemiológico en Redes Masivas

Este repositorio contiene la implementación de un sistema de simulación de alto rendimiento (HPC) diseñado para modelar la propagación espacial y temporal de un malware (amenaza Zero-Day) dentro de infraestructuras corporativas masivas. 

El proyecto resuelve el modelo epidemiológico SEIR (Susceptibles, Expuestos, Infectados, Parcheados) mediante la integración numérica del método de Runge-Kutta de cuarto orden (RK4). Para superar las limitaciones computacionales del modelado a gran escala, se contrastan empíricamente dos paradigmas de software distribuido: el paso de mensajes síncrono (MPI) y las colas de trabajo asíncronas (Fuzzing/Monte Carlo).

---

## Arquitectura del Software

El sistema está diseñado bajo una arquitectura modular, separando el núcleo matemático de las interfaces de paralelización. Las estrategias de cómputo se dividen en tres fases de ejecución:

1. **Baseline Secuencial:** Validación algorítmica de las curvas poblacionales en un único hilo de ejecución.
2. **Modelo SPMD (Memoria Distribuida):** Subdivisión topológica de la red en VLANs. Utiliza `mpi4py` para la sincronización de las zonas de halo (fronteras de red) entre procesos independientes mediante comunicación punto a punto. Demuestra empíricamente el impacto del overhead de red y las limitaciones de escalabilidad descritas por la Ley de Amdahl.
3. **Desacoplamiento Estocástico (Colas de Trabajo):** Ejecución masiva de simulaciones independientes (Fuzzing) variando las tasas de infección y latencia. Utiliza `ipyparallel` bajo un modelo asíncrono para lograr un factor de aceleración (Speedup) lineal.

---

## Estructura del Repositorio

```text
├── sim_solver/               # Paquete de integración matemática
│   ├── __init__.py
│   └── rk4.py                # Modelo SEIR y algoritmo RK4 abstracto
│
├── fase1.py        # FASE 1: Simulación base y graficación
├── fase2.py          # FASE 2: Ejecución acoplada vía MPI
├── fase3.py     # FASE 3: Simulaciones Monte Carlo asíncronas
├── .gitignore                # Reglas de exclusión para entornos y cachés
└── README.md                 # Documentación técnica

```

---

## Requisitos del Sistema e Instalación

El sistema requiere un entorno Linux con soporte nativo para MPI. Las pruebas fueron desarrolladas y validadas en Debian.

### 1. Dependencias a nivel de Sistema Operativo

Se requieren los compiladores base y las bibliotecas de OpenMPI:

```bash
sudo apt update
sudo apt install build-essential python3-dev openmpi-bin libopenmpi-dev python3-tk

```

### 2. Entorno Virtual y Dependencias de Python

Se recomienda el uso de un entorno virtual para aislar las dependencias del proyecto.

```bash
python3 -m venv venv
source venv/bin/activate
pip install numpy matplotlib mpi4py ipyparallel

```

---

## Instrucciones de Ejecución

Cada fase del proyecto debe ejecutarse con su respectivo gestor de recursos.

### Fase 1: Validación Secuencial

Genera la curva epidemiológica resolviendo el modelo sin particiones topológicas. Exporta el resultado en un archivo de imagen.

```bash
python3 fase1.py

```

### Fase 2: Ejecución MPI (Redes Acopladas)

Asigna un número específico de núcleos lógicos (VLANs). Reemplace `<num_procesos>` con la cantidad de núcleos deseada (por ejemplo, 4).

```bash
mpiexec -n <num_procesos> python3 fase2.py

```

### Fase 3: Ejecución en Clúster Virtual (ipyparallel)

Requiere el inicio previo de la infraestructura del clúster y los motores de procesamiento.

```bash
# 1. Iniciar los motores de trabajo en una terminal independiente
ipcluster start -n <num_procesos>

# 2. Ejecutar la orquestación masiva en la terminal principal
python3 fase3.py

```

Para detener el clúster una vez finalizada la simulación, utilice `Ctrl + C`  o `ipcluster stop` en la terminal donde se iniciaron los motores.

---

## Autores y Colaboradores

Proyecto desarrollado para la asignatura de Programación Científica, Universidad Autónoma de Chile (Sede Temuco).

* **Diego A. Henríquez**
* **Carlos I. Márquez**


*Ingeniería Civil Informática UA - 2026*

```

```
