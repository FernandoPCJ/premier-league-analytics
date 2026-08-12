from pathlib import Path
import getpass

import pandas as pd
import psycopg


ARQUIVO = Path(
    "data/processed/premier_league_matches_clean.csv"
)


print("=" * 80)
print("PREMIER LEAGUE ANALYTICS - CARGA DE TEMPORADAS E CLUBES")
print("=" * 80)


# ============================================================
# 1. LER DATASET
# ============================================================

df = pd.read_csv(ARQUIVO)


# ============================================================
# 2. EXTRAIR TEMPORADAS
# ============================================================

temporadas = sorted(
    df["season"].dropna().unique()
)


# ============================================================
# 3. EXTRAIR CLUBES
# ============================================================

clubes = sorted(
    set(df["home_team"]).union(
        set(df["away_team"])
    )
)


print(f"\nTemporadas encontradas: {len(temporadas)}")
print(f"Clubes encontrados: {len(clubes)}")


# ============================================================
# 4. CONECTAR AO POSTGRESQL
# ============================================================

senha = getpass.getpass(
    "\nDigite a senha do PostgreSQL: "
)


try:

    with psycopg.connect(
        dbname="premier_league_analytics",
        user="postgres",
        password=senha,
        host="127.0.0.1",
        port=5432
    ) as conexao:

        with conexao.cursor() as cursor:

            # =================================================
            # 5. INSERIR TEMPORADAS
            # =================================================

            cursor.executemany(
                """
                INSERT INTO seasons (season)
                VALUES (%s)
                ON CONFLICT (season)
                DO NOTHING;
                """,
                [(temporada,) for temporada in temporadas]
            )


            # =================================================
            # 6. INSERIR CLUBES
            # =================================================

            cursor.executemany(
                """
                INSERT INTO teams (name)
                VALUES (%s)
                ON CONFLICT (name)
                DO NOTHING;
                """,
                [(clube,) for clube in clubes]
            )


            # =================================================
            # 7. VALIDAR QUANTIDADES NO BANCO
            # =================================================

            cursor.execute(
                "SELECT COUNT(*) FROM seasons;"
            )

            total_temporadas = cursor.fetchone()[0]


            cursor.execute(
                "SELECT COUNT(*) FROM teams;"
            )

            total_clubes = cursor.fetchone()[0]


            print("\n" + "=" * 80)
            print("CARGA REALIZADA COM SUCESSO ✅")
            print("=" * 80)

            print(
                f"\nTemporadas no banco: "
                f"{total_temporadas}"
            )

            print(
                f"Clubes no banco: "
                f"{total_clubes}"
            )


except Exception as erro:

    print("\nERRO DURANTE A CARGA ❌")
    print(erro)