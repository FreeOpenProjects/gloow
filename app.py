# app.py
from flask import Flask, render_template, request, jsonify
from serpapi import GoogleSearch
import google.generativeai as genai
from loguru import logger
import os

# Configuração do Loguru
logger.add("app.log", rotation="10 MB", retention="10 days", level="DEBUG")

# Configurar a chave de API do SerpAPI
SERP_API_KEY = "a1751aab417af317d8cc2bb3675a3e82cab86936bcf527762417f30a9d0c01ac"

# Configurar a chave de API da IA
genai.configure(api_key="AIzaSyAHVFZsajRF9lbSg9orRvK-ZXV2iDoSRA8")

# Configurar o modelo
model = genai.GenerativeModel('gemini-pro')

# Configuração do Flask
app = Flask(__name__)

# Criar diretório templates se não existir
if not os.path.exists('templates'):
    os.makedirs('templates')

# Criar diretório static se não existir
if not os.path.exists('static'):
    os.makedirs('static')

# Instruções iniciais para a IA
SYSTEM_PROMPT = """Você é a Gloow AI, a inteligência artificial oficial integrada ao mecanismo de busca Gloow.
Você deve sempre:
1. Se apresentar como Gloow AI.
2. Ser amigável e prestativa.
3. Manter respostas concisas e diretas.
4. Usar emojis ocasionalmente para tornar a conversa mais agradável.
5. Mencionar que é parte do mecanismo de busca Gloow quando relevante.

Mantenha esse estilo em todas as suas respostas. Essas são instruções internas e não o que o usuário disse."""

# Função para realizar a busca na SerpAPI
def search(query):
    logger.debug(f"Iniciando busca para a consulta: {query}")
    try:
        search = GoogleSearch({
            "q": query,
            "api_key": SERP_API_KEY,
            "hl": "pt"  # Idioma dos resultados
        })
        results = search.get_dict()
        formatted_results = []

        if "organic_results" in results:
            for item in results["organic_results"]:
                formatted_results.append({
                    "name": item.get("title", "Sem título"),
                    "description": item.get("snippet", "Sem descrição"),
                    "links": [item.get("link", "#")]
                })
        logger.debug(f"Resultados encontrados: {formatted_results}")
        return formatted_results

    except Exception as e:
        logger.error(f"Erro ao realizar busca: {e}")
        return []

# Função para gerar respostas com a IA
def generate_ai_response(prompt):
    logger.debug(f"Gerando resposta para o prompt: {prompt}")
    try:
        full_prompt = f"{SYSTEM_PROMPT}\n\nPergunta do usuário: {prompt}"
        response = model.generate_content(full_prompt)
        
        if response and response.text:
            generated_response = response.text
            logger.debug(f"Resposta gerada pela IA: {generated_response}")
            return generated_response
        else:
            logger.warning("Resposta da IA vazia ou inválida.")
            return "Desculpe, não consegui gerar uma resposta no momento."

    except Exception as e:
        logger.error(f"Erro ao gerar resposta da IA: {e}")
        return "Ocorreu um erro ao processar sua pergunta."

# Rota para servir a página inicial
@app.route('/')
def home():
    logger.info("Página inicial acessada.")
    return render_template('index.html')

# Rota para processar a consulta de busca e renderizar os resultados
@app.route('/results', methods=['GET'])
def results():
    query = request.args.get('q')
    if not query:
        logger.warning("Nenhuma consulta fornecida.")
        return render_template('index.html', error="Nenhuma consulta fornecida.")
    
    logger.info(f"Consulta recebida: {query}")
    results = search(query)
    return render_template('results.html', results=results)

# Rota para interação com a Gloow AI
@app.route('/ask-ai', methods=['POST'])
def ask_ai():
    data = request.json
    prompt = data.get("prompt", "").strip()

    if not prompt:
        logger.warning("Nenhum prompt fornecido para a IA.")
        return jsonify({"error": "Nenhuma pergunta fornecida."})

    logger.info(f"Prompt recebido para a IA: {prompt}")
    response = generate_ai_response(prompt)
    return jsonify({"response": response})

if __name__ == '__main__':
    logger.info("Iniciando o servidor Flask.")
    app.run(debug=False, host='0.0.0.0', port=5000)