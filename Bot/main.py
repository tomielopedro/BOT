from langchain_community.document_loaders import PyPDFLoader
from langchain_openai import ChatOpenAI
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
import os

load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

answer = input("Insira sua pergunta: ")
llm = ChatOpenAI(model="gpt-4o")
file_path = "./avec.pdf"
loader = PyPDFLoader(file_path)

docs = loader.load()
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
splits = text_splitter.split_documents(docs)
vectorstore = Chroma.from_documents(documents=splits, embedding=OpenAIEmbeddings())

retriever = vectorstore.as_retriever()

system_prompt = (
    "Você é um assistante do salão Beleza para todos"
    "Seu nome é Gohan"
    "Comece se apresentando, inicie com 'Oi, eu sou o Gohan!'"
    "Você é um assistente especialista em responder questões sobre o salão"
    "Use o texto a seguir para responder uma pergunta"
    "Caso a resposta não esteja no texto diga que você só pode responder questões sobre o salão"
    "De uma resposta completa"
    "Responda em portugues"
    "\n\n"
    "{context}"
)

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        ("human", "{input}"),
    ]
)


question_answer_chain = create_stuff_documents_chain(llm, prompt)
rag_chain = create_retrieval_chain(retriever, question_answer_chain)

results = rag_chain.invoke({"input": answer})
# Page llm get content
print(results["answer"])
