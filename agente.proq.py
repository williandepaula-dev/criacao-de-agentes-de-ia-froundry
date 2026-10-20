import os
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox
from groq import Groq

# ---------------------------------------------------------------------------
# ENGENHARIA DE PROMPT (Estruturado via convenção semântica XML)
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """
<persona>
  <name>Willian (williandepaulatattoo)</name>
  <role>Tatuador Profissional com mais de 10 anos de experiência</role>
  <tone>Carismático, acolhedor, altamente profissional e especialista</tone>
  <specialties>
    - Estilo Black & Grey (Preto e Cinza)
    - Realismo avançado
    - Trabalho focado em texturas, sombreamento e profundidade
  </specialties>
  <social_media>
    - Instagram: https://www.instagram.com/williandepaulatattoo/
  </social_media>
</persona>

<instructions>
  <rule id="1">Atue sempre em primeira pessoa como o próprio Willian. Nunca revele que é uma IA.</rule>
  <rule id="2">Mantenha o foco estrito e exclusivo no universo da tatuagem. Recuse educadamente qualquer outro tema.</rule>
  <rule id="3">Ao interagir pela primeira vez ou ao ser solicitado um orçamento, acolha o cliente e peça APENAS:</rule>
    <data_request>
      1. A ideia ou imagem de referência da arte desejada.
      2. O local exato do corpo onde pretende tatuar (e tamanho estimado se souber).
    </data_request>
  <rule id="4">Nunca faça perguntas relacionadas a impressão gráfica, sites, metragem quadrada, engenharia ou serviços fora da tatuagem.</rule>
  <rule id="5">Mantenha o diálogo fluido: no máximo 1 ou 2 perguntas diretas por mensagem. Não repita perguntas já respondidas.</rule>
  <rule id="6">Sempre que apropriado, direcione o cliente para conferir os trabalhos e cicatrizados no Instagram oficial.</rule>
</instructions>

<constraints>
  <forbidden>Uso de palavrões, tom informal excessivo/desrespeitoso, inventar preços fixos sem ver referência e tamanho.</forbidden>
</constraints>

<examples>
  <example>
    <user>Olá, gostaria de saber quanto custa para fazer um leão no braço?</user>
    <assistant>Fala! Tudo certo? Fico feliz pelo interesse no meu trabalho! Para eu conseguir te passar uma estimativa exata do valor, me envia a foto de referência da arte que você tem em mente e me diz em qual parte do braço você pretende mandar (antebraço, bíceps, ombro)? Aproveita para dar uma olhada nos meus trabalhos recentes em Preto e Cinza lá no Instagram: https://www.instagram.com/williandepaulatattoo/</assistant>
  </example>
</examples>
"""

# ---------------------------------------------------------------------------
# INTERFACE GRÁFICA (Tkinter)
# ---------------------------------------------------------------------------
class TattooAssistantApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Atendimento - Willian de Paula Tattoo")
        self.root.geometry("550x650")
        self.root.configure(bg="#1e1e24")

        # Configuração da API Groq
        # DICA: Defina a variável de ambiente GROQ_API_KEY no sistema ou insira a chave na string abaixo
        api_key = os.environ.get("GROQ_API_KEY", "")
        self.client = Groq(api_key=api_key)
        self.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        self._build_ui()

    def _build_ui(self):
        # Cabeçalho
        header_frame = tk.Frame(self.root, bg="red")
        header_frame.pack(fill=tk.X)
        
        title_label = tk.Label(
            header_frame, 
            text="williandepaulatattoo | Chat Atendimento", 
            font=("Helvetica", 14, "bold"), 
            fg="#ffffff", 
            bg="#2b2b36"
        )
        title_label.pack()

        # Área de exibição do Chat
        self.chat_display = scrolledtext.ScrolledText(
            self.root, 
            wrap=tk.WORD, 
            font=("Helvetica", 10),
            bg="#121214", 
            fg="#e1e1e6",
            insertbackground="white"
        )
        self.chat_display.pack(padx=15, pady=15, fill=tk.BOTH, expand=True)
        self.chat_display.config(state=tk.DISABLED)

        # Container de Entrada
        input_frame = tk.Frame(self.root, bg="#1e1e24")
        input_frame.pack(padx=15, pady=(0, 15), fill=tk.X)

        self.user_input = tk.Entry(
            input_frame, 
            font=("Helvetica", 11),
            bg="#2b2b36", 
            fg="#ffffff",
            insertbackground="white",
            relief=tk.FLAT
        )
        self.user_input.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8, padx=(0, 10))
        self.user_input.bind("<Return>", lambda event: self.send_message())

        send_btn = tk.Button(
            input_frame, 
            text="Enviar", 
            font=("Helvetica", 10, "bold"),
            bg="#00875f", 
            fg="#ffffff",
            activebackground="#00b37e",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            command=self.send_message,
            padx=15
        )
        send_btn.pack(side=tk.RIGHT)

        self._append_message("Willian", "Fala! Tudo certo? Como posso te ajudar com sua nova tattoo hoje?")

    def _append_message(self, sender, text):
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, f"{sender}:\n", "sender_tag")
        self.chat_display.insert(tk.END, f"{text}\n\n", "text_tag")
        
        # Estilização básica de tags
        self.chat_display.tag_config("sender_tag", font=("Helvetica", 10, "bold"), foreground="#00b37e" if sender == "Willian" else "#61a5c2")
        self.chat_display.tag_config("text_tag", foreground="#ffffff")
        
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)

    def send_message(self):
        user_text = self.user_input.get().strip()
        if not user_text:
            return

        self._append_message("Você", user_text)
        self.user_input.delete(0, tk.END)

        # Adiciona histórico no contexto
        self.messages.append({"role": "user", "content": user_text})

        # Executa a chamada em thread separada para não travar a interface gráfica
        threading.Thread(target=self._fetch_response, daemon=True).start()

    def _fetch_response(self):
        try:
            response = self.client.chat.completions.create(
                model="openai/gpt-oss-120b",  # Modelo recomendado para instrução e diálogos estruturados na Groq
                messages=self.messages,
                temperature=0.6,
                max_tokens=400
            )
            bot_text = response.choices[0].message.content
            self.messages.append({"role": "assistant", "content": bot_text})
            
            # Atualiza a UI na thread principal
            self.root.after(0, lambda: self._append_message("Willian", bot_text))
            
        except Exception as e:
            error_msg = f"Erro na conexão com a API: {str(e)}"
            self.root.after(0, lambda: messagebox.showerror("Erro", error_msg))

# ---------------------------------------------------------------------------
# EXECUÇÃO
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = TattooAssistantApp(root)
    root.mainloop()