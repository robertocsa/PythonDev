import geopandas as gpd
import pandas as pd

# =========================================================
# CONFIGURAÇÕES
# =========================================================

SHAPEFILE = "./MalhasTerritoriais/BR_Municipios_2024/BR_Municipios_2024.shp"
EXCEL = "./DadosMunicipios.xlsx"
OUTPUT = "municipios_simplificados.geojson"

SIMPLIFY_TOLERANCE = 0.003  # ajuste fino depois se quiser

# Colunas do Excel que você quer manter
EXCEL_COLS = [
    "CD_MUN",
    "NOME_MUN",
    "SIGLA_UF",

    # Agrupamentos
    "CD_RGI",
    "NOME_RGI",
    "CD_RGINT",
    "NOME_RGINT",

    # Métricas (exemplo – ajuste à vontade)    
    "PRODUTO INTERNO BRUTO (R$ 1.000)",
    "MÉDIA DE PRODUTO INTERNO BRUTO PER CAPITA (R$ 1.000)",
    "POPULAÇÃO ESTIMADA",
    "ÁREA KM^2",
	"DENSIDADE POPULACIONAL",
	"IDHM ATLAS 2010",
	"MÉDIA DE SALÁRIOS MÍNIMOS MENSAIS 2022"
]

# =========================================================
# 1️⃣ LER SHAPEFILE
# =========================================================
print("Lendo shapefile...")
gdf = gpd.read_file(SHAPEFILE)[["CD_MUN", "geometry"]]
gdf["CD_MUN"] = pd.to_numeric(gdf["CD_MUN"], errors="coerce").astype("Int64")
gdf = gdf.dropna(subset=["CD_MUN"])

# =========================================================
# 2️⃣ SIMPLIFICAR GEOMETRIA
# =========================================================
print("Simplificando geometrias...")
gdf["geometry"] = gdf.geometry.simplify(
    SIMPLIFY_TOLERANCE,
    preserve_topology=True
)

# =========================================================
# 3️⃣ LER EXCEL (APENAS COLUNAS NECESSÁRIAS)
# =========================================================
print("Lendo Excel de dados municipais...")
df = pd.read_excel(EXCEL, usecols=EXCEL_COLS)
df["CD_MUN"] = pd.to_numeric(df["CD_MUN"], errors="coerce").astype("Int64")
df = df.dropna(subset=["CD_MUN"])

# =========================================================
# 4️⃣ MERGE SHAPE + DADOS
# =========================================================
print("Fazendo merge shapefile + dados...")
gdf = gdf.merge(df, on="CD_MUN", how="inner")

# ID textual para o Plotly/Dash
gdf["id"] = gdf["CD_MUN"].astype(str)

# =========================================================
# 5️⃣ SALVAR GEOJSON FINAL
# =========================================================
print("Salvando GeoJSON final...")
gdf.to_file(OUTPUT, driver="GeoJSON")

print("✅ GeoJSON gerado com sucesso:", OUTPUT)
print("Features:", len(gdf))
