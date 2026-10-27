"""Regras de Linguagem Simples para português brasileiro."""

from __future__ import annotations

import re

__all__ = ["JARGOES", "ESTRANGEIRISMOS", "VERBOS_DE_SUBSTANTIVOS", "SIGLAS_CONHECIDAS", "eh_participio"]

# padrão regex → sugestão. Todos são aplicados sem diferenciar maiúsculas.
JARGOES: dict[str, str] = {
    r"outrossim": "além disso / também",
    r"destarte|dessarte": "assim / dessa forma",
    r"mister se faz|faz-se mister": "é preciso",
    r"faz-se necessári[oa]": "é preciso",
    r"haja vista": "porque / considerando que",
    r"no tocante (?:a|ao|à|aos|às)": "sobre",
    r"no que (?:tange|concerne|diz respeito) (?:a|ao|à|aos|às)": "sobre",
    r"à guisa de": "como",
    r"supra(?:citad|mencionad)[oa]s?": "citado acima / esse",
    r"retro(?:citad|mencionad)[oa]s?": "citado antes / esse",
    r"aludid[oa]s?": "mencionado / esse",
    r"consoante": "conforme / de acordo com",
    r"porquanto": "porque",
    r"conquanto": "embora",
    r"data venia": "com todo o respeito",
    r"exordial": "petição inicial",
    r"vem,? (?:mui )?respeitosamente": "(vá direto ao pedido)",
    r"(?:vimos|venho),? (?:por meio|através) d[aeo]st[ae],?": "(vá direto ao assunto)",
    r"pelo presente(?: instrumento)?": "(pode remover)",
    r"para os devidos fins": "(pode remover)",
    r"solicitamos a gentileza de": "por favor,",
    r"a nível de": "em / sobre",
    r"doravante": "a partir de agora",
    r"hodiernamente": "hoje em dia",
    r"precipuamente": "principalmente",
    r"precípu[oa]s?": "principal",
    r"lídim[oa]s?": "legítimo",
    r"óbices?": "obstáculo / impedimento",
    r"ensej(?:a|am|ar|ou|aram|ará|ando)": "causar / permitir / dar motivo",
    r"elidir": "eliminar / afastar",
    r"adimplir|adimplemento": "pagar / pagamento",
    r"inadimplemento": "falta de pagamento",
    r"deferid[oa]s?": "aprovado / aceito",
    r"indeferid[oa]s?": "negado / recusado",
    r"indeferimento": "recusa / negativa",
    r"cientificad[oa]s?": "avisado / informado",
    r"cientificar": "avisar / informar",
    r"in casu": "neste caso",
    r"ab initio": "desde o início",
    r"em que pese": "embora / apesar de",
    r"sob pena de": "se não fizer isso, … (diga a consequência)",
    r"infra-?assinad[oa]s?": "que assina abaixo",
    r"a contento": "de forma satisfatória / bem",
    r"tempestivamente": "no prazo",
    r"intempestiv[oa]s?": "fora do prazo",
    r"(?:cumpre|insta|impende) (?:salientar|ressaltar|destacar|informar|esclarecer) que": (
        "(vá direto ao ponto)"
    ),
    r"oportunamente": "depois / no momento certo",
    r"(?:face|ante|diante) (?:a|ao|d)?o exposto|isto posto|isso posto": "por isso",
    r"(?:nesse|neste) diapasão": "nesse sentido",
    r"anuência": "concordância / autorização",
    r"exarad[oa]s?": "emitido / escrito",
    r"vossa senhoria": "você / o senhor / a senhora",
    r"mormente": "principalmente",
    r"quiçá": "talvez",
    r"amiúde": "com frequência",
    r"sobremaneira": "muito",
    r"via de regra": "em geral",
    r"ao revés": "ao contrário",
    r"efetu(?:ar|a|am|ou|aram|ará|ado|ada|ados|adas)": "fazer / feito",
    r"informamos que": "(vá direto à informação)",
}

ESTRANGEIRISMOS: dict[str, str] = {
    r"deadlines?": "prazo",
    r"feedbacks?": "retorno / opinião",
    r"budgets?": "orçamento",
    r"meetings?": "reunião",
    r"briefings?": "orientação / resumo",
    r"follow-?ups?": "acompanhamento / retorno",
    r"stakeholders?": "partes interessadas",
    r"insights?": "ideia / percepção",
    r"performance": "desempenho",
    r"know-?how": "conhecimento / experiência",
    r"delivery": "entrega",
    r"workshops?": "oficina",
    r"benchmarks?": "referência / comparação",
    r"report": "relatório",
    r"target": "meta / público-alvo",
}

VERBOS_DE_SUBSTANTIVOS: dict[str, str] = {
    "análise": "analisar",
    "pagamento": "pagar",
    "avaliação": "avaliar",
    "verificação": "verificar",
    "entrega": "entregar",
    "solicitação": "solicitar",
    "inscrição": "inscrever-se",
    "revisão": "revisar",
    "contratação": "contratar",
    "cobrança": "cobrar",
    "emissão": "emitir",
    "utilização": "usar",
    "aquisição": "comprar",
    "compra": "comprar",
    "venda": "vender",
    "consulta": "consultar",
    "busca": "buscar",
    "troca": "trocar",
    "escolha": "escolher",
    "leitura": "ler",
    "alteração": "alterar",
    "atualização": "atualizar",
    "correção": "corrigir",
    "instalação": "instalar",
    "manutenção": "manter / consertar",
    "transferência": "transferir",
    "devolução": "devolver",
    "aplicação": "aplicar",
    "apresentação": "apresentar",
    "comunicação": "comunicar",
    "distribuição": "distribuir",
    "execução": "executar",
    "implementação": "implementar",
    "investigação": "investigar",
    "medição": "medir",
    "notificação": "notificar",
    "organização": "organizar",
    "publicação": "publicar",
    "recuperação": "recuperar",
    "redução": "reduzir",
    "substituição": "substituir",
    "validação": "validar",
    "vistoria": "vistoriar",
    "fiscalização": "fiscalizar",
    "cadastro": "cadastrar",
    "agendamento": "agendar",
    "cancelamento": "cancelar",
    "encaminhamento": "encaminhar",
    "levantamento": "levantar",
    "monitoramento": "monitorar",
    "planejamento": "planejar",
    "processamento": "processar",
    "recebimento": "receber",
    "tratamento": "tratar",
    "limpeza": "limpar",
    "coleta": "coletar",
    "reunião": "reunir-se",
    "análises": "analisar",
    "pesquisa": "pesquisar",
    "visita": "visitar",
}

SIGLAS_CONHECIDAS: frozenset[str] = frozenset(
    "CPF RG CEP CNPJ PIX SUS TV PDF OK ONU EUA DVD USB HIV AIDS COVID UTI ID URL GPS SMS PIB "
    "CD AM PM FM SP RJ MG BA PA".split()
)

_PARTICIPIOS_IRREGULARES = frozenset(
    base + fim
    for base in (
        "feit dit post escrit abert vist aceit pag eleit pres suspens impress cobert descobert "
        "expost propost dispost compost extint gast"
    ).split()
    for fim in ("o", "a", "os", "as")
) | {"entregue", "entregues"}
_NAO_PARTICIPIOS = frozenset(
    "devido devida devidos devidas querido querida comprido comprida atrevido bandido partido "
    "sentido marido nado lado fado fígado".split()
)


def eh_participio(palavra: str) -> bool:
    p = palavra.lower()
    if p in _NAO_PARTICIPIOS:
        return False
    if p in _PARTICIPIOS_IRREGULARES:
        return True
    if len(p) > 4 and re.search(r"(?:ad|id|íd)(?:o|a|os|as)$", p):
        # "válido", "rápido" têm acento e não são particípios; "incluído" é.
        return not re.search(r"[áéíóúâêôãõ]", p) or bool(re.search(r"íd(?:o|a|os|as)$", p))
    return False
