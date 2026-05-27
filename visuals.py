import streamlit as st
import pandas as pd

from processing import *

def daily_count_chart(df):
    if df is not None and len( df.drop(columns=["Dia das Transações"]).dropna(how='all') ) != 0:
        col1, col2 = st.columns([3,1])

        long_df = df.melt(
        id_vars    = ['Dia das Transações', 'Media'], #o que vai ser os identificadores, vai ficar fixo
        value_vars = df.drop(columns=['Dia das Transações','Media']).columns.array, #o que vai ser uma nova linha 
        var_name   = 'modality', #o nome do variavel, que no caso vai ser as linhas
        value_name = 'quantity') #o nome do value(do header da coluna onde vai ficar a quantidade))
        st.write(df.dtypes)
        col1.vega_lite_chart(long_df, {
            'layer': [
                {
                    'mark': {
                        'type': 'bar',
                        'tooltip': True
                    },
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
                        'field': 'Media', 
                        'type': 'quantitative'
                    },
                    'tooltip': [
                    {'field': 'Media', 'title': 'Média do Mês', 'format': ',.0f'}
                    ]
                },
                },
                ]
        })

        df_sum = df.drop(columns=['Dia das Transações', 'Media']).sum()
        df_sum['Total'] = df_sum.sum()

        styler = df_sum.to_frame().style.format( thousands = '.')

        col2.table(styler)

    else:
        st.warning(':warning: Nenhum dado registrado sobre essa semana.')


def subsidy_charts(trans_df, subsidy_df):
	trans_series = trans_df.drop(columns=["Dia das Transações"]).sum()
	trans_sum = trans_series.sum()

	subsidy_series = subsidy_df.drop(columns=["Dia das Transações"]).sum()
	subsidy_sum = subsidy_series.sum()

	both_sum = [trans_sum, subsidy_sum]

	all_df = pd.DataFrame({
	    "Origem":      ["Transporte", "Subsídio"],
	    "value":       both_sum,
	    "Valor Total": map(money_format, both_sum)
	})

	trans_series = trans_series.reset_index(name='value').rename(columns={'index': 'Categoria'})
	trans_series['Valor Total'] = trans_series['value'].map(money_format)

	subsidy_series = subsidy_series.reset_index(name='value').rename(columns={'index': 'Categoria'})
	subsidy_series['Valor Total'] = subsidy_series['value'].map(money_format)


    
	col1, col2, col3 = st.columns([1, 1, 1])
    
    
	col1.vega_lite_chart(all_df, {
        "mark": {"type": "arc", "innerRadius": 60},
        "title": "Proporção Transporte/Subsídio",
        "encoding": {
            "theta": {"field": "value", "type": "quantitative"},
            "color": {"field": "Origem", "type": "nominal"},
            "tooltip": [{"field": "Origem"}, {"field": "Valor Total"}]
        }
    },  width='stretch')
    
	col2.vega_lite_chart(trans_series, {
        "mark": {"type": "arc", "innerRadius": 60},
        "title": "Proporção BU-BE-Gratuidade no Transporte",
        "encoding": {
            "theta": {"field": "value", "type": "quantitative"},
            "color": {"field": "Categoria", "type": "nominal"},
            "tooltip": [{"field": "Categoria"}, {"field": "Valor Total"}]
        }
    },  width='stretch')
    
	col3.vega_lite_chart(subsidy_series, {
        "mark": {"type": "arc", "innerRadius": 60},
        "title": "Proporção BU-BE-Gratuidade no Subsídio",
        "encoding": {
            "theta": {"field": "value", "type": "quantitative"},
            "color": {"field": "Categoria", "type": "nominal"},
            "tooltip": [{"field": "Categoria"}, {"field": "Valor Total"}]
        }
    },  width='stretch')




def hourly_chart(df):
    if df is not None:
        col1, col2 = st.columns([3,1])

        col1.bar_chart(df, x='Hora Transação', x_label='Horário', y_label='Quantidade de Transações', width='stretch')
        
        
        df = df.drop(columns=['Hora Transação']).sum().astype(int)
        styler = df.to_frame().style.format( thousands = '.')
        
        col2.table(styler)
    else:
        st.warning(':warning: Nenhum dado registrado sobre esse dia.')


def line_analysis_charts(df_filtered, selected_line):
    st.subheader(f"Análise Detalhada: Linha {selected_line}")
    
    # Gráfico 1: Passageiros por Modal
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("Passageiros por Modal/Hora")
        # Preparando dados para o gráfico de barras empilhadas
        chart_data = df_filtered.melt(id_vars=['Hora'], value_vars=['Bilhete Único', 'Bilhetagem Eletrônica', 'Gratuidade'], 
                                    var_name='Modal', value_name='Passageiros')
        st.vega_lite_chart(chart_data, {
            'mark': 'bar',
            'encoding': {
                'x': {'field': 'Hora', 'type': 'ordinal'},
                'y': {'field': 'Passageiros', 'type': 'quantitative'},
                'color': {'field': 'Modal', 'type': 'nominal'}
            }
        }, use_container_width=True)

    with col2:
        st.write("Passageiros por Veículo")
        st.line_chart(df_filtered, x='Hora', y='Passageiros_por_Veiculo', color="#ffaa00")