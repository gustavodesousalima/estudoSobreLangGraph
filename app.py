# Para criar uma variável de ambiente, execute o seguinte comando no terminal: $env:OPENAI_API_KEY="valor"
# Verificar variáveis de ambiente: echo %NOME_DA_VARIAVEL%

import getpass
import os
from typing import Annotated, TypedDict, List
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
import openai

# Configuração da API
def set_api_key(var: str):
    if not os.environ.get(var):
        os.environ[var] = getpass.getpass(f"{var}: ")

set_api_key("OPENAI_API_KEY")

# Definição do estado
class State(TypedDict):
    messages: Annotated[List[add_messages], "List of messages"]

# Criação do StateGraph
graph_builder = StateGraph(State)

# Função do chatbot
def chatbot(state: State):
    # Atualize esta linha
    messages = [{"role": msg.get("role", ""), "content": msg.get("content", "")} for msg in state["messages"]]

    # Chamar a API do OpenAI
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )

    # Retornar a resposta do modelo
    return {"messages": [{"role": response.choices[0].message.get("role", ""), "content": response.choices[0].message.get("content", "")}]}


# Adicionando o nó do chatbot
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)

# Compilando o gráfico
graph = graph_builder.compile()

# Função para atualizar o gráfico
def stream_graph_updates(user_input: str):
    for event in graph.stream({"messages": [{"role": "user", "content": user_input}]}):
        for value in event.values():
            print("Assistant:", value["messages"][-1]["content"])

# Loop de interação com o usuário
while True:
    try:
        user_input = input("User: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break
        stream_graph_updates(user_input)
    except Exception as e:
        print("Error:", e)
        user_input = "What do you know about LangGraph?"
        print("User: " + user_input)
        stream_graph_updates(user_input)
        break