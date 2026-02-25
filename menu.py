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
            'dir': 'org-BE/',
            'pref': 'be_',
            'dayfirst': False,
            'fullname': 'Bilhetagem Eletrônica'
        },
        'bu': {
            'dir': 'diario/org/',
            'pref': 'bu_',
            'dayfirst': False,
            'fullname': 'Bilhete Único'
        },
        'gt': {
            'dir': 'GT/',
            'pref': 'gt_',
            'dayfirst': False,
            'fullname': 'Gratuidade'
        },
    }


st.write("Arquivos carregados:")
st.write(list(st.session_state.arquivos.keys()))


pg.run()