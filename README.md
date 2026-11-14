# ChomskyLab

Simulador interactivo de la **Jerarquía de Chomsky**. Cada nivel tiene su propio módulo con diagrama, animación paso a paso y registro de lo que hace la máquina.

| Nivel | Modelo | Lenguaje u operación que simula |
|---|---|---|
| 3 | AFD (autómata finito determinista) | Cadenas binarias que terminan en `01` |
| 2 | PDA (autómata de pila) | `a^n b^n` |
| 1 | LBA (autómata linealmente acotado) | `a^n b^n c^n` |
| 0 | Máquina de Turing | Incremento en representación unaria |

La explicación de la teoría y de la implementación está en [`documentation.md`](documentation.md) (también disponible como `Documentacion_ChomskyLab.docx`).

---

## 1. Requisitos

| Componente | Versión | Notas |
|---|---|---|
| Python | 3.8 o superior (recomendado 3.10 o superior) | Instalador estándar de python.org |
| Tkinter / Tk | 8.6 | Viene incluido en los instaladores de Python para Windows y macOS |
| Librerías externas | Ninguna | Solo se usa la biblioteca estándar (`tkinter` y `math`) |
| Sistema operativo | Windows 10/11 (recomendado), macOS o Linux | El diseño usa las fuentes Segoe UI y Consolas; en otros sistemas Tk las sustituye y el aspecto puede variar un poco |
| Pantalla | Ventana mínima de 640 x 520 px | La ventana se adapta al tamaño de la pantalla |

Para comprobar lo que tienes instalado, abre una terminal y ejecuta:

```
python --version
python -m tkinter
```

El segundo comando debe abrir una ventana pequeña de prueba de Tk. Si aparece un error `No module named tkinter`, instala Tkinter:

- **Windows / macOS:** vuelve a ejecutar el instalador de Python desde python.org y deja marcada la opción *tcl/tk and IDLE*.
- **Ubuntu / Debian:** `sudo apt install python3-tk`
- **Fedora:** `sudo dnf install python3-tkinter`

## 2. Cómo ejecutar el proyecto

1. Descarga o clona el repositorio y entra a la carpeta del proyecto.
2. Abre una terminal en esa carpeta.
3. Ejecuta:

```
python chomskylab.py
```

En Windows también funciona `py chomskylab.py`; en macOS y Linux, `python3 chomskylab.py`. No hace falta instalar nada más ni crear entornos virtuales.

## 3. Cómo se usa

1. En el menú principal pulsa **Abrir modulo** en el nivel que quieras explorar.
2. Escribe una cadena y pulsa **Enter** o el botón **Iniciar**. También puedes pulsar uno de los **Ejemplos rapidos**: se carga la cadena e inicia la simulación con un solo clic.
3. Pulsa el botón de avance (**Siguiente simbolo**, **Siguiente transicion** o **Siguiente movimiento**) para ejecutar un paso. En el diagrama se resalta el estado actual y en el registro de abajo queda cada paso.
4. Al terminar aparece **CADENA ACEPTADA** o **CADENA RECHAZADA** (en la Máquina de Turing, **OPERACION COMPLETADA**).

### Botones

| Botón | Qué hace | Cuándo está activo |
|---|---|---|
| **Iniciar** | Valida la cadena y arranca la simulación | Solo cuando no hay una simulación en curso |
| **Reiniciar** | Repite la simulación con la misma cadena | Después de iniciar |
| **Siguiente ...** | Ejecuta un paso | Mientras la simulación está en curso |
| **Borrar todo** | Limpia la cadena, el dibujo, el estado y el registro para probar otra cadena sin salir del módulo | Siempre |
| **< Volver al inicio** | Regresa al menú principal | Siempre |

Después de pulsar **Iniciar**, el botón queda inactivo hasta que la simulación termine o hasta que pulses **Reiniciar** o **Borrar todo**.

### La alerta "La cadena no cumple la condicion"

Si la cadena escrita no pertenece al lenguaje del nivel (por ejemplo, `10` en el AFD, que no termina en `01`), aparece una alerta con dos opciones:

- **Cambiar cadena**: cierra la alerta y deja la cadena seleccionada para editarla.
- **Continuar**: ejecuta la simulación de todos modos, para ver cómo la máquina rechaza la cadena.

En las listas de abajo, las cadenas marcadas con **(saltar alerta)** son las que la máquina va a rechazar: al cargarlas debes pulsar **Continuar** en la alerta para ver el rechazo.

Si la cadena contiene símbolos que no pertenecen al alfabeto del nivel (por ejemplo, un `2` en el AFD), se muestra una ventana de **Error** y la simulación no inicia.

## 4. Cadenas de prueba por nivel

Son los mismos ejemplos que aparecen como botones en la interfaz, en el mismo orden.

### Nivel 3 – AFD (cadenas binarias que terminan en `01`)

Alfabeto: `0` y `1`. Estado final: `q2`.

| Cadena | Resultado esperado | Por qué |
|---|---|---|
| `1101` | ACEPTADA | Termina en `01` |
| `01` | ACEPTADA | Termina en `01` |
| `0001` | ACEPTADA | Termina en `01` |
| `10` (saltar alerta) | RECHAZADA | Termina en `10`; la máquina queda en `q1` |
| `100` (saltar alerta) | RECHAZADA | Termina en `00`; la máquina queda en `q1` |
| `1010` (saltar alerta) | RECHAZADA | Termina en `10`; la máquina queda en `q1` |

### Nivel 2 – PDA (`a^n b^n`)

Alfabeto: `a` y `b`. Cada `a` se apila y cada `b` desapila una `a`.

| Cadena | Resultado esperado | Por qué |
|---|---|---|
| `aaabbb` | ACEPTADA | 3 `a` seguidas de 3 `b`; la pila queda en `Z0` |
| `ab` | ACEPTADA | 1 `a` y 1 `b` |
| `aabb` | ACEPTADA | 2 `a` y 2 `b` |
| `aba` (saltar alerta) | RECHAZADA | Aparece una `a` después de una `b` |
| `abab` (saltar alerta) | RECHAZADA | Aparece una `a` después de una `b` |
| `ba` (saltar alerta) | RECHAZADA | La `b` llega con la pila vacía, no hay nada que desapilar |

### Nivel 1 – LBA (`a^n b^n c^n`)

Alfabeto: `a`, `b` y `c`. La cinta queda delimitada por `#` y la máquina marca una `a`, una `b` y una `c` en cada ronda.

| Cadena | Resultado esperado | Por qué |
|---|---|---|
| `aabbcc` | ACEPTADA | 2 `a`, 2 `b` y 2 `c` en orden |
| `abc` | ACEPTADA | 1 de cada letra |
| `aaabbbccc` | ACEPTADA | 3 de cada letra en orden |
| `abcc` (saltar alerta) | RECHAZADA | Sobra una `c`: "Quedaron letras sin emparejar." |
| `aabbc` (saltar alerta) | RECHAZADA | Falta una `c`: "Falta una c correspondiente." |
| `cba` (saltar alerta) | RECHAZADA | No empieza con `a`: "No se encontro una a valida." |

### Nivel 0 – Máquina de Turing (incremento unario)

Alfabeto: solo `1`. El número `n` se escribe como `n` unos y la máquina le suma uno. Aquí **ninguna cadena activa la alerta**, porque cualquier cadena de unos es una entrada válida.

| Cadena | Resultado esperado |
|---|---|
| `111` | `1111` (3 + 1 = 4) |
| `1` | `11` (1 + 1 = 2) |
| `11` | `111` (2 + 1 = 3) |
| `1111` | `11111` (4 + 1 = 5) |
| `11111` | `111111` (5 + 1 = 6) |


---


Sarah Chaves - Automatas, Lenguajes y Gramaticas