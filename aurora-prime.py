import flask
import requests
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import CSVLoader
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI

load_dotenv()
app = flask.Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    data = flask.request.json
    return flask.jsonify(data)

if __name__ == '__main__':
    app.run(port=5000)