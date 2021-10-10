import datetime
from getSNMP import consultaSNMP
from datetime import date
import os

def asignarTablaAgentes(agentes):
    for agente in agentes:
        obtenerTablaInterfaces(agente)
    
def obtenerTablaInterfaces(agente):
    parametro = int(agente.nInterfaces)
    for i in range(parametro):
        resultados = consultaSNMP(agente.comunidad,agente.host,"1.3.6.1.2.1.2.2.1.2."+str(i+1),agente.puerto,agente.version)
        if "Windows" in agente.so:
            decodificado = bytes.fromhex(resultados[2:]).decode(encoding='latin1')
            agente.cadenaMasGrande = len(decodificado) if len(decodificado) > agente.cadenaMasGrande else agente.cadenaMasGrande
            agente.descInterfaces.append(decodificado)
        else:
            agente.cadenaMasGrande = len(resultados) if len(resultados) > agente.cadenaMasGrande else agente.cadenaMasGrande
            agente.descInterfaces.append(resultados)
        resultados = int(consultaSNMP(agente.comunidad,agente.host,"1.3.6.1.2.1.2.2.1.7."+str(i+1),agente.puerto,agente.version))
        if resultados == 1:
            resultados = "Up"
        elif resultados == 2:
            resultados = "Down"
        else:
            resultados = "Test"
        agente.estadoInterfaces.append(resultados)

def asignarSO(agentes):
    for agente in agentes:
        obtenerSO(agente)
    
def obtenerSO(agente):
    """el tiempo de actividad desde el último reinicio. """
    resultados = consultaSNMP(agente.comunidad,agente.host,"1.3.6.1.2.1.1.1.0",agente.puerto,agente.version)
    agente.desc = resultados
    agente.so = "Windows" if agente.desc.find("Windows") != -1 else "Linux"

    resultados = consultaSNMP(agente.comunidad,agente.host,"1.3.6.1.2.1.1.6.0",agente.puerto,agente.version)
    agente.ubicacion = resultados

    ticks = consultaSNMP(agente.comunidad,agente.host,"1.3.6.1.2.1.1.3.0",agente.puerto,agente.version)
    seconds = int(ticks)/100
    agente.tiempoActividad = str(datetime.timedelta(seconds=seconds))

def asignarNumeroDeInterfaces(agentes):
    for agente in agentes:
        agente.nInterfaces = obtenerNumeroInterfaces(agente)

def obtenerNumeroInterfaces(agente):
    resultados = consultaSNMP(agente.comunidad,agente.host,"1.3.6.1.2.1.2.1.0",agente.puerto,agente.version)
    return resultados

def ping(ip):
    return os.system("ping -c 1 "+str(ip))

def estadoConectividadAgentes(agentes):
    bandera = False
    for agente in agentes:
        if ping(agente.host) == 0:
            agente.estado = True
            bandera = True
    return bandera

def algoritmoCalculoDias():
    fechaNacimiento = date(1998, 8, 22)
    fechaAsignada = date(2021, 9, 10)

    numDias = fechaAsignada - fechaNacimiento
    numDiasTotal = numDias.days
    print(
        f"El numero de dias desde que naci hasta el 10 de septiembre del 2021 es: {numDiasTotal}")

    R = numDiasTotal % 3
    print("Toca hacer los ejercicios con el numero", R+1)