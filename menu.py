import streamlit as st
import pandas as pd
import datetime

st.set_page_config(
    page_title="Transporte Inteligente",
    page_icon=":bus:",
    layout="wide",
)

pg = st.navigation([
    st.Page("inicio.py", icon="👋", title="Introdução"),
    st.Page("processamento.py", title="Analise de Dados"),
    st.Page("input.py", title="Insercao de Arquivos"),
    st.Page("novosgraficos.py", title="Customizacao de Graficos"),
    st.Page("main.py", title="Main")
])


if 'teste' not in st.session_state:
    st.session_state.teste = "Salvo!"

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

pg.run()