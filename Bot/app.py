import streamlit as st
import os
import json
from AI.agent import Agent
from screens.main_screen import main_screen
from screens.create_agent_screen import create_agent_screen
from screens.edit_agent_screen import edit_agent_screen
from screens.settings_screen import settings_screen


class SalonBotApp:
    def __init__(self):
        self.AGENT_FILE = "settings/agents.json"
        self.UPLOAD_DIR = "Base"
        os.makedirs(self.UPLOAD_DIR, exist_ok=True)
        self.agents = self.load_agents()

    def load_agents(self):
        if os.path.exists(self.AGENT_FILE):
            with open(self.AGENT_FILE, "r") as file:
                content = file.read()
                if content:
                    try:
                        data = json.loads(content)
                        return {name: Agent.from_dict(data) for name, data in data.items()}
                    except json.JSONDecodeError:
                        st.error("Erro ao decodificar o arquivo JSON. Verifique o formato do arquivo.")
                        return {}
                else:
                    return {}
        return {}

    def save_agents(self):
        with open(self.AGENT_FILE, "w") as file:
            json.dump({name: agent.to_dict() for name, agent in self.agents.items()}, file)

    def load_keys(sef,file_path='settings/keys.json'):
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                return json.load(f)
        else:
            return {"notion_keys": [], "openai_keys": []}

    def save_keys(self, new_data, key_type, file_path='settings/keys.json'):
        data = self.load_keys(file_path)
        if key_type == 'notion':
            data['notion_keys'].append(new_data)
        elif key_type == 'openai':
            data['openai_keys'].append(new_data)

        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)

    def main(self):
        st.sidebar.title("Menu")

        # Menu lateral para alternar entre telas
        if st.sidebar.button("Chat"):
            st.session_state['screen'] = 'main'

        if st.sidebar.button("Criar Novo Agente"):
            st.session_state['screen'] = 'create_agent'

        if st.sidebar.button("Editar"):
            st.session_state['screen'] = 'edit_agent'

        if st.sidebar.button("Settings"):
            st.session_state['screen'] = 'settings'

        # Definir a tela inicial se não houver nenhum estado
        if 'screen' not in st.session_state:
            st.session_state['screen'] = 'main'

        # Navegação entre telas
        if st.session_state['screen'] == 'main':
            main_screen(self.agents)
        elif st.session_state['screen'] == 'create_agent':
            create_agent_screen(self)
        elif st.session_state['screen'] == 'edit_agent':
            edit_agent_screen(self)
        elif st.session_state['screen'] == 'settings':
            settings_screen(self)


if __name__ == '__main__':
    app = SalonBotApp()
    app.main()
