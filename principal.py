from avaliador import AvaliadorEmocional

print("=== Sistema Especialista de Triagem e Pré-Diagnóstico de Saúde Mental ===\n")

# Inicializa o avaliador com a base de conhecimento
avaliador = AvaliadorEmocional("dados_mentais.json")

entrada_usuario = input("Descreva brevemente o que a pessoa está sentindo ou apresentando:\n> ")

# Identifica sinais psicológicos relatados
sinais_encontrados = avaliador.extrair_sinais(entrada_usuario)

if not sinais_encontrados:
    print("\nNenhum sinal emocional identificado no texto.")
else:
    print("\nSinais identificados:")
    for s in sinais_encontrados:
        print(f" - {s.replace('_', ' ')}")

    print("\nProcessando possíveis condições emocionais...\n")
    resultados = avaliador.analisar(sinais_encontrados)

    if not resultados:
        print("Nenhum quadro psicológico compatível encontrado.")
    else:
        for condicao, confianca in resultados:
            print(f"{condicao.capitalize()} ({confianca * 100:.0f}% de correspondência)")

        print(f"\n>>> Possível condição predominante: {resultados[0][0].capitalize()}")
