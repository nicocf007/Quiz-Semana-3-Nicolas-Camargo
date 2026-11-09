# quiz_nomina.py
# Quiz Semana 3 - Fundamentos de Software (Pilares de POO)
# Autor: Nicolas Camargo Franco - Ingenieria de Sistemas, CEIPA
#
# Tema: nomina de una empresa leida desde un EXCEL (empleados.xlsx).
# Se aplican los 3 pilares de la POO vistos en la Semana 3:
#   * ENCAPSULAMIENTO -> _salario_base es privado; se lee con un getter
#                        (@property) y se escribe con un setter que VALIDA.
#   * HERENCIA        -> EmpleadoPlanta y EmpleadoContratista heredan de
#                        EmpleadoBase (constructor, getter, setter y
#                        obtener_informacion() se escriben UNA sola vez).
#   * POLIMORFISMO    -> cada hija sobreescribe calcular_pago(); el bucle
#                        principal llama al mismo metodo sin preguntar el tipo.
#
# Y los dos principios SOLID de la semana:
#   * SRP -> cada pieza tiene una sola responsabilidad: las clases modelan al
#            empleado, crear_empleado() decide que clase instanciar,
#            leer_empleados_excel() solo lee, y las funciones de reporte
#            (resumen_nomina) solo calculan estadisticas.
#   * OCP -> para agregar un tipo nuevo (por ejemplo TEMPORAL) basta con crear
#            una clase hija y registrarla en TIPOS_EMPLEADO. No se modifica
#            EmpleadoBase ni el bucle de ejecutar_quiz().
#
# Instalar librerias (una sola vez):  pip install -r requirements.txt
# Para ejecutar:                      python quiz_nomina.py

import pandas as pd


# =====================================================================
# 1) CLASE BASE (PADRE): datos comunes + ENCAPSULAMIENTO del salario
# =====================================================================
class EmpleadoBase:
    """Clase base de la nomina: encapsula el salario y define lo comun.

    Atributos:
        nombre (str): nombre del empleado.
        ciudad (str): ciudad de trabajo (puede ser texto vacio).
        _salario_base (int): salario mensual, privado por convencion.
            Solo se accede a el mediante el getter y el setter.
    """

    def __init__(self, nombre, salario_base, ciudad):
        """Constructor comun para todos los tipos de empleado.

        Args:
            nombre (str): nombre del empleado.
            salario_base (int | str | float): salario leido del Excel.
            ciudad (str): ciudad de trabajo.

        Raises:
            ValueError: si el salario es negativo o no es numerico.
        """
        self.nombre = nombre
        self.ciudad = ciudad
        # Se escribe self.salario_base (SIN guion bajo) a proposito: asi
        # Python llama al SETTER y el dato se valida desde el nacimiento
        # del objeto. Ningun empleado puede existir con un salario invalido.
        self.salario_base = salario_base

    # GETTER: puente de LECTURA seguro hacia el atributo privado
    @property
    def salario_base(self):
        """int: salario base mensual del empleado (solo lectura segura)."""
        return self._salario_base

    # SETTER: puente de ESCRITURA; valida ANTES de guardar
    @salario_base.setter
    def salario_base(self, nuevo_salario):
        """Valida y guarda el salario.

        Reglas de integridad:
            * Debe poder convertirse a entero (int("no aplica") falla y
              lanza ValueError, que la lectura del Excel atrapa).
            * No puede ser negativo. El cero SI se acepta.
        """
        salario = int(nuevo_salario)
        if salario < 0:
            raise ValueError("El salario no puede ser negativo.")
        self._salario_base = salario

    # Metodo comun que CADA HIJA sobreescribe (POLIMORFISMO)
    def calcular_pago(self):
        """Placeholder: cada tipo de empleado define como se le paga."""
        raise NotImplementedError("Cada tipo de empleado calcula su pago.")

    def obtener_informacion(self):
        """Devuelve un texto legible con los datos del empleado.

        type(self).__name__ entrega el nombre de la clase REAL del objeto
        (EmpleadoPlanta o EmpleadoContratista), no el de la clase base.

        Returns:
            str: por ejemplo "Ana | EmpleadoPlanta | Medellin | base $3000000".
        """
        return (f"{self.nombre} | {type(self).__name__} | {self.ciudad} | "
                f"base ${self.salario_base}")


# =====================================================================
# 2) CLASES HIJAS (HERENCIA): solo escriben lo que las hace diferentes
# =====================================================================
class EmpleadoPlanta(EmpleadoBase):
    """Empleado de planta: recibe su salario base mas 30 % de prestaciones."""

    PORCENTAJE_PRESTACIONES = 0.30

    def calcular_pago(self):
        """POLIMORFISMO: salario base + 30 % de prestaciones sociales."""
        return self.salario_base * (1 + self.PORCENTAJE_PRESTACIONES)


class EmpleadoContratista(EmpleadoBase):
    """Contratista: recibe unicamente su salario base (sin prestaciones)."""

    def calcular_pago(self):
        """POLIMORFISMO: el contratista cobra solo su salario base."""
        return self.salario_base


# =====================================================================
# 3) Crear el objeto correcto segun el TIPO (aqui se aplica el OCP)
# =====================================================================
# Registro de tipos: relaciona el texto del Excel con la clase hija.
# Para soportar un tipo nuevo se agrega UNA linea aqui y su clase hija;
# crear_empleado() no necesita otro if.
TIPOS_EMPLEADO = {
    "PLANTA": EmpleadoPlanta,
    "CONTRATISTA": EmpleadoContratista,
}


def crear_empleado(nombre, tipo, salario_base, ciudad):
    """Instancia la clase hija que corresponde al tipo leido del Excel.

    Args:
        nombre (str): nombre del empleado.
        tipo (str): "PLANTA" o "CONTRATISTA" (ya normalizado en mayusculas).
        salario_base: salario tal como viene del Excel.
        ciudad (str): ciudad de trabajo.

    Returns:
        EmpleadoBase: un EmpleadoPlanta o un EmpleadoContratista.

    Raises:
        ValueError: si el tipo no existe o si el setter rechaza el salario.
    """
    if tipo not in TIPOS_EMPLEADO:
        raise ValueError(f"tipo desconocido '{tipo}'")
    clase_empleado = TIPOS_EMPLEADO[tipo]
    return clase_empleado(nombre, salario_base, ciudad)


# =====================================================================
# 4) LECTURA DEL EXCEL  --  entregada por el docente (sin modificar)
#    Es ROBUSTA: usa solo las columnas que necesita, ignora filas
#    incompletas y salta las invalidas sin detener el programa.
# =====================================================================
def leer_empleados_excel(nombre_archivo):
    """Lee empleados desde un Excel y devuelve una lista de objetos Empleado."""
    empleados = []
    df = pd.read_excel(nombre_archivo)

    # Normalizamos los nombres de columna (sin espacios y en minuscula)
    df.columns = [str(c).strip().lower() for c in df.columns]

    # Verificamos que existan las columnas minimas que necesitamos
    columnas_necesarias = {"nombre", "tipo", "salario_base"}
    if not columnas_necesarias.issubset(df.columns):
        faltan = columnas_necesarias - set(df.columns)
        print(f"  [Error] Al Excel le faltan columnas: {faltan}")
        return empleados

    for _, fila in df.iterrows():
        # Saltar filas incompletas (sin nombre, tipo o salario)
        if pd.isna(fila["nombre"]) or pd.isna(fila["tipo"]) or pd.isna(fila["salario_base"]):
            print("  [Aviso] Fila incompleta ignorada.")
            continue

        nombre = str(fila["nombre"]).strip()
        tipo = str(fila["tipo"]).strip().upper()
        salario = fila["salario_base"]
        # 'ciudad' es una columna extra: si no viene, usamos texto vacio
        ciudad = str(fila["ciudad"]).strip() if "ciudad" in df.columns and not pd.isna(fila["ciudad"]) else ""

        try:
            empleado = crear_empleado(nombre, tipo, salario, ciudad)
            if empleado is not None:  # (por si aun no completas crear_empleado)
                empleados.append(empleado)
        except ValueError as error:
            print(f"  [Aviso] Se ignoro {nombre}: {error}")

    return empleados


# =====================================================================
# 5) RETO EXTRA: FUNCIONES PROPIAS
# =====================================================================
def salario_promedio(empleados):
    """Calcula el promedio del salario_base de la nomina.

    Usa el GETTER salario_base de cada objeto (nunca toca _salario_base
    directamente). Si la lista esta vacia devuelve 0 para evitar una
    division por cero.

    Args:
        empleados (list[EmpleadoBase]): empleados validos de la nomina.

    Returns:
        float: salario base promedio, redondeado a 2 decimales.
    """
    if not empleados:
        return 0
    total = sum(empleado.salario_base for empleado in empleados)
    return round(total / len(empleados), 2)


def resumen_nomina(empleados):
    """Construye un resumen gerencial de la nomina (funcion propia).

    Aprovecha el POLIMORFISMO: suma calcular_pago() de cada empleado sin
    preguntar si es de planta o contratista; cada objeto responde con su
    propia formula. Tambien agrupa por tipo (con type(e).__name__) y
    encuentra al empleado con el mayor pago.

    Args:
        empleados (list[EmpleadoBase]): empleados validos de la nomina.

    Returns:
        dict: {
            "total_empleados": int,
            "nomina_total": float,      # lo que paga la empresa al mes
            "por_tipo": {nombre_clase: {"cantidad": int, "pago": float}},
            "mejor_pagado": EmpleadoBase | None,
        }
    """
    resumen = {
        "total_empleados": len(empleados),
        "nomina_total": 0,
        "por_tipo": {},
        "mejor_pagado": None,
    }
    for empleado in empleados:
        pago = empleado.calcular_pago()          # POLIMORFISMO
        resumen["nomina_total"] += pago

        tipo = type(empleado).__name__
        grupo = resumen["por_tipo"].setdefault(tipo, {"cantidad": 0, "pago": 0})
        grupo["cantidad"] += 1
        grupo["pago"] += pago

        mejor = resumen["mejor_pagado"]
        if mejor is None or pago > mejor.calcular_pago():
            resumen["mejor_pagado"] = empleado
    return resumen


# =====================================================================
# 6) Funcion principal
# =====================================================================
def ejecutar_quiz():
    """Lee la nomina, la imprime y muestra los resultados de las funciones propias."""
    empleados = leer_empleados_excel("empleados.xlsx")

    print("--- Nomina ---")
    for empleado in empleados:
        # POLIMORFISMO: la misma llamada, distinto resultado segun el tipo
        print(empleado.obtener_informacion(), "-> pago:", empleado.calcular_pago())

    # Reto: funciones propias
    print("\nSalario promedio:", salario_promedio(empleados))

    resumen = resumen_nomina(empleados)
    print("\n--- Resumen de la nomina ---")
    print(f"Empleados en nomina: {resumen['total_empleados']}")
    for tipo, datos in resumen["por_tipo"].items():
        print(f"  {tipo:<20} {datos['cantidad']:>2} empleados | pago ${datos['pago']:,.0f}")
    print(f"Nomina total mensual: ${resumen['nomina_total']:,.0f}")
    mejor = resumen["mejor_pagado"]
    if mejor is not None:
        print(f"Mejor pagado: {mejor.nombre} ({type(mejor).__name__}) "
              f"-> ${mejor.calcular_pago():,.0f}")


# Iniciar el programa
if __name__ == "__main__":
    ejecutar_quiz()
