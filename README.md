# Quiz Semana 3 — Pilares de POO y Principios SOLID (SRP/OCP)

**Autor:** Nicolás Camargo Franco · Ingeniería de Sistemas · Fundación Universitaria CEIPA
**Curso:** Fundamentos de Software

Nómina de una empresa leída desde `empleados.xlsx` (24 filas, 12 columnas). El programa
aplica los tres pilares de la Programación Orientada a Objetos y los principios SRP y OCP.

## Cómo ejecutar

```bash
pip install -r requirements.txt
python quiz_nomina.py
```

## 1. Pilares de POO aplicados

| Pilar | Dónde está | Qué resuelve |
|---|---|---|
| **Encapsulamiento** | `EmpleadoBase`: atributo privado `_salario_base`, *getter* `@property` y *setter* `@salario_base.setter` | El setter valida **antes** de guardar: rechaza salarios negativos (`Sofía, -100`) y no numéricos (`Felipe, "no aplica"`). Como el constructor asigna con `self.salario_base = ...`, ningún objeto puede nacer con un salario inválido. El cero sí se acepta (`Santiago`). |
| **Herencia** | `EmpleadoPlanta(EmpleadoBase)` y `EmpleadoContratista(EmpleadoBase)` | El constructor, el getter, el setter y `obtener_informacion()` se escriben **una sola vez** en la clase padre. Las hijas solo agregan lo que las diferencia. |
| **Polimorfismo** | `calcular_pago()` sobreescrito en cada hija | Planta = salario + 30 % de prestaciones; Contratista = solo salario. El bucle de `ejecutar_quiz()` llama `empleado.calcular_pago()` **sin un solo `if`** por tipo: cada objeto responde con su fórmula. |

## 2. Principios SOLID

- **SRP (Responsabilidad Única).** Cada pieza hace una sola cosa: las clases modelan al
  empleado y su pago, `crear_empleado()` decide qué clase instanciar, `leer_empleados_excel()`
  solo lee el archivo, y `salario_promedio()` / `resumen_nomina()` solo calculan estadísticas.
  Si cambia el formato del Excel, solo se toca la lectura; si cambian las prestaciones, solo
  se toca `EmpleadoPlanta`.
- **OCP (Abierto/Cerrado).** Los tipos están registrados en el diccionario `TIPOS_EMPLEADO`.
  Para soportar un tipo nuevo (por ejemplo `TEMPORAL`, hoy rechazado en la fila de Gabriela)
  basta con crear `class EmpleadoTemporal(EmpleadoBase)` con su `calcular_pago()` y agregar
  una línea al registro. **No se modifica** `EmpleadoBase`, ni `crear_empleado()`, ni el
  bucle principal: el código está abierto a la extensión y cerrado a la modificación.

## 3. Reto: funciones propias

- `salario_promedio(empleados)` → promedio de `salario_base` (usa el getter; evita la
  división por cero si la lista está vacía).
- `resumen_nomina(empleados)` → resumen gerencial: nómina total mensual, cantidad y pago por
  tipo de empleado y empleado mejor pagado. Usa polimorfismo: suma `calcular_pago()` sin
  preguntar el tipo de cada objeto.

## 4. Robustez: filas inválidas

| Fila | Problema | Quién lo detecta |
|---|---|---|
| Sofía | salario `-100` | el **setter** (`ValueError`) |
| *(sin nombre)* | fila incompleta | la lectura (`pd.isna`) |
| Gabriela | tipo `TEMPORAL` | `crear_empleado()` (`ValueError`) |
| Felipe | salario `"no aplica"` | el **setter** (`int()` falla) |
| Sara | sin tipo | la lectura (`pd.isna`) |

De 24 filas quedan **19 empleados** válidos.

## 5. Salida obtenida

```
  [Aviso] Se ignoro Sofia: El salario no puede ser negativo.
  [Aviso] Fila incompleta ignorada.
  [Aviso] Se ignoro Gabriela: tipo desconocido 'TEMPORAL'
  [Aviso] Se ignoro Felipe: invalid literal for int() with base 10: 'no aplica'
  [Aviso] Fila incompleta ignorada.
--- Nomina ---
Ana | EmpleadoPlanta | Medellin | base $3000000 -> pago: 3900000.0
Luis | EmpleadoContratista | Bogota | base $2500000 -> pago: 2500000
...
Santiago | EmpleadoContratista | Cali | base $0 -> pago: 0
Emilio | EmpleadoPlanta | Medellin | base $3300000 -> pago: 4290000.0

Salario promedio: 3273684.21

--- Resumen de la nomina ---
Empleados en nomina: 19
  EmpleadoPlanta       11 empleados | pago $54,210,000
  EmpleadoContratista   8 empleados | pago $20,500,000
Nomina total mensual: $74,710,000
Mejor pagado: Ricardo (EmpleadoPlanta) -> $7,930,000
```
