# legível 📖

[![CI](https://github.com/yagodejesus/legivel/actions/workflows/ci.yml/badge.svg)](https://github.com/yagodejesus/legivel/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/legivel.svg)](https://pypi.org/project/legivel/)
[![Python](https://img.shields.io/pypi/pyversions/legivel.svg)](https://pypi.org/project/legivel/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

**Um "linter" de Linguagem Simples para textos em português.** Mede a legibilidade (índice de Flesch adaptado ao português) e aponta, linha a linha, o que torna o texto difícil: frases longas, juridiquês, siglas sem explicação, voz passiva e muito mais — com sugestões de como reescrever.

> 🇺🇸 *A plain-language linter for Brazilian Portuguese: readability score (Flesch adapted to Portuguese), long sentences, legal jargon, undefined acronyms, passive voice — with rewrite suggestions. Works as a library, a CLI and a GitHub Action. Zero dependencies.*

Comunicados públicos, contratos, bulas, termos de uso e mensagens de saúde precisam ser entendidos por todo mundo. O `legivel` transforma as recomendações de Linguagem Simples em verificações automáticas — dá para rodar no editor, num notebook ou no CI, como um ESLint para textos.

```text
$ legivel exemplos/antes.md

exemplos/antes.md — Índice de Flesch: 14,1 (muito difícil · textos acadêmicos e especializados)
  2 frases · 64 palavras · 32,0 palavras/frase · 2,39 sílabas/palavra

  3:1     alta   FRASE_LONGA     Frase com 48 palavras (máx. 25): "Vimos, por meio desta, informar que, em que pese…"
                                 → Divida em frases menores: uma ideia por frase.
  3:38    media  JARGAO          "em que pese"
                                 → embora / apesar de
  3:95    media  JARGAO          "mister se faz"
                                 → é preciso
  3:151   baixa  VOZ_PASSIVA     Voz passiva: "foi efetuado"
                                 → Prefira a voz ativa: diga quem faz a ação.
  3:312   media  SIGLA           Sigla "INSS" sem explicação
                                 → Na primeira vez, escreva por extenso: Nome Completo (INSS).
  5:39    baixa  NOMINALIZACAO   "realizar a atualização"
                                 → Use o verbo: "atualizar".
  ...
```

Depois da reescrita ([`exemplos/depois.md`](exemplos/depois.md)), o índice sobe de **14 para 73**.

## Instalação

```bash
pip install legivel
```

## Uso

### Python

```python
from legivel import analisar

a = analisar(open("comunicado.md", encoding="utf-8").read())

a.flesch  # 41.3
a.nivel  # 'difícil'
a.estatisticas  # frases, palavras, sílabas, palavras por frase...
for p in a.problemas:
    print(p.linha, p.regra, p.trecho, "→", p.sugestao)

a.aprovado(min_flesch=50, falhar_em="media")  # útil em testes automatizados
```

### Linha de comando

```bash
legivel docs/*.md                          # relatório colorido
legivel carta.txt --json                   # saída para outras ferramentas
legivel docs/*.md --min-flesch 50 --falhar-em media   # código 1 se reprovar
legivel texto.md --ignorar VOZ_PASSIVA,ESTRANGEIRISMO --max-palavras-frase 20
cat texto.txt | legivel
```

### GitHub Action

Garanta que a documentação do seu projeto continue simples a cada pull request:

```yaml
- uses: actions/checkout@v4
- uses: yagodejesus/legivel@v0.1.0
  with:
    arquivos: "docs/**/*.md"
    min-flesch: "50"
    falhar-em: "alta"
```

## O que é verificado

| Regra | Gravidade | Exemplo | Sugestão |
|---|---|---|---|
| `FRASE_LONGA` | média/alta | frases com mais de 25 palavras (alta acima de 40) | uma ideia por frase |
| `PARAGRAFO_LONGO` | baixa | parágrafos com mais de 120 palavras | quebre ou use lista |
| `JARGAO` | média | *outrossim, destarte, mister se faz, supracitado, em que pese* (60+ expressões) | alternativa simples |
| `SIGLA` | média | "INSS" sem "Instituto Nacional do Seguro Social (INSS)" | escreva por extenso na 1ª vez |
| `VOZ_PASSIVA` | baixa | "o pedido foi indeferido" | diga quem faz a ação |
| `NOMINALIZACAO` | baixa | "realizar a análise" | "analisar" |
| `ESTRANGEIRISMO` | baixa | *deadline, feedback, budget* | prazo, retorno, orçamento |
| `CAIXA_ALTA` | baixa | linhas inteiras em maiúsculas | use negrito para destacar |

Markdown é entendido: blocos de código, links, imagens e tabelas não atrapalham, títulos não contam na média e a linha/coluna de cada problema aponta para o arquivo original.

## O índice de Flesch em português

Usamos a adaptação de **Martins, Ghiraldelo, Nunes e Oliveira Jr. (1996)**, a mesma usada em ferramentas acadêmicas como o Coh-Metrix-Port:

```
Índice = 248,835 − 1,015 × (palavras por frase) − 84,6 × (sílabas por palavra)
```

| Índice | Nível | Escolaridade aproximada |
|---|---|---|
| 75–100 | muito fácil | 1º ao 5º ano |
| 50–75 | fácil | 6º ao 9º ano |
| 25–50 | difícil | ensino médio e superior |
| 0–25 | muito difícil | textos acadêmicos e especializados |

As sílabas são contadas por uma heurística própria para o português (hiatos, ditongos nasais, `qu`/`gu`, ditongos crescentes átonos como em *his-tó-ria*), testada contra dezenas de palavras.

## Personalização

```python
from legivel import Config, analisar

cfg = Config(
    max_palavras_frase=20,
    ignorar={"ESTRANGEIRISMO"},
    jargoes_extras={r"favor providenciar": "por favor, envie"},
)
cfg.siglas_conhecidas |= {"UFPA", "CNPq"}  # siglas que seu público já conhece
analisar(texto, cfg)
```

## Limitações

- Fórmulas de legibilidade medem a *forma* do texto, não se ele faz sentido. Use o índice como termômetro, e não como meta absoluta.
- A detecção de voz passiva e de nominalizações é heurística e pode gerar alguns falsos positivos — por isso essas regras têm gravidade baixa.
- O dicionário de jargões é um começo. Pull requests com novas expressões (e boas alternativas) são muito bem-vindos!

## Desenvolvimento

```bash
git clone https://github.com/yagodejesus/legivel && cd legivel
pip install -e ".[dev]"
pytest && ruff check .
```

## Licença

MIT © Yago de Jesus Martins
