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

def money_format(quant):
    return f'R$ {float(quant):,.2f}'.replace(',', '-').replace('.', ',').replace('-', '.')

def init_variable(var, value):
    if var not in st.session_state:
        st.session_state[var] = value

def load_functions(vars, func):
    if type(vars) == str:
        vars = [vars] 

    for i in vars:
        if i not in st.session_state or st.session_state[i] is None:
            with st.spinner("Carregando dados...", show_time = True):
                func()

# ========================= WEEKLY =========================

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
        column_name = bases[i]['fullname']
        
        try:
            data[column_name] = [dfs[i]['Linha'].count()]
        except:
            data[column_name] = [None]
    
    return pd.DataFrame(data)
    
def get_transaction_counts_in_range(start_date, quant_days):
    data = [None] * quant_days
        
    for j in range(quant_days):
        current_date = start_date + datetime.timedelta(j)
        
        data[j] = get_daily_transaction_counts( current_date )
    
    
    df = pd.concat(data, axis=0, ignore_index=True)
    
    return df


# ========================= SUBSIDY =========================

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


# ========================= DAILY =========================

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

# ========================= PASSAGEIROS =========================

def get_unique_lines(dfs):
    """Retorna uma lista única de linhas presentes nos DataFrames BE e BU."""
    lines = set()
    for key in ['be', 'bu']:
        if dfs[key] is not None and 'Linha' in dfs[key].columns:
            lines.update(dfs[key]['Linha'].unique().tolist())
    return sorted(list(lines))

def get_filtered_hourly_data(dfs, selected_line):
    """Filtra os dados por linha e calcula passageiros por veículo."""
    hourly_data = []
    
    for hour in range(24):
        stats = {'Hora': hour, 'BU': 0, 'BE': 0, 'GT': 0, 'Passageiros_Total': 0, 'Veiculos_Unicos': set()}
        
        for key in bases:
            df = dfs[key]
            if df is not None:
                # Filtra por linha e hora
                mask = (df['Linha'] == selected_line) & (df['Data da Transação'].dt.hour == hour)
                filtered = df[mask]
                
                count = len(filtered)
                stats[bases[key]['fullname']] = count # Mapeia para o nome amigável (Bilhete Único, etc)
                stats['Passageiros_Total'] += count
                
                if 'Nº Carro' in filtered.columns:
                    stats['Veiculos_Unicos'].update(filtered['Nº Carro'].unique())
        
        # Cálculo da média por veículo
        qtd_veiculos = len(stats['Veiculos_Unicos'])
        stats['Passageiros_por_Veiculo'] = stats['Passageiros_Total'] / qtd_veiculos if qtd_veiculos > 0 else 0
        
        # Limpeza para o DataFrame
        del stats['Veiculos_Unicos']
        hourly_data.append(stats)
        
    return pd.DataFrame(hourly_data)