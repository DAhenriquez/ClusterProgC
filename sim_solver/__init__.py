# sim_solver/__init__.py
"""
Inicializador del paquete sim_solver.
Expone las herramientas de integración numérica directamente en la raíz.
"""

# Elevamos la función para no tener que escribir .rk4 al importar
from .rk4 import modelo_seir_base

# Definimos el __all__ para especificar qué se exporta públicamente
__all__ = ['modelo_seir_base']