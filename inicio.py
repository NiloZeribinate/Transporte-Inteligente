import streamlit as st
st.set_page_config(
    page_title="Oi!",
    page_icon="👋",
)

st.write("# Bem vindo! 👋")

st.sidebar.success("Selecione por onde comecar")

st.markdown(
    """
    Isso é um projeto de extensão, cujo objetivo é analisar dados de transporte.
    **Insira seus arquivos .csv para iniciar a análise!**
    ### Tipos de Processos Disponíveis
    - Visualização(gráficos)
    - Separação em Arquivos Diferentes
    - Análise separada por modo de transporte, ou modo de pagamento, por hora, dia da semana
    -Conjugada ao calendário
"""
)