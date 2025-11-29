# Motor de Inferência

import json
from pathlib import Path
from typing import Set, Dict, List


class BaseConhecimento:
    def __init__(self, caminho_json: str = "base_conhecimento.json"):
        p = Path(caminho_json)
        if p.exists():
            with p.open("r", encoding="utf-8") as f:
                dados = json.load(f)
        else:
            dados = self._fallback_base()

        # carregar elementos
        self.config = dados.get("config", {})

        # red_flags: é um dicionário no JSON
        rf_dict = dados.get("red_flags", {})
        self.red_flags = rf_dict

        # mappings
        self.mappings = {k.lower(): v.lower() for k, v in dados.get("mappings", {}).items()}

        # condicoes: nome -> {descricao, sintomas: {sintoma: peso}}
        conds = {}
        for nome, bloco in dados.get("condicoes", {}).items():
            sintomas = {s.lower(): float(p) for s, p in bloco.get("sintomas", {}).items()}
            conds[nome.lower()] = {
                "descricao": bloco.get("descricao", ""),
                "sintomas": sintomas
            }
        self.condicoes = conds

    def _fallback_base(self):
        return {
            "config": {
                "thresholds": {
                    "alto_risco": 0.75,
                    "medio_risco": 0.40,
                    "baixo_risco": 0.10
                }
            },
            "red_flags": {
                "ideacao_suicida": 1.0,
                "automutilacao": 1.0
            },
            "mappings": {
                "triste": "tristeza_persistente",
                "nao durmo": "insônia"
            },
            "condicoes": {
                "depressao": {
                    "descricao": "Humor deprimido, perda de prazer e energia",
                    "sintomas": {
                        "tristeza_persistente": 1.0,
                        "fadiga": 0.9,
                        "insônia": 0.8
                    }
                }
            }
        }

    def listar_condicoes(self) -> List[str]:
        return list(self.condicoes.keys())


class MotorInferencia:
    def __init__(self, caminho_base: str = "base_conhecimento.json"):
        self.base = BaseConhecimento(caminho_base)
        cfg = self.base.config.get("thresholds", {})
        self.threshold_alto = cfg.get("alto_risco", 0.75)
        self.threshold_medio = cfg.get("medio_risco", 0.40)
        self.threshold_baixo = cfg.get("baixo_risco", 0.10)

    def inferir(self, fatos: Set[str]) -> Dict:
        """
        Inferência principal com sistema de risco funcional.
        """
        resultados = []
        risco_global = 0.0

        if not isinstance(fatos, (set, list, tuple)):
            fatos = set()

        fatos_set = set([f.lower() for f in fatos])

        # Se não há fatos, retorna vazio
        if not fatos_set:
            return {
                "resultados": [],
                "nivel_risco": "Mínimo",
                "relatorio_queixas": "Nenhum sintoma específico detectado.",
                "recomendacoes": ["Monitorar possíveis sintomas e buscar avaliação se necessário."],
                "risco_global": 0.0
            }

        for nome, bloco in self.base.condicoes.items():
            sintomas_base = bloco["sintomas"]
            sintomas_presentes = sintomas_base.keys() & fatos_set

            if not sintomas_presentes:
                continue

            # Cálculo do score baseado na correspondência de sintomas
            soma_pesos_presentes = sum(sintomas_base[s] for s in sintomas_presentes)
            soma_pesos_totais = sum(sintomas_base.values())
            grau = soma_pesos_presentes / soma_pesos_totais if soma_pesos_totais > 0 else 0.0

            # Adicionar peso das red flags encontradas
            bonus_red_flags = 0.0
            red_encontradas = []

            for rf, peso_rf in self.base.red_flags.items():
                if rf in fatos_set:
                    red_encontradas.append(rf)
                    bonus_red_flags += peso_rf * 0.3  # bonus de 30% do peso da red flag

            score = min(grau + bonus_red_flags, 1.0)  # não ultrapassar 1.0

            justificativa = self._construir_justificativa(
                nome, sintomas_presentes, sintomas_base, grau, red_encontradas
            )

            resultados.append({
                "condicao": nome,
                "descricao": bloco.get("descricao", ""),
                "sintomas_que_casaram": sorted(list(sintomas_presentes)),
                "grau": grau,
                "score": score,
                "red_flags": sorted(red_encontradas),
                "justificativa": justificativa
            })

            # Atualizar risco global (maior score entre todas as condições)
            risco_global = max(risco_global, score)

        # Ordenar por score
        resultados.sort(key=lambda x: x["score"], reverse=True)

        # Determinar nível de risco
        nivel_risco = self._calcular_nivel_risco(risco_global, resultados, fatos_set)

        relatorio = self._gerar_relatorio_queixas(fatos_set)
        recomendacoes = self._gerar_recomendacoes(nivel_risco, resultados, fatos_set)

        return {
            "resultados": resultados,
            "nivel_risco": nivel_risco,
            "relatorio_queixas": relatorio,
            "recomendacoes": recomendacoes,
            "risco_global": risco_global
        }

    def _calcular_nivel_risco(self, risco_global: float, resultados: List[Dict], fatos_set: set) -> str:
        """Calcula o nível de risco considerando red flags e scores"""

        # Verificar se há red flags críticas diretamente nos fatos
        red_flags_criticas = {"ideacao_suicida", "automutilacao", "planos_suicidas"}
        tem_red_flag_critica = any(rf in fatos_set for rf in red_flags_criticas)

        # Verificar termos de emergência diretos
        termos_emergencia = {
            "vou me matar", "me enforcar", "overdose", "pular do", "atirar em mim",
            "carta de despedida", "tudo planejado", "amanhã", "agora"
        }

        # Verificar nos resultados também
        for res in resultados:
            if any(rf in red_flags_criticas for rf in res["red_flags"]):
                tem_red_flag_critica = True
                break

        if tem_red_flag_critica:
            return "Alto"
        elif risco_global >= self.threshold_alto:
            return "Alto"
        elif risco_global >= self.threshold_medio:
            return "Médio"
        elif risco_global >= self.threshold_baixo:
            return "Baixo"
        else:
            return "Mínimo"

    def _construir_justificativa(self, condicao_nome: str, sintomas_presentes: set,
                                 sintomas_base: dict, grau: float, red_encontradas: set) -> str:
        partes = []
        partes.append(f"Condição considerada: {condicao_nome.capitalize()}.")

        if sintomas_presentes:
            lista = ", ".join(s.replace("_", " ") for s in sorted(sintomas_presentes))
            partes.append(f"Sinais compatíveis: {lista}.")
            partes.append(f"Grau de correspondência: {grau * 100:.1f}%.")

        if red_encontradas:
            rf = ", ".join(r.replace("_", " ") for r in sorted(red_encontradas))
            partes.append(f"RED-FLAGS identificadas: {rf}.")

        return " ".join(partes)

    def _gerar_relatorio_queixas(self, fatos_set: set) -> str:
        if not fatos_set:
            return "Nenhuma queixa específica detectada."

        # Separar sintomas normais de red flags
        sintomas_normais = [f for f in fatos_set if f not in self.base.red_flags]
        red_flags = [f for f in fatos_set if f in self.base.red_flags]

        relatorio = ""
        if sintomas_normais:
            partes = [f.replace("_", " ") for f in sorted(sintomas_normais)[:6]]
            relatorio = "Queixas principais: " + ", ".join(partes) + "."

        if red_flags:
            rf_texto = ", ".join(rf.replace("_", " ") for rf in sorted(red_flags))
            if relatorio:
                relatorio += f" 🚨 ATENÇÃO: {rf_texto}."
            else:
                relatorio = f"🚨 ATENÇÃO: {rf_texto}."

        return relatorio

    def _gerar_recomendacoes(self, nivel_risco: str, resultados: List[Dict], fatos_set: set) -> List[str]:
        recs = []

        if nivel_risco == "Alto":
            recs.append("🚨 AVALIAÇÃO IMEDIATA - Busque atendimento de emergência")
            recs.append("📞 Contate CVV (188) ou serviço de saúde mental urgentemente")
            recs.append("👥 Não deixe a pessoa sozinha até receber atendimento")
            recs.append("🏥 Procure um hospital ou serviço de emergência psiquiátrica")
        elif nivel_risco == "Médio":
            recs.append("📞 Agendar consulta com psiquiatra/psicólogo esta semana")
            recs.append("📊 Monitorar sintomas diariamente")
            recs.append("👥 Buscar apoio familiar ou de amigos")
            recs.append("💊 Avaliar necessidade de intervenção farmacológica")
        elif nivel_risco == "Baixo":
            recs.append("👥 Agendar avaliação com profissional de saúde")
            recs.append("💪 Praticar autocuidado e monitorar evolução")
            recs.append("📝 Manter diário de sintomas")
            recs.append("🧘 Considerar psicoterapia como prevenção")
        else:
            recs.append("💡 Manter hábitos saudáveis e observar possíveis mudanças")
            recs.append("🏃 Praticar atividade física regular")
            recs.append("🍎 Manter alimentação balanceada")
            recs.append("😴 Cuidar da qualidade do sono")

        # Recomendações específicas por condição
        if resultados:
            top_condicao = resultados[0]["condicao"]
            if top_condicao == "depressao":
                recs.append("Específico para depressão: Atividade física regular e psicoterapia")
            elif top_condicao in ["ansiedade", "transtorno_panico", "crise_ansiedade"]:
                recs.append("Específico para ansiedade: Técnicas de respiração e mindfulness")
            elif top_condicao == "crise_suicida":
                recs.append("INTERVENÇÃO IMEDIATA: Risco suicida ativo detectado")

        # Se há red flags mas nenhuma condição foi detectada
        red_flags_presentes = [rf for rf in self.base.red_flags if rf in fatos_set]
        if red_flags_presentes and not resultados:
            recs.append("⚠️ Sintomas de alerta detectados - Busque avaliação profissional")

        recs.append("Lembre-se: Este é um sistema de triagem, não substitui diagnóstico profissional")

        return recs
