"""Linha de comando: ``legivel arquivo.md``."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .analise import REGRAS, Config, analisar


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        prog="legivel",
        description="Verifica legibilidade e Linguagem Simples em textos em português.",
    )
    p.add_argument("arquivos", nargs="*", help="arquivos .md/.txt (padrão: stdin)")
    p.add_argument("--json", action="store_true", help="saída em JSON")
    p.add_argument("--min-flesch", type=float, help="falha se o índice de Flesch ficar abaixo deste valor")
    p.add_argument(
        "--falhar-em",
        choices=("alta", "media", "baixa", "nunca"),
        default="nunca",
        help="falha (código 1) se houver problema desta gravidade ou mais grave",
    )
    p.add_argument("--max-palavras-frase", type=int, default=25)
    p.add_argument("--max-palavras-paragrafo", type=int, default=120)
    p.add_argument(
        "--ignorar", default="", help=f"regras a ignorar, separadas por vírgula ({', '.join(REGRAS)})"
    )
    p.add_argument("--sem-cor", action="store_true", help="desliga as cores do terminal")
    p.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    a = p.parse_args(argv)

    cfg = Config(
        max_palavras_frase=a.max_palavras_frase,
        max_palavras_paragrafo=a.max_palavras_paragrafo,
        ignorar={r.strip().upper() for r in a.ignorar.split(",") if r.strip()},
    )
    entradas = [(f, Path(f).read_text(encoding="utf-8")) for f in a.arquivos] or [("stdin", sys.stdin.read())]
    cor = not a.sem_cor and not a.json and sys.stdout.isatty()

    falhou = False
    resultados = {}
    for nome, texto in entradas:
        analise = analisar(texto, cfg)
        if not analise.aprovado(a.min_flesch, a.falhar_em):
            falhou = True
        if a.json:
            resultados[nome] = analise.to_dict()
        else:
            print(analise.relatorio(nome, cor=cor))
            print()
    if a.json:
        print(json.dumps(resultados, ensure_ascii=False, indent=2))
    return 1 if falhou else 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
