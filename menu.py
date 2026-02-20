import streamlit as st
import pandas as pd
import datetime

st.set_page_config(
    page_title="Transporte Inteligente",
    page_icon=":bus:",
    layout="wide",
)
arquivos = st.Page("input.py", title="Insercao de Arquivos")
amostra = st.Page("processamento.py", title="Analise de Dados")
menu = st.Page("inicio.py", title="Menu")
user= st.Page("novosgraficos.py", title="Customizacao de Graficos")
pg = st.navigation([menu,amostra,arquivos,user])


if 'weekly_df' not in st.session_state:
    st.session_state['weekly_df'] = None

if 'weekly_date' not in st.session_state:
    st.session_state['weekly_date'] = datetime.date(2025, 8, 5)

if 'arquivos' not in st.session_state:
    st.session_state.arquivos={}

if 'bases' not in st.session_state :
    st.session_state.bases={
        'be': {
            'dir': './org-BE/',
            'pref': 'be_',
            'dayfirst': True,
            'fullname': 'Bilhetagem Eletrônica'
        },
        'bu': {
            'dir': './diario/org/',
            'pref': 'bu_',
            'dayfirst': True,
            'fullname': 'Bilhete Único'
        },
        'gt': {
            'dir': './GT/',
            'pref': 'gt_',
            'dayfirst': False,
            'fullname': 'Gratuidade'
        },
    }

def get_dfs(selected_date): #mesma funcao de pegar dataframe de antes, so que adaptada pra qualquer diretorio
    data = {}
    
    for key in st.session_state.bases:
        filename = (
            st.session_state.bases[key]['pref']
            + f'{selected_date.year}-{selected_date.month:02d}-{selected_date.day:02d}.csv'
        )
        
        try:
            data[key] = pd.read_csv(st.session_state.arquivos[filename], sep=';', dayfirst = st.session_state.bases[key]['dayfirst'], parse_dates=['Data da Transação', 'Data do Processamento'])
        except Exception as e:
            print(e)
            data[key] = None
    return data

pg.run()