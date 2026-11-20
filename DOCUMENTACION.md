# ChomskyLab: documentación

Proyecto: Sarah Chaves · Autómatas, gramáticas y lenguajes

Explica la teoría que usa el simulador, cómo está construido y por qué cada cadena se acepta o se rechaza. Para instalar y ejecutar, ver `README.md`.

## 1. Marco teórico

### 1.1 Conceptos que usa el simulador

- **Alfabeto:** símbolos permitidos en un nivel (`{0,1}`, `{a,b}`, `{a,b,c}` o `{1}`).
- **Cadena:** secuencia de símbolos del alfabeto. La interfaz no admite la cadena vacía.
- **Lenguaje:** conjunto de cadenas que una máquina debe aceptar. Una cadena fuera del lenguaje sigue siendo una entrada válida: la máquina simplemente la rechaza.
- **Estado, transición y configuración:** la máquina está siempre en un estado; según el símbolo que lee (y su memoria) pasa a otro. Cada clic del simulador avanza una transición.
- **Determinismo:** las cuatro máquinas son deterministas, es decir, cada cadena tiene un único recorrido posible.

### 1.2 La Jerarquía de Chomsky en el simulador

| Nivel | Lenguajes | Máquina | Memoria | Lenguaje que simula |
|---|---|---|---|---|
| 3 | Regulares | AFD | Solo el estado actual | Termina en `01` |
| 2 | Libres de contexto | PDA | Una pila | `a^n b^n` |
| 1 | Sensibles al contexto | LBA | Cinta limitada a la entrada | `a^n b^n c^n` |
| 0 | Recursivamente enumerables | Máquina de Turing | Cinta ilimitada | Incremento unario |

Cada nivel incluye al anterior y tiene más memoria, y por eso reconoce lenguajes que el de abajo no puede.

### 1.3 Cuándo se acepta y cuándo se rechaza

Una cadena se **acepta** si la máquina consume toda la cadena y termina en un estado de aceptación (doble círculo en el dibujo). Se **rechaza** en cualquier otro caso:

| Forma de rechazo | Dónde se ve |
|---|---|
| Termina la cadena en un estado que no es de aceptación | AFD |
| La máquina se bloquea: no existe transición para lo que lee | PDA (`a` después de `b`, `b` con la pila vacía) y LBA (letra inesperada) |
| Termina la cadena, pero la memoria quedó mal | PDA (la pila no vuelve a `Z0`) y LBA (sobran letras sin marcar) |

La aceptación se decide **solo al final**. Pasar por un estado de aceptación a mitad de camino no cuenta (ejemplo: `1010` en el AFD).

### 1.4 Por qué cada lenguaje está en su nivel

- **Termina en `01` (regular).** Basta recordar los dos últimos símbolos, que es información finita: tres estados alcanzan.
- **`a^n b^n` (libre de contexto, no regular).** Hay que comparar cuántas `a` y cuántas `b` hay, y `n` no tiene límite. Un AFD solo tiene un número finito de estados y no puede contar sin tope; una pila sí: cada `a` apila una `A` y cada `b` la desapila.
- **`a^n b^n c^n` (sensible al contexto, no libre de contexto).** Una pila compara dos cantidades, pero al desapilar para las `b` pierde la cuenta que haría falta para las `c`. Un LBA lo resuelve marcando letras sobre la cinta y recorriéndola en ambos sentidos.
- **Incremento unario (nivel 0).** La máquina deja de ser solo un reconocedor: escribe en la cinta y calcula `n + 1`.

## 2. Cómo funciona el simulador

### 2.1 Estructura del programa

El programa está en un solo archivo, `chomskylab.py`, hecho con `tkinter`.

| Clase | Qué hace |
|---|---|
| `ScrollableFrame` | Zona con desplazamiento vertical que se adapta a la ventana |
| `FlowFrame` | Reparte los botones de ejemplos en varias filas si no caben |
| `ModuleUI` | Lee y valida la cadena, muestra la alerta, carga ejemplos y controla los botones |
| `ChomskyLab` | Ventana, menú principal, diseño común, dibujo y los cuatro módulos |

Cada módulo (`module_afd`, `module_pda`, `module_lba`, `module_tm`) sigue el mismo patrón:

| Elemento | Función |
|---|---|
| `state` | Diccionario con toda la configuración de la máquina |
| `draw()` / `render()` | Dibujan el estado actual en el lienzo y actualizan la línea de texto |
| `reset_state(word)` | Deja la máquina en su configuración inicial |
| `start()`, `restart()`, `clear_all()` | Acciones de *Iniciar* (y Enter), *Reiniciar* y *Borrar todo* |
| `step()` | Ejecuta una sola transición y la anota en el registro |

### 2.2 Qué pasa al pulsar Iniciar

1. Si ya hay una simulación en curso, se ignora la acción.
2. Si la cadena está vacía o tiene símbolos fuera del alfabeto, aparece la ventana de **Error** y no inicia.
3. Si la cadena no pertenece al lenguaje del nivel, aparece la **alerta** (sección 2.3).
4. Se prepara la máquina y cada clic en *Siguiente ...* ejecuta un paso hasta llegar a **CADENA ACEPTADA** o **CADENA RECHAZADA**.

El botón *Iniciar* queda inactivo mientras la simulación está en curso, y vuelve a estar disponible cuando termina, o al pulsar *Reiniciar* o *Borrar todo*.

### 2.3 Por qué salta la alerta y por qué se puede continuar

La alerta "La cadena no cumple la condicion" aparece cuando la cadena usa símbolos válidos pero **no pertenece al lenguaje** del nivel. Cada módulo tiene su propia comprobación:

| Nivel | La alerta salta si... | Mensaje |
|---|---|---|
| AFD | La cadena no termina en `01` | La cadena no termina en 01. |
| PDA | La cadena no es `a^n b^n` | La cadena no cumple el patron a^n b^n. |
| LBA | La cadena no es `a^n b^n c^n` | La cadena no cumple el patron a^n b^n c^n. |
| MT | Nunca: toda cadena de unos es válida | (no hay alerta) |

Existe por dos razones: avisar de antemano que la máquina va a rechazar la cadena (en el LBA, `aabbc` necesita 16 clics para llegar al rechazo) y dar la oportunidad de corregir un error de digitación con **Cambiar cadena**.

Se puede **Continuar** porque ver cómo la máquina rechaza es tan importante como ver cómo acepta: cada rechazo tiene un motivo concreto que se observa paso a paso. La alerta solo avisa; quien decide si la cadena se acepta es siempre la simulación. Las comprobaciones coinciden con las máquinas: la alerta salta exactamente en las cadenas que la máquina va a rechazar (se comprobó con todas las cadenas hasta 12 símbolos en el AFD y el PDA, y hasta 9 en el LBA).

## 3. Nivel 3: AFD (termina en `01`)

Estados `q0`, `q1`, `q2`; estado inicial `q0`; estado de aceptación `q2`.

| Estado | Lee `0` | Lee `1` | Significa |
|---|---|---|---|
| `q0` | `q1` | `q0` | Aún no hay un `0` útil al final |
| `q1` | `q1` | `q2` | El último símbolo fue `0` |
| `q2` | `q1` | `q0` | Los dos últimos símbolos fueron `01` |

La máquina lee un símbolo por clic y, cuando se acaba la cadena, un clic más da el veredicto: se acepta si está en `q2`.

| Cadena | Recorrido | Resultado | Por qué |
|---|---|---|---|
| `1101` | `q0 → q0 → q0 → q1 → q2` | ACEPTADA | Termina en `01`, así que acaba en `q2` |
| `01` | `q0 → q1 → q2` | ACEPTADA | Es exactamente `01` |
| `0001` | `q0 → q1 → q1 → q1 → q2` | ACEPTADA | Termina en `01` |
| `10` (saltar alerta) | `q0 → q0 → q1` | RECHAZADA | Termina en `0`: falta el `1` final, queda en `q1` |
| `100` (saltar alerta) | `q0 → q0 → q1 → q1` | RECHAZADA | Termina en `00`, queda en `q1` |
| `1010` (saltar alerta) | `q0 → q0 → q1 → q2 → q1` | RECHAZADA | Pasa por `q2`, pero el último `0` la devuelve a `q1` |

## 4. Nivel 2: PDA (`a^n b^n`)

Estados `q0` (apilando), `q1` (desapilando) y `qA` (aceptación). La pila empieza con `Z0` en el fondo.

| Lee | Condición | Acción |
|---|---|---|
| `a` | Todavía no se ha leído ninguna `b` | Apila una `A` |
| `a` | Ya se empezó a desapilar | **Rechaza:** No se permiten a despues de b. |
| `b` | Hay una `A` en la pila | Desapila una `A` y pasa a `q1` |
| `b` | Solo queda `Z0` | **Rechaza:** No hay elementos para desapilar. |
| (fin) | Pila en `Z0` y se leyó al menos una `b` | **Acepta** (`qA`) |
| (fin) | Quedan `A` en la pila | **Rechaza:** La pila no termino correctamente. |

| Cadena | Qué ocurre | Resultado | Por qué |
|---|---|---|---|
| `aaabbb` | Apila 3 `A` y desapila 3 | ACEPTADA | 3 `a` seguidas de 3 `b`; la pila vuelve a `Z0` |
| `ab` | Apila 1 y desapila 1 | ACEPTADA | 1 `a` y 1 `b` |
| `aabb` | Apila 2 y desapila 2 | ACEPTADA | 2 `a` y 2 `b` |
| `aba` (saltar alerta) | Apila, desapila y la `a` final llega ya desapilando | RECHAZADA | Una `a` después de una `b` rompe el orden `a...b...` |
| `abab` (saltar alerta) | Igual, se detiene en el tercer símbolo | RECHAZADA | Misma razón: la segunda `a` llega después de una `b` |
| `ba` (saltar alerta) | La primera `b` llega con la pila en `Z0` | RECHAZADA | Hay una `b` sin ninguna `a` antes |

Las tres formas de rechazo corresponden a las tres condiciones del lenguaje: el orden (`aba`), que no sobren `b` (`ba`, `abb`) y que no sobren `a` (`aab`, `aaa`). Los dos últimos grupos no están en los botones, pero se pueden escribir para verlos.

## 5. Nivel 1: LBA (`a^n b^n c^n`)

La cinta se cierra con fronteras `#` (para `abc` queda `#abc#`) y el cabezal no puede salir de ellas. La máquina usa solo las operaciones vistas en clase:

| Operación | En el programa |
|---|---|
| **Inicio** | Se arma la cinta `#` + cadena + `#`, con el cabezal en la primera letra y la fase `q0` |
| **Leer** | Se lee el símbolo bajo el cabezal |
| **Marcar** | Se cambia una letra por su mayúscula (`a → A`, `b → B`, `c → C`) |
| **Mover izquierda / derecha** | El cabezal retrocede o avanza una celda |
| **Final** | La máquina termina en `qA` (acepta) o `qR` (rechaza) |

La máquina trabaja por **rondas**: en cada una marca una `a`, la primera `b` sin marcar y la primera `c` sin marcar, y vuelve a la frontera izquierda. Cuando ya no quedan `a`, verifica que solo queden marcas.

| Fase | Qué hace | Rechaza con |
|---|---|---|
| `q0` | Salta las `A` y marca la siguiente `a`; si no hay más `a`, pasa a `q4` | No se encontro una a valida. |
| `q1` | Avanza hasta la primera `b` y la marca | Falta una b correspondiente. |
| `q2` | Avanza hasta la primera `c` y la marca | Falta una c correspondiente. |
| `q3` | Regresa a la frontera izquierda `#` | (no rechaza) |
| `q4` | Recorre la cinta comprobando que solo haya marcas; al llegar a `#` acepta | Quedaron letras sin emparejar. |

Si la cadena es `a^n b^n c^n`, las `n` rondas encuentran su `b` y su `c`, y no sobra nada. Si no, alguna fase falla. Una cadena aceptada tarda `5n² + 4n + 2` clics (11 para `n = 1`, 30 para `n = 2`, 59 para `n = 3`).

| Cadena | Qué ocurre | Resultado | Por qué |
|---|---|---|---|
| `aabbcc` | 2 rondas y verificación sin sobrantes | ACEPTADA | 2 `a`, 2 `b` y 2 `c` en orden |
| `abc` | 1 ronda y verificación | ACEPTADA | 1 de cada letra |
| `aaabbbccc` | 3 rondas y verificación | ACEPTADA | 3 de cada letra en orden |
| `abcc` (saltar alerta) | La ronda 1 empareja `a`, `b`, `c`; en `q4` aparece otra `c` sin marcar (clic 11) | RECHAZADA | Sobra una `c`: Quedaron letras sin emparejar. |
| `aabbc` (saltar alerta) | La ronda 2 no encuentra su `c` y `q2` llega a `#` (clic 16) | RECHAZADA | Falta una `c`: Falta una c correspondiente. |
| `cba` (saltar alerta) | `q0` lee `c` y no hay ninguna `a` (clic 1) | RECHAZADA | No empieza con `a`: No se encontro una a valida. |

## 6. Nivel 0: Máquina de Turing (incremento unario)

El número `n` se escribe como `n` unos y la máquina deja `n + 1` unos. La cinta es la cadena seguida de tres blancos `B` (para `111`: `1 1 1 B B B`), con el cabezal en la posición 0.

| Estado | Lee | Acción |
|---|---|---|
| `q0` | `1` | Se mueve a la derecha |
| `q0` | `B` | Escribe `1` y pasa a `qA` (termina) |

Con entrada `1^n` la máquina avanza sobre los `n` unos, encuentra el primer blanco y escribe ahí un `1`. No existe ninguna entrada de unos que la bloquee, por eso aquí no hay cadenas rechazadas ni alerta: el veredicto siempre es **OPERACION COMPLETADA**. Una entrada de `n` unos necesita `n + 1` clics.

| Cadena | Cinta final | Resultado |
|---|---|---|
| `111` | `1 1 1 1 B B` | `1111` (3 + 1 = 4) |
| `1` | `1 1 B B` | `11` (1 + 1 = 2) |
| `11` | `1 1 1 B B` | `111` (2 + 1 = 3) |
| `1111` | `1 1 1 1 1 B B` | `11111` (4 + 1 = 5) |
| `11111` | `1 1 1 1 1 1 B B` | `111111` (5 + 1 = 6) |

## 7. Referencias

- Hopcroft, J. E., Motwani, R. y Ullman, J. D. (2007). Introducción a la teoría de autómatas, lenguajes y computación (3.ª ed.). Pearson Educación.
- Martin, J. C. (2004). Lenguajes formales y teoría de la computación (3.ª ed.). McGraw-Hill.
- Kelley, D. (1995). Teoría de autómatas y lenguajes formales. Prentice Hall.
- Python Software Foundation. tkinter — Interface de Python para Tcl/Tk. Documentación oficial de Python en español: https://docs.python.org/es/3/library/tkinter.html