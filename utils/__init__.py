# utils/__init__.py
"""
Paquete de utilidades y servicios transversales para el clúster.
Expone las herramientas de telemetría y benchmarking.
"""

# Elevamos las funciones principales a la raíz del paquete utils
from .telemetria import registrar_tiempo, generar_graficas_desde_json

# Definimos la API pública del paquete
__all__ = ['registrar_tiempo', 'generar_graficas_desde_json']