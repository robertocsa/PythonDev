# =========================================================
# VERSÃO FUNCIONAL BASE — ESTÁVEL
# =========================================================
# - Uma única camada choropleth
# - Divisão territorial selecionável (Município, RGI, RGINT)
# - Filtros: Região, UF, Entidade
# - Escala logarítmica automática para métricas de alta variância
# - Paleta: magma
# - Hover consistente (sem sobreposição de camadas)
#
# - Sem Micro e Mesorregiões
# - Base geométrica sempre municipal
# - Limites municipais visíveis mesmo em RGI e RGINT
# - Municípios sempre identificáveis em RGI e RGINT
# - Hover retorna métricas do Município + RGI + RGINT
# =========================================================

import geopandas as gpd
import pandas as pd
import numpy as np
import plotly.express as px
from dash import Dash, dcc, html, Input, Output
import locale

# =========================================================
# LOCALE
# =========================================================

try:
    locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")
except:
    locale.setlocale(locale.LC_ALL, "C")


# =========================================================
# CONSTANTES
# =========================================================

METRICAS = [
    "PRODUTO INTERNO BRUTO (R$ 1.000)",
    "MÉDIA DE PRODUTO INTERNO BRUTO PER CAPITA (R$ 1.000)",
    "POPULAÇÃO ESTIMADA",
    "ÁREA KM^2",
    "DENSIDADE POPULACIONAL",
    "IDHM ATLAS 2010",
    "MÉDIA DE SALÁRIOS MÍNIMOS MENSAIS 2022"
]

LOG_METRICAS = [
    "PRODUTO INTERNO BRUTO (R$ 1.000)",
    "POPULAÇÃO ESTIMADA",
    "ÁREA KM^2"
]

DIVISOES = {
    "Município": {"cod": "CD_MUN", "nome": "NOME_MUN"},
    "RGI": {"cod": "CD_RGI", "nome": "NOME_RGI"},
    "RGINT": {"cod": "CD_RGINT", "nome": "NOME_RGINT"}
}

REGIAO_UF = {
    "Norte": ["AC","AP","AM","PA","RO","RR","TO"],
    "Nordeste": ["AL","BA","CE","MA","PB","PE","PI","RN","SE"],
    "Sudeste": ["ES","MG","RJ","SP"],
    "Sul": ["PR","RS","SC"],
    "Centro-Oeste": ["DF","GO","MS","MT"]
}

DECIMAIS_POR_METRICA = {
    "PRODUTO INTERNO BRUTO (R$ 1.000)": 2,
    "MÉDIA DE PRODUTO INTERNO BRUTO PER CAPITA (R$ 1.000)": 2,
    "POPULAÇÃO ESTIMADA": 0,
    "ÁREA KM^2": 2,
    "DENSIDADE POPULACIONAL": 3,
    "IDHM ATLAS 2010": 3,
    "MÉDIA DE SALÁRIOS MÍNIMOS MENSAIS 2022": 2,
}


# =========================================================
# FUNÇÕES AUXILIARES
# =========================================================
def montar_hover_template(metrica):
    return (
        "<b>Município: %{hovertext}</b><br>"
        "UF: %{customdata[0]}<br>"
        "RGI: %{customdata[1]}<br>"
        "RGINT: %{customdata[2]}<br><br>"
        f"<b>{metrica}</b><br>"
        "Município: %{customdata[3]}<br>"
        "RGI: %{customdata[4]}<br>"
        "RGINT: %{customdata[5]}"
        "<extra></extra>"
    )

def criar_colunas_formatadas(df):
    for m in METRICAS:
        # Município
        df[f"{m}_FMT"] = df[m].apply(lambda v: format_br_por_metrica(m, v))

        # RGI
        df[f"{m} (RGI)_FMT"] = df[f"{m} (RGI)"].apply(
            lambda v: format_br_por_metrica(m, v)
        )

        # RGINT
        df[f"{m} (RGINT)_FMT"] = df[f"{m} (RGINT)"].apply(
            lambda v: format_br_por_metrica(m, v)
        )

    return df


def format_br_por_metrica(metrica, valor):
    if pd.isna(valor):
        return "—"

    casas = DECIMAIS_POR_METRICA.get(metrica, 2)

    # inteiro forçado
    if casas == 0:
        try:
            return locale.format_string("%d", int(round(valor)), grouping=True)
        except:
            return f"{int(round(valor)):,}".replace(",", ".")

    fmt = f"%.{casas}f"
    try:
        return locale.format_string(fmt, valor, grouping=True)
    except:
        return (
            format(valor, f",.{casas}f")
            .replace(",", "X")
            .replace(".", ",")
            .replace("X", ".")
        )


def get_regiao(uf):
    for r, ufs in REGIAO_UF.items():
        if uf in ufs:
            return r
    return "Desconhecida"


def agregar_tabela(df, col_cod, sufixo):
    agg = (
        df
        .groupby(col_cod)
        .agg({
            "PRODUTO INTERNO BRUTO (R$ 1.000)": "sum",
            "POPULAÇÃO ESTIMADA": "sum",
            "ÁREA KM^2": "sum",
            "DENSIDADE POPULACIONAL": "mean",
            "IDHM ATLAS 2010": "mean",
            "MÉDIA DE SALÁRIOS MÍNIMOS MENSAIS 2022": "mean",
            "MÉDIA DE PRODUTO INTERNO BRUTO PER CAPITA (R$ 1.000)": "mean",
        })
        .reset_index()
    )

    agg.columns = [
        col_cod if c == col_cod else f"{c} ({sufixo})"
        for c in agg.columns
    ]
    return agg
   

# =========================================================
# LOAD GEOJSON BASE (MUNICÍPIOS)
# =========================================================

gdf = gpd.read_file("municipios_simplificados.geojson")
gdf["REGIAO"] = gdf["SIGLA_UF"].apply(get_regiao)
gdf["id"] = gdf["CD_MUN"].astype(str)

# =========================================================
# AGREGAÇÕES (SEM GEOMETRIA)
# =========================================================

rgi_tbl = agregar_tabela(gdf, "CD_RGI", "RGI")
rgint_tbl = agregar_tabela(gdf, "CD_RGINT", "RGINT")

gdf = gdf.merge(rgi_tbl, on="CD_RGI", how="left")
gdf = gdf.merge(rgint_tbl, on="CD_RGINT", how="left")

# 🔹 aplica formatação BR uma única vez
gdf = criar_colunas_formatadas(gdf)

# =========================================================
# APP DASH
# =========================================================

app = Dash(__name__)
server = app.server

app.layout = html.Div(
    style={"display": "flex", "height": "100vh"},
    children=[
        html.Div(
            style={"width": "320px", "padding": "12px", "borderRight": "1px solid #ccc"},
            children=[
                dcc.Dropdown(
                    id="regiao",
                    options=[{"label": "Brasil", "value": "Brasil"}] +
                            [{"label": r, "value": r} for r in REGIAO_UF],
                    value="Brasil",
                    clearable=False
                ),
                dcc.Dropdown(id="uf", clearable=False),
                dcc.Dropdown(
                    id="divisao",
                    options=[{"label": k, "value": k} for k in DIVISOES],
                    value="Município",
                    clearable=False
                ),
                dcc.Dropdown(id="entidade", clearable=False),
                dcc.Dropdown(
                    id="metrica",
                    options=[{"label": m, "value": m} for m in METRICAS],
                    value=METRICAS[0]
                )
            ]
        ),
        dcc.Graph(id="mapa", style={"flex": "1 1 auto", "width":"100%", "height":"100%"}, config={"displayModeBar": False})
    ]
)

# =========================================================
# CALLBACKS
# =========================================================

@app.callback(
    Output("uf", "options"),
    Output("uf", "value"),
    Input("regiao", "value")
)
def atualizar_ufs(regiao):
    if regiao == "Brasil":
        ufs = sorted(gdf["SIGLA_UF"].unique())
    else:
        ufs = REGIAO_UF[regiao]
    return (
        [{"label": "Todos", "value": "Todos"}] +
        [{"label": u, "value": u} for u in ufs],
        "Todos"
    )


@app.callback(
    Output("entidade", "options"),
    Output("entidade", "value"),
    Input("divisao", "value"),
    Input("regiao", "value"),
    Input("uf", "value")
)
def atualizar_entidades(div, regiao, uf):
    df = gdf.copy()
    if regiao != "Brasil":
        df = df[df["REGIAO"] == regiao]
    if uf != "Todos":
        df = df[df["SIGLA_UF"] == uf]

    col = DIVISOES[div]["nome"]
    valores = sorted(df[col].dropna().unique())
    return (
        [{"label": "Todas", "value": "Todas"}] +
        [{"label": v, "value": v} for v in valores],
        "Todas"
    )


@app.callback(
    Output("mapa", "figure"),
    Input("regiao", "value"),
    Input("uf", "value"),
    Input("divisao", "value"),
    Input("entidade", "value"),
    Input("metrica", "value")
)
def atualizar_mapa(regiao, uf, divisao, entidade, metrica):
    df = gdf.copy()

    if regiao != "Brasil":
        df = df[df["REGIAO"] == regiao]
    if uf != "Todos":
        df = df[df["SIGLA_UF"] == uf]
    if entidade != "Todas":
        col = DIVISOES[divisao]["nome"]
        df = df[df[col] == entidade]

    valor = metrica if divisao == "Município" else f"{metrica} ({divisao})"

    if metrica in LOG_METRICAS:
        df["_color"] = np.log10(df[valor].clip(lower=1))
    else:
        df["_color"] = df[valor]

    lw = 0.3 if divisao == "Município" else 1.2

    fig = px.choropleth(
        df,
        geojson=df.__geo_interface__,
        locations="id",
        featureidkey="properties.id",
        color="_color",
        color_continuous_scale="magma",
        hover_name="NOME_MUN",
        custom_data=[
            "SIGLA_UF",
            "NOME_RGI",
            "NOME_RGINT",
            f"{metrica}_FMT",
            f"{metrica} (RGI)_FMT",
            f"{metrica} (RGINT)_FMT"
        ]
    )

    fig.update_traces(
        hovertemplate=montar_hover_template(metrica),
        marker_line_width=lw,
        marker_line_color="#222"
    )

    fig.update_geos(
        fitbounds="locations",
        visible=True,
        showframe=False,
        showcountries=False,
        showcoastlines=False,
        projection_type="mercator",
        domain=dict(x=[0, 1], y=[0, 1])
    )

    #fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))
    
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        coloraxis_colorbar=dict(
        thickness=25,
        len=0.95,
        x=0.99
    )
)

    return fig

# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":
    app.run(debug=False, port=8052)
