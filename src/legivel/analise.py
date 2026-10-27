"""Análise de legibilidade e Linguagem Simples."""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import asdict, dataclass, field
from typing import Any

from .regras import ESTRANGEIRISMOS, JARGOES, SIGLAS_CONHECIDAS, VERBOS_DE_SUBSTANTIVOS, eh_participio
from .silabas import contar_silabas
from .texto import Frase, limpar_markdown, palavras, segmentar

__all__ = ["Config", "Problema", "Estatisticas", "Analise", "analisar", "flesch", "nivel_flesch", "REGRAS"]

REGRAS = (
    "FRASE_LONGA",
    "PARAGRAFO_LONGO",
    "JARGAO",
    "ESTRANGEIRISMO",
    "VOZ_PASSIVA",
    "NOMINALIZACAO",
    "SIGLA",
    "CAIXA_ALTA",
)
GRAVIDADES = ("alta", "media", "baixa")
_PESO = {"alta": 0, "media": 1, "baixa": 2}

_SER = (
    r"(?:é|são|foi|foram|será|serão|era|eram|seria|seriam|seja|sejam|fosse|fossem|for|forem|"
    r"sido|ser|sendo|fora)"
)
_PASSIVA = re.compile(rf"\b{_SER}\s+(?:\w+mente\s+)?(\w+)\b", re.I)
_VERBO_VAZIO = re.compile(
    r"\b(realiz\w*|efetu\w*|proced\w*|promov\w*|fazer|faz|fazem|fez|fizemos|fizeram|fará|farão|"
    r"faremos|execut\w*)\s+(?:(?:a|à|o|ao|as|às|os|aos|uma|um|essa|esse|esta|este|nova|novo)\s+)?"
    r"(\w+)\b",
    re.I,
)
_SUFIXO_NOMINAL = re.compile(r"(?:ção|ções|mento|mentos|ância|ência|agem|são|sões)$")
_SIGLA = re.compile(r"\b(?=\w*[A-Z]\w*[A-Z])[A-Z][A-Za-z0-9]{1,7}\b")
_ROMANO = re.compile(r"[IVXLCDM]+")


def _compilar(dic: dict[str, str]) -> list[tuple[re.Pattern[str], str]]:
    return [(re.compile(rf"(?<!\w)(?:{p})(?!\w)", re.I), s) for p, s in dic.items()]


_JARGOES_RE = _compilar(JARGOES)
_ESTRANGEIRISMOS_RE = _compilar(ESTRANGEIRISMOS)


def flesch(palavras_por_frase: float, silabas_por_palavra: float) -> float:
    """Índice de Facilidade de Leitura de Flesch adaptado ao português.

    Martins, Ghiraldelo, Nunes & Oliveira Jr. (1996):
    ``248,835 − 1,015 × (palavras/frase) − 84,6 × (sílabas/palavra)``, limitado a 0–100.
    """
    valor = 248.835 - 1.015 * palavras_por_frase - 84.6 * silabas_por_palavra
    return max(0.0, min(100.0, valor))


def nivel_flesch(indice: float) -> tuple[str, str]:
    """Faixa de dificuldade e escolaridade aproximada (Martins et al., 1996)."""
    if indice >= 75:
        return "muito fácil", "1º ao 5º ano"
    if indice >= 50:
        return "fácil", "6º ao 9º ano"
    if indice >= 25:
        return "difícil", "ensino médio e superior"
    return "muito difícil", "textos acadêmicos e especializados"


@dataclass
class Config:
    max_palavras_frase: int = 25
    max_palavras_paragrafo: int = 120
    ignorar: set[str] = field(default_factory=set)
    siglas_conhecidas: set[str] = field(default_factory=lambda: set(SIGLAS_CONHECIDAS))
    jargoes_extras: dict[str, str] = field(default_factory=dict)


@dataclass
class Problema:
    regra: str
    gravidade: str
    mensagem: str
    trecho: str
    linha: int
    coluna: int
    sugestao: str | None = None


@dataclass
class Estatisticas:
    paragrafos: int
    frases: int
    palavras: int
    silabas: int
    palavras_longas: int
    palavras_por_frase: float
    silabas_por_palavra: float
    flesch: float


@dataclass
class Analise:
    estatisticas: Estatisticas
    problemas: list[Problema]

    @property
    def flesch(self) -> float:
        return self.estatisticas.flesch

    @property
    def nivel(self) -> str:
        return nivel_flesch(self.flesch)[0]

    def contagem(self) -> dict[str, int]:
        c = Counter(p.gravidade for p in self.problemas)
        return {g: c.get(g, 0) for g in GRAVIDADES}

    def aprovado(self, min_flesch: float | None = None, falhar_em: str = "alta") -> bool:
        """``False`` se o índice ficar abaixo de ``min_flesch`` ou houver problema da gravidade dada."""
        if min_flesch is not None and self.flesch < min_flesch:
            return False
        if falhar_em == "nunca":
            return True
        limite = _PESO[falhar_em]
        return not any(_PESO[p.gravidade] <= limite for p in self.problemas)

    def to_dict(self) -> dict[str, Any]:
        return {
            "estatisticas": asdict(self.estatisticas),
            "nivel": self.nivel,
            "escolaridade": nivel_flesch(self.flesch)[1],
            "problemas": [asdict(p) for p in self.problemas],
        }

    def relatorio(self, nome: str = "texto", cor: bool = False) -> str:
        def c(codigo: str, s: str) -> str:
            return f"\033[{codigo}m{s}\033[0m" if cor else s

        e = self.estatisticas
        nivel, escolaridade = nivel_flesch(e.flesch)
        tom = "32" if e.flesch >= 50 else "33" if e.flesch >= 25 else "31"
        linhas = [
            f"{c('1', nome)} — Índice de Flesch: {c(tom, _br(e.flesch))} ({nivel} · {escolaridade})",
            f"  {e.frases} frases · {e.palavras} palavras · {_br(e.palavras_por_frase)} palavras/frase"
            f" · {_br(e.silabas_por_palavra, 2)} sílabas/palavra",
        ]
        cores = {"alta": "31", "media": "33", "baixa": "36"}
        if self.problemas:
            linhas.append("")
        for p in self.problemas:
            pos = f"{p.linha}:{p.coluna}"
            linhas.append(
                f"  {pos:<7} {c(cores[p.gravidade], f'{p.gravidade:<5}')}  {p.regra:<15} {p.mensagem}"
            )
            if p.sugestao:
                linhas.append(f"  {'':<7} {'':<5}  {'':<15} → {p.sugestao}")
        n = self.contagem()
        linhas.append("")
        linhas.append(f"  {n['alta']} alta · {n['media']} média · {n['baixa']} baixa")
        return "\n".join(linhas)


def _br(x: float, casas: int = 1) -> str:
    return f"{x:.{casas}f}".replace(".", ",")


def _resumo(s: str, n: int = 60) -> str:
    s = " ".join(s.split())
    return s if len(s) <= n else s[: n - 1].rstrip() + "…"


def analisar(texto: str, config: Config | None = None, **opcoes: Any) -> Analise:
    """Analisa a legibilidade de um texto (Markdown ou texto puro) em português.

    >>> a = analisar("O gato subiu no telhado. Depois desceu.")
    >>> a.nivel
    'muito fácil'
    """
    cfg = config or Config(**opcoes)
    limpo = limpar_markdown(texto)
    paragrafos = segmentar(limpo, texto)
    quebras = [m.start() for m in re.finditer("\n", texto)]

    def posicao(offset: int) -> tuple[int, int]:
        import bisect

        i = bisect.bisect_left(quebras, offset)
        inicio_linha = quebras[i - 1] + 1 if i else 0
        return i + 1, offset - inicio_linha + 1

    problemas: list[Problema] = []

    def add(regra: str, grav: str, msg: str, ini: int, trecho: str, sug: str | None = None) -> None:
        if regra in cfg.ignorar:
            return
        linha, coluna = posicao(ini)
        problemas.append(Problema(regra, grav, msg, _resumo(trecho), linha, coluna, sug))

    # ----------------------------------------------------------- estatísticas
    frases_prosa: list[Frase] = [f for p in paragrafos for f in p.frases if not f.titulo]
    n_palavras = n_silabas = n_longas = 0
    for f in frases_prosa:
        ps = palavras(f.texto)
        sil = [contar_silabas(w.group()) for w in ps]
        n_palavras += len(ps)
        n_silabas += sum(sil)
        n_longas += sum(s >= 4 for s in sil)
        if len(ps) > cfg.max_palavras_frase:
            grav = "alta" if len(ps) > cfg.max_palavras_frase * 1.6 else "media"
            add(
                "FRASE_LONGA",
                grav,
                f'Frase com {len(ps)} palavras (máx. {cfg.max_palavras_frase}): "{_resumo(f.texto, 50)}"',
                f.inicio,
                f.texto,
                "Divida em frases menores: uma ideia por frase.",
            )
    n_frases = len(frases_prosa)
    ppf = n_palavras / n_frases if n_frases else 0.0
    spp = n_silabas / n_palavras if n_palavras else 0.0
    indice = flesch(ppf, spp) if n_palavras else 100.0

    for p in paragrafos:
        total = sum(len(palavras(f.texto)) for f in p.frases if not f.titulo)
        if total > cfg.max_palavras_paragrafo:
            add(
                "PARAGRAFO_LONGO",
                "baixa",
                f"Parágrafo com {total} palavras (máx. {cfg.max_palavras_paragrafo})",
                p.inicio,
                p.frases[0].texto,
                "Quebre o parágrafo ou transforme partes em lista.",
            )

    # -------------------------------------------------------------- vocabulário
    jargoes = _JARGOES_RE + _compilar(cfg.jargoes_extras)
    for regex, sugestao in jargoes:
        for m in regex.finditer(limpo):
            add("JARGAO", "media", f'"{m.group()}"', m.start(), m.group(), sugestao)
    for regex, sugestao in _ESTRANGEIRISMOS_RE:
        for m in regex.finditer(limpo):
            add("ESTRANGEIRISMO", "baixa", f'"{m.group()}"', m.start(), m.group(), sugestao)

    for m in _PASSIVA.finditer(limpo):
        if eh_participio(m.group(1)):
            add(
                "VOZ_PASSIVA",
                "baixa",
                f'Voz passiva: "{_resumo(m.group(), 40)}"',
                m.start(),
                m.group(),
                "Prefira a voz ativa: diga quem faz a ação.",
            )

    for m in _VERBO_VAZIO.finditer(limpo):
        nome = m.group(2).lower()
        verbo = VERBOS_DE_SUBSTANTIVOS.get(nome)
        if verbo or _SUFIXO_NOMINAL.search(nome):
            add(
                "NOMINALIZACAO",
                "baixa",
                f'"{_resumo(m.group(), 40)}"',
                m.start(),
                m.group(),
                f'Use o verbo: "{verbo}".' if verbo else "Use o verbo correspondente ao substantivo.",
            )

    # ------------------------------------------------------------------ siglas
    linhas_caixa_alta: set[int] = set()
    for m in re.finditer(r"[^\n]+", limpo):
        letras = [ch for ch in m.group() if ch.isalpha()]
        if (
            len(palavras(m.group())) >= 4
            and letras
            and sum(ch.isupper() for ch in letras) / len(letras) > 0.8
        ):
            linhas_caixa_alta.add(posicao(m.start())[0])
            add(
                "CAIXA_ALTA",
                "baixa",
                "Linha inteira em CAIXA ALTA",
                m.start(),
                m.group(),
                "Use maiúsculas e minúsculas; para destacar, use negrito.",
            )

    vistas: set[str] = set()
    for m in _SIGLA.finditer(limpo):
        sigla = m.group()
        base = sigla[:-1] if sigla.endswith("s") and sigla[:-1].isupper() else sigla
        if (
            base in vistas
            or base in cfg.siglas_conhecidas
            or _ROMANO.fullmatch(base)
            or posicao(m.start())[0] in linhas_caixa_alta
        ):
            continue
        vistas.add(base)
        b = re.escape(base)
        definida = (
            re.search(rf"\(\s*{b}s?\s*\)", texto)
            or re.search(rf"\b{b}s?\s*\((?=[^)]*[a-zà-ÿ])", texto)
            or re.search(rf"\b{b}s?\s*[–—-]\s+[A-ZÀ-Ý][a-zà-ÿ]", texto)
        )
        if not definida:
            add(
                "SIGLA",
                "media",
                f'Sigla "{base}" sem explicação',
                m.start(),
                sigla,
                f"Na primeira vez, escreva por extenso: Nome Completo ({base}).",
            )

    problemas.sort(key=lambda p: (p.linha, p.coluna, _PESO[p.gravidade]))
    estat = Estatisticas(
        paragrafos=len(paragrafos),
        frases=n_frases,
        palavras=n_palavras,
        silabas=n_silabas,
        palavras_longas=n_longas,
        palavras_por_frase=round(ppf, 2),
        silabas_por_palavra=round(spp, 3),
        flesch=round(indice, 1),
    )
    return Analise(estat, problemas)
