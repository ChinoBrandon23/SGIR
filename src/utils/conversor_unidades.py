from typing import Dict, List, Optional, Tuple
import unicodedata

class ConversorUnidades:
    """
    Modulo de utilidad estatico para la validacion, estandarizacion y conversion
    de unidades de medida en el sistema (masa,volumen y conteo).
    """

    # factores de conversion hacia la unidad base de cada categoría
    # - masa - unidad base 'g' (gramo)
    # - volumen - unidad base 'ml' (mililitro)
    # - conteo - unidad base 'pza' (pieza)
    _FACTORES = {
        # Masa base = gramo
        "kg": 1000.0,
        "g": 1.0,
        "mg": 0.001,
        "lb": 453.592,
        "oz": 28.3495,

        # volumen Base = mililitro
        "l": 1000.0,
        "ml": 1.0,
        "taza": 240.0,       # Taza culinaria estándar (240 ml)
        "cda": 15.0,         # Cucharada (15 ml)
        "cdita": 5.0,        # Cucharadita (5 ml)
        "fl_oz": 29.5735,    # Onza líquida
        "gal": 3785.41,      # Galón

        # conteos Base = Pieza
        "pza": 1.0,
        "docena": 12.0,
        "paq": 1.0,
    }

    # categorias a las que pertenence cada unidad estandar
    _CATEGORIAS = {
        "kg": "MASA", "g": "MASA", "mg": "MASA", "lb": "MASA", "oz": "MASA",
        "l": "VOLUMEN", "ml": "VOLUMEN", "taza": "VOLUMEN", "cda": "VOLUMEN",
        "cdita": "VOLUMEN", "fl_oz": "VOLUMEN", "gal": "VOLUMEN",
        "pza": "CONTEO", "docena": "CONTEO", "paq": "CONTEO",
    }

    # Alias o sinonimos para lo que es posible que el usuario ingrese
    _SINONIMOS = {
        # Masa
        "kilo": "kg", "kilos": "kg", "kilogramo": "kg", "kilogramos": "kg",
        "gramo": "g", "gramos": "g", "gr": "g", "grs": "g",
        "miligramo": "mg", "miligramos": "mg",
        "libra": "lb", "libras": "lb",
        "onza": "oz", "onzas": "oz",

        # Volumen
        "litro": "l", "litros": "l", "lt": "l", "lts": "l",
        "mililitro": "ml", "mililitros": "ml", "cc": "ml",
        "tazas": "taza", "cup": "taza",
        "cucharada": "cda", "cucharadas": "cda", "tbsp": "cda",
        "cucharadita": "cdita", "cucharaditas": "cdita", "tsp": "cdita",
        "galon": "gal", "galones": "gal",
        "onza fluida": "fl_oz", "onza liquida": "fl_oz", "onzas fluidas": "fl_oz",

        # Conteo
        "pieza": "pza", "piezas": "pza", "pz": "pza", "pzas": "pza",
        "unidad": "pza", "unidades": "pza", "u": "pza",
        "docenas": "docena",
        "paquete": "paq", "paquetes": "paq",
    }

    @classmethod
    def normalizar(cls, unidad: str) -> str:
        """ 
        Limpia y estandariza una unidad a su su 'clave' que maneja el sistema.
        por ejemplo: 'Kilos -> 'kg', 'Litros' -> 'l', 'piezas' -> 'pza'.
        """
        if not unidad:
            return ""
        unidad_limpia = str(unidad).strip().lower()

        # eliminar tildes
        unidad_limpia = ''.join(
        c for c in unicodedata.normalize('NFD', unidad_limpia)
                if unicodedata.category(c) != 'Mn')

        # Si ya es una unidad estandar
        if unidad_limpia in cls._FACTORES:
            return unidad_limpia

        # Si es un sinonimo conocido
        if unidad_limpia in cls._SINONIMOS:
            return cls._SINONIMOS[unidad_limpia]

        return unidad_limpia

    @classmethod
    def es_valida(cls, unidad: str) -> bool:
        """Retorna True si la unidad (o su sinonimo) esta permitida en el sistema."""
        return cls.normalizar(unidad) in cls._FACTORES

    @classmethod
    def obtener_categoria(cls, unidad: str) -> Optional[str]:
        """Devuelve 'MASA', 'VOLUMEN', 'CONTEO' o None si no existe."""
        unidad_norm = cls.normalizar(unidad)
        return cls._CATEGORIAS.get(unidad_norm)

    @classmethod
    def son_compatibles(cls, unidad_origen: str, unidad_destino: str) -> bool:
        """Indica si dos unidades pueden convertirse entre si (pertenecen a la misma categoria)."""
        cat_origen = cls.obtener_categoria(unidad_origen)
        cat_destino = cls.obtener_categoria(unidad_destino)
        return cat_origen is not None and cat_origen == cat_destino

    @classmethod
    def convertir(cls, cantidad: float, unidad_origen: str, unidad_destino: str, decimales: int = 4) -> float:
        """
        Convierte una cantidad de una unidad a otra.
        Lanza ValueError si alguna unidad no existe o si son incompatibles.
        """
        origen = cls.normalizar(unidad_origen)
        destino = cls.normalizar(unidad_destino)

        # 1. Validar existencia
        if origen not in cls._FACTORES:
            raise ValueError(f"Unidad de origen no reconocida: '{unidad_origen}'")
        if destino not in cls._FACTORES:
            raise ValueError(f"Unidad de destino no reconocida: '{unidad_destino}'")

        # 2. Mismo tipo de unidad (p.e. kg a kg)
        if origen == destino:
            return round(float(cantidad), decimales)

        # 3. Validar compatibilidad de dimensiones (no convertir litros a kilogramos)
        cat_origen = cls._CATEGORIAS[origen]
        cat_destino = cls._CATEGORIAS[destino]
        if cat_origen != cat_destino:
            raise ValueError(
                f"Conversión incompatible: No se puede convertir de '{unidad_origen}' ({cat_origen}) "
                f"a '{unidad_destino}' ({cat_destino})."
            )

        # 4. Calculo por medio de  unidad base:
        # cantidad_base = cantidad * factor_origen
        # resultado = cantidad_base / factor_destino
        factor_origen = cls._FACTORES[origen]
        factor_destino = cls._FACTORES[destino]

        cantidad_en_base = float(cantidad) * factor_origen
        resultado = cantidad_en_base / factor_destino

        return round(resultado, decimales)

    @classmethod
    def obtener_unidades_permitidas(cls) -> List[str]:
        """Devuelve la lista de unidades oficiales del sistema para prompts o validaciones."""
        return list(cls._FACTORES.keys())

    @classmethod
    def obtener_catalogo_por_categoria(cls) -> Dict[str, List[str]]:
        """Devuelve las unidades oficiales organizadas por categoria para mostrarlas al usuario."""
        resultado: Dict[str, List[str]] = {"MASA": [], "VOLUMEN": [], "CONTEO": []}
        for unidad, cat in cls._CATEGORIAS.items():
            resultado[cat].append(unidad)
        return resultado

    @classmethod
    def obtener_unidad_base(cls, unidad: str) -> str:
        """
        Retorna la unidad oficial que debe guardarse en la BD según la categoría:
        - MASA    -> 'kg'
        - VOLUMEN -> 'l'
        - CONTEO  -> 'pza'
        """
        cat = cls.obtener_categoria(unidad)
        if cat == "MASA":
            return "kg"
        elif cat == "VOLUMEN":
            return "l"
        elif cat == "CONTEO":
            return "pza"
        else:
            raise ValueError(f"Unidad no reconocida: '{unidad}'")