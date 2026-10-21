import os
import streamlit as st
from groq import Groq
from dotenv import load_dotenv
load_dotenv()

# Carrega variáveis de ambiente do arquivo .env (uso local)
load_dotenv()

# Configuração da página Streamlit
st.set_page_config(page_title="Willian - Tattoo & IA", page_icon="🖋️", layout="centered")

# Inicialização do Cliente Groq
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    st.error("Chave da API Groq não encontrada. Configure a variável GROQ_API_KEY.")
    st.stop()

client = Groq(api_key=api_key)

# ---------------------------------------------------------------------------
# CONFIGURAÇÕES DO AGENTE E MEMÓRIA
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """
Você é um tatuador e gestor de estúdio especialista em inteligência artificial.
Tem mais de 11 anos de experiência, focado em trabalhos sombreados preto e branco e realismo.

OBJETIVO:
Responder às dúvidas do usuário com precisão técnica e clareza didática. Mantenha total coerência contextual baseando-se no resumo da memória e no histórico recente.

ESTILO E TOM:
Profissional, articulado, didático, calmo, confiante e acolhedor. Foco na segurança da tatuagem e gestão. Use termos técnicos autênticos explicados de forma acessível.

FORMATO:
- Respostas diretas, parágrafos curtos.
- Se o usuário mudar de assunto, adapte-se naturalmente (ex: "Entendido, alterando nossa rota para...").
- Consistência factual rigorosa com o histórico.
"""

# Função para condensar a memória (Sliding Window)
def condense_memory(old_messages):
    prompt_resumo = f"""
    Analise as mensagens abaixo e gere uma atualização condensada da memória de longo prazo.
    1. Extraia apenas fatos, decisões tomadas, dados técnicos citados e intenções do usuário.
    2. Elimine saudações, conversas fiadas e redundâncias.
    3. Se o usuário mudou de assunto, registre explicitamente o novo foco.
    
    Responda APENAS com tópicos curtos (máximo 3 a 4 linhas).
    
    Mensagens:
    {old_messages}
    """
    
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role": "system", "content": prompt_resumo}],
        temperature=0.3,
        max_tokens=150
    )
    return response.choices[0].message.content

# ---------------------------------------------------------------------------
# GERENCIAMENTO DE ESTADO (SESSION STATE)
# ---------------------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []
    
if "long_term_memory" not in st.session_state:
    st.session_state.long_term_memory = "Nenhum histórico anterior."

# Janela deslizante: se o histórico passar de 6 mensagens (3 interações), sumariza as mais antigas
MAX_HISTORY = 6 

# ---------------------------------------------------------------------------
# INTERFACE DO USUÁRIO
# ---------------------------------------------------------------------------
st.title("🖋️ Atendimento Especializado - Willian Tattoo")
st.markdown("*Especialista em Preto e Cinza, Realismo e Gestão de IA*")

# Exibe o histórico de chat na tela
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Entrada do Usuário
if user_input := st.chat_input("Como posso te ajudar com sua próxima tatuagem ou gestão de estúdio?"):
    
    # Adiciona e exibe a mensagem do usuário
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Verifica se precisa condensar a memória (Sliding Window)
    if len(st.session_state.messages) > MAX_HISTORY:
        # Pega as mensagens antigas que vão sair da janela
        mensagens_para_resumir = st.session_state.messages[:-MAX_HISTORY]
        # Gera o novo resumo condensado
        novo_resumo = condense_memory(mensagens_para_resumir)
        st.session_state.long_term_memory = novo_resumo
        # Mantém apenas as mensagens mais recentes na memória de curto prazo
        st.session_state.messages = st.session_state.messages[-MAX_HISTORY:]

    # Monta o contexto para a IA (Prompt do Sistema + Memória Condensada + Histórico Recente)
    context_prompt = f"{SYSTEM_PROMPT}\n\nMEMÓRIA DE LONGO PRAZO CONSOLIDADA:\n{st.session_state.long_term_memory}"
    
    api_messages = [{"role": "system", "content": context_prompt}] + st.session_state.messages

    # Chamada para a API da Groq
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        try:
            completion = client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=api_messages,
                temperature=0.7,
                max_tokens=800,
            )
            ai_response = completion.choices[0].message.content
            message_placeholder.markdown(ai_response)
            
            # Salva a resposta no histórico
            st.session_state.messages.append({"role": "assistant", "content": ai_response})
            
        except Exception as e:
            st.error(f"Erro ao conectar com a IA: {e}")

# Opcional: Barra lateral para mostrar o que a IA está lembrando nos bastidores
with st.sidebar:
    st.header("🧠 Memória de Longo Prazo (Debug)")
    st.info(st.session_state.long_term_memory)
    if st.button("Limpar Histórico"):
        st.session_state.messages = []
        st.session_state.long_term_memory = "Nenhum histórico anterior."
        st.rerun()