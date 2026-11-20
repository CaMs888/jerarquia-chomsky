# ChomskyLab
 
Simulador interactivo de la **Jerarquía de Chomsky**. Cada nivel tiene su propio módulo con diagrama, animación paso a paso y registro de lo que hace la máquina.
 
| Nivel | Modelo | Lenguaje u operación que simula |
|---|---|---|
| 3 | AFD (autómata finito determinista) | Cadenas binarias que terminan en `01` |
| 2 | PDA (autómata de pila) | `a^n b^n` |
| 1 | LBA (autómata linealmente acotado) | `a^n b^n c^n` |
| 0 | Máquina de Turing | Incremento en representación unaria |
 
La explicación de la teoría, de la implementación y de por qué cada cadena se acepta o se rechaza está en [`documentation.md`](documentation.md).
 
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
En `documentation.md`, las cadenas marcadas con **(saltar alerta)** son las que la máquina va a rechazar: al cargarlas debes pulsar **Continuar** en la alerta para ver el rechazo.
 
Si la cadena contiene símbolos que no pertenecen al alfabeto del nivel (por ejemplo, un `2` en el AFD), se muestra una ventana de **Error** y la simulación no inicia.
 
## 4. Cadenas de prueba
 
Cada módulo trae sus propios **Ejemplos rapidos** como botones: un clic carga la cadena e inicia la simulación. En [`documentation.md`](documentation.md) se indica, nivel por nivel, cuáles de esos ejemplos son aceptados y cuáles rechazados, y la razón de cada resultado.
 
## 5. Solución de problemas
 
| Problema | Solución |
|---|---|
| `ModuleNotFoundError: No module named 'tkinter'` | Instala Tkinter como se indica en la sección 1 |
| `python` no se reconoce como comando | En Windows usa `py chomskylab.py`; en macOS y Linux usa `python3 chomskylab.py` |
| La letra se ve distinta que en Windows | En macOS y Linux no existen las fuentes Segoe UI y Consolas; Tk usa otras y el aspecto cambia un poco, sin afectar el funcionamiento |
| No veo los botones de abajo | Agranda la ventana; la zona central tiene barra de desplazamiento y los botones de control quedan siempre fijos en la parte inferior |
 
## 6. Contenido del repositorio
 
| Archivo | Descripción |
|---|---|
| `chomskylab.py` | Código fuente completo de la aplicación |
| `README.md` | Este manual de usuario |
| `documentation.md` | Documentación: marco teórico, implementación, alerta de validación y por qué cada cadena se acepta o se rechaza |
 
---
 
Proyecto: Sarah Chaves · Autómatas, gramáticas y lenguajes
 