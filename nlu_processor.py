# NLU básico para pt-BR: normalização, mapeamentos, extração de sintomas e red-flags,
# resumo de queixas e saída estruturada para o MotorInferencia.

import json
import re
from collections import defaultdict


class NLUProcessor:
    def __init__(self, caminho_base: str = "base_conhecimento.json"):
        """
        Carrega mappings e red_flags da base se existir.
        """
        self.mappings = {}  # termo (lower) -> sintoma_normalizado
        self.red_flags_lex = {}  # termo -> red_flag_normalizado
        self.red_flags_set = set()  # conjunto de red flags para busca rápida
        try:
            with open(caminho_base, "r", encoding="utf-8") as f:
                dados = json.load(f)

            # carregar mappings
            raw_maps = dados.get("mappings", {})
            self.mappings = {k.lower(): v.lower() for k, v in raw_maps.items()}

            # carregar red_flags
            rf_dict = dados.get("red_flags", {})
            self.red_flags_set = set(rf_dict.keys())

            # criar mapeamento para busca de red flags
            for termo in self.red_flags_set:
                self.red_flags_lex[termo] = termo

        except FileNotFoundError:
            print(f"Aviso: Arquivo {caminho_base} não encontrado. Usando base vazia.")
            self.mappings = {}
            self.red_flags_lex = {}
            self.red_flags_set = set()

    def normalizar_texto(self, texto: str) -> str:
        t = texto.lower()
        # mantém acentos; remove pontuação que não seja útil
        t = re.sub(r"[^\w\sáéíóúâêôãõç-]", " ", t)
        t = re.sub(r"\s+", " ", t).strip()
        return t

    def extrair_sintomas(self, texto_normalizado: str) -> dict:
        """
        Retorna dicionário sintoma -> contagem/peso bruto.
        """
        encontrados = defaultdict(float)

        # verifica mapeamentos (termos curtos e compostos)
        for termo, sint in self.mappings.items():
            # busca por palavra inteira para evitar falsos positivos
            padrao = r'\b' + re.escape(termo) + r'\b'
            if re.search(padrao, texto_normalizado):
                encontrados[sint] += 1.0

        return dict(encontrados)

    def extrair_red_flags(self, texto_normalizado: str) -> list:
        encontrados = []
        for termo, flag in self.red_flags_lex.items():
            # busca por palavra inteira
            padrao = r'\b' + re.escape(termo) + r'\b'
            if re.search(padrao, texto_normalizado):
                encontrados.append(flag)
        return list(set(encontrados))

    def gerar_resumo(self, texto_original: str, sintomas: dict) -> str:
        """
        Tenta extrair frases relevantes contendo termos dos sintomas.
        """
        frases = re.split(r"[.!?]\s*", texto_original.strip())
        frases = [f.strip() for f in frases if f and len(f.strip()) > 3]
        resumo = []

        # cada sintoma: procurar palavras que o representem na frase
        termos_sintomas = list(self.mappings.keys())
        for t in termos_sintomas:
            for fr in frases:
                if t in fr.lower() and fr not in resumo:
                    resumo.append(fr)
                    if len(resumo) >= 2:  # limite de 2 frases no resumo
                        return " ".join(resumo)
                    break

        if not resumo and frases:
            resumo = frases[:1]

        return " ".join(resumo) if resumo else texto_original[:100] + "..."

    def processar_texto(self, texto_usuario: str) -> dict:
        """
        Pipeline NLU completo.
        """
        if not texto_usuario or not texto_usuario.strip():
            return {
                "texto_original": "",
                "texto_normalizado": "",
                "sintomas": {},
                "red_flags": [],
                "resumo": "",
                "pontuacao_total": 0.0
            }

        tn = self.normalizar_texto(texto_usuario)
        sintomas = self.extrair_sintomas(tn)
        red_flags = self.extrair_red_flags(tn)
        resumo = self.gerar_resumo(texto_usuario, sintomas)
        pontuacao_total = sum(sintomas.values()) if sintomas else 0.0

        return {
            "texto_original": texto_usuario,
            "texto_normalizado": tn,
            "sintomas": sintomas,
            "red_flags": red_flags,
            "resumo": resumo,
            "pontuacao_total": pontuacao_total
        }

