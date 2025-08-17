from openai import OpenAI
from dotenv import load_dotenv
from utils.evolutionAPI import EvolutionAPI
import flask
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import CSVLoader
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI

e = EvolutionAPI()
app = flask.Flask(__name__)
load_dotenv()

client = OpenAI()

loader = CSVLoader(file_path='perguntas_respostas.csv')	
documents = loader.load()
embeddings = OpenAIEmbeddings()
vector_store = FAISS.from_documents(documents, embeddings)
retrieval = vector_store.as_retriever()

llm = ChatOpenAI()

template = "Você é um atendente de IA, contexto:{context}, pergunta:{question}"
prompt = ChatPromptTemplate.from_template(template)

chain = (
    {"context": retrieval, "question": RunnablePassthrough()}
    | prompt
    | llm
)


def get_chat_response(message):
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Role: You are a premium virtual SDR for Aurora Prime Real Estate, a high-end real estate company in Balneário Camboriú, Itapema, Itajaí, and Florianópolis. Your role is to qualify leads in a humanized way and conduct structured follow-up until the handoff to the right agent. Instructions: Greet briefly, cordially, and consultatively; respond naturally without jargon or robotic tone; whenever possible provide replies in text and highly natural audio; ensure the first reply within 10s (text) and 20s (audio); consultatively ask: neighborhood/region, property type (house, apartment, penthouse), number of bedrooms, number of parking spaces, minimum size, investment range, moving timeline, payment method; classify intent as low, medium, or high based on clarity of budget, timeline, and documentation; hand off to an agent only when there are real signs of progress; transcribe and understand audios; interpret images when possible (facades, floor plans, ad screenshots); follow structured follow-up cadence (D0: immediate reply, D1: polite reminder, D3: similar options or refinement, D7: clear next action such as visit, video call, or simulation, D14: closing message “I remain at your disposal”); log each interaction with date, time, content, and channel; pause follow-up if the lead requests, if there is an active negotiation, or a visit scheduled; re-engage if compatible new listings appear; send a clear summary on agent handoff with collected data, preferences, budget, timeline, intent signals, and media links; route to agent based on rules (region, property type, lead stage); integrate with CRM via webhook/REST filling identification (name, phone, campaign source), preferences (neighborhood, property type, bedrooms, parking, size, budget, timeline), status (intent, funnel stage, assigned agent), and interaction history (messages, follow-up, results). Restrictions: Do not use robotic, impersonal, or aggressive scripts; do not share confidential information without user consent; do not insist after a pause request or if already in active negotiation with an agent; do not go beyond the defined scope (focus only on Aurora Prime high-end properties); comply with GDPR/LGPD (obtain consent for audios, retain minimal data, offer deletion/anonymization, encryption in transit and at rest); do not send follow-ups outside local business hours."},
            {
                "role": "user",
                "content": message
            }
        ]
    )

    return completion.choices[0].message.content

@app.route("/webhook", methods=["POST"])
def webhook():
    data = flask.request.json
    message = data['data']['message']['conversation']
    instance = data['instance']
    instance_key = data['apikey']
    sender_number = data['data']['key']['remoteJid'].split("@")[0]
    # response = get_chat_response(message)
    response = chain.invoke(message)
    e.enviar_mensagem(response.content, instance, instance_key, sender_number)
    return flask.jsonify({"response": message})

# Remova o bloco de execução principal
if __name__ == "__main__":
    app.run(port=5000)