Documentación técnica – ChomskyLab

1. Introducción

La Jerarquía de Chomsky clasifica las gramáticas formales en cuatro niveles, según su capacidad de generación de lenguajes y los modelos computacionales asociados.

2. Objetivo general

Diseñar e implementar una aplicación gráfica que permita visualizar y simular los modelos computacionales correspondientes a los cuatro niveles de la Jerarquía de Chomsky.

3. Fundamentos teóricos

3.1 Tipo 3 – Lenguajes regulares

Se utiliza un Autómata Finito Determinista (AFD), compuesto por estados, un alfabeto, una función de transición, un estado inicial y estados finales.

3.2 Tipo 2 – Lenguajes independientes del contexto

Se utiliza un Autómata de Pila (PDA), que incorpora memoria LIFO para almacenar y retirar símbolos.

3.3 Tipo 1 – Lenguajes sensibles al contexto

Se utiliza una Máquina Linealmente Acotada (LBA), cuya cinta de trabajo está limitada por la longitud de la entrada.

3.4 Tipo 0 – Lenguajes recursivamente enumerables

Se utiliza una Máquina de Turing (MT), que dispone de una cinta de lectura y escritura y un cabezal que permite desplazamientos.

4. Tecnologías utilizadas

Python 3.

Tkinter para la interfaz gráfica.

Diccionarios para representar transiciones.

Listas para representar pilas y cintas.

Funciones para controlar las simulaciones.

5. Implementación

5.1 Módulo AFD

Se implementa un conjunto de estados y transiciones para reconocer cadenas binarias que terminan en 01.

5.2 Módulo PDA

Se utiliza una pila para almacenar las letras a y retirarlas al procesar las letras b.

5.3 Módulo LBA

Se utiliza una cinta delimitada y símbolos auxiliares para marcar las letras que ya fueron emparejadas.

5.4 Módulo Máquina de Turing

Se implementa una cinta con espacios en blanco y un cabezal que recorre la entrada hasta encontrar una posición vacía y escribir un nuevo símbolo.

6. Pruebas

Se realizan pruebas con cadenas válidas e inválidas para verificar el comportamiento de cada modelo.

7. Conclusiones

El proyecto permite comprender las diferencias entre los modelos computacionales de la Jerarquía de Chomsky, especialmente sus mecanismos de memoria, transiciones y reconocimiento de lenguajes.
