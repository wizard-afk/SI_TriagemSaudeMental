import json
import re


class AvaliadorEmocional:
    """
    Classe responsável por interpretar descrições de comportamento ou estado emocional
    e sugerir possíveis condições psicológicas com base em correspondência e semântica.
    """

    def __init__(self, caminho_base):
        with open(caminho_base, "r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)

        # Normaliza os sinais e condições para minúsculas
        self.base_mental = {}
        for condicao, sinais in dados.items():
            self.base_mental[condicao] = {s.lower() for s in sinais}

        # Carrega modelo linguístico para similaridade semântica
        try:
            import spacy
            self.nlp = spacy.load("pt_core_news_md")
        except:
            try:
                import spacy
                self.nlp = spacy.load("pt_core_news_sm")
            except:
                print("Aviso: spaCy não encontrado. Comparações semânticas desativadas.")
                self.nlp = None

    # ------------------------
    # MÉTODOS PRINCIPAIS
    # ------------------------

    def comparar_semelhanca(self, termo1, termo2, limite=0.75):
        """Compara semanticamente dois termos e retorna True se forem semelhantes."""
        if self.nlp is None:
            return False

        doc1 = self.nlp(termo1.replace("_", " "))
        doc2 = self.nlp(termo2.replace("_", " "))
        return doc1.similarity(doc2) >= limite

    def extrair_sinais(self, texto):
        """Identifica sinais emocionais presentes no texto digitado pelo usuário."""
        texto = texto.lower()
        encontrados = set()

        todos_sinais = set().union(*self.base_mental.values())

        # Busca direta por termos
        for sinal in todos_sinais:
            padrao = sinal.replace("_", " ")
            if re.search(rf"\b{padrao}\b", texto):
                encontrados.add(sinal)

        # Busca semântica, caso spaCy esteja disponível
        if self.nlp is not None:
            doc = self.nlp(texto)

            for sinal in todos_sinais:
                if sinal in encontrados:
                    continue

                sinal_doc = self.nlp(sinal.replace("_", " "))

                for token in doc:
                    if token.has_vector and sinal_doc.has_vector:
                        if token.similarity(sinal_doc) >= 0.75:
                            encontrados.add(sinal)
                            break

                if sinal not in encontrados:
                    for sentenca in doc.sents:
                        if sentenca.has_vector and sinal_doc.has_vector:
                            if sentenca.similarity(sinal_doc) >= 0.70:
                                encontrados.add(sinal)
                                break

        return encontrados

    def analisar(self, sinais_usuario):
        """
        Avalia as condições possíveis com base nos sinais detectados.
        Retorna uma lista de tuplas (condição, grau_de_aderência).
        """
        possibilidades = []

        for condicao, sinais_requeridos in self.base_mental.items():
            intersecao = sinais_usuario.intersection(sinais_requeridos)
            if intersecao:
                grau = len(intersecao) / len(sinais_requeridos)
                possibilidades.append((condicao, grau))

        possibilidades.sort(key=lambda x: x[1], reverse=True)
        return possibilidades
