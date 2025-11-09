import json
import re


class AvaliadorEmocional:
    """
    Interpreta descrições de comportamento e estado emocional
    e sugere possíveis condições psicológicas com base em uma base de conhecimento.
    """

    def __init__(self, caminho_base):
        with open(caminho_base, "r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)

        self.base_mental = {cond: {s.lower() for s in sinais} for cond, sinais in dados.items()}

        try:
            import spacy
            self.nlp = spacy.load("pt_core_news_md")
        except:
            try:
                import spacy
                self.nlp = spacy.load("pt_core_news_sm")
            except:
                print("Aviso: spaCy não encontrado. Similaridade desativada.")
                self.nlp = None

    def extrair_sinais(self, texto):
        """Identifica sinais emocionais no texto informado (com dicionário de sinônimos)."""
        texto = texto.lower()
        encontrados = set()

        # Dicionário de sinônimos simples
        sinonimos = {
            "triste": "tristeza persistente",
            "tristeza": "tristeza persistente",
            "cansado": "cansaco mental",
            "cansada": "cansaco mental",
            "nervoso": "irritabilidade",
            "nervosa": "irritabilidade",
            "ansioso": "preocupacao constante",
            "ansiosa": "preocupacao constante",
            "sem energia": "fadiga",
            "sem vontade": "falta de prazer",
            "taquicardico": "taquicardia",
            "taquicardica": "taquicardia",
        }

        todos_sinais = set().union(*self.base_mental.values())

        # Busca literal e substituição de sinônimos
        for palavra, substituto in sinonimos.items():
            if palavra in texto:
                encontrados.add(substituto)

        for sinal in todos_sinais:
            if sinal in texto:
                encontrados.add(sinal)

        # Busca semântica (caso spaCy esteja ativo)
        if self.nlp is not None:
            doc = self.nlp(texto)
            for sinal in todos_sinais:
                if sinal in encontrados:
                    continue
                sinal_doc = self.nlp(sinal.replace("_", " "))
                for token in doc:
                    if token.has_vector and sinal_doc.has_vector:
                        if token.similarity(sinal_doc) >= 0.70:
                            encontrados.add(sinal)
                            break

        return encontrados


    def analisar(self, sinais_usuario):
        """Compara os sinais com a base e retorna possíveis condições."""
        resultados = []
        for condicao, sinais_base in self.base_mental.items():
            intersec = sinais_usuario.intersection(sinais_base)
            if intersec:
                grau = len(intersec) / len(sinais_base)
                resultados.append((condicao, grau))

        resultados.sort(key=lambda x: x[1], reverse=True)
        return resultados
