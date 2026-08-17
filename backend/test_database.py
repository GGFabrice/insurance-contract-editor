from sqlalchemy import text
from database import engine


try:
    with engine.connect() as connection:
        result = connection.execute(text("SELECT current_database(), version()"))
        row = result.fetchone()

        print("===================================")
        print("CONNEXION PostgreSQL : OK")
        print("===================================")
        print(f"Base de données : {row[0]}")
        print(f"PostgreSQL     : {row[1]}")

except Exception as e:
    print("===================================")
    print("ERREUR DE CONNEXION")
    print("===================================")
    print(e)