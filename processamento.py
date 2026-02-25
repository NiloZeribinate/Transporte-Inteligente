import streamlit as st
import pandas as pd
import datetime

def encontrar_arquivo(nome_final):
    for nome_real in st.session_state.arquivos:
        if nome_real.endswith(nome_final):
            return st.session_state.arquivos[nome_real]
    return None

def get_dfs(selected_date): #mesma funcao de pegar dataframe de antes, so que adaptada pra qualquer diretorio
    st.write("get_dfs FOI CHAMADA")
    data = {}
    
    for key in st.session_state.bases:
        nome_final = (
            st.session_state.bases[key]['pref']
            + f'{selected_date.year}-{selected_date.month:02d}-{selected_date.day:02d}.csv'
        )

        file = encontrar_arquivo(nome_final)
        st.write("Procurando:", nome_final)
        st.write("Arquivos disponíveis:", list(st.session_state.arquivos.keys()))
        if file is not None:
            data[key] = pd.read_csv(
                file,
                sep=';',
                dayfirst=st.session_state.bases[key]['dayfirst'],
                parse_dates=['Data da Transação', 'Data do Processamento']
            )
        else:
            print("Nao encontrado:", nome_final)
            data[key] = None
    
    return data


st.title("Transporte Inteligente")
st.caption("Um protótipo da ferramenta de exibição das informações sobre o Sistema de Bilhetagem Eletrônica do Estado do Rio de Janeiro")


st.warning(":warning:  Nessa versão é possível verificar apenas informações referentes ao mês de agosto de 2025.")



st.divider() # -------------------------



if st.button("TESTAR GET DFS"):
    get_dfs(datetime.date(2025,8,1))

def get_quant(selected_date):
    data = {}
    dfs = get_dfs(selected_date)
    # st.write("DFS recebidos:", {k: type(v) for k,v in dfs.items()})
    for i in dfs:
        try:
            data[i] = dfs[i]['Linha'].count()
        except:
            data[i] = None
            # st.write("Erro")
    
    return data #retorna um dict com a contagem de 'Linha' de cada df na lista de dataframes em certa data?
    
def get_week_count(selected_sunday):
    data = {}
    
    for i in st.session_state.bases:
        data[ st.session_state.bases[i]['fullname'] ] = [None] * 7 #inicia 7 campos vazios
        
    for j in range(7):
        quant = get_quant(selected_sunday + datetime.timedelta(j)) #faz isso para cada dia da semana
        
        for i in quant:
            data[ st.session_state.bases[i]['fullname'] ][j] = quant[i] #preenche os 7 campos vazios com cada quantidade de cada dia da semana preenchidos em quant
    if data is None:
        st.write("Weekcount deu ruim")
    return data #retorna um dict de contagem de 'Linha' dado um certo dia da semana(separa em 7 dias)


def weekly_change():
    selected_date = st.session_state['weekly_date']
    
    last_sunday = selected_date - datetime.timedelta((selected_date.weekday() + 1) % 7)
    
    data = get_week_count(last_sunday)
    
    if data is None:
        st.session_state['weekly_df'] = None
        return 
    
    data['Dia das Transações'] = [None] * 7
    
    for i in range(7):
        day_i = last_sunday + datetime.timedelta(i)
        data['Dia das Transações'][i] = f'{day_i.day:02d}/{day_i.month:02d}'
    
    st.session_state['weekly_df'] = pd.DataFrame(data) #cria um dataframe da semana selecionada


if st.session_state['weekly_df'] is None:
    weekly_change()


with st.container():
    st.header("Balanço Semanal")

    selected_week_day = st.date_input(
        "Selecione um dia da semana que deseja analisar",
        min_value = datetime.date(2025, 5, 1),
        max_value = datetime.datetime.today(),
        on_change = weekly_change,
        key='weekly_date'
    )
    
    df = st.session_state['weekly_df']
    
    if df is not None:
        col1, col2 = st.columns([3,1])

        col1.bar_chart(df, x='Dia das Transações', x_label='Dias', y_label='Quantidade de Transações', use_container_width=True)
        col2.table(df.drop(columns=['Dia das Transações']).sum())



st.divider() # -------------------------

if 'daily_merge' not in st.session_state:
    st.session_state['daily_merge'] = None

if 'daily_date' not in st.session_state:
    st.session_state['daily_date'] = datetime.date(2025, 8, 1)


def get_hourly_groups(dfs, selected_date):
    data = {}
    
    for key in st.session_state.bases:
        try:
            if dfs[key].empty:
                data[key] = None
                continue
            
            df = dfs[key].groupby(pd.Grouper(key='Data da Transação', freq='1h'))['Linha'].count().reset_index().rename(columns={'Linha': st.session_state.bases[key]['fullname']})
            
            # A seguinte linha deverá ser deletada após o ajuste no código versão gratuidade, e o código da função daily_change deve ser descomentada, além de retirar o "selected_date" daqui também:
            if(key == 'gt'):
                print(df)
                df = df[df['Data da Transação'].dt.day == selected_date.day]
                
            data[key] = df
            
        except Exception as e:
            print(e)
    
    return data

def merge_hourly_date(hourly_groups):
    merge = None
    
    for key in st.session_state.bases:
        try:
            merge = pd.merge(merge, hourly_groups[key], on='Data da Transação', how='outer') if (merge is not None) else hourly_groups[key]
        except Exception as e:
            print(e)
    
    try:
        merge['Data da Transação'] = merge['Data da Transação'].dt.hour
        merge = merge.rename(columns={'Data da Transação': 'Horário da Transação'})
    except Exception as e:
        print(e)
    
    return merge

def daily_change():
    global merge
    merge = None

    selected_date = st.session_state['daily_date']
    
    df = get_dfs(selected_date)
    daily_chart_data = get_hourly_groups(df, selected_date)
    merge = merge_hourly_date(daily_chart_data)
    
    st.session_state['hourly_merge'] = merge


if st.session_state['daily_merge'] is None:
    daily_change()


with st.container():
    st.header("Balanço Diário")

    selected_date = st.date_input(
        "Selecione o dia que deseja analisar",
        value = datetime.date(2025, 8, 1),
        min_value = datetime.date(2025, 5, 1),
        max_value = datetime.datetime.today(),
        on_change = daily_change,
        key='daily_date'
    )
    
    merge = st.session_state['hourly_merge']
    
    if merge is not None:
        col1, col2 = st.columns([3,1])

        col1.bar_chart(merge, x='Horário da Transação', x_label='Horário', y_label='Quantidade de Transações', use_container_width=True)
        col2.table(merge.drop(columns=['Horário da Transação']).sum())
    else:
        st.warning(':warning: Nenhum dado registrado sobre esse dia.')



st.divider() # -------------------------

'''
### Pontos de Melhoria da Disposição dos Dados

1. Separação das informações pela Data da Transação
2. Padronização dos arquivos
3. Clareza sobre as informações
'''



st.divider() # -------------------------

if 'trans_df' not in st.session_state:
    st.session_state['trans_df'] = None

if 'subsidy_df' not in st.session_state:
    st.session_state['subsidy_df'] = None

if 'subsidy_first_date' not in st.session_state:
    st.session_state['subsidy_first_date'] = datetime.date(2025, 8, 5)

if 'subsidy_sec_date' not in st.session_state:
    st.session_state['subsidy_sec_date'] = datetime.date(2025, 8, 12)



def get_vl_trans(dfs):
    data = {}
    
    for i in dfs:
        try:
            dfs[i]['Vl Trans'] = dfs[i]['Vl Trans'].str.replace(',', '.').astype(float)
            data[i] = dfs[i]['Vl Trans'].sum()
        except:
            data[i] = 0
    
    return data


def get_vl_sub(dfs):
    data = {}
    
    for i in dfs:
        try:
            dfs[i]['Vl Subsídio'] = dfs[i]['Vl Subsídio'].str.replace(',', '.').astype(float)
            data[i] = dfs[i]['Vl Subsídio'].sum()
        except:
            data[i] = 0
    
    return data

def subsidy_change():
    first_date = st.session_state['subsidy_first_date']
    sec_date = st.session_state['subsidy_sec_date']
    
    dif = sec_date - first_date
    
    data = {
        'vl_trans': {
            'Dia das Transações': [None] * (dif.days + 1)
        },
        'vl_sub': {
            'Dia das Transações': [None] * (dif.days + 1)
        }
    }
    
    for j in st.session_state.bases:
        data['vl_trans'][j] = [None] * (dif.days + 1)
        data['vl_sub'][j] = [None] * (dif.days + 1)
    
    for i in range(dif.days + 1):
        current_day = first_date + datetime.timedelta(i)
        dfs = get_dfs(current_day)
        
        data['vl_trans']['Dia das Transações'][i] = f'{current_day.day}/{current_day.month}'
        data['vl_sub']['Dia das Transações'][i]   = f'{current_day.day}/{current_day.month}'
        
        for j in dfs:
            data['vl_trans'][j][i] = get_vl_trans( dfs )[j]
            data['vl_sub'][j][i]   =   get_vl_sub( dfs )[j]
    
    st.session_state['trans_df']   = pd.DataFrame( data['vl_trans'] )
    st.session_state['subsidy_df'] = pd.DataFrame( data['vl_sub'] )



if (st.session_state['trans_df'] is None) | (st.session_state['subsidy_df'] is None):
    subsidy_change()


with st.container():
    st.header('Pagamento de subsídio no período')
    
    col1, col2, col3 = st.columns([2, 2, 1])

    first_day = col1.date_input(
        "Selecione um dia da semana que deseja analisar",
        value = datetime.date(2025, 8, 1),
        min_value = datetime.date(2025, 5, 1),
        max_value = st.session_state['subsidy_sec_date'],
        key='subsidy_first_date'
    )
    
    last_day = col2.date_input(
        "Selecione um dia da semana que deseja analisar",
        value = datetime.date(2025, 8, 5),
        min_value = st.session_state['subsidy_first_date'],
        max_value = datetime.datetime.today(),
        key='subsidy_sec_date'
    )
    
    submit = col3.button(
        "Calcular",
        on_click = subsidy_change
    )
    
    trans_df   = st.session_state['trans_df']
    print(trans_df)
    
    subsidy_df = st.session_state['subsidy_df']
    print(subsidy_df)
    
    df = pd.merge(trans_df, subsidy_df, on='Dia das Transações', how='outer')
    
    col1.bar_chart(df, x='Dia das Transações', x_label='Dias', y_label='Quantidade de Transações', use_container_width=True)



