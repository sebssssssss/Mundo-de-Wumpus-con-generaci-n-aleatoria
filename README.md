# Mundo-de-Wumpus-con-generaci-n-aleatoria
El programa genera un mundo cuadrado  n×n con los siguientes elementos colocados aleatoriamente:
Wumpus (1)
Oro (1)
Pozos (k = 20% de n2 con la misma probabilidad aparecen en el mundo)
Agente (inicio fijo en (1,1))

El usuario no ve directamente el mapa completo, sino solo las percepciones asociadas a la celda actual:
Brisa: indica que hay un pozo en una celda adyacente.
Hedor: indica que el Wumpus está en una celda adyacente.
Resplandor: indica que el oro está en la celda actual.
Golpe: si el agente choca con un muro.
Grito: si el Wumpus ha sido eliminado.

El agente inicia sin conocimiento del entorno y el usuario, mediante un menú interactivo, debe decidir qué hacer en cada paso.
