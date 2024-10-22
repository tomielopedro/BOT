import streamlit as st

def settings_screen(app):
    st.title("Gestão de Chaves")
    keys_data = app.load_keys()
    openai_keys_names = [key["name"] for key in keys_data["openai_keys"]]
    notion_keys_names = [key["name"] for key in keys_data["notion_keys"]]

    tab1, tab2 = st.tabs(["Visualizar Chaves", "Criar Novas Chaves"])

    with tab1:

        if keys_data["openai_keys"]:

            st.write("### Chaves do Notion")
            if keys_data["notion_keys"]:
                for i, key in enumerate(keys_data["notion_keys"], start=1):
                    st.text_input(f"{i} - Name: `{key['name']}`", value=key['api_key'], type="password")
        else:
            st.write("#### Nenhuma chave da openAi encontrada.")

        if keys_data["notion_keys"]:
            st.write("### Chaves do OpenAI")
            if keys_data["openai_keys"]:
                for i, key in enumerate(keys_data["openai_keys"], start=1):
                    st.text_input(f"{i} - Name: `{key['name']}`", value=key['api_key'], type="password")
        else:
            st.write("#### Nenhuma chave do Notion encontrada.")



    with tab2:
        # Novo cadastro de chaves
        st.write("Cadastrar Nova Chave de OpenAI")
        openai_key_name = st.text_input("Nome da chave OpenAI")
        openai_api_key = st.text_input("OpenAI API Key")

        if st.button("Salvar OpenAI"):

            if openai_key_name not in openai_keys_names:
                if openai_key_name and openai_api_key:
                    new_data = {"name": openai_key_name, "api_key": openai_api_key}
                    app.save_keys(new_data, "openai")
                    st.success("Chave OpenAI salva com sucesso!")
                    st.session_state.keys_data = app.load_keys()
                else:
                    st.warning("Por favor, preencha todos os campos.")
            else:
                st.warning("Já existe uma chave com esse nome")

        st.write("Cadastrar Nova Chave de Notion")
        notion_key_name = st.text_input("Nome da chave Notion")
        notion_api_key = st.text_input("Notion API Key")

        if st.button("Salvar Notion"):
            if notion_key_name not in notion_keys_names:
                if notion_key_name and notion_api_key:
                    new_data = {"name": notion_key_name, "api_key": notion_api_key}
                    app.save_keys(new_data,"notion")
                    st.success("Chave Notion salva com sucesso!")
                    app.load_keys()
                else:
                    st.warning("Por favor, preencha todos os campos.")
            else:
                st.warning("Já existe uma chave com esse nome")
