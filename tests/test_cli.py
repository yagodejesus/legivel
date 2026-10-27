import json

from legivel.cli import main


def test_cli_relatorio_e_codigo_de_saida(tmp_path, capsys):
    f = tmp_path / "carta.md"
    f.write_text("Outrossim, informamos que o prazo acabou.", encoding="utf-8")
    assert main([str(f)]) == 0
    assert "JARGAO" in capsys.readouterr().out
    assert main([str(f), "--falhar-em", "media"]) == 1
    assert main([str(f), "--falhar-em", "media", "--ignorar", "JARGAO"]) == 0


def test_cli_min_flesch(tmp_path):
    f = tmp_path / "a.txt"
    f.write_text("O gato subiu no muro. Depois desceu.", encoding="utf-8")
    assert main([str(f), "--min-flesch", "60"]) == 0
    assert main([str(f), "--min-flesch", "101"]) == 1


def test_cli_json(tmp_path, capsys):
    f = tmp_path / "a.txt"
    f.write_text("Procure a ANPD.", encoding="utf-8")
    main([str(f), "--json"])
    dados = json.loads(capsys.readouterr().out)
    assert dados[str(f)]["problemas"][0]["regra"] == "SIGLA"
