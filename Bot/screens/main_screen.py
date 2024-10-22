import streamlit as st

def main_screen(agents):
    st.title("🤖 Chatbot")
    st.caption("🚀 Make big things")
    if agents:
        selected_agent = st.selectbox("Selecione um Agente:", list(agents.keys()))
        agent = agents[selected_agent]
        message = st.text_area("Envie uma mensagem ao agente:")

        if st.button("Enviar"):
            if message:
                st.write("Gerando resposta...")
                result = agent.llm_response(message)
                st.info(result.content)
            else:
                st.warning("Por favor, digite uma mensagem antes de enviar.")
    else:
        st.write("Nenhum agente criado. Vá para a tela de criação de agente.")
