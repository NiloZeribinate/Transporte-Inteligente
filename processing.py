import streamlit as st
import pandas as pd
import datetime

root_path = '../../../'
data_path = './Downloads/transporte-inteligente-dados/'

bases = {
	'be': {
		'dir': './org-BE/',
		'pref': 'be_',
		'dayfirst': False,
		'fullname': 'Bilhetagem Eletrônica',
		'color': '#2ca1e7',
        'suf':'_BE'
	},
	'bu': {
		'dir': './diario/org/',
		'pref': 'bu_',
		'dayfirst': False,
		'fullname': 'Bilhete Único',
		'color': '#ff6683',
        'suf':'_BU'
	},
	'gt': {
		'dir': './GT/',
		'pref': 'gt_',
		'dayfirst': True,
		'fullname': 'Gratuidade',
		'color': '#ffcb61',
        'suf':'_GT'
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
def encontrar_arquivo(nome_final):
    for nome_real in st.session_state.arquivos:
        if nome_real.endswith(nome_final):
            return st.session_state.arquivos[nome_real]
    return None

def get_dfs(selected_date): #mesma funcao de pegar dataframe de antes, so que adaptada pra qualquer diretorio
    data = {}
    
    for key in st.session_state.bases:
        nome_final = (f"{selected_date.year}-{selected_date.month:02d}-{selected_date.day:02d}{st.session_state.bases[key]['suf']}.csv")
        if key=='gt':
            nome_final = (f"{selected_date.year}-{selected_date.day:02d}-{selected_date.month:02d}{st.session_state.bases[key]['suf']}.csv") #template de arquivo de GT eh diferente
        file = encontrar_arquivo(nome_final)
        if file is not None:
            file.seek(0) #se ele ler o mesmo arquivo mais de uma vez, como file eh um tipo *FILE, tem que resetar o ponteiro pro inicio do arquivo
            try:
                data[key] = pd.read_csv(
                    file,
                    sep=',',
                    dayfirst=st.session_state.bases[key]['dayfirst'],
                    parse_dates=['Data da Transação', 'Data do Processamento'],
                    dtype={
                        'Escola': 'string',
                        'Nº Censo Escola': 'string',
                        'Hora Transação': 'Int64'  # or 'Int64' if truly numeric 
                    } #se ainda der errado, colocar low_memory=False, mas deu certo com isso
                )
                # print(data[key].dtypes)
            except Exception as e:
                print(e)
                st.write(nome_final)
                data[key]=None
            if  key in data and data[key] is not None:
                if 'Vl Trans' in data[key].columns:
                    data[key]['Vl Trans'] = (data[key]['Vl Trans'].str.replace(',', '.')).astype(float)
                if 'Vl Subsídio' in data[key].columns:
                    data[key]['Vl Subsídio'] = (data[key]['Vl Subsídio'].str.replace(',', '.')).astype(float)
        else:
            st.write("Nao encontrado:" ,nome_final)
            data[key] = None
    
    return data

def get_daily_transaction_counts(selected_date):
    data = {
        'Dia das Transações': [ pd.Timestamp(selected_date) ] #keep it as a date
    }
    dfs = get_dfs(selected_date)
    
    for i in dfs:
        column_name = bases[i]['fullname']
        
        try:
            val = int(dfs[i]['Linha'].count())
            st.write(f"{i}: {val} ({type(val)})")
            data[column_name] = [val]
        except Exception as e:
            st.write(f"{i} FAILED: {e}")
            data[column_name] = [0]
    
    return pd.DataFrame(data)
    
def get_transaction_counts_in_range(start_date, quant_days):
    data = [None] * quant_days
        
    for j in range(quant_days):
        current_date = start_date + datetime.timedelta(j)
        
        data[j] = get_daily_transaction_counts( current_date )
    
    
    df = pd.concat(data, axis=0, ignore_index=True)
     # Force correct types after concat
    df['Dia das Transações'] = pd.to_datetime(df['Dia das Transações'])
    st.write(df)        # add this — show raw df before any conversion
    st.write(df.dtypes)
    # for col in df.columns:
    #     if col != 'Dia das Transações':
    #         df[col] = pd.to_numeric(df[col], errors='coerce')
    
    st.write(data[0])
    return df


# ========================= SUBSIDY =========================

def get_monetary_sum(dfs, collumn_name):
    data = {}
    
    for i in dfs:
        try:
            cdf = dfs[i]
            
            series = cdf[collumn_name][cdf[collumn_name].notna()] #remove valores nulos
            series = (series*100).astype(int) #multiplica tudo por 100
            data[i] = series.sum() / 100 #divide(pra fazer as operacoes com centavo tudo certo)
        except:
            data[i] = 0
    
    return data #retorna soma de dinheiro de certa coluna

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
    
    return pd.DataFrame(data) #retorna df com soma de uma certa coluna em uma data selecionada

def get_columns_sum_in_range(start_date, quant_days, column):
    data = [None] * quant_days
    
    for i in range(quant_days):
        current_date = start_date + datetime.timedelta(i)
        
        data[i] = get_daily_column_df_sum(current_date, column)
    
    df = pd.concat(data, axis=0, ignore_index=True)
    
    return df #retorna df com soma de certa coluna em um espaco de tempo


# ========================= DAILY =========================

def get_hourly_groups(dfs, selected_date):
    data = {}
    
    for key in bases:
        try:
            if dfs[key] is None or dfs[key].empty:
                data[key] = None
                continue
            df=dfs[key].groupby('Hora Transação').size().reset_index(name=bases[key]['fullname'])

                
            data[key] = df
            
        except Exception as e:
            print('get_hourly_groups:')
            print(e)
    
    return data

def merge_hourly_date(hourly_groups):
    merge = None
    
    for key in bases:
        df = hourly_groups.get(key)
        if df is None:
            continue #se hourly_groups[key] n existir, n tem pra que adicionar um null 
        try:
            if merge is not None:
                merge = pd.merge(merge,df,on='Hora Transação',how='outer')
            else:
                merge = df
        except Exception as e:
            print('merge_hourly_date:') #??? porque isso aconteceria
            print(e)
            print(key)
    
    try:
        merge['Data da Transação'] = merge['Data da Transação'].dt.hour
        merge = merge.rename(columns={'Data da Transação': 'Hora Transação'})
    except Exception as e:
        print('merge_hourly_date 02:') # ??????
        print(e)
        print(key)
    
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
                mask = (df['Linha'] == selected_line) & (df['Hora Transação'] == hour)
                filtered = df[mask]
                
                count = len(filtered) #conta quantos
                stats[bases[key]['fullname']] = count # Mapeia para o nome amigável (Bilhete Único, etc)
                stats['Passageiros_Total'] += count #adiciona ao total 
                
                if 'Nº Carro' in filtered.columns:
                    stats['Veiculos_Unicos'].update(filtered['Nº Carro'].unique())
            else:
                stats[bases[key]['fullname']] = 0
        
        # Cálculo da média por veículo
        qtd_veiculos = len(stats['Veiculos_Unicos'])
        stats['Passageiros_por_Veiculo'] = stats['Passageiros_Total'] / qtd_veiculos if qtd_veiculos > 0 else 0
        # Limpeza para o DataFrame
        del stats['Veiculos_Unicos']
        hourly_data.append(stats)
    return pd.DataFrame(hourly_data)