# tests/test_schema_consistency.py
from sqlalchemy.inspection import inspect
from app.db.database import Base
import pytest

@pytest.mark.parametrize("model", Base.__subclasses__())
def test_model_matches_table(model, connection):
    inspector = inspect(connection)
    table_name = model.__tablename__

    # Verificar que la tabla existe
    assert table_name in inspector.get_table_names(), f"Tabla faltante: {table_name}"

    # Obtener columnas de la tabla real en la DB
    db_columns = {col["name"]: col for col in inspector.get_columns(table_name)}

    # Obtener columnas desde el modelo
    model_columns = {col.name: col for col in model.__table__.columns}

    for col_name, col in model_columns.items():
        assert col_name in db_columns, f"Columna {col_name} no encontrada en tabla {table_name}"

        # Comparamos tipos si es posible
        model_type = str(col.type)
        db_type = str(db_columns[col_name]["type"])

        assert model_type in db_type or db_type in model_type, (
            f"Tipo distinto en '{col_name}' de '{table_name}': modelo({model_type}) vs db({db_type})"
        )
