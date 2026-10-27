"""legivel — verificador de Linguagem Simples e legibilidade para textos em português."""

__version__ = "0.1.0"

from .analise import REGRAS, Analise, Config, Estatisticas, Problema, analisar, flesch, nivel_flesch
from .silabas import contar_silabas

__all__ = [
    "__version__",
    "Analise",
    "Config",
    "Estatisticas",
    "Problema",
    "REGRAS",
    "analisar",
    "contar_silabas",
    "flesch",
    "nivel_flesch",
]
