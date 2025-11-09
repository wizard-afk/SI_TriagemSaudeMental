import json
class BaseDados:

    def base_conhecimento (self):
        return json.load(open("dados_mentais.json"))


