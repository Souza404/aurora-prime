# Aurora Prime

## 📌 Visão Geral
Este projeto consiste no desenvolvimento de um **chatbot em Python**, integrado com a **Evolution API** e voltado para a **Aurora Prime Imóveis**.  

O chatbot tem como objetivo **automatizar o atendimento ao usuário**, oferecendo:  
- Uma **base de conhecimento própria** com perguntas e respostas frequentes.  
- Capacidade de manter **contexto entre mensagens** (memória de sessão).  
- **Tom de voz consultivo e formal**, simulando o atendimento de um corretor.  

---

## ⚙️ Tecnologias Utilizadas
- **Python 3.12+**  
- **Flask** para criação do webhook.  
- **LangChain** para estruturação de prompts, memória e encadeamento.  
- **FAISS** para busca vetorial de documentos.  
- **OpenAI API** para geração de respostas.  
- **Evolution API** para envio e recebimento de mensagens via WhatsApp.  
- **Docker Compose** para orquestração de containers (Evolution API, Redis, PostgreSQL).  

---

## 🛠️ Estrutura do Projeto

- `app.py` → Código principal do chatbot em Flask (webhook).  
- `utils/evolutionAPI.py` → Wrapper para chamadas HTTP na Evolution API.  
- `perguntas_respostas.csv` → Base de conhecimento utilizada no RAG (Retrieval-Augmented Generation).  
- `docker-compose.yml` → Configuração de containers para Evolution API, Redis e PostgreSQL.  

---

## 🚀 Como Executar o Projeto

### 1. Pré-requisitos
- Python 3.12+  
- Docker + Docker Compose para instalação da Evolution API
- Chave da API OpenAI (`OPENAI_API_KEY`) configurada no `.env`  
- Chave da Evolution API (`AUTHENTICATION_API_KEY`) configurada no `docker-compose.yml`  

### 2. Clonar o repositório
```bash
git clone https://github.com/Souza404/aurora-prime
cd aurora-prime
```

### 3. Instalar ngrok para expor a porta 5000
```bash
ngrok http 5000
```

### 4. Copiar a URL forncecida pelo ngrok no passo anterior e adicionar como URL do WebHook no manager da Evolution API, com o sufixo `/webhook`:
```bash
Exemplo: https://123d4a5c678.ngrok-free.app/webhook
```
### 🚧 Desafios na Implementação
Durante o desenvolvimento, alguns problemas críticos foram encontrados ao utilizar a Evolution API:

1. **Versão v2.1.1 (`atendai/evolution-api:v2.1.1`)**  (Imagem docker recomendada no site oficial da Evolution -> https://doc.evolution-api.com/v2/pt/install/docker)
   - Erro crítico: o número do usuário que enviava a mensagem não era retornado corretamente.  
   - O campo `remoteJid` fazia referência ao **próprio número** em vez do número do usuário. Consequência: **não era possível responder ao usuário**.  
   - Nessa versão, o QR code para conectar ao WhatsApp não é exibido.
   - ❌ Versão bem instável 


2. **Versão v2.3.1 (`evoapicloud/evolution-api:v2.3.1`)**  
   - Problema resolvido: finalmente foi possível **enviar mensagens ao usuário**.  
   - Novo erro crítico: **não retorna o base64** de áudios ou imagens.  
   - Consequência: funcionalidades de **reconhecimento de áudio e imagem** ficaram comprometidas.  

## 📌 Observações Finais
Com base na experiência adquirida:  

- ❌ Para **projetos de grande escala** ou com **prazos curtos**, **não é recomendável** utilizar a Evolution API, devido ao tempo excessivo gasto na resolução de erros.  
- ✅ Recomenda-se o uso da **API oficial do WhatsApp**: embora tenha custo, oferece **maior estabilidade e confiabilidade**, justificando o investimento.  

---

## 🔮 Próximos Passos
- Implementar fallback para **reconhecimento de áudio e imagem** quando o base64 não for retornado.  
- Implementar handoff com corretor.
- Avaliar migração definitiva para a **WhatsApp Cloud API**. 