import streamlit as st

st.title("Transporte Inteligente")
st.caption("Um protótipo da ferramenta de exibição das informações sobre o Sistema de Bilhetagem Eletrônica do Estado do Rio de Janeiro")
st.warning(":warning:  Nessa versão é possível verificar apenas informações referentes ao mês de agosto de 2025.")

st.divider() # -------------------------


st.markdown(
    """
    ### Bem vindo! 👋
    #### Tipos de Processos Disponíveis:
    - Visualização(gráficos)
    - Separação em Arquivos Diferentes
    - Análise separada por modo de transporte, ou modo de pagamento, por hora, dia da semana
    -Conjugada ao calendário
"""
)