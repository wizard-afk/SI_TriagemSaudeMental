class CondicaoEmocional:
    """
    Representa uma categoria psicológica ou emocional
    e faz o cálculo de correspondência com base em sinais relatados.
    """

    def __init__(self, base_mental):
        self.base_mental = base_mental

    def sugerir(self, sinais_detectados):
        """Retorna as condições que têm pelo menos 50% de correspondência."""
        resultados = []

        for condicao, sinais in self.base_mental.items():
            intersec = sinais.intersection(sinais_detectados)
            if intersec:
                taxa = len(intersec) / len(sinais)
                resultados.append((condicao, taxa))

        resultados.sort(key=lambda x: x[1], reverse=True)
        return [c for c, t in resultados if t >= 0.5]
