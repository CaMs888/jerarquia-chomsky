ChomskyLab – Simulador de la Jerarquía de Chomsky

1. Descripción

ChomskyLab es una aplicación desarrollada en Python que permite visualizar y simular los cuatro niveles de la Jerarquía de Chomsky mediante modelos computacionales.

2. Requisitos

Python 3.

Tkinter.

Visual Studio Code (opcional).

3. Instalación y ejecución

Descargar o clonar el repositorio.

Abrir la carpeta ChomskyLab.

Abrir una terminal.

Ejecutar:

python main.py

4. Módulos disponibles

- Nivel 3 – Autómata Finito Determinista (AFD)

Reconoce cadenas binarias que terminan en 01.

Ejemplos:

1101: aceptada.

1100: rechazada.

01: aceptada.

- Nivel 2 – Autómata de Pila (PDA)

Reconoce el lenguaje aⁿbⁿ mediante operaciones PUSH y POP.

Ejemplos:

aaabbb: aceptada.

aabb: aceptada.

aabbb: rechazada.

- Nivel 1 – Autómata Linealmente Acotado (LBA)

Reconoce el lenguaje aⁿbⁿcⁿ mediante una cinta delimitada.

Ejemplos:

aabbcc: aceptada.

aaabbbccc: aceptada.

aabbccc: rechazada.

- Nivel 0 – Máquina de Turing

Realiza un incremento de números representados en sistema unario.

Ejemplos:

1 → 11.

111 → 1111.

5. Funcionamiento

Cada módulo permite introducir una cadena, iniciar la simulación y observar las transiciones de los estados o los cambios en la memoria.

6. Tecnologías

Python.

Tkinter.

Programación orientada a objetos y estructuras de datos.

7. Autores

Proyecto académico – Ingeniería de Sistemas.