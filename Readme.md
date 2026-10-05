# Guía del Taller SOLID Race Lab

Ingeniería de Software II · Universidad Nacional de Colombia · 2026-2



## 1\. ¿De qué trata todo esto?

### 1.1 Los dos documentos

* **Material-Estudio-SOLID.pdf**: una guía teórica de una página por principio, con ejemplos "antes / después" usando el código de carreras de vehículos.
* **Taller-SOLID-Enunciado.pdf**: el taller práctico (*SOLID Race Lab*). Son 5 ejercicios en Python, uno por principio. Cada uno se resuelve completando código, se ve correr en la terminal (la carrera se anima) y se valida con `pytest`.

### 1.2 Objetivo del taller

Al terminar, deberías poder:

1. **Reconocer** la violación de cada principio SOLID en código existente.
2. **Explicar** por qué es un problema.
3. **Refactorizar o extender** el código para arreglarlo, sin romper el programa.

### 1.3 Preparación (Setup)

```bash
git clone <repositorio-solid-race-lab>   # la rama main ya trae los ejercicios
cd solid-race-lab
python3 -m venv .venv
source .venv/bin/activate                # en Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
```

Lee el `README.md` una vez: explica cómo correr cada demo visual y sus pruebas.

### 1.4 Flujo de cada ejercicio

1. Abre el archivo en `exercises/` y lee el docstring (problema + lista de TODOs).
2. Completa los TODOs **en ese mismo archivo**.
3. **No modifiques `engine/track.py`.**
4. Corre la demo: `python -m exercises.exN\_xxx`
5. Corre las pruebas: `pytest tests/test\_exN\_xxx.py -v`

Un ejercicio está terminado cuando las pruebas pasan **y** la demo corre sin errores ni comportamientos raros (sin crashes, sin vehículos que retroceden, etc.).

\---

## 2\. Qué es SOLID

Cinco pautas de diseño orientado a objetos, nombradas por Robert C. Martin. No son leyes: son reglas prácticas que cuestan un poco más de estructura hoy a cambio de mucho menos dolor cuando cambien los requisitos.

|Letra|Principio|Idea en una frase|
|-|-|-|
|**S**|Single Responsibility|Una clase, **una razón para cambiar**.|
|**O**|Open/Closed|Abierto a extensión, **cerrado a modificación**.|
|**L**|Liskov Substitution|Una subclase debe poder **reemplazar a su clase base** sin romper nada.|
|**I**|Interface Segregation|Mejor **varias interfaces pequeñas** que una gigante.|
|**D**|Dependency Inversion|Depender de **abstracciones**, no de clases concretas.|

\---

## 3\. Ejercicio 1: SRP (Single Responsibility Principle)

### Teoría

Una clase debe tener una sola responsabilidad, es decir, un solo motivo para cambiar. Si una clase mezcla trabajos no relacionados (calcular, imprimir, guardar en archivo), un cambio en uno puede romper los otros, y la clase se vuelve difícil de leer, probar y reutilizar. Síntoma clásico: dos personas editan el mismo archivo por razones distintas.

Preguntas de autoevaluación:

* Si describo la clase en una frase, ¿aparece la palabra "y"?
* ¿Quién me pediría cambiar esta clase? ¿Es más de un tipo de persona o preocupación?

### Problema

`Car.move()` hace tres cosas: (1) actualiza su estado, (2) imprime su estado en consola (presentación), (3) escribe resultados en un archivo de log (persistencia).

### Qué hacer

* Dejar `Car` solo con estado y movimiento.
* Crear `RaceLogger` con `record(tick, racers)`, `save(path)` y `entries`.
* Pasar `RaceLogger.record` como callback `on\_tick` a `Track.run(...)` y llamar `logger.save()` al terminar la carrera.

### Solución (boceto)

```python
class Car(Vehicle):
    def move(self):
        self.position += self.speed        # solo estado y movimiento


class RaceLogger:
    def \_\_init\_\_(self):
        self.entries = \[]

    def record(self, tick, racers):
        for r in racers:
            self.entries.append((tick, r.name, r.position))

    def save(self, path):
        with open(path, "w") as f:
            for tick, name, pos in self.entries:
                f.write(f"{tick},{name},{pos}\\n")


def main():
    logger = RaceLogger()
    track = Track(length=30)
    track.run(racers, on\_tick=logger.record)
    logger.save("log.txt")
```

> La impresión en consola la hace el motor (`Track`), que no se debe tocar. `Car` simplemente deja de imprimir.

### Pregunta de discusión

**¿Por qué es mejor que `Car` no sepa nada de logging ni de impresión? ¿Qué se rompería primero si un profesor pide guardar en JSON?**

* Un carro es una entidad de la carrera: su trabajo es moverse. Cómo se muestra o se guarda son preocupaciones distintas que cambian por razones distintas (formato, destino, idioma).
* Si `Car` hace todo, cambiar el formato obliga a editar `Car.move()`, que ya está probada y es el núcleo de la simulación. Un error al tocar el log podría dañar el movimiento.
* Además, la clase es más fácil de probar: se puede probar `move()` sin crear archivos ni capturar la salida.
* **Con el diseño original, lo primero que se rompería** es `Car.move()` mismo: habría que reescribir la parte de `open("log.txt")` y `f.write(...)` dentro de él, y todas las pruebas que dependen de `Car` quedarían expuestas al cambio. Con el diseño nuevo solo se cambia `RaceLogger.save` (o se crea un `JsonRaceLogger`) y `Car` ni se entera.

\---

## 4\. Ejercicio 2: OCP (Open/Closed Principle)

### Teoría

Debes poder agregar comportamiento nuevo **sin editar código ya existente y probado**. Si cada caso nuevo (un vehículo, una profesión) obliga a editar una cadena `if/elif`, cada edición arriesga romper casos que ya funcionaban. El polimorfismo permite añadir el caso como **código nuevo**.

Preguntas de autoevaluación:

* Para soportar un caso nuevo, ¿edito una clase existente o agrego una nueva?
* ¿`Track.run` necesita conocer cada tipo de vehículo por nombre?

### Problema

`Vehicle`, `Car` y `Truck` están completos y **no se deben tocar**. `Motorcycle` y `Bicycle` están incompletos.

### Qué hacer

* `Motorcycle.move()`: paso que varía notablemente de tick a tick (rápida pero errática).
* `Bicycle.move()`: el paso se reduce con el tiempo (el ciclista se cansa) pero **nunca baja de 1**.
* Todo mediante código nuevo en las subclases.

### Solución (boceto)

```python
import random

class Motorcycle(Vehicle):
    def move(self):
        self.position += random.randint(1, 8)      # varía mucho en cada tick


class Bicycle(Vehicle):
    def \_\_init\_\_(self, \*args, \*\*kwargs):
        super().\_\_init\_\_(\*args, \*\*kwargs)
        self.ticks = 0

    def move(self):
        self.ticks += 1
        step = max(1, 4 - self.ticks // 5)         # decrece, mínimo 1
        self.position += step
```

### Pregunta de discusión

**Si sentiste que tenías que editar `Vehicle` o `Track` para terminarlo, ¿qué dice eso de tu diseño?**

Dice que el diseño **no está realmente abierto a extensión**: la abstracción (`Vehicle`) no captura bien lo que varía, o `Track` conoce detalles de tipos concretos. En un diseño bien hecho, `Track` solo habla con la interfaz común (`move()`, `position`), así que un vehículo nuevo se agrega como una subclase más. Si necesitas tocar lo existente, hay un acoplamiento oculto (por ejemplo, un `if tipo == ...`) que conviene corregir.

\---

## 5\. Ejercicio 3: LSP (Liskov Substitution Principle)

### Teoría

Un objeto de una subclase debe poder usarse donde se espera la clase base **sin alterar la corrección del programa**. La subclase debe respetar el contrato (precondiciones, postcondiciones, invariantes). Estas violaciones son difíciles de ver en una revisión de código y dolorosas en producción: todo el código escrito contra la clase base queda en riesgo sin haber sido avisado.

Preguntas de autoevaluación:

* ¿Qué promete la clase base a quienes la usan, implícita o explícitamente?
* ¿Puedo cambiar esta subclase en cualquier lugar donde se espere la base sin que nada lo note?

### Problema

El contrato de `Vehicle` es: **`move()` nunca disminuye la posición y nunca lanza excepciones**. `UnreliableCar` rompe ambas reglas (lanza `RuntimeError` y resta posición).

### Qué hacer

Rediseñar `UnreliableCar.move()` para que la "falta de fiabilidad" respete el contrato, por ejemplo **no avanzando** en algunos ticks. No cambiar `Vehicle` ni `Track`.

### Solución (boceto)

```python
import random

class UnreliableCar(Vehicle):
    def move(self):
        if random.random() < 0.3:
            return                  # se atasca, pero no rompe el contrato
        self.position += 5
```

### Pregunta de discusión

**¿Qué habrías tenido que agregar a `Track` si NO arreglabas `UnreliableCar`? ¿Por qué es mejor arreglar la subclase?**

* A `Track` habría que añadirle un `try/except` alrededor de cada `move()` y un "clamp" de posición (por ejemplo `position = max(old\_position, position)`) para deshacer retrocesos.
* Es peor porque: (1) el motor ahora desconfía de los vehículos y carga con parches; (2) cada nueva clase que consuma `Vehicle` tendría que repetir esas defensas; (3) el contrato queda oculto y roto en vez de cumplido; (4) hay que modificar código que debería ser estable (`Track`), lo que además viola OCP.
* Arreglar la subclase corrige el problema **en su origen**, una sola vez, y todo el código que usa `Vehicle` sigue siendo simple y confiable.

\---

## 6\. Ejercicio 4: ISP (Interface Segregation Principle)

### Teoría

Un cliente no debe depender de métodos que no usa. Es mejor tener varias interfaces pequeñas y específicas que una grande y general. Una interfaz "gorda" obliga a los implementadores a dar una implementación falsa (`raise NotImplementedError`, valores dummy) de métodos que no tienen sentido para ellos, lo que genera confusión y código frágil.

Preguntas de autoevaluación:

* ¿Cada implementador tiene una implementación real y con sentido de todos los métodos?
* Si divido esta interfaz en dos, ¿alguna clase necesitaría implementar ambas?

### Problema

`VehicleActions` obliga a todos a implementar `refuel()`, `fly()` y `pedal\_harder()`, aunque una bicicleta no vuele ni un carro pedalee.

### Qué hacer

* Reemplazar `VehicleActions` por cuatro interfaces con **un método abstracto** cada una: `Movable`, `Refuelable`, `Flyable`, `Pedalable`.
* `GasCar` → `Movable` + `Refuelable`. `Bicycle` → `Movable` + `Pedalable`. Borrar los métodos "no puedo hacer eso".
* Crear `Drone` → `Movable` + `Flyable`, y añadirlo a la carrera en `main()`.

### Solución (boceto)

```python
from abc import ABC, abstractmethod

class Movable(ABC):
    @abstractmethod
    def move(self): ...

class Refuelable(ABC):
    @abstractmethod
    def refuel(self): ...

class Flyable(ABC):
    @abstractmethod
    def fly(self): ...

class Pedalable(ABC):
    @abstractmethod
    def pedal\_harder(self): ...


class GasCar(Movable, Refuelable):
    def move(self): ...
    def refuel(self): ...

class Bicycle(Movable, Pedalable):
    def move(self): ...
    def pedal\_harder(self): ...

class Drone(Movable, Flyable):
    def move(self): ...
    def fly(self): ...


# en main(): agregar Drone("Buzz") a la lista de corredores
```

### Pregunta de discusión

**¿Qué interfaces necesitaría un futuro `Submarine` o `Airplane`? ¿Agregarlos obliga a tocar vehículos existentes?**

* `Airplane`: `Movable` + `Flyable` + `Refuelable` (ya existen las tres).
* `Submarine`: `Movable` y probablemente `Refuelable` (o una nueva `Divable` con `dive()` para la inmersión).
* **No se toca ningún vehículo existente.** Si hace falta una capacidad nueva (`Divable`), se agrega como interfaz nueva y solo la implementa quien la necesite. Esto es OCP e ISP trabajando juntos.

\---

## 7\. Ejercicio 5: DIP (Dependency Inversion Principle)

### Teoría

Los módulos de alto nivel no deben depender de los de bajo nivel; **ambos deben depender de abstracciones**. Si la política de alto nivel ("cómo correr una carrera") está atada a clases concretas (`SportsCar`, `DeliveryVan`), no se puede reutilizar ni probar sin esas clases exactas. Si depende de una abstracción (algo con `move()`, `position`, `symbol`), se pueden **inyectar** objetos reales o dobles de prueba.

Preguntas de autoevaluación:

* ¿Esta clase construye sus colaboradores o los recibe?
* ¿Puedo probarla con una versión falsa en memoria de su dependencia, sin cambiar la clase?

### Problema

`Race` crea sus propios `SportsCar` y `DeliveryVan` dentro de `\_\_init\_\_`. Para correr otro grupo de vehículos hay que editar `Race`.

### Qué hacer

* `Race` recibe los corredores (y opcionalmente un `Track`) por el constructor y los guarda en `self.racers`. **No debe importar ni conocer ninguna clase concreta de vehículo.**
* Crear la clase `RocketSled`.
* En `main()`, armar **dos plantillas distintas** y correr `Race` con cada una, demostrando que `Race` no cambió.

### Solución (boceto)

```python
class Race:
    def \_\_init\_\_(self, racers, track=None):
        self.racers = racers
        self.track = track or Track(length=30)

    def start(self):
        return self.track.run(self.racers)


class RocketSled(Vehicle):
    def move(self):
        self.position += 6


def main():
    Race(\[SportsCar("Flash"), DeliveryVan("Steady Eddie")]).start()
    Race(\[RocketSled("Rocky"), Drone("Buzz")]).start()
```

> Los vehículos concretos se importan/crean en `main()` (la "raíz de composición"), nunca dentro de `Race`.

### Pregunta de discusión

**¿Cómo facilita la inyección de la lista de corredores probar `Race` sin una animación real en la terminal?**

* En una prueba puedes pasar corredores falsos (`FakeRacer` con `move()` y `position` simples) y un `Track` falso que no imprime nada o que solo registra las llamadas.
* Así pruebas la lógica de `Race` rápido, de forma determinista y sin depender de la terminal, de temporizadores ni de aleatoriedad.
* Si `Race` construyera sus propios vehículos, siempre arrastraría clases concretas (y su animación) en cada prueba.

\---

## 8\. Cierre (Wrap-up)

### Verificación final

```bash
pytest -v        # deben pasar las pruebas de los 5 ejercicios
```

### Preguntas de cierre

**1. Identifica un lugar de tu proyecto (o de uno pasado) donde se violaba uno de los cinco principios. ¿Qué cambiarías?**

Esta es personal, pero aquí van ejemplos típicos para inspirarte:

|Situación común|Principio violado|Cambio|
|-|-|-|
|Una clase `Usuario` que valida, guarda en BD y envía correos|SRP|Separar en `Usuario`, `UsuarioRepository` y `EmailService`.|
|Una función con `if tipo == "pdf" ... elif tipo == "csv"` para exportar|OCP|Una interfaz `Exportador` con una clase por formato.|
|Una subclase que lanza `NotImplementedError` o ignora lo que promete la base|LSP|Replantear la jerarquía o respetar el contrato.|
|Una interfaz `Repository` con 15 métodos que nadie implementa completos|ISP|Dividirla en `Reader`, `Writer`, etc.|
|Un controlador que hace `db = MySQLDatabase()` dentro del código|DIP|Recibir la base de datos por constructor (inyección).|

**2. La idea de `engine/track.py` y el patrón "racer".**

El mismo patrón del Ejercicio 5 (DIP) permite conectar objetos nuevos y no relacionados a un motor compartido sin modificarlo: mientras el objeto cumpla la abstracción (`move()`, `position`, `symbol`), `Track` puede animarlo. Es el mismo principio que usan los motores de juegos, los sistemas de plugins y los frameworks: el motor define la interfaz y los demás se acoplan a ella.

\---

## 9\. Resumen rápido

|Ejercicio|Principio|Cambio clave|Señal de alerta|
|-|-|-|-|
|1|SRP|Separar `Car` y `RaceLogger`|Clase que "hace X **y** Y"|
|2|OCP|Subclases nuevas sin editar lo existente|Cadenas `if/elif` por tipo|
|3|LSP|`UnreliableCar` no avanza, pero no rompe el contrato|Subclase que lanza o retrocede|
|4|ISP|Cuatro interfaces pequeñas|`NotImplementedError` en métodos|
|5|DIP|`Race` recibe los corredores|`Clase()` construida dentro de otra|

## 10\. Analisis con IA



Realice el analisis con la IA de Claude para comprender los principios de SOLID, entender el codigo y redactar mejor las preguntas del taller.

