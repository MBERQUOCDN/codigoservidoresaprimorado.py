import streamlit as st
from datetime import datetime
import json
import os
import math
import plotly.express as px

# Caminho para o arquivo JSON que armazenará os dados
FILE_PATH = "servidores.json"

# Função para carregar os servidores do arquivo JSON
def carregar_servidores():
    if os.path.exists(FILE_PATH):
        with open(FILE_PATH, "r") as file:
            dados = json.load(file)
            servidores = {nome: Servidor(**dados) for nome, dados in dados.items()}
            return servidores
    return {}

# Função para salvar servidores no arquivo JSON
def salvar_servidores():
    with open(FILE_PATH, "w") as file:
        json.dump({nome: vars(servidor) for nome, servidor in st.session_state['servidores_hash'].items()}, file)

# Classe para armazenar dados dos servidores
class Servidor:
    def __init__(self, nome, cargo, remuneracao, cidade, escolaridade, especialidade, 
                 taxa_absenteismo, avaliacao, data_inicio=None):
        self.nome = nome.upper()
        self.cargo = cargo.upper()
        self.remuneracao = remuneracao
        self.cidade = cidade.upper()
        self.escolaridade = escolaridade.upper()
        self.especialidade = especialidade.upper()
        self.taxa_absenteismo = taxa_absenteismo
        self.avaliacao = avaliacao
        self.data_inicio = data_inicio if data_inicio else datetime.now().isoformat()

    @property
    def tempo_servico(self):
        delta = datetime.now() - datetime.fromisoformat(self.data_inicio)
        return delta.days  # Retorna o tempo de serviço em dias

# Inicialização dos servidores na tabela hash usando st.session_state
if 'servidores_hash' not in st.session_state:
    st.session_state['servidores_hash'] = carregar_servidores()

# Função para adicionar um servidor
def adicionar_servidor_hash(nome, cargo, remuneracao, cidade, escolaridade, especialidade, 
                            taxa_absenteismo, avaliacao):
    if not nome:
        st.error("O nome do servidor é obrigatório.")
        return
    
    nome = nome.upper()
    cargo = cargo.upper()
    cidade = cidade.upper()

    novo_servidor = Servidor(
        nome=nome,
        cargo=cargo,
        remuneracao=remuneracao,
        cidade=cidade,
        escolaridade=escolaridade,
        especialidade=especialidade,
        taxa_absenteismo=taxa_absenteismo,
        avaliacao=avaliacao
    )

    st.session_state['servidores_hash'][nome] = novo_servidor
    salvar_servidores()  # Salva no arquivo JSON
    st.success(f"{nome} ({cargo}) adicionado com sucesso!")

# Função de ordenação Quicksort para nomes
def quicksort_nome(lista):
    if len(lista) <= 1:
        return lista
    pivo = lista[0]
    menores = [x for x in lista[1:] if x.nome <= pivo.nome]
    maiores = [x for x in lista[1:] if x.nome > pivo.nome]
    return quicksort_nome(menores) + [pivo] + quicksort_nome(maiores)

# Exibição dos servidores em ordem alfabética
def mostrar_servidores_alfabetica():
    ordenados = quicksort_nome(list(st.session_state['servidores_hash'].values()))
    st.write("### Servidores em ordem alfabética:")
    for s in ordenados:
        st.write(s.nome)

# Cálculo de distância para KNN
def calcular_distancia(s1, s2):
    return math.sqrt(
        (s1.taxa_absenteismo - s2.taxa_absenteismo) ** 2 +
        (s1.avaliacao - s2.avaliacao) ** 2 +
        (s1.remuneracao - s2.remuneracao) ** 2
    )

# Implementação do algoritmo KNN para servidores
def knn(k, servidor_alvo):
    distancias = [
        (calcular_distancia(servidor_alvo, servidor), servidor)
        for servidor in st.session_state['servidores_hash'].values() if servidor != servidor_alvo
    ]
    distancias.sort(key=lambda x: x[0])
    return [servidor for _, servidor in distancias[:k]]

# Exibe servidores mais próximos com base no KNN
def mostrar_servidores_similares(nome, k):
    nome = nome.upper()
    if nome in st.session_state['servidores_hash']:
        servidor_alvo = st.session_state['servidores_hash'][nome]
        similares = knn(k, servidor_alvo)
        st.write(f"{k} servidores mais próximos de {servidor_alvo.nome}:")
        for s in similares:
            st.write(f"{s.nome} - Avaliação: {s.avaliacao}/100 - Absenteísmo: {s.taxa_absenteismo}% - R${s.remuneracao:.2f}")
    else:
        st.error("Servidor não encontrado.")

# Gráfico de remuneração dos servidores
def mostrar_grafico_remuneracao():
    if st.session_state['servidores_hash']:
        nomes = [s.nome for s in st.session_state['servidores_hash'].values()]
        remuneracoes = [s.remuneracao for s in st.session_state['servidores_hash'].values()]
        fig = px.bar(x=nomes, y=remuneracoes, labels={'x':'Servidores', 'y':'Remuneração (R$)'})
        st.plotly_chart(fig)
    else:
        st.write("Nenhum servidor cadastrado para exibir.")

# Interface principal do aplicativo
def interface():
    st.title("Sistema de Gerenciamento de Servidores")

    menu = ["Adicionar servidor", "Mostrar servidores por ordem alfabética", 
            "Mostrar servidores mais similares (KNN)", "Gráfico de remuneração"]
    escolha = st.sidebar.selectbox("Menu", menu)

    if escolha == "Adicionar servidor":
        st.subheader("Adicionar novo servidor")
        nome = st.text_input("Nome")
        cargo = st.text_input("Cargo")
        cidade = st.text_input("Cidade")
        escolaridade = st.text_input("Escolaridade")
        especialidade = st.text_input("Especialidade")
        taxa_absenteismo = st.number_input("Taxa de absenteísmo (%)", 0.0, 100.0)
        avaliacao = st.slider("Avaliação de desempenho (0 a 100)", 0, 100)
        remuneracao = st.number_input("Remuneração (R$)", 0.0)

        if st.button("Adicionar"):
            adicionar_servidor_hash(nome, cargo, remuneracao, cidade, escolaridade, 
                                    especialidade, taxa_absenteismo, avaliacao)

    elif escolha == "Mostrar servidores por ordem alfabética":
        mostrar_servidores_alfabetica()

    elif escolha == "Mostrar servidores mais similares (KNN)":
        nome = st.text_input("Nome do servidor")
        k = st.number_input("Número de servidores similares (K)", min_value=1, value=3)
        if st.button("Mostrar servidores similares"):
            mostrar_servidores_similares(nome, k)

    elif escolha == "Gráfico de remuneração":
        mostrar_grafico_remuneracao()

if __name__ == "__main__":
    interface()
