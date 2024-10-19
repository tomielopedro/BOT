import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_openai import ChatOpenAI
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from notion import PageNotion
import os

# Carregar variáveis de ambiente
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
api_key = os.getenv("NOTION_API_KEY")
page_id = os.getenv("AVEC_PAGE_ID")
# Inicializar a aplicação FastAPI
app = FastAPI()

# Definição do modelo para a requisição
class Question(BaseModel):
    question: str

# Carregar e preparar o modelo
llm = ChatOpenAI(model="gpt-4o")

# Carregar e processar o documento PDF
file_path = "Base/pagina_notion.pdf"
loader = PyPDFLoader(file_path)
docs = loader.load()
print(loader)

# Separar o texto em partes
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
splits = text_splitter.split_documents(docs)

# Transformar o texto em embeddings
vectorstore = Chroma.from_documents(documents=splits, embedding=OpenAIEmbeddings())
retriever = vectorstore.as_retriever()

# Definir o prompt do modelo
system_prompt = (
    "Você é um assistente do salão Beleza para todos. "
    "Seu nome é Gohan. "
    "Comece se apresentando, inicie com 'Oi, eu sou o Gohan!'. "
    "Você é um assistente especialista em responder questões sobre o salão. "
    "Use o texto a seguir para responder uma pergunta. "
    "Caso a resposta não esteja no texto, diga que você só pode responder questões sobre o salão que estão em sua base de dados. "
    "Dê uma resposta completa. "
    "Responda em português. "
    "\n\n"
    "{context}"
)

# Definir o chat
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        ("human", "{input}"),
    ]
)

question_answer_chain = create_stuff_documents_chain(llm, prompt)
rag_chain = create_retrieval_chain(retriever, question_answer_chain)

# api
@app.post("/ask/")
async def ask_question(question: Question):
    try:
        # Executar o modelo de recuperação e resposta
        results = rag_chain.invoke({"input": question.question})
        return {results["answer"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
