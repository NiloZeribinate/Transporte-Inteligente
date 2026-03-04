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
    st.Page("weekly-analysis.py", icon="📊", title="Análise Semanal e Diária"),
    st.Page("custom-analysis.py", icon="🧮", title="Análise Customizável"),
    st.Page("novosgraficos.py", title="Testes"),
    st.Page("input.py",title="Inserir Novos Arquivos")
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
            'dayfirst': True,
            'fullname': 'Bilhetagem Eletrônica'
        },
        'bu': {
            'dir': 'diario/org/',
            'pref': 'bu_',
            'dayfirst': True,
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