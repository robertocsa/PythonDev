import geopandas as gpd
import pandas as pd
import plotly.express as px
import numpy as np
from dash import Dash, dcc, html, Input, Output, State, exceptions, callback_context
import locale

# Configura o locale para brasileiro
try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
except locale.Error:
    locale.setlocale(locale.LC_ALL, 'C')

def format_br(value):
    """Formata valor numérico para notação brasileira com 3 decimais."""
    if pd.isna(value):
        return ''
    try:
        formatted = locale.format_string('%.3f', value, grouping=True)
    except:
        formatted = f"{float(value):,.3f}".replace(',', 'TEMP').replace('.', ',').replace('TEMP', '.')
    return formatted

# Dicionário das regiões do país por UF
regiao_uf = {
    'Norte': ['AC', 'AP', 'AM', 'PA', 'RO', 'RR', 'TO'],
    'Nordeste': ['AL', 'BA', 'CE', 'MA', 'PB', 'PE', 'PI', 'RN', 'SE'],
    'Sudeste': ['ES', 'MG', 'RJ', 'SP'],
    'Sul': ['PR', 'RS', 'SC'],
    'Centro-Oeste': ['DF', 'GO', 'MS', 'MT']
}

# Carregamento de dados
gdf_mun_path = "./MalhasTerritoriais/BR_Municipios_2024/BR_Municipios_2024.shp"
gdf_mun = gpd.read_file(gdf_mun_path)[['CD_MUN', 'geometry']]
gdf_mun['CD_MUN'] = gdf_mun['CD_MUN'].astype(int)

df_path = "./DadosMunicipios.xlsx"
df = pd.read_excel(df_path)
df['CD_MUN'] = df['CD_MUN'].astype(int)

def get_regiao(sigla_uf):
    for reg, ufs in regiao_uf.items():
        if sigla_uf in ufs:
            return reg
    return 'Desconhecida'

df['REGIAO'] = df['SIGLA_UF'].apply(get_regiao)

merged = gdf_mun.merge(df, on='CD_MUN', how='inner')

# Formatar colunas numéricas
float_cols = [
    'PRODUTO INTERNO BRUTO', 'MÉDIA DE PRODUTO INTERNO BRUTO PER CAPITA',
    'ÁREA KM^2', 'DENSIDADE POPULACIONAL', 'IDHM ATLAS 2010',
    'ESCOLAS POR DENSIDADE POPULACIONAL', 'MÉDIA DE SALÁRIOS MÍNIMOS MENSAIS 2022'
]
int_cols = ['POPULAÇÃO ESTIMADA', 'CONTAGEM ESCOLAS 2023']

for col in float_cols:
    if col in merged.columns:
        merged[col] = pd.to_numeric(merged[col], errors='coerce').round(3)
for col in int_cols:
    if col in merged.columns:
        merged[col] = pd.to_numeric(merged[col], errors='coerce').astype('Int64')

metricas = [col for col in float_cols + int_cols if col in merged.columns]

group_config = {
    'Municípios': {'group_col': 'CD_MUN', 'name_col': 'NOME_MUN'},
    'Mesorregiões': {'group_col': 'MESORREGIÃO GEOGRÁFICA', 'name_col': 'NOME_MESORREGIÃO'},
    'Microrregiões': {'group_col': 'MICRORREGIÃO GEOGRÁFICA', 'name_col': 'NOME_MICRORREGIÃO'},
    'RGI': {'group_col': 'CD_RGI', 'name_col': 'NOME_RGI'},
    'RGINT': {'group_col': 'CD_RGINT', 'name_col': 'NOME_RGINT'}
}

# Inicializar o aplicativo Dash
app = Dash(__name__)
server = app.server

# Layout ajustado com colunas lado a lado
app.layout = html.Div(style={'display': 'flex', 'flexDirection': 'row'}, children=[
    html.Div(style={'width': '25%', 'padding': '10px'}, children=[
        html.H1("Mapa Interativo de Divisões Territoriais do Brasil", style={'fontSize': '24px'}),
        html.Label("Selecione a Região do País:"),
        dcc.Dropdown(
            id='regiao-dropdown',
            options=[{'label': 'Brasil', 'value': 'Brasil'}] + [{'label': r, 'value': r} for r in sorted(regiao_uf.keys())],
            value='Brasil',
            style={'width': '100%'}
        ),
        html.Label("Selecione o Estado (UF):"),
        dcc.Dropdown(
            id='uf-dropdown',
            value='Todos',
            style={'width': '100%'}
        ),
        html.Label("Selecione a Divisão Territorial:"),
        dcc.Dropdown(
            id='divisao-dropdown',
            options=[
                {'label': 'Municípios', 'value': 'Municípios'},
                {'label': 'Mesorregiões', 'value': 'Mesorregiões'},
                {'label': 'Microrregiões', 'value': 'Microrregiões'},
                {'label': 'Regiões Geográficas Imediatas (RGI)', 'value': 'RGI'},
                {'label': 'Regiões Geográficas Intermediárias (RGINT)', 'value': 'RGINT'}
            ],
            value='Municípios',
            style={'width': '100%'}
        ),
        html.Label("Selecione a Métrica:"),
        dcc.Dropdown(
            id='metric-dropdown',
            options=[{'label': m, 'value': m} for m in metricas],
            value='IDHM ATLAS 2010' if 'IDHM ATLAS 2010' in metricas else (metricas[0] if metricas else None),
            style={'width': '100%'}
        ),
    ]),
    html.Div(style={'width': '75%', 'height': '800px'}, children=[
        dcc.Graph(id='mapa', style={'width': '100%', 'height': '100%'})
    ])
])

# Callback para opções de UF
@app.callback(
    Output('uf-dropdown', 'options'),
    Input('regiao-dropdown', 'value')
)
def update_uf_options(selected_regiao):
    if selected_regiao == 'Brasil':
        ufs = sorted(merged['SIGLA_UF'].unique())
    else:
        ufs = sorted(regiao_uf.get(selected_regiao, []))
    return [{'label': 'Todos', 'value': 'Todos'}] + [{'label': uf, 'value': uf} for uf in ufs]

# Callback para atualizar valor de UF
@app.callback(
    Output('uf-dropdown', 'value'),
    [Input('regiao-dropdown', 'value'),
     Input('mapa', 'clickData')],
    [State('uf-dropdown', 'value'),
     State('uf-dropdown', 'options'),
     State('divisao-dropdown', 'value')],
    prevent_initial_call=True
)
def update_uf_value(selected_regiao, click_data, current_value, options, divisao):
    ctx = callback_context
    if not ctx.triggered:
        raise exceptions.PreventUpdate

    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if triggered_id == 'regiao-dropdown':
        if current_value == 'Todos':
            return 'Todos'
        valid_ufs = [opt['value'] for opt in options if opt['value'] != 'Todos']
        if current_value in valid_ufs:
            return current_value
        return 'Todos'
    elif triggered_id == 'mapa':
        if not click_data or divisao != 'Municípios' or 'points' not in click_data or not click_data['points']:
            raise exceptions.PreventUpdate
        point = click_data['points'][0]
        if 'location' not in point or point['location'] is None:
            raise exceptions.PreventUpdate
        customdata = point.get('customdata', [])
        if len(customdata) >= 5 and customdata[4]:
            return customdata[4]  # SIGLA_UF
        raise exceptions.PreventUpdate

    raise exceptions.PreventUpdate

# Callback principal para o mapa
@app.callback(
    Output('mapa', 'figure'),
    [Input('regiao-dropdown', 'value'),
     Input('uf-dropdown', 'value'),
     Input('divisao-dropdown', 'value'),
     Input('metric-dropdown', 'value')]
)
def update_map(selected_regiao, selected_uf, selected_divisao, selected_metric):
    filtered = merged.copy()
    if selected_regiao != 'Brasil':
        filtered = filtered[filtered['REGIAO'] == selected_regiao]
    if selected_uf != 'Todos':
        filtered = filtered[filtered['SIGLA_UF'] == selected_uf]

    config = group_config[selected_divisao]
    group_col = config['group_col']
    name_col = config['name_col']
    extra_cols = [c for c in ['REGIAO', 'NOME_RGI', 'NOME_RGINT'] if c in filtered.columns]

    if selected_divisao == 'Municípios':
        base_cols = ['CD_MUN', name_col, selected_metric, 'SIGLA_UF', 'geometry']
        lean_cols = base_cols + extra_cols
        lean_df = filtered[lean_cols].copy()
        lean_df = lean_df.rename(columns={name_col: 'NOME'})
        tol = 0.01 if len(lean_df) > 500 else 0.001
        lean_df['geometry'] = lean_df['geometry'].simplify(tol, preserve_topology=True)
        id_col = 'CD_MUN'
        agg_func = None
    else:
        if any(keyword in selected_metric for keyword in ['MÉDIA', 'DENSIDADE', 'IDHM', 'ESCOLAS POR DENSIDADE POPULACIONAL']):
            agg_func = 'mean'
        else:
            agg_func = 'sum'

        dissolved = filtered.dissolve(by=group_col)
        dissolved['SIGLA_UF'] = filtered.groupby(group_col)['SIGLA_UF'].first().reindex(dissolved.index)
        if 'REGIAO' in filtered.columns:
            dissolved['REGIAO'] = filtered.groupby(group_col)['REGIAO'].first().reindex(dissolved.index)
        if 'NOME_RGI' in filtered.columns:
            dissolved['NOME_RGI'] = filtered.groupby(group_col)['NOME_RGI'].first().reindex(dissolved.index)
        if 'NOME_RGINT' in filtered.columns:
            dissolved['NOME_RGINT'] = filtered.groupby(group_col)['NOME_RGINT'].first().reindex(dissolved.index)

        if selected_metric == 'DENSIDADE POPULACIONAL':
            pop_area_grouped = filtered.groupby(group_col)[['POPULAÇÃO ESTIMADA', 'ÁREA KM^2']].sum()
            density_values = pop_area_grouped['POPULAÇÃO ESTIMADA'] / pop_area_grouped['ÁREA KM^2']
            dissolved[selected_metric] = density_values.reindex(dissolved.index)
        else:
            metric_grouped = filtered.groupby(group_col)[selected_metric].agg(agg_func)
            dissolved[selected_metric] = metric_grouped.reindex(dissolved.index)

        names_grouped = filtered.groupby(group_col)[name_col].first()
        dissolved['NOME'] = names_grouped.reindex(dissolved.index)

        lean_df = dissolved.reset_index()
        tol = 0.005
        lean_df['geometry'] = lean_df['geometry'].simplify(tol, preserve_topology=True)
        lean_df['id'] = lean_df[group_col].astype(str) + '_' + lean_df['SIGLA_UF'].astype(str)
        id_col = 'id'

    # Recalcular min e max com base na divisão territorial selecionada
    values = lean_df[selected_metric].dropna()
    if len(values) > 0:
        min_val = values.min()
        max_val = values.max()
    else:
        min_val, max_val = 0, 0

    # Normalização condicional
    if max_val > min_val and len(values) > 0:
        lean_df['normalized_metric'] = (lean_df[selected_metric] - min_val) / (max_val - min_val)
    else:
        lean_df['normalized_metric'] = 0

    steps = 20
    tickvals = [i / (steps - 1) for i in range(steps)]
    ticktext = [format_br(min_val + (i / (steps - 1)) * (max_val - min_val)) for i in range(steps)]

    lean_df['formatted_metric'] = lean_df[selected_metric].apply(format_br)
    lean_df['formatted_normalized'] = lean_df['normalized_metric'].apply(format_br)

    for c in extra_cols:
        if c in lean_df.columns:
            lean_df[c] = lean_df[c].fillna('').astype(str)

    if selected_divisao == 'Municípios':
        lean_df['id'] = lean_df['CD_MUN'].astype(str)
    lean_df = lean_df.set_index('id', drop=False)

    custom_cols = [id_col, 'NOME', 'formatted_metric', 'formatted_normalized', 'SIGLA_UF']
    for extra in ['REGIAO', 'NOME_RGI', 'NOME_RGINT']:
        if extra in lean_df.columns:
            custom_cols.append(extra)

    title_suffix = f" - {selected_divisao}"
    if selected_regiao != 'Brasil':
        title_suffix += f" ({selected_regiao})"
    if selected_uf != 'Todos':
        title_suffix += f" - UF: {selected_uf}"

    fig = px.choropleth(
        lean_df,
        geojson=lean_df.__geo_interface__,
        locations=lean_df.index,
        color='normalized_metric',
        custom_data=custom_cols,
        hover_data={col: False for col in ['formatted_metric', 'formatted_normalized']},
        color_continuous_scale='Magma',
        range_color=(0, 1),
        labels={'normalized_metric': selected_metric},
        title=f'{selected_metric}{title_suffix}'
    )

    def cidx(col):
        return custom_cols.index(col)

    hover_lines = [
        f"ID: %{{customdata[{cidx(id_col)}]}}",
        f"Nome: %{{customdata[{cidx('NOME')}]}}",
        f"{selected_metric}: %{{customdata[{cidx('formatted_metric')}]}}",
        f"{selected_metric} (normalizado): %{{customdata[{cidx('formatted_normalized')}]}}",
        f"UF: %{{customdata[{cidx('SIGLA_UF')}]}}"
    ]
    if 'REGIAO' in custom_cols:
        hover_lines.append(f"Região: %{{customdata[{cidx('REGIAO')}]}}")
    if 'NOME_RGI' in custom_cols:
        hover_lines.append(f"RGI: %{{customdata[{cidx('NOME_RGI')}]}}")
    if 'NOME_RGINT' in custom_cols:
        hover_lines.append(f"RGINT: %{{customdata[{cidx('NOME_RGINT')}]}}")

    hovertemplate = "<br>".join(hover_lines) + "<extra></extra>"

    fig.update_traces(hovertemplate=hovertemplate)
    fig.update_geos(fitbounds="locations", visible=False, projection_type="mercator")
    fig.update_layout(
        margin={"r": 0, "t": 50, "l": 0, "b": 0},
        coloraxis_colorbar_title=selected_metric,
        coloraxis_colorbar_thickness=25,
        coloraxis_colorbar_len=0.7
    )
    fig.update_coloraxes(
        colorbar=dict(
            title=selected_metric,
            tickvals=tickvals,
            ticktext=ticktext,
            tickformat=None
        )
    )

    return fig

if __name__ == '__main__':
    app.run(debug=True, port=8052)