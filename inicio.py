import streamlit as st

st.write("# Bem vindo! 👋")

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

st.divider() # -------------------------

'''
### Pontos de Melhoria da Disposição dos Dados

1. Separação das informações pela Data da Transação
2. Padronização dos arquivos
3. Clareza sobre as informações
'''