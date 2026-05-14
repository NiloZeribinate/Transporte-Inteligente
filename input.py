import streamlit as st
import numpy as np
import pandas as pd

input=st.file_uploader("Insira aqui a pasta com os arquivos que voce quer analisar", type="csv", accept_multiple_files="directory")
#file uploader retorna uma lista de objetos arquivos, mas nao salva informacao de diretorio
if input:
    for i in range(len(input)):
        st.session_state.arquivos[input[i].name]=input[i]  #crio um dict com todos os arquivos, so referir ao nome do arquivo agora para acha-lo

st.markdown(
    """
    O formato para a insercao de arquivos eh o seguinte\n
    **Insira o seu diretorio no formato indicado!**
    - Pode ser um grande diretorio ou 3 feitos separadamente, mas os nomes dos arquivos devem ser padronizados
    - Bilhetagem eletronica -->Prefixo 'be_', com o dia primeiro(dayfirst)
    - Bilhete Unico --> Prefixo 'bu_', com o dia primeiro(dayfirst)
    - Gratuidade --> refixo 'gt_', com o dayfirst=False
"""
) #manter padrao de nome de arquivo, em vez de padronizar diretorio

st.write("Arquivos carregados:")
st.write(list(st.session_state.arquivos.keys()))