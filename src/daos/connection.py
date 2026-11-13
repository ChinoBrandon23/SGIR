from mysql.connector import pooling
from mysql.connector.errors import PoolError
import os


# Configuracion de la base de datos
DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "localhost"),
    "database": os.environ.get("DB_NAME", "sogir"),
    "user": os.environ.get("DB_USER", "admin"),
    "password": os.environ.get("DB_PASSWORD", "")
}

class DatabaseConnection:
    _pool = None

    @classmethod
    def _initialize_pool(cls):
        if cls._pool is None:
            try:
                cls._pool = pooling.MySQLConnectionPool(
                    pool_name="sogir_pool",
                    pool_size=5, # Ajusta la cantidad de conexiones que habra para los hilos
                    pool_reset_session=True, # resetea un pool una vez usado
                    **DB_CONFIG
                )
            except Exception as e:
                print(f"Error al inicializar el pool de conexiones: {e}")
                raise

    @classmethod
    def get_connection(cls):
        """Obtiene una conexion disponible del pool para el hilo actual"""
        if cls._pool is None:
            cls._initialize_pool()
        
        try:
            return cls._pool.get_connection() # type: ignore
        except PoolError as e:
            # indica que todas las conexiones estan siendo usadas
            print(f"El pool de conexiones esta agotado: {e}")
            raise