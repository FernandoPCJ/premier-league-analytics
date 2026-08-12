from pathlib import Path
import pandas as pd


ARQUIVO_ENTRADA = Path(
    "data/processed/premier_league_2016_2026.csv"
)

ARQUIVO_SAIDA = Path(
    "data/processed/premier_league_matches_clean.csv"
)


print("=" * 80)
print("PREMIER LEAGUE ANALYTICS - PREPARAÇÃO DO DATASET")
print("=" * 80)


# Carrega os dados
df = pd.read_csv(ARQUIVO_ENTRADA)


# -------------------------------------------------------------------
# 1. CONVERSÃO DA DATA
# -------------------------------------------------------------------

df["Date"] = pd.to_datetime(
    df["Date"],
    format="mixed",
    dayfirst=True,
    errors="raise"
)


# -------------------------------------------------------------------
# 2. LIMPEZA DE CAMPOS TEXTUAIS
# -------------------------------------------------------------------

colunas_texto = [
    "Season",
    "Div",
    "HomeTeam",
    "AwayTeam",
    "FTR",
    "HTR",
    "Referee"
]

for coluna in colunas_texto:
    df[coluna] = df[coluna].str.strip()


# -------------------------------------------------------------------
# 3. PADRONIZAÇÃO DOS NOMES DAS COLUNAS
# -------------------------------------------------------------------

df = df.rename(columns={
    "Season": "season",
    "Div": "division",
    "Date": "match_date",

    "HomeTeam": "home_team",
    "AwayTeam": "away_team",

    "FTHG": "home_goals",
    "FTAG": "away_goals",
    "FTR": "full_time_result",

    "HTHG": "home_half_time_goals",
    "HTAG": "away_half_time_goals",
    "HTR": "half_time_result",

    "Referee": "referee",

    "HS": "home_shots",
    "AS": "away_shots",

    "HST": "home_shots_on_target",
    "AST": "away_shots_on_target",

    "HF": "home_fouls",
    "AF": "away_fouls",

    "HC": "home_corners",
    "AC": "away_corners",

    "HY": "home_yellow_cards",
    "AY": "away_yellow_cards",

    "HR": "home_red_cards",
    "AR": "away_red_cards"
})


# -------------------------------------------------------------------
# 4. VALIDAÇÕES
# -------------------------------------------------------------------

print("\nDIMENSÕES")
print("-" * 80)

print(f"Partidas: {len(df)}")
print(f"Colunas: {len(df.columns)}")


print("\nINTERVALO DE DATAS")
print("-" * 80)

print(f"Primeira partida: {df['match_date'].min()}")
print(f"Última partida:   {df['match_date'].max()}")


print("\nRESULTADOS POSSÍVEIS")
print("-" * 80)

print(sorted(df["full_time_result"].unique()))


print("\nVALORES AUSENTES")
print("-" * 80)

print(df.isnull().sum().sum())


print("\nLINHAS DUPLICADAS")
print("-" * 80)

print(df.duplicated().sum())


print("\nTIPOS DAS COLUNAS")
print("-" * 80)

print(df.dtypes)


# -------------------------------------------------------------------
# 5. SALVAR DATASET LIMPO
# -------------------------------------------------------------------

df.to_csv(
    ARQUIVO_SAIDA,
    index=False,
    encoding="utf-8",
    date_format="%Y-%m-%d"
)


print("\n" + "=" * 80)
print("DATASET PREPARADO COM SUCESSO")
print("=" * 80)

print(f"\nArquivo criado:")
print(ARQUIVO_SAIDA)