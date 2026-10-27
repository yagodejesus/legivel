"""Contagem aproximada de sílabas em português brasileiro.

Heurística baseada em grupos vocálicos, com regras para hiatos, ditongos
nasais (``ão``, ``õe``), ``qu``/``gu`` e ditongos crescentes átonos
(``his-tó-ria`` tem 3 sílabas; ``di-a`` tem 2). Erra em casos raros, o que é
aceitável para fórmulas de legibilidade, que trabalham com médias.
"""

from __future__ import annotations

import re

__all__ = ["contar_silabas"]

_FORTES = frozenset("aeoáéóâêôãõà")
_FRACAS = frozenset("iuy")
_FRACAS_ACENTUADAS = frozenset("íú")
_GRUPO = re.compile(r"[aeiouyáéíóúâêôãõà]+")
_TONICA = re.compile(r"[áéíóúâêô]")
_QU_GU = re.compile(r"([qg])[uü](?=[aeioáéíóâêôãõ])")
_NAO_LETRA = re.compile(r"[^a-zà-öø-ÿ]")


def _separa(a: str, b: str, pos_a: int, pos_tonica: int | None) -> bool:
    if b in _FRACAS_ACENTUADAS or a in _FRACAS_ACENTUADAS:
        return True  # hiato: sa-ú-de, pa-ís, sa-í-a
    if a in "ãõ" and b in "eo":
        return False  # ditongo nasal: ão, ãe, õe
    if a in _FORTES and b in _FORTES:
        return True  # hiato: po-e-ta, vo-o
    if a in _FORTES or b in _FRACAS:
        return False  # ditongo decrescente (ai, eu, ou) ou ui/iu
    # fraca + forte (ia, io, ua, ie): ditongo se vier depois da sílaba tônica marcada
    return not (pos_tonica is not None and pos_tonica < pos_a)


def contar_silabas(palavra: str) -> int:
    """Conta as sílabas de uma palavra (números contam como 1 sílaba por dígito, até 6)."""
    p = palavra.lower()
    if not any(c.isalpha() for c in p):
        digitos = sum(c.isdigit() for c in p)
        return max(1, min(digitos, 6)) if digitos else 0
    p = _NAO_LETRA.sub("", p)
    p = _QU_GU.sub(r"\1", p).replace("ü", "u")
    tonica = _TONICA.search(p)
    pos_tonica = tonica.start() if tonica else None
    total = 0
    for m in _GRUPO.finditer(p):
        g = m.group()
        total += 1 + sum(_separa(g[i], g[i + 1], m.start() + i, pos_tonica) for i in range(len(g) - 1))
    return max(total, 1)
