import streamlit as st
import pandas as pd
import datetime

root_path = '../../../'
data_path = './Downloads/transporte-inteligente-dados/'

bases = {
	'be': {
		'dir': './org-BE/',
		'pref': 'be_',
		'dayfirst': True,
		'fullname': 'Bilhetagem Eletrônica'
	},
	'bu': {
		'dir': './diario/org/',
		'pref': 'bu_',
		'dayfirst': True,
		'fullname': 'Bilhete Único'
	},
	'gt': {
		'dir': './GT/',
		'pref': 'gt_',
		'dayfirst': False,
		'fullname': 'Gratuidade'
	},
}

st.set_page_config(
    page_title="Transporte Inteligente",
    page_icon=":bus:",

    layout="wide",
)


st.title("Transporte Inteligente")
st.caption("Um protótipo da ferramenta de exibição das informações sobre o Sistema de Bilhetagem Eletrônica do Estado do Rio de Janeiro")


st.warning(":warning:  Nessa versão é possível verificar apenas informações referentes ao mês de agosto de 2025.")



st.divider() # -------------------------

if 'weekly_df' not in st.session_state:
    st.session_state['weekly_df'] = None

if 'weekly_date' not in st.session_state:
    st.session_state['weekly_date'] = datetime.date(2025, 8, 5)


def get_dfs(selected_date):
    data = {}
    
    for key in bases:
        filename = (
            root_path
            + data_path
            + bases[key]['dir']
            + bases[key]['pref']
            + f'{selected_date.year}-{selected_date.month:02d}-{selected_date.day:02d}.csv'
        )
        
        try:
            data[key] = pd.read_csv(
                filename,
                sep=';',
                dayfirst = bases[key]['dayfirst'],
                parse_dates = ['Data da Transação', 'Data do Processamento'],
                low_memory = False
            )

            if 'Vl Trans' in data[key].columns:
                data[key]['Vl Trans'] = (data[key]['Vl Trans'].str.replace(',', '.')).astype(float)

            if 'Vl Subsídio' in data[key].columns:
                data[key]['Vl Subsídio'] = (data[key]['Vl Subsídio'].str.replace(',', '.')).astype(float)
        
        except Exception as e:
            print('\nget_dfs:')
            print(e)
            data[key] = None
    
    return data

def get_quant(selected_date):
    data = {}
    dfs = get_dfs(selected_date);
    
    for i in dfs:
        try:
            data[i] = dfs[i]['Linha'].count()
        except:
            data[i] = None
    
    return data
    
def get_week_count(selected_sunday):
    data = {}
    
    for i in bases:
        data[ bases[i]['fullname'] ] = [None] * 7
        
    for j in range(7):
        quant = get_quant(selected_sunday + datetime.timedelta(j))
        
        for i in quant:
            data[ bases[i]['fullname'] ][j] = quant[i]
    
    return data

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
    
    st.session_state['weekly_df'] = pd.DataFrame(data)


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
        
        df = df.drop(columns=['Dia das Transações']).sum()
        styler = df.to_frame().style.format( thousands = '.')
        
        print(df.to_frame().columns)

        col2.table(styler)



st.divider() # -------------------------

if 'daily_merge' not in st.session_state:
    st.session_state['daily_merge'] = None

if 'daily_date' not in st.session_state:
    st.session_state['daily_date'] = datetime.date(2025, 8, 1)


def get_hourly_groups(dfs, selected_date):
    data = {}
    
    for key in bases:
        try:
            if dfs[key].empty:
                data[key] = None
                continue
            
            df = dfs[key].groupby(pd.Grouper(key='Data da Transação', freq='1h'))['Linha'].count().reset_index().rename(columns={'Linha': bases[key]['fullname']})
            
            # A seguinte linha deverá ser deletada após o ajuste no código versão gratuidade, e o código da função daily_change deve ser descomentada, além de retirar o "selected_date" daqui também:
            if(key == 'gt'):
                df = df[df['Data da Transação'].dt.day == selected_date.day]
                
            data[key] = df
            
        except Exception as e:
            print('get_hourly_groups:')
            print(e)
    
    return data

def merge_hourly_date(hourly_groups):
    merge = None
    
    for key in bases:
        try:
            merge = pd.merge(merge, hourly_groups[key], on='Data da Transação', how='outer') if (merge is not None) else hourly_groups[key]
        except Exception as e:
            print('merge_hourly_date 01:')
            print(e)
    
    try:
        merge['Data da Transação'] = merge['Data da Transação'].dt.hour
        merge = merge.rename(columns={'Data da Transação': 'Horário da Transação'})
    except Exception as e:
        print('merge_hourly_date 02:')
        print(e)
    
    return merge

def daily_change():
    merge = None

    selected_date = st.session_state['daily_date']
    
    dfs = get_dfs(selected_date)
    daily_chart_data = get_hourly_groups(dfs, selected_date)
    merge = merge_hourly_date(daily_chart_data)
    
    st.session_state['hourly_merge'] = merge


if st.session_state['daily_merge'] is None:
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
    
    merge = st.session_state['hourly_merge']
    styler = merge.style.format( thousands = '.')
    
    if merge is not None:
        col1, col2 = st.columns([3,1])

        col1.bar_chart(merge, x='Horário da Transação', x_label='Horário', y_label='Quantidade de Transações', use_container_width=True)
        
        
        merge = merge.drop(columns=['Horário da Transação']).sum().astype(int)
        styler = merge.to_frame().style.format( thousands = '.')
        
        col2.table(styler)
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



def money_format(quant):
    return f'R$ {float(quant):,.2f}'.replace(',', '-').replace('.', ',').replace('-', '.')

def enable_button():
    st.session_state.subsidy_submit_button_enabled = True

def disable_button():
    st.session_state.subsidy_submit_button_enabled = False



def get_monetary_sum(dfs, collumn_name):
    data = {}
    
    for i in dfs:
        try:
            cdf = dfs[i]
            
            series = cdf[collumn_name][cdf[collumn_name].notna()]
            series = (series*100).astype(int)
            data[i] = series.sum() / 100
        except Exception as e:
            print('get_monetary_sum:')
            print(e)
            
            print(f'key: {i}')
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
    
    for j in bases:
        data['vl_trans'][j] = [None] * (dif.days + 1)
        data['vl_sub'][j] = [None] * (dif.days + 1)
    
    for i in range(dif.days + 1):
        current_day = first_date + datetime.timedelta(i)
        dfs = get_dfs(current_day)
        
        data['vl_trans']['Dia das Transações'][i] = f'{current_day.day}/{current_day.month}'
        data['vl_sub']['Dia das Transações'][i]   = f'{current_day.day}/{current_day.month}'
        
        for j in dfs:
            data['vl_trans'][j][i] = get_monetary_sum( dfs, 'Vl Trans')[j]
            data['vl_sub'][j][i]   = get_monetary_sum( dfs, 'Vl Subsídio')[j]
    
    st.session_state['trans_df']   = pd.DataFrame( data['vl_trans'] )
    st.session_state['subsidy_df'] = pd.DataFrame( data['vl_sub'] )
    disable_button()


if (st.session_state['trans_df'] is None) | (st.session_state['subsidy_df'] is None):
    subsidy_change()

if 'subsidy_submit_button_enabled' not in st.session_state:
    st.session_state.subsidy_submit_button_enabled = True


with st.container():
    st.header('Pagamento de subsídio no período')
    
    col1, col2, col3 = st.columns([2, 2, 1])

    first_day = col1.date_input(
        "Selecione um dia da semana que deseja analisar",
        value = datetime.date(2025, 8, 1),
        min_value = datetime.date(2025, 5, 1),
        max_value = st.session_state['subsidy_sec_date'],
        key='subsidy_first_date',
        on_change=enable_button
    )
    
    last_day = col2.date_input(
        "Selecione um dia da semana que deseja analisar",
        value = datetime.date(2025, 8, 5),
        min_value = st.session_state['subsidy_first_date'],
        max_value = datetime.datetime.today(),
        key='subsidy_sec_date',
        on_change=enable_button
    )
    
    submit = col3.button(
        "Calcular",
        on_click = subsidy_change,
        disabled = not st.session_state.subsidy_submit_button_enabled
    )
    
    
    
    trans_df   = st.session_state['trans_df']
    subsidy_df = st.session_state['subsidy_df']
    
    total_trans   = trans_df.drop(columns=['Dia das Transações']).sum()
    total_subsidy = subsidy_df.drop(columns=['Dia das Transações']).sum()
    
    for i in total_trans.index:
        total_trans = total_trans.rename(index={i: f'Transporte {bases[i]["fullname"]}'})
        total_subsidy = total_subsidy.rename(index={i: f'Subsídio {bases[i]["fullname"]}'})
    
    compare_df = pd.concat([total_trans, total_subsidy]).reset_index().rename(columns={0: 'value', 'index': 'Categoria'})

    for i in range(len(compare_df)):
        compare_df.loc[i, 'Valor Total'] = money_format(compare_df.loc[i, 'value'])
    
    col1, col2 = st.columns([1, 1])
    
    col1.vega_lite_chart(compare_df, {
        "mark": {"type": "arc", "innerRadius": 60},
        "encoding": {
            "theta": {"field": "value", "type": "quantitative"},
            "color": {"field": "Categoria", "type": "nominal"},
            "tooltip": [{"field": "Categoria"}, {"field": "Valor Total"}]
        }
    }, use_container_width=True)
    
    
    df = pd.Series( map(money_format, [total_trans.sum(), total_subsidy.sum(), total_trans.sum() + total_subsidy.sum()]), ['Somatório Transporte', 'Somatório Subsídio', 'Arrecadação Total'])
    
    col2.table(df)  
    
    '''
    
    ### Próximos passos:
    - Fazer o somatório por coluna
    - Colocar no gráfico circular, deixando as cores do transporte próximas entre si, e diferentes das de subsídio
    - Mudar o gráfico do semanal para aquele que possui as linhas para média, que por enquanto são apenas supostos
    '''


