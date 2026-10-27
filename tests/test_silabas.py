import pytest

from legivel import contar_silabas

CASOS = {
    "casa": 2,
    "ação": 2,
    "corações": 3,
    "mãe": 1,
    "saúde": 3,
    "país": 2,
    "pais": 1,
    "muito": 2,
    "Paraguai": 3,
    "joelho": 3,
    "leão": 2,
    "poesia": 4,
    "notícia": 3,
    "dia": 2,
    "Maria": 3,
    "família": 3,
    "quando": 2,
    "linguagem": 3,
    "você": 2,
    "também": 2,
    "ou": 1,
    "rua": 2,
    "boa": 2,
    "voo": 2,
    "série": 2,
    "história": 3,
    "água": 2,
    "frequência": 3,
    "piano": 3,
    "ciência": 3,
    "aguentar": 3,
    "administração": 5,
    "responsabilidade": 7,
    "que": 1,
    "guerra": 2,
    "saída": 3,
    "ruído": 3,
    "cidadão": 3,
    "linguística": 4,
    "e": 1,
}


@pytest.mark.parametrize("palavra,esperado", CASOS.items())
def test_silabas(palavra, esperado):
    assert contar_silabas(palavra) == esperado


def test_numeros_e_vazios():
    assert contar_silabas("2026") == 4
    assert contar_silabas("—") == 0
