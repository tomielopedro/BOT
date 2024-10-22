import streamlit as st
from Bot.AI.agent import Agent
import os
from Bot.notion.notion_database import get_notion_data

def create_agent_screen(app):
    st.title("Create new agent")

    # Uploader de arquivo PDF
    name = st.text_input("Agent name")
    option = st.radio("select how the model receives knowledge:", ["Upload Document", "Notion Integration"])
    notion_api_key = None
    notion_pageid = None
    uploaded_file = None
    keys = app.load_keys()

    if option == "Upload Document":
        uploaded_file = st.file_uploader("Select a document", type=["pdf"])
    if option == "Notion Integration":
        api_keys_name_notion = [key["name"] for key in keys["notion_keys"]]
        notion_api_key = st.selectbox("Notion API Key", options=api_keys_name_notion)
        notion_pageid = st.text_input("Notion PageId")

    api_keys_name = [key["name"] for key in keys["openai_keys"]]
    api_key = st.selectbox("API Key", options=api_keys_name)
    model = st.selectbox("Modelo:", ["gpt-4o", "gpt-3.5-turbo"])
    template = st.text_area("Template:", key="template")

    if st.button("Salvar Agente"):
        api_key = [key["api_key"] for key in keys["openai_keys"] if key["name"] == api_key][0]
        if notion_api_key:
            notion_api_key = [key["api_key"] for key in keys["notion_keys"] if key["name"] == notion_api_key][0]

        if (option == "Upload Document" or option == "Notion Integration") and template:
            if uploaded_file:
                pdf_path = os.path.join(app.UPLOAD_DIR, f"{name}.pdf")
                with open(pdf_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                new_agent = Agent(name, model, api_key, template, notion_api_key, notion_pageid, f"./Base/{name}.pdf")
            else:
                get_notion_data(name, notion_api_key, notion_pageid)
                new_agent = Agent(name, model, api_key, template, notion_api_key, notion_pageid, None)

            app.agents[name] = new_agent
            app.save_agents()
            st.success("Agente criado com sucesso!")
            st.session_state['screen'] = 'main'
        else:
            st.error("Por favor, preencha todos os campos.")
