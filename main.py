
import math
import sys
import networkx as nx
from simulation import Simulation
from complexNetwork import ComplexNetwork
from event import Event
from paquete import Paquete
import config

class Main:#hereda de la clase object, hay que recordar que en Python todo es un objeto

	def __init__(self):
		#--------ANILLO------------------
		self.__nodes=config.NODOS_ANILLO # Número de nodos del anillo
		self.__diametro=20               # Se asume que el radio del anillo es 10 unidades
		#--------MALLA-------------------
		self.__rows=config.ROWS          # Filas de la malla
		self.__columns=config.COLUMNS    # Columnas de la malla
		self.__diagonal=self.diag()      # Longitud de la diagonal principal de la malla
		#--------------------------------
		self.__ciclos=config.CICLOS      # Número de ciclos de simulación
		#self.__tamEnlace=self.__diagonal # Longitud máxima del enlace dinámico, se puede ajustar con self.__diagonal para la malla y self.__diametro para el anillo
		self.__grafo=config.RED          # Topología sobre la que se desarrollará la simulación
		self.__graph = None              # Grafo NetworkX sobre el que se desarrollará la simulación
		self.__coordinador=1             # Identificador del nodo coordinador de la simulación
		self.__nodosTotales=-1           # Número de nodos total del grafo
	
	#---MALLA----------------------------

	def createGrid(self):
		self.__graph = nx.grid_2d_graph(self.__rows,self.__columns,periodic=False)
		self.__graph = nx.convert_node_labels_to_integers(self.__graph,first_label=1,ordering="sorted")
		self.__tamEnlace=self.__diagonal / config.LONG_ENLACE
		nx.write_adjlist(self.__graph,"graph.adjlist")

	def diag(self):
		n1=[0,0]
		n2=[self.__rows-1,self.__columns-1]
		d=math.sqrt(math.pow(n2[0]-n1[0],2)+math.pow(n2[1]-n1[1],2))
		return d

	#---ANILLO----------------------------

	def createRing(self):
		self.__graph = nx.circulant_graph(self.__nodes, [1])
		self.__graph = nx.convert_node_labels_to_integers(self.__graph,first_label=1,ordering="sorted")
		self.__tamEnlace=self.__diametro / config.LONG_ENLACE
		nx.write_adjlist(self.__graph,"graph.adjlist")

	#---ESFERA---------------------------

	def fibonacci_sphere(self, n_nodos):
		puntos = []
		phi = math.pi * (3 - math.sqrt(5))
		for i in range(n_nodos):
			y = 1 - (i / (n_nodos - 1)) * 2
			radio = math.sqrt(1 - y * y)
			theta = phi * i
			x = math.cos(theta) * radio
			z = math.sin(theta) * radio
			puntos.append((x, y, z))
		return puntos

	def distancia_esfera(self, p1, p2):
		dot = p1[0]*p2[0] + p1[1]*p2[1] + p1[2]*p2[2]
		dot = max(-1, min(1, dot))
		return math.acos(dot)

	def distancia_haversine(self, p1, p2):
		"""Great circle distance usando Haversine. p1, p2 en (x,y,z)."""
		lat1 = math.asin(p1[1])
		lon1 = math.atan2(p1[2], p1[0])
		lat2 = math.asin(p2[1])
		lon2 = math.atan2(p2[2], p2[0])
		dlat = lat2 - lat1
		dlon = lon2 - lon1
		a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
		return 2 * math.asin(math.sqrt(a))

	def createSphere(self):
		n = self.__nodes
		k = config.K_VECINOS if hasattr(config, 'K_VECINOS') else 4
		puntos = self.fibonacci_sphere(n)
		G = nx.Graph()
		for i in range(n):
			G.add_node(i + 1)
		for i in range(n):
			distancias = []
			for j in range(n):
				if i != j:
					d = self.distancia_haversine(puntos[i], puntos[j])
					distancias.append((j + 1, d))
			distancias.sort(key=lambda x: x[1])
			for j, d in distancias[:k]:
				G.add_edge(i + 1, j)
		self.__graph = G
		self.__sphere_points = puntos
		self.__tamEnlace = math.pi / config.LONG_ENLACE
		nx.write_adjlist(self.__graph, "graph.adjlist")


	@property
	def sphere_points(self):
		return self.__sphere_points

	#---GETTERS y SETTERS------------------

	@property
	def nodes(self):
		return self.__nodes

	@property
	def rows(self): 
		return self.__rows

	@property
	def columns(self):
		return self.__columns

	@property
	def ciclos(self):
		return self.__ciclos

	@property
	def tamEnlace(self):
		return self.__tamEnlace

	@property
	def grafo(self):
		return self.__grafo

	@grafo.setter
	def grafo(self,value):
		self.__grafo=value

	@property
	def graph(self):
		return self.__graph

	@property
	def coordinador(self):
		return self.__coordinador

	@property
	def nodosTotales(self):
		return self.__nodosTotales

	@nodosTotales.setter
	def nodosTotales(self,value):
		self.__nodosTotales=value

#---MAIN()-----------------------
if __name__ == "__main__":
	#Se crea una instancia de la clase Main
	main=Main()
	#Se selecciona el grafo con el que se trabajará en la simulación
	#1.- Malla
	#3.- Anillo
	#7.- Esfera
	if(main.grafo==1):
		main.createGrid()
		main.nodosTotales=main.rows*main.columns
	elif(main.grafo==3): 
		main.createRing()
		main.nodosTotales=main.nodes
	elif(main.grafo==7):
		main.createSphere()
		main.nodosTotales=main.nodes
	#se muestra el grafo en una imágen:
	#plt.cla()
	#nx.draw_networkx(main.graph)
	#plt.show()
	#Se construye una instancia de la clase Simulation
	experiment = Simulation(sys.maxsize,main)
	experiment.readAdjacencyListNetworkX()
	#Se asocia un pareja proceso/modelo con cada nodo de la gráfica
	for i in range(1,len(experiment.graph)+1):
		#parámetros del constructor de la clase ComplexNetwork
		#el primer parámetro es una referencia al objeto principal de la simulación
		#el segundo parámetro es el número de enlaces dinámicos del nodo
		#el tercer parámetro es el número de conexiones soportadas por el nodo 
		#el cuarto parámetro es el número de paquetes exploradores que enviará el nodo en fase de exploración
		#el quinto parámetro indica el algoritmo de encaminamiento que el nodo ejecutará en la fase de exploración
		#opciones de algoritmo de encaminamiento: "COMPASS-ROUTING", "RANDOM-WALK", "SHORTEST-PATH"
		#el sexto parámetro indica el número de la regla de recableado que el nodo ejecutará en la fase de negociación
		#el septimo parámetro es el número de ejecucipon para ubicar archivo de log donde se registrarán los eventos del nodo
  		#opciones de reglas de recableado: R1=>1, R2=>2, R3=>3
		m = ComplexNetwork(main,config.ENLACES_DINAMICOS,main.nodosTotales/config.DIV_CONEXIONES,config.EXPLORADORES,config.REGLA,config.ROUTING,config.P,config.Q, config.ALPHA, config.VECTOR_POPULARIDAD, config.VECTOR_DISTANCIA)#,sys.argv[1])
		experiment.setModel(m, i)
	#inserta un evento semilla en la agenda y arranca
	#para comenzar la simulacion el coordinador arranca un PIF en donde avisará a todos que hagan su fase de EXPOLRACIÓN
	new_package=Paquete(0,0)
	new_package.diametro=nx.diameter(main.graph)
	seed=Event("PIF-EXPLORACION", 0.0, main.coordinador,main.coordinador,new_package)
	experiment.init(seed)
	
	import time
	from pathlib import Path
	
	start_time = time.perf_counter()
	experiment.run()
	elapsed_time = time.perf_counter() - start_time
	
	total_mensajes = experiment.engine.total_events
	event_counts = experiment.engine.event_counts
	
	event_types = [
		"PIF-EXPLORACION",
		"PACKAGE",
		"ACK",
		"PIF-NEGOCIACION",
		"SOLICITUD-CONEXION",
		"ACEPTO-CONEXION",
		"DESCONEXION",
		"DESCONEXION-RECIBIDA",
		"RECHAZO-CONEXION",
		"PIF-CONEXION"
	]
	
	if len(sys.argv) > 1:
		hoja_dir = Path(sys.argv[1]).parent
	else:
		hoja_dir = Path(".")
		
	metrics_file = hoja_dir / "metricas_rendimiento.csv"
	with open(metrics_file, "w", encoding="utf-8") as mf:
		header = ["Tiempo_Ejecucion_Segundos", "Mensajes_Intercambiados"] + event_types
		mf.write(",".join(header) + "\n")
		
		row = [f"{elapsed_time:.6f}", str(total_mensajes)]
		for et in event_types:
			row.append(str(event_counts.get(et, 0)))
		mf.write(",".join(row) + "\n")


	if main.grafo == 7:
		import matplotlib.pyplot as plt
		
		pts = main.sphere_points
		grados = dict(main.graph.degree())
		
		fig, ax = plt.subplots(figsize=(15, 15))
		ax.axis('off')
		
		coordenadas = {i+1: (pts[i][0], pts[i][2]) for i in range(len(pts))}
		
		color = [float(grados[v]) for v in sorted(main.graph.nodes())]
		size  = [float(grados[v]) * 50 for v in sorted(main.graph.nodes())]
		
		nodes_draw = nx.draw_networkx_nodes(main.graph, coordenadas,
											node_color=color, node_size=size,
											cmap='rainbow', alpha=0.9, ax=ax)
		nx.draw_networkx_edges(main.graph, coordenadas, alpha=0.3,
							width=0.5, edge_color='gray', ax=ax)
		
		from mpl_toolkits.axes_grid1 import make_axes_locatable
		divider = make_axes_locatable(ax)
		cax = divider.append_axes("right", size="3%", pad=0.1)
		clb = plt.colorbar(nodes_draw, cax=cax)
		clb.set_label("Grado", size=12)
		plt.title(f"Esfera Fibonacci — Regla {config.REGLA}, {config.ROUTING}")
		plt.savefig(f"esfera_fibonacci_R{config.REGLA}.png", dpi=150)
		plt.close()
		print(f"Imagen guardada: esfera_fibonacci_R{config.REGLA}.png")