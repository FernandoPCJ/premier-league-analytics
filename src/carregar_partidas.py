from pathlib import Path
import getpass

import pandas as pd
import psycopg


ARQUIVO = Path(
    "data/processed/premier_league_matches_clean.csv"
)


print("=" * 80)
print("PREMIER LEAGUE ANALYTICS - CARGA DAS PARTIDAS")
print("=" * 80)


# ============================================================
# 1. LER DATASET
# ============================================================

df = pd.read_csv(ARQUIVO)

df["match_date"] = pd.to_datetime(df["match_date"])


print(f"\nPartidas encontradas no CSV: {len(df)}")


# ============================================================
# 2. CONECTAR AO POSTGRESQL
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
            # 3. BUSCAR IDs DAS TEMPORADAS
            # =================================================

            cursor.execute(
                "SELECT id, season FROM seasons;"
            )

            temporadas = {
                season: id_
                for id_, season in cursor.fetchall()
            }


            # =================================================
            # 4. BUSCAR IDs DOS CLUBES
            # =================================================

            cursor.execute(
                "SELECT id, name FROM teams;"
            )

            clubes = {
                name: id_
                for id_, name in cursor.fetchall()
            }


            print(
                f"Temporadas carregadas do banco: "
                f"{len(temporadas)}"
            )

            print(
                f"Clubes carregados do banco: "
                f"{len(clubes)}"
            )


            # =================================================
            # 5. PREPARAR AS PARTIDAS
            # =================================================

            partidas = []

            for _, linha in df.iterrows():

                season_id = temporadas[
                    linha["season"]
                ]

                home_team_id = clubes[
                    linha["home_team"]
                ]

                away_team_id = clubes[
                    linha["away_team"]
                ]

                partida = (
                    season_id,
                    str(linha["division"]),
                    linha["match_date"].date(),

                    home_team_id,
                    away_team_id,

                    int(linha["home_goals"]),
                    int(linha["away_goals"]),
                    str(linha["full_time_result"]),

                    int(linha["home_half_time_goals"]),
                    int(linha["away_half_time_goals"]),
                    str(linha["half_time_result"]),

                    str(linha["referee"]),

                    int(linha["home_shots"]),
                    int(linha["away_shots"]),

                    int(linha["home_shots_on_target"]),
                    int(linha["away_shots_on_target"]),

                    int(linha["home_fouls"]),
                    int(linha["away_fouls"]),

                    int(linha["home_corners"]),
                    int(linha["away_corners"]),

                    int(linha["home_yellow_cards"]),
                    int(linha["away_yellow_cards"]),

                    int(linha["home_red_cards"]),
                    int(linha["away_red_cards"])
                )

                partidas.append(partida)


            # =================================================
            # 6. INSERIR AS PARTIDAS
            # =================================================

            cursor.executemany(
                """
                INSERT INTO matches (
                    season_id,
                    division,
                    match_date,

                    home_team_id,
                    away_team_id,

                    home_goals,
                    away_goals,
                    full_time_result,

                    home_half_time_goals,
                    away_half_time_goals,
                    half_time_result,

                    referee,

                    home_shots,
                    away_shots,

                    home_shots_on_target,
                    away_shots_on_target,

                    home_fouls,
                    away_fouls,

                    home_corners,
                    away_corners,

                    home_yellow_cards,
                    away_yellow_cards,

                    home_red_cards,
                    away_red_cards
                )
                VALUES (
                    %s, %s, %s,
                    %s, %s,
                    %s, %s, %s,
                    %s, %s, %s,
                    %s,
                    %s, %s,
                    %s, %s,
                    %s, %s,
                    %s, %s,
                    %s, %s,
                    %s, %s
                )
                ON CONFLICT (
                    season_id,
                    match_date,
                    home_team_id,
                    away_team_id
                )
                DO NOTHING;
                """,
                partidas
            )


            # =================================================
            # 7. VALIDAR
            # =================================================

            cursor.execute(
                "SELECT COUNT(*) FROM matches;"
            )

            total_partidas = cursor.fetchone()[0]


            print("\n" + "=" * 80)
            print("CARGA REALIZADA COM SUCESSO ✅")
            print("=" * 80)

            print(
                f"\nPartidas no banco: "
                f"{total_partidas}"
            )


except Exception as erro:

    print("\nERRO DURANTE A CARGA ❌")
    print(erro)