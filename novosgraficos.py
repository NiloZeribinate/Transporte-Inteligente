import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt 
import datetime

st.markdown(
    """
    Agora, cabe a você selecionar o que você quer ver
"""
)

modos_transporte = st.multiselect(
    "Quantos modos de transporte selecionar",
    ["Onibus", "Barca", "Metrô", "Van"],
)

tipo_grafico = st.radio(
    "Escolher o tipo de gráfico",
    ["Histograma", "Linha", "Área","Tabela de Torta"],
)
tipo_temp = st.radio(
    "Escolha o tipo intervalo de tempo",
    ["Por hora", "Por dia", "Por semana","Mes", "Ano"],
)
intervalo_tempo = st.date_input(
        "Selecione o intervalo que voce quer analisar",
        (datetime.date(2025, 5, 1),datetime.datetime.today()),
        min_value = datetime.date(2025, 5, 1),
        max_value = datetime.datetime.today(),
        key='intervalo_tempo'
    ) #retorna um intervalo de tempo escolhido pelo usuario, depois sera usado para criar o dataframe
formas_ingresso = st.multiselect(
    "Quais modalidades de ingresso voce quer incluir?",
    ["Bilhete Unico", "Gratuidade", "Bilhetagem Eletronica"],
)

for i in range(len(formas_ingresso)):
    color = st.color_picker("Escolha uma cor para "+formas_ingresso[i], "#00f900")

st.divider() # -------------------------


modos_formatado=""
for i in modos_transporte:
    modos_formatado+=i
    modos_formatado+=", "
modos_formatado=modos_formatado[:-2]


ingressos_form=""
for i in formas_ingresso:
    ingressos_form+=i
    ingressos_form+=", "
ingressos_form=ingressos_form[:-2]

st.markdown(
    f"""
    ### Elementos Escolhidos
    - {modos_formatado}
    - {tipo_grafico}
    - {intervalo_tempo}
    - {ingressos_form}
"""
    
)