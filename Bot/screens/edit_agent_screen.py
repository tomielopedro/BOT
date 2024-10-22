import streamlit as st
from Bot.notion.notion_database import get_notion_data
import os

def edit_agent_screen(app):
    st.title("Editar ou Excluir Agente")

    if app.agents:
        keys = app.load_keys()
        selected_agent = st.selectbox("Selecione um Agente para editar:", list(app.agents.keys()))
        agent = app.agents[selected_agent]
        openai_key_names = [key["name"] for key in keys["openai_keys"]]
        new_api_key = st.selectbox("API Key:", options=openai_key_names)
        new_model = st.selectbox("Modelo:", ["gpt-4o", "gpt-3.5-turbo"],
                                     index=["gpt-4o", "gpt-3.5-turbo"].index(agent.model))
        new_template = st.text_area("Template:", value=agent.template)
        new_uploaded_file = None
        new_notion_api_key = ''
        new_notion_pageid = ''

        if agent.notion_key and agent.notion_page:
            api_keys_name_notion = [key["name"] for key in keys["notion_keys"]]
            notion_api_key = st.selectbox("Notion API Key", options=api_keys_name_notion)
            new_notion_pageid = st.text_input("Notion PageId", value=agent.notion_page)
            new_notion_api_key = [key["api_key"] for key in keys["notion_keys"] if key["name"] == notion_api_key][0]
            notion = get_notion_data(agent.name, agent.notion_key, agent.notion_page)
        else:
            new_uploaded_file = st.file_uploader("Select a document", type=["pdf"])

        if st.button("Salvar Alterações"):
            if new_uploaded_file:
                pdf_path = os.path.join(app.UPLOAD_DIR, f"{agent.name}.pdf")
                with open(pdf_path, "wb") as f:
                    f.write(new_uploaded_file.getbuffer())
            agent.notion_key = new_notion_api_key
            agent.notion_page = new_notion_pageid
            agent.api_key = [key["api_key"] for key in keys["openai_keys"] if key["name"] == new_api_key][0]
            agent.model = new_model
            agent.template = new_template

            app.agents[selected_agent] = agent
            app.save_agents()
            st.success("Agente atualizado com sucesso!")

        if st.button("Excluir Agente"):
            del app.agents[selected_agent]
            app.save_agents()
            st.success(f"Agente '{selected_agent}' excluído com sucesso!")
            st.rerun()
    else:
        st.warning("Nenhum agente disponível para editar.")
