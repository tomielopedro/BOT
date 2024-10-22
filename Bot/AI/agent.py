from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_community.document_loaders import PyPDFLoader, CSVLoader
from Bot.notion.notion_database import *


class Agent:
    def __init__(self, name: str, model: str, api_key: str, template: str, notion_key=None, notion_page=None, document_path=None):
        self.name = name

        self.model = model
        self.api_key = api_key
        self.template = template
        self.llm = ChatOpenAI(temperature=0, model=model, api_key=self.api_key)
        self.prompt = PromptTemplate(
            input_variables=["message", "system_information"], 
            template=template)
        self.chain = self.prompt | self.llm
        self.notion_key = notion_key
        self.notion_page = notion_page
        self.document_path = document_path


    # Load the documente and retorn a Document type
    def _load_knowledge_pdf(self):
        loader = PyPDFLoader(self.document_path)
        documents = loader.load()
        return documents

    def _load_knowledge_csv(self):
        loader = CSVLoader(f"./Base/{self.name}.csv")
        documents = loader.load()
        print(documents)
        return documents

    # Get the document and transform in embeddings
    def _make_embeddings(self):

        if self.notion_key is not None and self.notion_page is not None:

            embeddings = OpenAIEmbeddings(api_key=self.api_key)
            db = FAISS.from_documents(self._load_knowledge_csv(), embeddings)
            return db

        if self.document_path is not None:
            embeddings = OpenAIEmbeddings(api_key=self.api_key)
            db = FAISS.from_documents(self._load_knowledge_pdf(), embeddings)
            return db

    # Search for similarity
    def search(self, query):
        db = self._make_embeddings()
        response = db.similarity_search(query, k=3)
        return [doc.page_content for doc in response]

    def to_dict(self):
        return {
            "name":self.name,
            "pdf_path": self.document_path,
            "model": self.model,
            "api_key": self.api_key,
            "template": self.template,
            "notion_key": self.notion_key,
            "notion_page": self.notion_page,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(data["name"], data["model"], data["api_key"], data["template"], data["notion_key"], data["notion_page"], data["pdf_path"])

    def llm_response(self, message):
        system_information = self.search(message)  # Busca por similaridade no FAISS
        response = self.chain.invoke({
            'message': message,
            'system_information': system_information  # Informações do sistema para embasar a resposta
        })
        return response