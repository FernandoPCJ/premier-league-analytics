from pathlib import Path
import pandas as pd


PASTA_RAW = Path("data/raw")
PASTA_PROCESSED = Path("data/processed")

COLUNAS_ANALISE = [
    "Div",
    "Date",
    "HomeTeam",
    "AwayTeam",
    "FTHG",
    "FTAG",
    "FTR",
    "HTHG",
    "HTAG",
    "HTR",
    "Referee",
    "HS",
    "AS",
    "HST",
    "AST",
    "HF",
    "AF",
    "HC",
    "AC",
    "HY",
    "AY",
    "HR",
    "AR"
]


arquivos = sorted(PASTA_RAW.glob("*.csv"))

datasets = []


print("=" * 80)
print("PREMIER LEAGUE ANALYTICS - CONSOLIDAÇÃO DOS DADOS")
print("=" * 80)


for arquivo in arquivos:

    df = pd.read_csv(arquivo)

    # Mantém apenas as colunas utilizadas no projeto
    df = df[COLUNAS_ANALISE].copy()

    # Extrai a temporada do nome do arquivo
    # Exemplo:
    # premier_league_2016_17.csv -> 2016/17

    partes = arquivo.stem.split("_")

    ano_inicio = partes[-2]
    ano_fim = partes[-1]

    temporada = f"{ano_inicio}/{ano_fim}"

    # Insere a temporada como primeira coluna
    df.insert(0, "Season", temporada)

    datasets.append(df)

    print(
        f"{temporada}: "
        f"{len(df)} partidas | "
        f"{len(df.columns)} colunas"
    )


# Junta todas as temporadas
df_final = pd.concat(datasets, ignore_index=True)


print("\n" + "=" * 80)
print("DATASET CONSOLIDADO")
print("=" * 80)

print(f"Total de partidas: {len(df_final)}")
print(f"Total de colunas: {len(df_final.columns)}")
print(f"Valores ausentes: {df_final.isnull().sum().sum()}")
print(f"Linhas duplicadas: {df_final.duplicated().sum()}")


# Salva o dataset consolidado
arquivo_saida = PASTA_PROCESSED / "premier_league_2016_2026.csv"

df_final.to_csv(
    arquivo_saida,
    index=False,
    encoding="utf-8"
)


print(f"\nArquivo criado com sucesso:")
print(arquivo_saida)