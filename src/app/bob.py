from flask import Blueprint, request, jsonify
import os
import datetime
import urllib.parse
import locale
import requests

from src.app.comandos_respostas import (
    PALAVRA_ATIVACAO,
    LISTA_HORAS,
    LISTA_DATA,
    LISTA_LEMBRETE,
    LISTA_LER_LEMBRETES,
    LISTA_EXCLUIR_LEMBRETES,
    LISTA_PESQUISA,
    LISTA_SAIR,
    LISTA_TOCAR_MUSICA,
)

ITUNES_API_URL = "https://itunes.apple.com/search"

bob_bp = Blueprint('bob', __name__)
ARQUIVO_LEMBRETES = os.path.join(os.path.dirname(__file__), 'lembretes.txt')
if not os.path.isfile(ARQUIVO_LEMBRETES):
    open(ARQUIVO_LEMBRETES, "w", encoding="utf-8").close()

try:
    locale.setlocale(locale.LC_TIME, "pt_BR.UTF-8")
    locale_configurado = True
except locale.Error:
    locale_configurado = False
    meses_manual = {1:"janeiro",2:"fevereiro",3:"março",4:"abril",5:"maio",6:"junho",7:"julho",8:"agosto",9:"setembro",10:"outubro",11:"novembro",12:"dezembro"}
    dias_semana_manual = {0:"segunda-feira",1:"terça-feira",2:"quarta-feira",3:"quinta-feira",4:"sexta-feira",5:"sábado",6:"domingo"}

def gravar_lembrete(texto_lembrete: str) -> str:
    try:
        with open(ARQUIVO_LEMBRETES, "a+", encoding="utf-8") as f:
            f.write(f" {texto_lembrete}\n")
        return f"Ok, lembrete salvo: {texto_lembrete}"
    except:
        return "Desculpe, não consegui salvar o lembrete."

def ler_todos_lembretes():
    try:
        with open(ARQUIVO_LEMBRETES, "r", encoding="utf-8") as f:
            return [l.strip() for l in f.readlines()]
    except:
        return []

def excluir_lembrete(parte_texto: str) -> str:
    try:
        with open(ARQUIVO_LEMBRETES, "r", encoding="utf-8") as f:
            linhas = f.readlines()
        novas = [l for l in linhas if parte_texto.lower() not in l.lower()]
        if len(novas) == len(linhas):
            return f"Nenhum lembrete encontrado contendo: '{parte_texto}'"
        with open(ARQUIVO_LEMBRETES, "w", encoding="utf-8") as f:
            f.writelines(novas)
        return f"Lembrete(s) contendo '{parte_texto}' foram excluídos."
    except:
        return "Houve um erro ao tentar excluir o lembrete."

def obter_data_hora_texto() -> str:
    agora = datetime.datetime.now()
    h, m = int(agora.strftime("%H")), int(agora.strftime("%M"))
    part_hora = (f"Agora {'é' if h==1 else 'são'} {h} hora{'s' if h!=1 else ''}"
                 f" e {m} minuto{'s' if m!=1 else ''}.")
    dia, ano = agora.strftime("%d"), agora.strftime("%Y")
    if locale_configurado:
        mes = agora.strftime("%B").capitalize()
        dia_semana = agora.strftime("%A").capitalize()
    else:
        mes = meses_manual[int(agora.strftime("%m"))]
        dia_semana = dias_semana_manual[agora.weekday()]
    part_data = f"Hoje é {dia_semana}, dia {dia} de {mes} de {ano}."
    return f"{part_hora} {part_data}"

def obter_resposta_ia(pergunta, max_tokens=150, temperature=0.7, top_p=0.9):
    headers = {"Authorization": f"Bearer {os.getenv('MISTRAL_API_KEY')}", "Content-Type":"application/json"}
    payload = {
        "model":"mistral-medium",
        "messages":[{"role":"system","content":"Você é o Bob, um assistente educado e objetivo."},
                    {"role":"user","content":pergunta}],
        "max_tokens":max_tokens,"temperature":temperature,"top_p":top_p
    }
    try:
        resp = requests.post("https://api.mistral.ai/v1/chat/completions", json=payload, headers=headers)
        resp.raise_for_status()
        return resp.json()['choices'][0]['message']['content'].strip()
    except:
        return "Desculpe, não consegui responder no momento."

def processar_comando(comando: str):
    cmd = comando.strip().lower()
    tipo, dados = 'texto', {}

    if any(f in cmd for f in LISTA_HORAS + LISTA_DATA):
        resposta = obter_data_hora_texto()

    elif any(f in cmd for f in LISTA_LER_LEMBRETES):
        lembs = ler_todos_lembretes()
        if lembs:
            resposta = f"Você tem {len(lembs)} lembrete(s)."
            tipo = 'lembretes'
            dados['lembretes'] = lembs
        else:
            resposta = "Você não tem nenhum lembrete salvo."

    elif any(cmd.startswith(p) for p in LISTA_LEMBRETE):
        txt = next((cmd[len(p):].strip() for p in LISTA_LEMBRETE if cmd.startswith(p)), "")
        resposta = gravar_lembrete(txt) if txt else "Diga 'lembrete de' e o conteúdo."

    elif any(f in cmd for f in LISTA_EXCLUIR_LEMBRETES):
        trecho = next((cmd.split(f,1)[1].strip() for f in LISTA_EXCLUIR_LEMBRETES if f in cmd), "")
        resposta = excluir_lembrete(trecho) if trecho else "Diga 'excluir lembrete' seguido do trecho."

    elif any(f in cmd for f in LISTA_PESQUISA):
        termo = next((cmd.split(p,1)[1].strip() for p in LISTA_PESQUISA if p in cmd), "")
        if termo:
            tipo, resposta, dados['url'] = 'pesquisa', f"Pesquisando por {termo} no Google.", f"https://www.google.com/search?q={urllib.parse.quote_plus(termo)}"
        else:
            resposta = "Diga 'pesquisar por' seguido do termo."

    elif any(f in cmd for f in LISTA_SAIR):
        resposta = "Até logo!"

    elif any(f in cmd for f in LISTA_TOCAR_MUSICA):
        termo = next((cmd.split(p,1)[1].strip() for p in LISTA_TOCAR_MUSICA if p in cmd), "")
        if termo:
            resp = requests.get(ITUNES_API_URL, params={"term": termo, "media": "music", "limit": 1})
            resultados = resp.json().get("results", [])
            if resultados:
                faixa = resultados[0]
                tipo = 'musica'
                resposta = f'Tocando "{faixa["trackName"]}" de {faixa["artistName"]}.'
                dados = {"preview_url": faixa["previewUrl"]}
            else:
                resposta = f"Não encontrei nenhuma música para '{termo}'."
        else:
            resposta = "Diga 'tocar música <nome>' para eu tocar."

    else:
        resposta = obter_resposta_ia(comando)

    return {'resposta': resposta, 'tipo': tipo, 'dados': dados}

@bob_bp.route('/comando', methods=['POST'])
def receber_comando():
    cmd = request.json.get('comando', '').strip()
    if not cmd:
        return jsonify({'erro': 'Comando não fornecido'}), 400
    return jsonify(processar_comando(cmd))

@bob_bp.route('/lembretes', methods=['GET'])
def get_lembretes():
    return jsonify({'lembretes': ler_todos_lembretes()})

@bob_bp.route('/lembretes', methods=['DELETE'])
def del_lembrete():
    trecho = request.json.get('trecho', '').strip()
    if not trecho:
        return jsonify({'erro': 'Trecho do lembrete não fornecido'}), 400
    return jsonify({'mensagem': excluir_lembrete(trecho)})

@bob_bp.route('/hora', methods=['GET'])
def rota_hora():
    return jsonify({'resposta': obter_data_hora_texto()})

@bob_bp.route('/boasvindas', methods=['GET'])
def boasvindas():
    return jsonify({'resposta': 'Olá! Eu sou o Bob. Como posso ajudar você hoje?', 'tipo': 'texto', 'dados': {}})
