from pathlib import Path
import pandas as pd


ARQUIVO = Path(
    "data/processed/premier_league_2016_2026.csv"
)

df = pd.read_csv(ARQUIVO)


print("=" * 80)
print("PREMIER LEAGUE ANALYTICS - INSPEÇÃO DO DATASET CONSOLIDADO")
print("=" * 80)


# Dimensões
print("\n1. DIMENSÕES")
print("-" * 80)

print(f"Linhas: {df.shape[0]}")
print(f"Colunas: {df.shape[1]}")


# Primeiras partidas
print("\n2. PRIMEIRAS 5 PARTIDAS")
print("-" * 80)

print(
    df[
        [
            "Season",
            "Date",
            "HomeTeam",
            "AwayTeam",
            "FTHG",
            "FTAG",
            "FTR"
        ]
    ].head()
)


# Últimas partidas
print("\n3. ÚLTIMAS 5 PARTIDAS")
print("-" * 80)

print(
    df[
        [
            "Season",
            "Date",
            "HomeTeam",
            "AwayTeam",
            "FTHG",
            "FTAG",
            "FTR"
        ]
    ].tail()
)


# Tipos das colunas
print("\n4. TIPOS DAS COLUNAS")
print("-" * 80)

print(df.dtypes)


# Partidas por temporada
print("\n5. PARTIDAS POR TEMPORADA")
print("-" * 80)

print(
    df["Season"]
    .value_counts()
    .sort_index()
)


# Resultados possíveis
print("\n6. RESULTADOS ENCONTRADOS")
print("-" * 80)

print(df["FTR"].value_counts())


# Clubes
clubes = sorted(
    set(df["HomeTeam"]).union(set(df["AwayTeam"]))
)

print("\n7. CLUBES ENCONTRADOS NAS 10 TEMPORADAS")
print("-" * 80)

print(f"Quantidade de clubes diferentes: {len(clubes)}")

for clube in clubes:
    print(clube)