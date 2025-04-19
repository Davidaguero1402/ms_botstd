from sqlalchemy.sql import text

def test_database_connection(connection):
    """Verifica que la conexión a la base de datos sea exitosa y que existan tablas."""
    try:
        # Verificar que la conexión es válida
        result = connection.execute(text("SELECT 1"))
        assert result.fetchone()[0] == 1, "La conexión a la base de datos falló."

        # Verificar que existan tablas en la base de datos
        tables = connection.execute(
            text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
        ).fetchall()
        assert len(tables) > 0, "No se encontraron tablas en la base de datos."

        # Mostrar las tablas encontradas (opcional)
        print("Tablas en la base de datos:")
        for table in tables:
            print(f"- {table[0]}")

    except Exception as e:
        assert False, f"Error al conectar con la base de datos o al verificar tablas: {e}"