import networkx as nx
import random
import matplotlib.pyplot as plt
import os
import glob
import numpy as np

def encontrar_gexf(carpeta_ejecucion):
    """Encuentra el archivo GEXF en una carpeta de ejecución"""
    archivos = glob.glob(os.path.join(carpeta_ejecucion, "graph_test_*.gexf"))
    if archivos:
        return archivos[0]
    return None

def simular_ataque(G):
    """Elimina nodos por grado descendente (ataque dirigido)"""
    G_copia = G.copy()
    n_total = len(G_copia)
    fracciones = []
    
    while len(G_copia) > 0:
        componentes = nx.connected_components(G_copia)
        mayor = max(componentes, key=len)
        fracciones.append(len(mayor) / n_total)
        nodo_max = max(G_copia.degree(), key=lambda x: x[1])[0]
        G_copia.remove_node(nodo_max)
    
    fracciones.append(0)
    return fracciones

def simular_falla(G, repeticiones=10):
    """Elimina nodos aleatoriamente (falla) - promedia varias repeticiones"""
    n_total = len(G)
    todas = []
    
    for _ in range(repeticiones):
        G_copia = G.copy()
        nodos = list(G_copia.nodes())
        random.shuffle(nodos)
        fracciones = []
        
        for nodo in nodos:
            componentes = nx.connected_components(G_copia)
            mayor = max(componentes, key=len)
            fracciones.append(len(mayor) / n_total)
            G_copia.remove_node(nodo)
        fracciones.append(0)
        todas.append(fracciones)
    
    promedio = [sum(t[i] for t in todas) / repeticiones for i in range(n_total + 1)]
    return promedio

def punto_critico(fracciones, f_eje, umbral=0.5):
    """Encuentra el punto donde la red cae por debajo del umbral"""
    for i, f in enumerate(fracciones):
        if f < umbral:
            return f_eje[i]
    return 1.0

def analizar_robustez_promedio(carpeta_base, ejecuciones=3):
    """
    Lee las N ejecuciones, calcula ataque y falla para cada una
    y devuelve el promedio y desviación estándar
    """
    ataques = []
    fallas  = []
    n_total = None

    for i in range(1, ejecuciones + 1):
        carpeta = os.path.join(carpeta_base, str(i))
        gexf = encontrar_gexf(carpeta)
        
        if not gexf:
            print(f"No se encontró GEXF en {carpeta}")
            continue
        
        print(f"  Leyendo ejecución {i}: {os.path.basename(gexf)}")
        G = nx.Graph(nx.read_gexf(gexf))
        
        if n_total is None:
            n_total = len(G)
        
        ataques.append(simular_ataque(G))
        fallas.append(simular_falla(G))
    
    if not ataques:
        return None, None, None, None, None
    
    # Asegurar misma longitud (pad con 0)
    max_len = max(len(a) for a in ataques)
    ataques = [a + [0]*(max_len - len(a)) for a in ataques]
    fallas  = [f + [0]*(max_len - len(f)) for f in fallas]
    
    ataque_prom = np.mean(ataques, axis=0)
    ataque_std  = np.std(ataques,  axis=0)
    falla_prom  = np.mean(fallas,  axis=0)
    falla_std   = np.std(fallas,   axis=0)
    f_eje       = [i/n_total for i in range(max_len)]
    
    return ataque_prom, ataque_std, falla_prom, falla_std, f_eje


if __name__ == "__main__":
    BASE = r"C:\Users\pablo\OneDrive\Documents\DUAL\Repositorios\ResultadosCN\Formacion"
    EJECUCIONES = 3
    TOPOLOGIA   = "malla48x48"
    RUTEO       = "SP"
    LONGITUD    = "D4"

    regla_1= os.path.join(BASE, TOPOLOGIA, "R1", RUTEO, LONGITUD)
    regla_2= os.path.join(BASE, TOPOLOGIA, "R2", RUTEO, LONGITUD)
    regla_3= os.path.join(BASE, TOPOLOGIA, "R3", RUTEO, LONGITUD)
    regla_4= os.path.join(BASE, TOPOLOGIA, "R4", RUTEO, LONGITUD)
    regla_5= os.path.join(BASE, TOPOLOGIA, "R5", RUTEO, LONGITUD)

    fig, ax = plt.subplots(figsize=(10, 6))

    print("R1")
    a_prom, a_std, f_prom, f_std, f_eje = analizar_robustez_promedio(regla_1, EJECUCIONES)
    if a_prom is not None:
        ax.plot(f_eje, a_prom, color="#E85D24", linewidth=2, label="R1- ATAQUE")
        ax.fill_between(f_eje, a_prom-a_std, a_prom+a_std, color="#E85D24", alpha=0.15)
        ax.plot(f_eje, f_prom, color="#E85D24", linewidth=2, linestyle="--", label="R1 - FALLA")
        ax.fill_between(f_eje, f_prom-f_std, f_prom+f_std, color="#E85D24", alpha=0.15)
        pc_a = punto_critico(a_prom, f_eje)
        pc_f = punto_critico(f_prom, f_eje)
        print(f"  Punto crítico ataque: {pc_a*100:.1f}% nodos eliminados")
        print(f"  Punto crítico falla:  {pc_f*100:.1f}% nodos eliminados")

    print("R2")
    a_prom, a_std, f_prom, f_std, f_eje = analizar_robustez_promedio(regla_2, EJECUCIONES)
    if a_prom is not None:
        ax.plot(f_eje, a_prom, color="#00FA43", linewidth=2, label="R2- ATAQUE")
        ax.fill_between(f_eje, a_prom-a_std, a_prom+a_std, color="#00FA43", alpha=0.15)
        ax.plot(f_eje, f_prom, color="#00FA43", linewidth=2, linestyle="--", label="R2 - FALLA")
        ax.fill_between(f_eje, f_prom-f_std, f_prom+f_std, color="#00FA43", alpha=0.15)
        pc_a = punto_critico(a_prom, f_eje)
        pc_f = punto_critico(f_prom, f_eje)
        print(f"  Punto crítico ataque: {pc_a*100:.1f}% nodos eliminados")
        print(f"  Punto crítico falla:  {pc_f*100:.1f}% nodos eliminados")

    print("R3")
    a_prom, a_std, f_prom, f_std, f_eje = analizar_robustez_promedio(regla_3, EJECUCIONES)
    if a_prom is not None:
        ax.plot(f_eje, a_prom, color="#EEFF00", linewidth=2, label="R3- ATAQUE")
        ax.fill_between(f_eje, a_prom-a_std, a_prom+a_std, color="#EEFF00", alpha=0.15)
        ax.plot(f_eje, f_prom, color="#EEFF00", linewidth=2, linestyle="--", label="R3 - FALLA")
        ax.fill_between(f_eje, f_prom-f_std, f_prom+f_std, color="#EEFF00", alpha=0.15)
        pc_a = punto_critico(a_prom, f_eje)
        pc_f = punto_critico(f_prom, f_eje)
        print(f"  Punto crítico ataque: {pc_a*100:.1f}% nodos eliminados")
        print(f"  Punto crítico falla:  {pc_f*100:.1f}% nodos eliminados")

    print("R4")
    a_prom, a_std, f_prom, f_std, f_eje = analizar_robustez_promedio(regla_4, EJECUCIONES)
    if a_prom is not None:
        ax.plot(f_eje, a_prom, color="#00F4FD", linewidth=2, label="R4- ATAQUE")
        ax.fill_between(f_eje, a_prom-a_std, a_prom+a_std, color="#00F4FD", alpha=0.15)
        ax.plot(f_eje, f_prom, color="#00F4FD", linewidth=2, linestyle="--", label="R4 - FALLA")
        ax.fill_between(f_eje, f_prom-f_std, f_prom+f_std, color="#00F4FD", alpha=0.15)
        pc_a = punto_critico(a_prom, f_eje)
        pc_f = punto_critico(f_prom, f_eje)
        print(f"  Punto crítico ataque: {pc_a*100:.1f}% nodos eliminados")
        print(f"  Punto crítico falla:  {pc_f*100:.1f}% nodos eliminados")

    print("R5")
    a_prom, a_std, f_prom, f_std, f_eje = analizar_robustez_promedio(regla_5, EJECUCIONES)
    if a_prom is not None:
        ax.plot(f_eje, a_prom, color="#1400F4", linewidth=2, label="R5- ATAQUE")
        ax.fill_between(f_eje, a_prom-a_std, a_prom+a_std, color="#1400F4", alpha=0.15)
        ax.plot(f_eje, f_prom, color="#1400F4", linewidth=2, linestyle="--", label="R5 - FALLA")
        ax.fill_between(f_eje, f_prom-f_std, f_prom+f_std, color="#1400F4", alpha=0.15)
        pc_a = punto_critico(a_prom, f_eje)
        pc_f = punto_critico(f_prom, f_eje)
        print(f"  Punto crítico ataque: {pc_a*100:.1f}% nodos eliminados")
        print(f"  Punto crítico falla:  {pc_f*100:.1f}% nodos eliminados")

    ax.axhline(y=0.5, color="gray", linestyle=":", linewidth=1, label="Umbral 50%")
    ax.axhline(y=0.9, color="gray", linestyle=":", linewidth=0.7, label="Umbral 90%")
    ax.set_xlabel("Fracción de nodos eliminados (f)", fontsize=12)
    ax.set_ylabel("Fracción del componente conectado más grande (N_LCC)", fontsize=12)
    ax.set_title(f"Robustez: — {TOPOLOGIA}, {RUTEO}, {LONGITUD}", fontsize=13)
    ax.legend(loc="upper right")
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    plt.tight_layout()
    salida = f"robustez_{TOPOLOGIA}_{RUTEO}_{LONGITUD}.png"
    plt.savefig(salida, dpi=200)
    plt.show()
    print(f"\nGráfica guardada como {salida}")