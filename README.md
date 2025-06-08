# Interface Web para o Assistente Bob

Este projeto implementa uma interface web em Flask para o assistente virtual Bob, permitindo interação através de um navegador.

## Funcionalidades

- Consulta de data e hora
- Criação e gerenciamento de lembretes
- Pesquisa no Google
- Interface responsiva e amigável

## Requisitos

- Python 3.11 ou superior
- Flask
- Flask-CORS
- pyttsx3
- SpeechRecognition

## Instalação

1. Clone este repositório
2. Crie um ambiente virtual:
   ```
   python -m venv venv
   ```
3. Ative o ambiente virtual:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`
4. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```

## Executando o projeto

1. Ative o ambiente virtual (se ainda não estiver ativado)
2. Execute o servidor Flask:
   ```
   python src/main.py
   ```
3. Acesse a interface web em `http://localhost:5000`

## Comandos disponíveis

- **Hora e data:** "que horas são", "que dia é hoje"
- **Lembretes:** "lembrete de [sua anotação]"
- **Ver lembretes:** "ler lembretes", "mostrar lembretes"
- **Pesquisar:** "pesquisar por [termo]"
- **Sair:** "sair", "tchau"

## Estrutura do projeto

- `src/main.py`: Arquivo principal do Flask
- `src/routes/bob.py`: Rotas da API para o assistente Bob
- `src/comandos_respostas.py`: Definições de comandos e respostas
- `src/static/`: Arquivos estáticos (HTML, CSS, JavaScript)
- `src/lembretes.txt`: Arquivo para armazenamento de lembretes

## Reconhecimento de voz

A interface web suporta reconhecimento de voz nos navegadores compatíveis com a API Web Speech. Clique no ícone do microfone para ativar o reconhecimento de voz.

