import tkinter as tk
from tkinter import ttk, messagebox
from avaliador import AvaliadorEmocional


class AppTriagemMental(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🧠 Sistema de Triagem de Saúde Mental")
        self.geometry("720x480")
        self.config(bg="#f2f2f2")

        self.avaliador = AvaliadorEmocional("dados_mentais.json")

        # Título
        lbl_titulo = tk.Label(
            self,
            text="Sistema Especialista de Triagem Psicológica",
            font=("Helvetica", 18, "bold"),
            bg="#f2f2f2",
            fg="#333"
        )
        lbl_titulo.pack(pady=20)

        # Caixa de texto
        self.texto = tk.Text(self, height=6, width=70, wrap="word", font=("Helvetica", 11))
        self.texto.pack(pady=10)
        self.texto.insert(tk.END, "Descreva aqui o que você está sentindo...")

        # Botão de análise
        btn_analisar = ttk.Button(self, text="Analisar", command=self.analisar_texto)
        btn_analisar.pack(pady=15)

        # Área de resultados
        frame_resultados = tk.Frame(self, bg="#f2f2f2")
        frame_resultados.pack(pady=10, fill="both", expand=True)

        lbl_sinais = tk.Label(frame_resultados, text="Sinais identificados:", font=("Helvetica", 12, "bold"), bg="#f2f2f2")
        lbl_sinais.pack(anchor="w", padx=20, pady=(5, 0))

        self.txt_sinais = tk.Text(frame_resultados, height=5, width=80, state="disabled", wrap="word")
        self.txt_sinais.pack(padx=20, pady=5)

        lbl_diagnosticos = tk.Label(frame_resultados, text="Possíveis condições:", font=("Helvetica", 12, "bold"), bg="#f2f2f2")
        lbl_diagnosticos.pack(anchor="w", padx=20, pady=(10, 0))

        self.txt_resultado = tk.Text(frame_resultados, height=7, width=80, state="disabled", wrap="word")
        self.txt_resultado.pack(padx=20, pady=5)

        # Rodapé
        lbl_rodape = tk.Label(self, text="* Este sistema não substitui avaliação profissional.", bg="#f2f2f2", fg="#666")
        lbl_rodape.pack(pady=10)

    def analisar_texto(self):
        texto = self.texto.get("1.0", tk.END).strip()
        if not texto:
            messagebox.showwarning("Aviso", "Por favor, descreva o que está sentindo.")
            return

        sinais = self.avaliador.extrair_sinais(texto)
        resultados = self.avaliador.analisar(sinais)

        # Atualiza campos de texto
        self.txt_sinais.config(state="normal")
        self.txt_resultado.config(state="normal")
        self.txt_sinais.delete("1.0", tk.END)
        self.txt_resultado.delete("1.0", tk.END)

        if not sinais:
            self.txt_sinais.insert(tk.END, "Nenhum sinal emocional identificado.\n")
        else:
            self.txt_sinais.insert(tk.END, "\n".join(f"• {s.replace('_', ' ')}" for s in sinais))

        if not resultados:
            self.txt_resultado.insert(tk.END, "Nenhuma condição compatível encontrada.\n")
        else:
            for condicao, grau in resultados:
                self.txt_resultado.insert(tk.END, f"{condicao.capitalize()} ({grau * 100:.0f}% de correspondência)\n")

            self.txt_resultado.insert(tk.END, f"\n>>> Condição mais provável: {resultados[0][0].capitalize()}")

        self.txt_sinais.config(state="disabled")
        self.txt_resultado.config(state="disabled")


if __name__ == "__main__":
    app = AppTriagemMental()
    app.mainloop()
