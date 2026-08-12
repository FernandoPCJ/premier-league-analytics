import getpass
import psycopg


print("=" * 70)
print("PREMIER LEAGUE ANALYTICS - TESTE DE CONEXÃO")
print("=" * 70)

senha = getpass.getpass("\nDigite a senha do PostgreSQL: ")

try:
    with psycopg.connect(
        dbname="premier_league_analytics",
        user="postgres",
        password=senha,
        host="127.0.0.1",
        port=5432
    ) as conexao:

        with conexao.cursor() as cursor:

            cursor.execute("SELECT version();")
            versao = cursor.fetchone()

            cursor.execute("SELECT current_database();")
            banco = cursor.fetchone()

            print("\nCONEXÃO REALIZADA COM SUCESSO! ✅")
            print(f"\nBanco conectado: {banco[0]}")
            print(f"PostgreSQL: {versao[0]}")

except Exception as erro:

    print("\nERRO AO CONECTAR ❌")
    print(erro)