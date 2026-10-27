"""Limpeza de Markdown e segmentação em parágrafos, frases e palavras.

A limpeza troca a sintaxe por espaços em vez de apagá-la, preservando as
posições originais: assim cada problema aponta a linha e a coluna exatas.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

__all__ = ["limpar_markdown", "segmentar", "palavras", "Frase", "Paragrafo"]

_ABREVIACOES = frozenset(
    """sr sra srta srs sras dr dra drs dras prof profa profs art arts inc n nº no núm num p pp pág
    págs ex exa exmo exma etc av r tel cel vol cap min máx mín obs fl fls ltda jr ed op cit aprox
    dept depto esq cia vs séc sec cf adm eng arq fig figs tab ib id ibid pe sto sta""".split()
)
_FIM_FRASE = re.compile(r"[.!?…]+[\"'”»)\]]*(?=\s|$)")
_PALAVRA = re.compile(r"[A-Za-zÀ-ÖØ-öø-ÿ]+(?:[-'’][A-Za-zÀ-ÖØ-öø-ÿ]+)*|\d+(?:[.,]\d+)*")
_MARCADOR_LISTA = re.compile(r"[ \t]*(?:[-*+•–]|\d{1,3}[.)]|[a-z][)])[ \t]+")
_TITULO = re.compile(r"(?m)^[ \t]{0,3}#{1,6}[ \t]")


def _brancos(m: re.Match[str]) -> str:
    return re.sub(r"[^\n]", " ", m.group())


def limpar_markdown(texto: str) -> str:
    """Remove a sintaxe Markdown/HTML mantendo o comprimento e as quebras de linha."""
    t = re.sub(r"(?ms)^[ \t]*(```|~~~).*?^[ \t]*\1[^\n]*$", _brancos, texto)
    t = re.sub(r"`[^`\n]*`", _brancos, t)
    t = re.sub(r"(?s)<!--.*?-->", _brancos, t)
    t = re.sub(r"<[^>\n]+>", _brancos, t)
    t = re.sub(r"!\[[^\]\n]*\]\([^)\n]*\)", _brancos, t)
    t = re.sub(
        r"\[([^\]\n]*)\]\([^)\n]*\)",
        lambda m: " " + m.group(1) + " " * (len(m.group()) - len(m.group(1)) - 1),
        t,
    )
    t = re.sub(r"https?://\S+", _brancos, t)
    t = re.sub(r"(?m)^[ \t]{0,3}#{1,6}[ \t]", _brancos, t)
    t = re.sub(r"(?m)^[ \t]*>[ \t]?", _brancos, t)
    t = re.sub(r"(?m)^[ \t]*\|?[ \t:|-]*-{3,}[ \t:|-]*$", _brancos, t)
    t = re.sub(r"(?<!\w)[*_]{1,3}(?=\S)|(?<=\S)[*_]{1,3}(?!\w)", _brancos, t)
    return t.replace("|", "\n")


@dataclass(frozen=True)
class Frase:
    inicio: int
    fim: int
    texto: str
    titulo: bool = False


@dataclass(frozen=True)
class Paragrafo:
    inicio: int
    fim: int
    frases: tuple[Frase, ...]


def palavras(texto: str) -> list[re.Match[str]]:
    return list(_PALAVRA.finditer(texto))


def _frases(texto: str, ini: int, fim: int) -> list[Frase]:
    resultado: list[Frase] = []
    primeiro = re.compile(r"\S").search(texto, ini, fim)
    inicio = primeiro.start() if primeiro else fim
    for m in _FIM_FRASE.finditer(texto, ini, fim):
        if m.start() <= inicio:
            continue
        anterior = re.search(r"(\S+)$", texto[inicio : m.start()])
        palavra = anterior.group(1).lower() if anterior else ""
        if m.group() == ".":
            base = palavra.strip("([\"'“")
            if (
                base in _ABREVIACOES
                or re.fullmatch(r"[a-zà-ÿ]", base)
                or re.fullmatch(r"(?:[a-zà-ÿ]{1,3}\.)+[a-zà-ÿ]{1,3}", base)
            ):
                continue
        seguinte = re.compile(r"\S").search(texto, m.end(), fim)
        if seguinte and seguinte.group().islower():
            continue
        resultado.append(Frase(inicio, m.end(), texto[inicio : m.end()]))
        inicio = seguinte.start() if seguinte else fim
    resto = texto[inicio:fim]
    if _PALAVRA.search(resto):
        fim_util = inicio + len(resto.rstrip())
        resultado.append(Frase(inicio, fim_util, texto[inicio:fim_util]))
    return resultado


def segmentar(texto_limpo: str, original: str | None = None) -> list[Paragrafo]:
    """Divide o texto em parágrafos (separados por linha em branco) e frases.

    Itens de lista e títulos (detectados no ``original``) viram unidades próprias;
    frases de títulos são marcadas com ``titulo=True``.
    """
    original = original if original is not None else texto_limpo
    titulos = {m.start() for m in _TITULO.finditer(original)}
    paragrafos: list[Paragrafo] = []
    for bloco in re.finditer(r"(?:[^\n]|\n(?![ \t]*\n))+", texto_limpo):
        unidades: list[list] = []  # [inicio, fim, eh_titulo]
        for linha in re.finditer(r"[^\n]+", bloco.group()):
            if not linha.group().strip():
                continue
            ini = bloco.start() + linha.start()
            fim = bloco.start() + linha.end()
            item = _MARCADOR_LISTA.match(original, ini)
            eh_titulo = ini in titulos
            if item or eh_titulo or not unidades or unidades[-1][2]:
                unidades.append([item.end() if item else ini, fim, eh_titulo])
            else:
                unidades[-1][1] = fim
        frases: list[Frase] = []
        for ini, fim, eh_titulo in unidades:
            for f in _frases(texto_limpo, ini, fim):
                frases.append(Frase(f.inicio, f.fim, f.texto, eh_titulo))
        if frases:
            paragrafos.append(Paragrafo(frases[0].inicio, frases[-1].fim, tuple(frases)))
    return paragrafos
