from os import system
from claseAgente import Agente
from getSNMP import consultaSNMP
import datetime as dt

def mostrarAcuerdo(agente: Agente):
    a_file = open("acuerdo.txt", "r")
    list_of_lines = a_file.readlines()
    list_of_lines[0] = "CONTRATO DE PRESTACIÓN DE SERVICIOS PARA LA ADMINISTRACION DE RENDIMIENTO DEL HOST "+agente.host+"\n"
    a_file = open("acuerdo.txt", "w")
    a_file.writelines(list_of_lines)
    a_file.close()
    #system("gedit ./acuerdo.txt")

def tablaInventario(agente: Agente):
    #Nombre del dispositivo
    #Version del SW
    #TIempo de actividad
    #Fecha y hora del host
    #ComunidadSNMP
    if "Windows" in agente.desc:
        nombre = agente.desc[:agente.desc.find("-")]
    else:
        nombre = agente.desc[:agente.desc.find("#")]
    primera = "Nombre del dispositivo"
    segunda = "Version del software"
    tercera = "Tiempo de actividad"
    cuarta = "Fecha y hora del host"
    quinta = "Comunidad SNMP"
    
    columnas = [primera,segunda,tercera,cuarta,quinta]
    contenido = [str(nombre),str(agente.so),str(agente.tiempoActividad),str(dt.date.today()),str(agente.comunidad)]
    
    for i in range(5):
        if len(columnas[i]) >= len(contenido[i]):
            for j in range(len(contenido[i]),len(columnas[i])):
                contenido[i] = contenido[i] + " "
        else:
            for j in range(len(columnas[i]),len(contenido[i])):
                columnas[i] = columnas[i] + " "
            



    print(f"""
    {columnas[0]}\t{columnas[1]}\t{columnas[2]}\t{columnas[3]}\t{columnas[4]}
    {contenido[0]}\t{contenido[1]}\t{contenido[2]}\t{contenido[3]}\t{contenido[4]}\n
    """)