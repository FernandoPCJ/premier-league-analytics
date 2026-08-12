from pathlib import Path
import pandas as pd


PASTA_DADOS = Path("data/raw")

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


arquivos = sorted(PASTA_DADOS.glob("*.csv"))

print("=" * 80)
print("PREMIER LEAGUE ANALYTICS - VALIDAÇÃO DOS DADOS")
print("=" * 80)


for arquivo in arquivos:

    df = pd.read_csv(arquivo)

    # Seleciona apenas as colunas do projeto
    df = df[COLUNAS_ANALISE]

    total_nulos = df.isnull().sum().sum()

    duplicados = df.duplicated().sum()

    print(f"\n{arquivo.name}")
    print("-" * 80)

    print(f"Partidas: {len(df)}")
    print(f"Colunas utilizadas: {len(df.columns)}")
    print(f"Valores ausentes: {total_nulos}")
    print(f"Linhas duplicadas: {duplicados}")