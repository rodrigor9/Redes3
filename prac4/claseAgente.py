from datetime import time
from io import open
from CreateRRD import *
from inicio import *
import os

class Agente():
    
    def __init__(self, host, version, comunidad, puerto) -> None:
        self.host = host
        self.version = version
        self.comunidad = comunidad
        self.puerto = int(puerto)
        self.estado = False #Down
        self.nInterfaces = 0
        self.descInterfaces = []
        self.estadoInterfaces = []
        self.interfazSelec = 0
        self.desc = ""
        self.so = ""
        self.tablaInterfaces = ""
        self.cadenaMasGrande = 0
        self.ubicacion = ""
        self.tiempoActividad = 0
        self.umbralCPU = {}
        self.umbralRAM = {}
        self.umbralHDD = {}
    def __str__(self) -> str:
        estado = "Up" if self.estado else "Down"
        columnaDesc = "Descripcion"
        for i in range(len(columnaDesc),self.cadenaMasGrande):
            columnaDesc = columnaDesc + " "

        for j in range(int(self.nInterfaces)):
            for i in range(len(self.descInterfaces[j]),self.cadenaMasGrande):
                self.descInterfaces[j] = self.descInterfaces[j]+" "

        interfaces = f"""Tabla de interfaces
        """
        interfaces = interfaces+f"""Indice\t{columnaDesc}\tEstado
        """
        for i in range(int(self.nInterfaces)):
            interfaces = interfaces + f"""{i+1}\t{self.descInterfaces[i]}\t{self.estadoInterfaces[i]}
        """
        self.tablaInterfaces = interfaces
        return f"""\tHost: {self.host}
        Version: {self.version}
        Comunidad: {self.comunidad}
        Ubicacion: {self.ubicacion}
        Tiempo de actividad: {self.tiempoActividad}
        Puerto: {self.puerto}
        Estado: {estado}
        Numero de interfaces: {self.nInterfaces}
        
        {self.tablaInterfaces}

        Descripcion: {self.desc}
        SO: {self.so}
        """


def obtenerAgentes():
    # Recuperar datos de los agentes a administrar
    archivo_texto = open("datos.txt", 'r')
    lineas_texto = archivo_texto.readlines()
    archivo_texto.close()

    if len(lineas_texto) == 0:
        print("El archivo esta vacio, no hay agentes para monitorear")
        exit()

    lineas_texto = [linea.replace("\n", "") for linea in lineas_texto]

    agentes = []
    os.system("mkdir datosGenerados")
    for linea in lineas_texto:
        data = linea.split(" ")
        agente = Agente(data[0], data[1], data[2], data[3])
        agentes.append(agente)
        os.system("mkdir datosGenerados/agente_"+data[0])
        if not os.path.exists("datosGenerados/agente_"+data[0]+"/RRDagente_"+data[0]+".rrd"):
            crearRRD(data[0])
        if not os.path.exists("datosGenerados/agente_"+data[0]+"/RRDagenteTrend_"+data[0]+".rrd"):
            trendCreate(data[0])
        if not os.path.exists("datosGenerados/agente_"+data[0]+"/RRDagenteUDP_"+data[0]+".rrd"):
            udpCreate(data[0])



    if estadoConectividadAgentes(agentes):
        os.system("clear")
        asignarNumeroDeInterfaces(agentes)
        asignarSO(agentes)
        #asignarTablaAgentes(agentes)

    return agentes

def mostrarAgentes(agentes):
    print("Los agentes que se monitorean son: ", end="\n\n")
    for agente in agentes:
        print(agente)

def agregarAgente(agente: Agente, agentes):
    archivo_texto = open("datos.txt", 'r')
    linea = archivo_texto.read()
    archivo_texto.close()
    texto = f"{agente.host} {agente.version} {agente.comunidad} {agente.puerto}"
    archivo_texto = open("datos.txt", 'a')
    if len(linea) == 0:
        archivo_texto.write(texto)
    else:
        texto = "\n"+texto
        archivo_texto.write(texto)
    archivo_texto.close()
    agentes.append(agente)

    os.system("mkdir datosGenerados/agente_"+agente.host)
    if not os.path.exists("datosGenerados/agente_"+agente.host+"/RRDagente_"+agente.host+".rrd"):
        crearRRD(agente.host)
    if not os.path.exists("datosGenerados/agente_"+agente.host+"/RRDagenteTrend_"+agente.host+".rrd"):
        trendCreate(agente.host)
    if not os.path.exists("datosGenerados/agente_"+agente.host+"/RRDagenteUDP_"+agente.host+".rrd"):
            udpCreate(agente.host)

    if ping(agente.host) == 0:
        os.system("clear")  
        agente.estado = True
        asignarNumeroDeInterfaces(agentes)
        asignarSO(agentes)
        asignarTablaAgentes(agentes)

    os.system("clear")
    mostrarAgentes(agentes)

def eliminarAgente(host, agentes):
    archivo_texto = open("datos.txt", 'r')
    lineas_texto = archivo_texto.readlines()
    archivo_texto.close()

    tamanioLista = len(lineas_texto)
    if(tamanioLista == 0):
        print("El archivo esta vacio")
        return

    i = 0
    for linea in lineas_texto:
        if linea.find(host+" ") != -1:
            lineas_texto.pop(i)
            break
        i = i+1

    if len(lineas_texto) == tamanioLista:
        print("El agente que se quiere elminar no existe")
        return

    lineas_texto[len(lineas_texto) -
                 1] = lineas_texto[len(lineas_texto)-1].replace("\n", "")
    archivo_texto = open("datos.txt", "w")
    for linea in lineas_texto:
        archivo_texto.write(linea)
    archivo_texto.close()
    agentes.pop(i)
    os.system("rm datosGenerados/agente_"+host+"/*")
    os.system("rmdir datosGenerados/agente_"+host)
    os.system("clear")
    mostrarAgentes(agentes)
