# UI Tkinter que integra NLU + MotorInferencia e mostra justificativas, risco e recomendações.
import tkinter as tk
from tkinter import ttk, messagebox
from nlu_processor import NLUProcessor
from motor_inferencia import MotorInferencia


class AppTriagem(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🧠 Sistema Especialista de Triagem e Pré-diagnóstico")
        self.geometry("920x760")
        self.config(bg="#f7f7f7")

        # inicializa NLU e Motor (apontando para base_conhecimento.json)
        self.nlu = NLUProcessor("base_conhecimento.json")
        self.motor = MotorInferencia("base_conhecimento.json")

        # Cabeçalho
        lbl = tk.Label(self, text="Sistema Especialista de Triagem e Pré-diagnóstico", font=("Helvetica", 16, "bold"),
                       bg="#f7f7f7")
        lbl.pack(pady=10)

        # Frame de entrada
        frm_in = tk.Frame(self, bg="#f7f7f7")
        frm_in.pack(padx=12, pady=6, fill="x")

        tk.Label(frm_in, text="Descreva o que a pessoa está sentindo:", bg="#f7f7f7").pack(anchor="w")
        self.txt_entrada = tk.Text(frm_in, height=6, width=120)
        self.txt_entrada.pack(pady=6)

        btn = ttk.Button(frm_in, text="Analisar", command=self.analisar)
        btn.pack(pady=6)

        # Notebook com abas de saída
        notebook = ttk.Notebook(self)
        notebook.pack(padx=10, pady=10, fill="both", expand=True)

        # Aba 1: Relatório resumo / sinais / risco / recomendações
        self.frame_rel = tk.Frame(notebook, bg="#ffffff")
        notebook.add(self.frame_rel, text="Relatório")

        tk.Label(self.frame_rel, text="Relatório sumarizado:", bg="#ffffff", font=("Helvetica", 12, "bold")).pack(
            anchor="w", padx=10, pady=(10, 0))
        self.txt_rel = tk.Text(self.frame_rel, height=4, width=105, state="disabled", wrap="word")
        self.txt_rel.pack(padx=10, pady=6)

        tk.Label(self.frame_rel, text="Sinais detectados:", bg="#ffffff", font=("Helvetica", 12, "bold")).pack(
            anchor="w", padx=10, pady=(8, 0))
        self.txt_sinais = tk.Text(self.frame_rel, height=6, width=105, state="disabled", wrap="word")
        self.txt_sinais.pack(padx=10, pady=6)

        tk.Label(self.frame_rel, text="Nível de risco:", bg="#ffffff", font=("Helvetica", 12, "bold")).pack(anchor="w",
                                                                                                            padx=10,
                                                                                                            pady=(8, 0))
        self.lbl_risco = tk.Label(self.frame_rel, text="-", bg="#ffffff", font=("Helvetica", 12))
        self.lbl_risco.pack(anchor="w", padx=10, pady=6)

        tk.Label(self.frame_rel, text="Recomendações:", bg="#ffffff", font=("Helvetica", 12, "bold")).pack(anchor="w",
                                                                                                           padx=10,
                                                                                                           pady=(8, 0))
        self.txt_recs = tk.Text(self.frame_rel, height=6, width=105, state="disabled", wrap="word")
        self.txt_recs.pack(padx=10, pady=6)

        # Aba 2: Inferências e justificativas
        self.frame_inf = tk.Frame(notebook, bg="#ffffff")
        notebook.add(self.frame_inf, text="Inferências")

        tk.Label(self.frame_inf, text="Possíveis condições detectadas (com justificativas):", bg="#ffffff",
                 font=("Helvetica", 12, "bold")).pack(anchor="w", padx=10, pady=(10, 0))
        self.txt_inf = tk.Text(self.frame_inf, height=30, width=105, state="disabled", wrap="word")
        self.txt_inf.pack(padx=10, pady=6)

        # Aba 3: Debug NLU (mostra saída do NLU para inspeção)
        self.frame_nlu = tk.Frame(notebook, bg="#ffffff")
        notebook.add(self.frame_nlu, text="NLU (debug)")

        tk.Label(self.frame_nlu, text="Saída do NLU (sintomas, red-flags, resumo):", bg="#ffffff",
                 font=("Helvetica", 12, "bold")).pack(anchor="w", padx=10, pady=(10, 0))
        self.txt_nlu = tk.Text(self.frame_nlu, height=18, width=105, state="disabled", wrap="word")
        self.txt_nlu.pack(padx=10, pady=6)

        # Rodapé
        lbl_rodape = tk.Label(self, text="* Protótipo para triagem. NÃO substitui avaliação profissional.",
                              bg="#f7f7f7", fg="#666")
        lbl_rodape.pack(pady=8)

    def analisar(self):
        texto = self.txt_entrada.get("1.0", tk.END).strip()
        if not texto:
            messagebox.showwarning("Aviso", "Por favor, descreva a queixa ou sintomas.")
            return

        # NLU -> retorna sintomas (dict), red_flags (list), resumo
        nlu_out = self.nlu.processar_texto(texto)
        sintomas_dict = nlu_out.get("sintomas", {})
        red_flags = nlu_out.get("red_flags", [])
        resumo = nlu_out.get("resumo", "")

        # transforma para conjunto de chaves (fatos) para o motor
        fatos = set(k.lower() for k in sintomas_dict.keys())
        # inclui red_flags textuais como fatos també
        for rf in red_flags:
            fatos.add(rf.lower())

        # inferência
        out = self.motor.inferir(fatos)

        # atualizar GUI
        self.txt_rel.config(state="normal")
        self.txt_sinais.config(state="normal")
        self.txt_recs.config(state="normal")
        self.txt_inf.config(state="normal")
        self.txt_nlu.config(state="normal")

        # limpar
        self.txt_rel.delete("1.0", tk.END)
        self.txt_sinais.delete("1.0", tk.END)
        self.txt_recs.delete("1.0", tk.END)
        self.txt_inf.delete("1.0", tk.END)
        self.txt_nlu.delete("1.0", tk.END)

        # preencher relatorio
        rel_motor = out.get("relatorio_queixas", "")
        texto_relatorio = resumo if resumo else rel_motor
        self.txt_rel.insert(tk.END, texto_relatorio)

        # sinais detectados (NLU)
        if sintomas_dict:
            for k, v in sorted(sintomas_dict.items()):
                self.txt_sinais.insert(tk.END, f"• {k.replace('_', ' ')} (ocorrências: {v})\n")
        else:
            self.txt_sinais.insert(tk.END, "Nenhum sinal identificado pelo NLU.\n")

        # risco com cores
        nivel_risco = out.get("nivel_risco", "-")
        cor_risco = {
            "Alto": "#ff4444",
            "Médio": "#ffaa00",
            "Baixo": "#44aa44",
            "Mínimo": "#666666"
        }.get(nivel_risco, "#000000")

        self.lbl_risco.config(text=nivel_risco, fg=cor_risco, font=("Helvetica", 12, "bold"))

        # recomendações
        for r in out.get("recomendacoes", []):
            self.txt_recs.insert(tk.END, f"• {r}\n")

        # inferências e justificativas
        resultados = out.get("resultados", [])
        if not resultados:
            self.txt_inf.insert(tk.END, "Nenhuma condição compatível encontrada.\n")
        else:
            for item in resultados:
                self.txt_inf.insert(tk.END, f"== {item['condicao'].capitalize()} — Score: {item['score'] * 100:.0f}%\n")
                self.txt_inf.insert(tk.END, item['justificativa'] + "\n\n")

        # saída NLU completa (debug)
        self.txt_nlu.insert(tk.END, f"Resumo NLU: {resumo}\n")
        self.txt_nlu.insert(tk.END, f"Sintomas extraídos (NLU):\n")
        for k, v in sorted(sintomas_dict.items()):
            self.txt_nlu.insert(tk.END, f" - {k}: {v}\n")
        self.txt_nlu.insert(tk.END, f"Red-flags detectadas (NLU): {', '.join(red_flags) if red_flags else 'Nenhuma'}\n")
        self.txt_nlu.insert(tk.END, f"\nFatos passados ao motor: {', '.join(sorted(fatos))}\n")

        # bloquear campos
        self.txt_rel.config(state="disabled")
        self.txt_sinais.config(state="disabled")
        self.txt_recs.config(state="disabled")
        self.txt_inf.config(state="disabled")
        self.txt_nlu.config(state="disabled")


if __name__ == "__main__":
    app = AppTriagem()
    app.mainloop()