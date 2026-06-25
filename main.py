import os
import yaml 
from bs4 import BeautifulSoup
import requests
from openai import OpenAI
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__)
client = OpenAI()

def call_ai(prompt_master):
    response = client.responses.create(
        model="gpt-5.5",
        input=prompt_master
    )
    return response.output_text

def read_yaml(place):
    with open(place, 'r', encoding='utf8') as file:
        data = yaml.safe_load(file)
        return data

directives_folder = './directives'

## interpretador
def interpreter_yaml(data):
    obj = {
        'site' : '',
        'selectors' : []
    }
    obj['site'] = data['target']
    obj['selectors'] = data['selectors']
    return obj

## agente
def agent_yaml(obj):
    site = requests.get(obj['site'], headers={'User-Agent': 'Mozilla/5.0'})
    soup = BeautifulSoup(site.text, 'html.parser')
    output = {}
    for i in obj['selectors']:
        output[f'{i}'] = f'{soup.select_one(i)}'
    return output

def ai_reader(data, pergunta):
    PROMPT = f'com base nos dados abaixo, responda a pergunta: {pergunta} com base nos dados abaixo: {data}'
    return call_ai(PROMPT)

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/targets')
def get_targets():
    arquivos = []

    for arquivo in os.listdir(directives_folder):
        if arquivo.endswith('.yaml') or arquivo.endswith('.yml'):
            arquivos.append(arquivo)

    return jsonify({'targets': arquivos})

@app.route('/get_ai_response')
def get_ai_response():
    pergunta = request.args.get('pergunta', '')
    target = request.args.get('target', 'teste.yaml')

    if pergunta == '':
        return jsonify({'erro': 'Digite uma pergunta.'}), 400

    if '/' in target or '\\' in target:
        return jsonify({'erro': 'Arquivo invalido.'}), 400

    place = os.path.join(directives_folder, target)

    if not os.path.exists(place):
        return jsonify({'erro': 'Arquivo nao encontrado.'}), 404

    dados = agent_yaml(interpreter_yaml(read_yaml(place)))
    resposta = ai_reader(dados, pergunta)

    return jsonify({'resposta': resposta})

if __name__ == '__main__':
    app.run(debug=True)

