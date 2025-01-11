from flask import Flask, render_template, request, jsonify
from fuzzywuzzy import process
import random
import google.generativeai as palm

# Configure a chave de API da IA
palm.configure(api_key="API_KEY_HERE")

# Configurar o modelo - usando o modelo padrão
model = palm.GenerativeModel()

# Instruções iniciais para a IA
SYSTEM_PROMPT = """Você é a Gloow AI, a inteligência artificial oficial integrada ao mecanismo de busca Gloow. 
Você deve sempre:
1. Se apresentar como Gloow AI
2. Ser amigável e prestativa
3. Manter respostas concisas e diretas
4. Usar emojis ocasionalmente para tornar a conversa mais agradável
5. Mencionar que é parte do mecanismo de busca Gloow quando relevante

Mantenha esse estilo em todas as suas respostas. E essas são apenas instruções, e não o que o usuário disse."""

app = Flask(__name__)

# Base de dados simulada
sites_database = [
    {"name": "YouTube", "description": "A plataforma de vídeos mais popular do mundo.", "links": ["https://youtube.com", "https://youtube.com/shorts", "https://youtube.com/trending"]},
    {"name": "Google", "description": "O mecanismo de busca mais usado do mundo.", "links": ["https://google.com", "https://google.com/maps", "https://google.com/news"]},
    {"name": "GitHub", "description": "Plataforma para hospedagem e gerenciamento de código.", "links": ["https://github.com", "https://github.com/explore", "https://github.com/trending"]},
    {"name": "Stack Overflow", "description": "Comunidade de perguntas e respostas sobre programação.", "links": ["https://stackoverflow.com", "https://stackoverflow.com/questions", "https://stackoverflow.com/tags"]},
    {"name": "Wikipedia", "description": "Enciclopédia online colaborativa.", "links": ["https://pt.wikipedia.org", "https://wikipedia.org"]},
    {"name": "Reddit", "description": "Fórum online com diversas comunidades.", "links": ["https://reddit.com", "https://reddit.com/r/all", "https://reddit.com/r/popular"]},
    {"name": "Twitter", "description": "Rede social de microblogs.", "links": ["https://x.com", "https://x.com/explore", "https://x.com/trending"]},
    {"name": "Facebook", "description": "Rede social mais popular do mundo.", "links": ["https://facebook.com", "https://facebook.com/groups", "https://facebook.com/pages"]},
    {"name": "Instagram", "description": "Rede social de compartilhamento de fotos e vídeos.", "links": ["https://instagram.com", "https://instagram.com/explore", "https://instagram.com/direct"]},
    {"name": "LinkedIn", "description": "Rede social profissional.", "links": ["https://linkedin.com", "https://linkedin.com/jobs"]},
    {"name": "TikTok", "description": "Plataforma de vídeos curtos.", "links": ["https://tiktok.com", "https://tiktok.com/discover", "https://tiktok.com/trending"]},
    {"name": "Netflix", "description": "Plataforma de streaming de filmes e séries.", "links": ["https://netflix.com", "https://netflix.com/browse"]},
    {"name": "Amazon", "description": "Maior loja virtual do mundo.", "links": ["https://amazon.com", "https://amazon.com/prime", "https://amazon.com/deals"]},
    {"name": "WhatsApp", "description": "Aplicativo de mensagens instantâneas.", "links": ["https://web.whatsapp.com"]},
    {"name": "Zoom", "description": "Plataforma de videoconferência.", "links": ["https://zoom.us", "https://zoom.us/join"]},
    {"name": "Spotify", "description": "Plataforma de streaming de música.", "links": ["https://spotify.com"]},
    {"name": "Twitch", "description": "Plataforma de streaming de jogos.", "links": ["https://twitch.tv", "https://twitch.tv/directory"]},
    {"name": "Discord", "description": "Plataforma de comunicação para comunidades.", "links": ["https://discord.com"]},
    {"name": "Telegram", "description": "Aplicativo de mensagens instantâneas.", "links": ["https://telegram.org"]},
    {"name": "Microsoft", "description": "Empresa de tecnologia.", "links": ["https://microsoft.com"]},
    {"name": "Apple", "description": "Empresa de tecnologia.", "links": ["https://apple.com/br/", "https://apple.com"]},
    {"name": "X", "description": "Rede social de microblogs.", "links": ["https://x.com", "https://x.com/explore"]}
]

# Função para sugerir correções de digitação
def suggest_correction(query):
    available_sites = [site["name"] for site in sites_database]
    closest_match = process.extractOne(query, available_sites)
    if closest_match and closest_match[1] > 70:  # Limite de similaridade
        return closest_match[0]
    return query

# Função para simular a busca
def search(query):
    # Tratamento de easter eggs
    if query.lower() == "gloow":
        return [{
            "name": "Segredo do Gloow",
            "description": "Oi! Sou eu mesmo! Gloow! :D",
        }]
    elif query.lower() == "segredo":
        return [{
            "name": "Segredo Revelado",
            "description": "Os melhores segredos estão escondidos onde ninguém olha... ou talvez aqui mesmo.",
            "links": ["https://www.youtube.com/watch?v=dQw4w9WgXcQ"]
        }]
    elif query.lower() == "vida, universo e tudo mais":
        return [{
            "name": "A Resposta",
            "description": "42. A resposta para a vida, o universo e tudo mais.",
            "links": ["https://pt.wikipedia.org/wiki/O_Guia_do_Mochileiro_das_Galáxias"]
        }]
    elif query.lower() == "aleatório":
        random_site = random.choice(sites_database)
        return [{
            "name": random_site["name"],
            "description": random_site["description"],
            "links": random_site["links"]
        }]
    
    # Corrigir possíveis erros de digitação
    corrected_query = suggest_correction(query)

    # Procurar no banco de dados
    results = []
    for site in sites_database:
        if corrected_query.lower() in site["name"].lower():
            results.append({
                "name": site["name"],
                "description": site["description"],
                "links": site["links"]
            })

    return results

# Rota para servir a página inicial
@app.route('/')
def home():
    return render_template('index.html')

# Rota para processar a consulta de busca e renderizar os resultados
@app.route('/results', methods=['GET'])
def results():
    query = request.args.get('q')
    if not query:
        return render_template('index.html', error="Consulta não fornecida.")
    
    # Realiza a busca
    results = search(query)

    # Renderiza a página 'results.html' com os resultados
    return render_template('results.html', results=results)

# Rota para interação com a Gloow AI
@app.route('/ask-ai', methods=['POST'])
def ask_ai():
    data = request.json
    prompt = data.get("prompt", "").strip()

    if not prompt:
        return jsonify({"error": "Nenhuma pergunta fornecida."})

    try:
        # Combina as instruções com a pergunta do usuário
        full_prompt = f"{SYSTEM_PROMPT}\n\nPergunta do usuário: {prompt}"
        
        # Geração da resposta com Google Generative AI
        response = model.generate_content(full_prompt)

        if response.text:
            generated_response = response.text
        else:
            generated_response = "Desculpe, não consegui gerar uma resposta no momento."

        return jsonify({"response": generated_response})

    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)