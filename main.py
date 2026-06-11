import yaml 
from bs4 import BeautifulSoup
import requests
from openai import OpenAI
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

place = './directives/teste.yaml'

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
    site = requests.get(obj['site'])
    soup = BeautifulSoup(site.text, 'html.parser')
    output = {}
    for i in obj['selectors']:
        output[f'{i}'] = f'{soup.find(i)}'
    return output

def ai_reader(data, pergunta):
    PROMPT = f'com base nos dados abaixo, responda a pergunta: {pergunta} com base nos dados abaixo: {data}'
    return call_ai(PROMPT)

dados = (agent_yaml(interpreter_yaml(read_yaml(place))))
pergunta = input('Digite sua pergunta: ')
print(ai_reader(dados, pergunta))

