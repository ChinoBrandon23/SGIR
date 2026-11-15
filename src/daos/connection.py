from mysql.connector import pooling
from mysql.connector.errors import PoolError
from dotenv import load_dotenv, find_dotenv
import os

# Carga las variables del archivo .env
load_dotenv(find_dotenv())

# Validar que la contraseña exista para evitar sorpresas
password = os.getenv("DB_PASSWORD")
if not password:
    raise ValueError(
    "Falta configurar DB_PASSWORD en el archivo .env de esta rama"
)

# Configuracion de la base de datos
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "database": os.getenv("DB_NAME", ""),
    "user": os.getenv("DB_USER", "admin"),
    "password": os.getenv("DB_PASSWORD",""),
    "port": int(os.getenv("DB_PORT", 3306))
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
