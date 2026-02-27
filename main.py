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
		'fullname': 'Bilhetagem Eletrônica',
		'color': '#2ca1e7'
	},
	'bu': {
		'dir': './diario/org/',
		'pref': 'bu_',
		'dayfirst': True,
		'fullname': 'Bilhete Único',
		'color': '#ff6683'
	},
	'gt': {
		'dir': './GT/',
		'pref': 'gt_',
		'dayfirst': False,
		'fullname': 'Gratuidade',
		'color': '#ffcb61'
	},
}

def get_base_values_by_key(key):
    values = []
    
    for i in bases:
        values.append( bases[i][key] )
    
    return values


st.title("Transporte Inteligente")
st.caption("Um protótipo da ferramenta de exibição das informações sobre o Sistema de Bilhetagem Eletrônica do Estado do Rio de Janeiro")

st.warning(":warning:  Nessa versão é possível verificar apenas informações referentes ao mês de agosto de 2025.")



st.divider() # -------------------------

if 'weekly_df' not in st.session_state:
    st.session_state['weekly_df'] = None


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

def get_daily_transaction_counts(selected_date):
    data = {
        'Dia das Transações': [ selected_date ]
    }
    
    dfs = get_dfs(selected_date)
    
    for i in dfs:
        column_name = bases[i]["fullname"]
        
        try:
            data[ column_name ] = [ dfs[i]['Linha'].count() ]
        except:
            data[ column_name ] = [ None ]
    
    return pd.DataFrame(data)
    
def get_transaction_counts_in_range(start_date, quant_days):
    data = [None] * quant_days
        
    for j in range(quant_days):
        current_date = start_date + datetime.timedelta(j)
        
        data[j] = get_daily_transaction_counts( current_date )
    
    
    df = pd.concat(data, axis=0, ignore_index=True)
    
    return df

def weekly_change():
    selected_date = st.session_state['weekly_date']
    
    last_sunday = selected_date - datetime.timedelta( selected_date.weekday() + 1 )
    
    data = get_transaction_counts_in_range(last_sunday, 7)
    
    st.session_state['weekly_df'] = data

if st.session_state['weekly_df'] is None:
    weekly_change()


with st.container():
    st.header("Balanço Semanal")
    
    selected_week_day = st.date_input(
        "Selecione um dia da semana que deseja analisar",
        datetime.date(2025, 8, 5),
        min_value = datetime.date(2025, 5, 1),
        max_value = datetime.datetime.today(),
        on_change = weekly_change,
        key='weekly_date'
    )
    
    df = st.session_state['weekly_df']
    
    if df is not None:
        col1, col2 = st.columns([3,1])

        average = [1300000, 3200000, 3300000, 2900000, 2800000, 2600000, 1300000]
        
        df['Média'] = average
        
        df_long = df.melt(
            id_vars    = ['Dia das Transações', 'Média'],
            value_vars = df.drop(columns=['Dia das Transações']).columns.array,
            var_name   = 'modality',
            value_name = 'quantity'
        )
        
        styler = df_long.copy()
        
    
        col1.vega_lite_chart(styler, {
            'layer': [
                {
                    'mark': {'type': 'bar', 'tooltip': True},
                    'encoding': {
                        'x': {
                            'field': 'Dia das Transações', 
                            'type': 'temporal'
                        },
                        'y': {
                            'field': 'quantity', 
                            'type': 'quantitative', 
                            'title': 'Total de Transações',
                            'stack': 'zero'
                        },
                        'color': {
                            'field': 'modality', 
                            'type': 'nominal', 
                            'title': 'Tipo de Transporte',
                            'scale': {
                                'domain': get_base_values_by_key('fullname'),
                                'range': get_base_values_by_key('color')
                            }
                        },
                        'tooltip': [
                            {'field': 'quantity', 'type': 'quantitative', 'title': 'Total:', 'format': ',.0f'}
                        ]
                    },
                },
                {
                    'mark': {
                        'type': 'tick',
                        'color': 'red',
                        'thickness': 2,
                        'tooltip': {'content': 'data'}
                    },
                    'encoding': {
                        'x': {
                            'field': 'Dia das Transações', 
                            'type': 'ordinal'
                        },
                        'y': {
                            'field': 'Média', 
                            'type': 'quantitative'
                        },
                        'tooltip': [
                            {'field': 'Média', 'title': 'Média do Mês', 'format': ',.0f'}
                        ]
                    },
                },
            ]
        })
        
        
        df = df.drop(columns=['Dia das Transações']).sum()
        df['Total dessa semana'] = df.drop(labels=['Média']).sum()
        
        styler = df.to_frame().style.format( thousands = '.')
        
        col2.table(styler)



st.divider() # -------------------------

if 'trans_df' not in st.session_state:
    st.session_state['trans_df'] = None

if 'subsidy_df' not in st.session_state:
    st.session_state['subsidy_df'] = None


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
        except:
            data[i] = 0
    
    return data

def get_daily_column_df_sum(selected_date, column):
    data = {
        "Dia das Transações": selected_date
    }
    
    dfs = get_dfs(selected_date)
    
    for i in dfs:
        category_name = bases[i]["fullname"]
        
        try:
            data[ category_name ] = [ dfs[i][column].sum() ]
        except:
            data[ category_name ] = [ None ]
    
    return pd.DataFrame(data)

def get_columns_sum_in_range(start_date, quant_days, column):
    data = [None] * quant_days
    
    for i in range(quant_days):
        current_date = start_date + datetime.timedelta(i)
        
        data[i] = get_daily_column_df_sum(current_date, column)
    
    df = pd.concat(data, axis=0, ignore_index=True)
    
    return df


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



#if (st.session_state['trans_df'] is None) | (st.session_state['subsidy_df'] is None):
#    subsidy_change()


with st.container():
    st.header('Pagamento de subsídio no período')

    st.date_input(
        "Selecione um dia da semana que deseja analisar",
        (datetime.date(2025, 8, 5), datetime.date(2025, 8, 7)),
        min_value = datetime.date(2025, 5, 1),
        max_value = datetime.datetime.today(),
        key = 'subsidy_date',
        on_change = subsidy_change
    )
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    trans_df = st.session_state['trans_df']
    trans_df = trans_df.drop(columns=["Dia das Transações"]).sum()
    
    total_trans = trans_df.sum()
    
    
    subsidy_df = st.session_state['subsidy_df']
    subsidy_df = subsidy_df.drop(columns=["Dia das Transações"]).sum()
    
    total_subsidy = subsidy_df.sum()
    
    all_dic = {
        "Origem": ["Transporte", "Subsídio"],
        "value": [total_trans, total_subsidy]
    }
    
    all_df = pd.DataFrame(all_dic)
    
    all_df['Valor Total'] = all_df["value"].map(money_format)
    
    col1.vega_lite_chart(all_df, {
        "mark": {"type": "arc", "innerRadius": 60},
        "title": "Proporção Transporte/Subsídio",
        "encoding": {
            "theta": {"field": "value", "type": "quantitative"},
            "color": {"field": "Origem", "type": "nominal"},
            "tooltip": [{"field": "Origem"}, {"field": "Valor Total"}]
        }
    }, use_container_width=True)

    trans_df = trans_df.reset_index(name='value').rename(columns={'index': 'Categoria'})
    trans_df['Valor Total'] = trans_df['value'].map(money_format)
    
    subsidy_df = subsidy_df.reset_index(name='value').rename(columns={'index': 'Categoria'})
    subsidy_df['Valor Total'] = subsidy_df['value'].map(money_format)
    
    col2.vega_lite_chart(trans_df, {
        "mark": {"type": "arc", "innerRadius": 60},
        "title": "Proporção BU-BE-Gratuidade no Transporte",
        "encoding": {
            "theta": {"field": "value", "type": "quantitative"},
            "color": {"field": "Categoria", "type": "nominal"},
            "tooltip": [{"field": "Categoria"}, {"field": "Valor Total"}]
        }
    }, use_container_width=True)
    
    col3.vega_lite_chart(subsidy_df, {
        "mark": {"type": "arc", "innerRadius": 60},
        "title": "Proporção BU-BE-Gratuidade no Subsídio",
        "encoding": {
            "theta": {"field": "value", "type": "quantitative"},
            "color": {"field": "Categoria", "type": "nominal"},
            "tooltip": [{"field": "Categoria"}, {"field": "Valor Total"}]
        }
    }, use_container_width=True)



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
