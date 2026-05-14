import streamlit as st
import pandas as pd
import datetime

from processing import *
from visuals import *

def daily_change():
    merge = None

    selected_date = st.session_state['selected_date']
    
    dfs = get_dfs(selected_date)
    daily_chart_data = get_hourly_groups(dfs, selected_date)
    merge = merge_hourly_date(daily_chart_data)
    
    st.session_state['hourly_df'] = merge


init_variable('last_sunday_weekly', None)
init_variable('last_sunday_subsidy', None)


def weekly_change():
    selected_date = st.session_state['selected_date']
    
    last_sunday = selected_date - datetime.timedelta( selected_date.weekday() + 1 )
    
    if last_sunday == st.session_state['last_sunday_weekly']:
        return
    else:
        st.session_state['last_sunday_weekly'] = last_sunday

    data = get_transaction_counts_in_range(last_sunday, 7)

    data['Média'] = [1300000, 3200000, 3300000, 2900000, 2800000, 2600000, 1300000]
    
    st.session_state['weekly_df'] = data


def subsidy_change():
    selected_date = st.session_state['selected_date']
    

    last_sunday = selected_date - datetime.timedelta( selected_date.weekday() + 1 )
    
    if last_sunday == st.session_state['last_sunday_subsidy']:
        return
    else:
        st.session_state['last_sunday_subsidy'] = last_sunday

    df_sub   = get_columns_sum_in_range(selected_date, 7, 'Vl Subsídio')
    df_trans = get_columns_sum_in_range(selected_date, 7, 'Vl Trans')

    st.session_state['subsidy_df'] = df_sub
    st.session_state['trans_df']   = df_trans


def change():
    daily_change()
    weekly_change()
    subsidy_change()



init_variable('selected_date', datetime.date(2025, 8, 5))

with st.container():
    st.title('Analise Semanal e Diaria')

    selected_week_day = st.date_input(
        'Selecione um dia da semana que deseja analisar',
        min_value = datetime.date(2025, 4, 1),
        max_value = datetime.datetime.today(),
        on_change = change,
        key = 'selected_date'
    )


# ===================================== DAILY =====================================

with st.container():
    st.header("Balanço Diário")
    
    load_functions('hourly_df', daily_change)
    
    df = st.session_state['hourly_df']

    hourly_chart(df)

    st.divider()
    st.header("Análise por Linha Específica")
    
    # Pegamos os DataFrames do dia selecionado
    current_dfs = get_dfs(st.session_state['selected_date'])
    lista_linhas = get_unique_lines(current_dfs)
    
    if lista_linhas:
        selected_line = st.selectbox("Selecione a Linha para análise:", options=lista_linhas)
        
        # Processa os dados filtrados
        df_line_stats = get_filtered_hourly_data(current_dfs, selected_line)
        
        # Exibe os gráficos
        line_analysis_charts(df_line_stats, selected_line)
    else:
        st.info("Nenhuma linha encontrada para a data selecionada.")

st.divider() # -------------------------

# ===================================== WEEKLY =====================================

with st.container():
    st.header('Balanço da Semana')

    load_functions('weekly_df', weekly_change)
    
    df = st.session_state['weekly_df']

    daily_count_chart(df)

st.divider() # -------------------------

# ===================================== SUBSIDY =====================================


with st.container():
    st.header('Pagamento de subsídio na semana')

    load_functions(['trans_df', 'subsidy_df'], subsidy_change)

    trans_df = st.session_state['trans_df']
    subsidy_df = st.session_state['subsidy_df']

    subsidy_charts(trans_df, subsidy_df)

