import streamlit as st
import pandas as pd
import datetime

from processing import *
from visuals import *

# ===================================== WEEKLY =====================================

init_variable("weekly_df", None)
init_variable("weekly_date", datetime.date(2025, 8, 5))

if 'weekly_df' not in st.session_state:
    st.session_state['weekly_df'] = None

def weekly_change():
    selected_date = st.session_state['weekly_date']
    
    last_sunday = selected_date - datetime.timedelta( selected_date.weekday() + 1 )
    
    data = get_transaction_counts_in_range(last_sunday, 7)

    data['Média'] = [1300000, 3200000, 3300000, 2900000, 2800000, 2600000, 1300000]
    
    st.session_state['weekly_df'] = data

if st.session_state['weekly_df'] is None:
    weekly_change()


with st.container():
    st.header("Balanço Semanal")
    
    selected_week_day = st.date_input(
        "Selecione um dia da semana que deseja analisar",
        min_value = datetime.date(2025, 4, 1),
        max_value = datetime.datetime.today(),
        on_change = weekly_change,
        key='weekly_date'
    )
    
    df = st.session_state['weekly_df']

    daily_count_chart(df)


# ===================================== SUBSIDY =====================================



st.divider() # -------------------------

init_variable("subsidy_date", (datetime.date(2025, 8, 5), datetime.date(2025, 8, 7)))

def subsidy_change():
    inputs = st.session_state['subsidy_date']
    
    start_date = end_date = None
    
    try:
        (start_date, end_date) = inputs
    except:
        return
    
    quant_days = (end_date - start_date).days + 1

    df_sub   = get_columns_sum_in_range(start_date, quant_days, 'Vl Subsídio')
    df_trans = get_columns_sum_in_range(start_date, quant_days, 'Vl Trans')
    
    st.session_state['subsidy_df'] = df_sub
    st.session_state['trans_df']   = df_trans



if ('trans_df' or 'subsidy_df') not in st.session_state:
    subsidy_change()


trans_df = st.session_state['trans_df']
subsidy_df = st.session_state['subsidy_df']

with st.container():
    st.header('Pagamento de subsídio no período')

    st.date_input(
        "Selecione um dia da semana que deseja analisar",
        min_value = datetime.date(2025, 5, 1),
        max_value = datetime.datetime.today(),
        key = 'subsidy_date',
        on_change = subsidy_change
    )

    subsidy_charts(trans_df, subsidy_df)



# ===================================== DAILY =====================================

st.divider() # -------------------------

init_variable("hourly_df", None)
init_variable("daily_date", datetime.date(2025, 8, 1))

def daily_change():
    merge = None

    selected_date = st.session_state['daily_date']
    
    dfs = get_dfs(selected_date)
    daily_chart_data = get_hourly_groups(dfs, selected_date)
    merge = merge_hourly_date(daily_chart_data)
    
    st.session_state['hourly_df'] = merge


if st.session_state['hourly_df'] is None:
    daily_change()


with st.container():
    st.header("Balanço Diário")

    selected_date = st.date_input(
        "Selecione o dia que deseja analisar",
        min_value = datetime.date(2025, 5, 1),
        max_value = datetime.datetime.today(),
        on_change = daily_change,
        key='daily_date'
    )
    
    df = st.session_state['hourly_df']

    hourly_chart(df)

