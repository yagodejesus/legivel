import pytest

from legivel import Config, analisar, flesch, nivel_flesch

BUROCRATES = (
    "Vimos, por meio desta, informar que, em que pese o requerimento protocolado pelo interessado, "
    "mister se faz salientar que o pagamento supracitado não foi efetuado tempestivamente, razão pela "
    "qual o pedido foi indeferido, consoante o disposto na legislação vigente, sob pena de cancelamento "
    "do cadastro junto ao INSS."
)
SIMPLES = "Recebemos seu pedido. Mas você não pagou a taxa no prazo. Por isso, negamos o pedido."


def regras(analise):
    return {p.regra for p in analise.problemas}


def test_formula_de_flesch():
    assert flesch(20, 2.0) == pytest.approx(248.835 - 20.3 - 169.2)
    assert flesch(100, 5) == 0.0
    assert flesch(1, 0.1) == 100.0
    assert nivel_flesch(80)[0] == "muito fácil"
    assert nivel_flesch(10)[0] == "muito difícil"


def test_texto_simples_e_facil_e_sem_problemas():
    a = analisar(SIMPLES)
    assert a.flesch > 75
    assert a.problemas == []
    assert a.estatisticas.frases == 3
    assert a.aprovado(min_flesch=60, falhar_em="baixa")


def test_burocratês_e_difícil_e_cheio_de_problemas():
    a = analisar(BUROCRATES)
    assert a.flesch < 25
    assert {"FRASE_LONGA", "JARGAO", "VOZ_PASSIVA", "SIGLA"} <= regras(a)
    assert not a.aprovado(falhar_em="media")
    assert not a.aprovado(min_flesch=50, falhar_em="nunca")


def test_sigla_definida_nao_e_problema():
    assert "SIGLA" not in regras(analisar("O Sistema Único de Saúde (SUS) e a Receita Federal (RFB). A RFB."))
    assert "SIGLA" not in regras(analisar("A ANPD (Autoridade Nacional de Proteção de Dados) fiscaliza."))
    assert "SIGLA" in regras(analisar("Procure a ANPD."))


def test_sigla_reportada_uma_vez_e_ignora_romanos():
    a = analisar("A ANPD multou. A ANPD voltou. Capítulo IV do livro.")
    assert [p.regra for p in a.problemas].count("SIGLA") == 1


def test_nominalizacao_com_sugestao():
    a = analisar("Vamos realizar a análise dos dados.")
    [p] = [p for p in a.problemas if p.regra == "NOMINALIZACAO"]
    assert "analisar" in p.sugestao


def test_passiva_ignora_adjetivos_acentuados():
    assert "VOZ_PASSIVA" not in regras(analisar("O documento é válido. O processo é rápido."))
    assert "VOZ_PASSIVA" in regras(analisar("O documento foi assinado ontem."))
    assert "VOZ_PASSIVA" in regras(analisar("O item foi incluído na lista."))


def test_markdown_e_posicoes():
    md = "# Título\n\nTexto com [link](https://x.com) e `código`.\n\nOutrossim, seguimos."
    a = analisar(md)
    [p] = [p for p in a.problemas if p.regra == "JARGAO"]
    assert (p.linha, p.coluna) == (5, 1)
    assert a.estatisticas.frases == 2  # título não conta


def test_abreviacoes_nao_quebram_frases():
    a = analisar("O Sr. Silva e a Dra. Ana chegaram. Trouxeram 1.500,00 reais, etc. e saíram.")
    assert a.estatisticas.frases == 2


def test_lista_vira_frases_separadas():
    a = analisar("Leve:\n- documento com foto\n- comprovante de endereço\n- CPF")
    assert a.estatisticas.frases == 4


def test_config_ignorar_e_limites():
    a = analisar(BUROCRATES, Config(ignorar={"JARGAO", "SIGLA"}, max_palavras_frase=100))
    assert not {"JARGAO", "SIGLA", "FRASE_LONGA"} & regras(a)


def test_jargoes_extras():
    a = analisar(
        "Favor providenciar o documento.", jargoes_extras={r"favor providenciar": "por favor, envie"}
    )
    assert "JARGAO" in regras(a)


def test_caixa_alta():
    a = analisar("ATENÇÃO SENHOR CONTRIBUINTE LEIA COM CUIDADO\n\nTexto normal aqui.")
    assert "CAIXA_ALTA" in regras(a)
    assert "SIGLA" not in regras(a)


def test_texto_vazio():
    a = analisar("")
    assert a.estatisticas.palavras == 0 and a.problemas == []


def test_to_dict_e_relatorio():
    a = analisar(BUROCRATES)
    d = a.to_dict()
    assert d["nivel"] == "muito difícil" and d["problemas"]
    assert "Índice de Flesch" in a.relatorio("carta.txt")
