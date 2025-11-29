"""
Loader da base de conhecimento.
"""
import json
from pathlib import Path

class BaseConhecimento:
    def __init__(self, caminho_json: str = "base_conhecimento.json"):
        caminho = Path(caminho_json)
        if not caminho.exists():
            raise FileNotFoundError(f"Base de conhecimento não encontrada: {caminho}")
        with caminho.open("r", encoding="utf-8") as f:
            dados = json.load(f)

        self.config = dados.get("config", {})
        self.red_flags = set(dados.get("red_flags", []))
        self.mappings = {k.lower(): v.lower() for k, v in dados.get("mappings", {}).items()}

        # condicoes: dict -> cada sintoma normalizado
        conds = {}
        for nome, bloco in dados.get("condicoes", {}).items():
            sintomas = {s.lower(): float(p) for s, p in bloco.get("sintomas", {}).items()}
            conds[nome.lower()] = {
                "descricao": bloco.get("descricao", ""),
                "sintomas": sintomas
            }
        self.condicoes = conds

    def listar_condicoes(self):
        return list(self.condicoes.keys())

    def obter_condicao(self, nome):
        return self.condicoes.get(nome.lower())