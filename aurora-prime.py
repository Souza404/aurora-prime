from openai import OpenAI
from dotenv import load_dotenv
from utils.evolutionAPI import EvolutionAPI
import flask

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory

from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import CSVLoader
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.chat_message_histories import ChatMessageHistory

from langchain_openai import ChatOpenAI


# --- Setup base ---
e = EvolutionAPI()
app = flask.Flask(__name__)
load_dotenv()

client = OpenAI()

# Base de conhecimento (RAG)
loader = CSVLoader(file_path="perguntas_respostas.csv")
documents = loader.load()
embeddings = OpenAIEmbeddings()
vector_store = FAISS.from_documents(documents, embeddings)
retrieval = vector_store.as_retriever()


llm = ChatOpenAI()

# --- Memória por sessão (RAM; para produção, trocar por Redis/DB) ---
_session_store = {} 

def get_history(session_id: str) -> ChatMessageHistory:
    if session_id not in _session_store:
        _session_store[session_id] = ChatMessageHistory()
    return _session_store[session_id]

# --- Prompt com histórico ---
SYSTEM_PROMPT = "Role: Seu nome é Rogério, um assistente virtual da empresa Aurora Prime Imóveis, você conversa de forma educada e formal. Instructions: No início da interação com o usuário envie uma breve saudação com linguagem consultiva e sem jargões. Seu objetivo principal é coletar a localização/bairro, tipologia (casa, apê, cobertura), número de quartos, vagas, metragem mínima, faixa de investimento, prazo de mudança e forma de pagamento (à vista, financiamento, permuta/consórcio) isso deve ser coletado no decorrer da conversa, evite enviar mensagens longas e sempre pergunte apenas uma coisa por vez. Restrictions: Caso o usuário utilize palavras ofensivas, o repreenda de forma educada e encerre a conversa. Se o usuário fizer perguntas sem relação com o escopo da imobiliária envie uma mensagem informando que você não trata desse escopo. context {context}"


prompt = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{question}"),
    ]
)

# Faz o retriever receber só a pergunta (x["question"]) e retornar documentos.
get_context = RunnableLambda(lambda x: retrieval.get_relevant_documents(x["question"]))

base_chain = (
    RunnablePassthrough.assign(context=get_context)  # exige dict de entrada, ex.: {"question": "..."}
    | prompt
    | llm
    | StrOutputParser()
)

# Empacota com histórico por sessão
history_chain = RunnableWithMessageHistory(
    base_chain,
    get_history,
    input_messages_key="question",
    history_messages_key="history",
)

# --- Webhook ---
@app.route("/webhook", methods=["POST"])
def webhook():
    data = flask.request.json

    message = data["data"]["message"]["conversation"]
    instance = data["instance"]
    instance_key = data["apikey"]
    sender_number = data["data"]["key"]["remoteJid"].split("@")[0]

    response_text = history_chain.invoke(
        {"question": message},
        config={"configurable": {"session_id": sender_number}},
    )

    e.enviar_mensagem(response_text, instance, instance_key, sender_number)
    return flask.jsonify({"ok": True})

if __name__ == "__main__":
    app.run(port=5000)
