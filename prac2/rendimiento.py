from os import system
from claseAgente import Agente
from getSNMP import consultaSNMP
import datetime as dt


def mostrarAcuerdo(agente: Agente):
    a_file = open("acuerdo.txt", "r")
    list_of_lines = a_file.readlines()

    if "Windows" in agente.desc:
        agente.umbralCPU["go"] = 30
        agente.umbralCPU["set"] = 25
        agente.umbralCPU["ready"] = 20

        agente.umbralRAM["go"] = 60
        agente.umbralRAM["set"] = 50
        agente.umbralRAM["ready"] = 40

        agente.umbralHDD["go"] = 0
        agente.umbralHDD["set"] = 0
        agente.umbralHDD["ready"] = 0

    else:
        agente.umbralCPU["go"] = 70
        agente.umbralCPU["set"] = 60
        agente.umbralCPU["ready"] = 45

        agente.umbralRAM["go"] = 30
        agente.umbralRAM["set"] = 25
        agente.umbralRAM["ready"] = 20

        agente.umbralHDD["go"] = 0
        agente.umbralHDD["set"] = 0
        agente.umbralHDD["ready"] = 0


    list_of_lines[0] = "CONTRATO DE PRESTACIÓN DE SERVICIOS PARA LA ADMINISTRACION DE RENDIMIENTO DEL HOST "+agente.host+"\n"
    list_of_lines[35] = "Rendimiento de procesador, Memoria RAM y Almacenamiento del host "+agente.host+"\n"
    list_of_lines[37] = "Se estipula que la sociedad ASR se compromete a que el uso del procesador no superara el "+str(agente.umbralCPU["go"])+"%\n"
    list_of_lines[38] = "De la misma forma el uso de la memoria RAM no superara el "+str(agente.umbralRAM["go"])+"%\n"
    list_of_lines[39] = "Y finalmente el almacenamiento no sobrepasara el "+str(agente.umbralHDD["go"])+"%\n"
    a_file = open("acuerdo.txt", "w")
    a_file.writelines(list_of_lines)
    a_file.close()
    system("gedit ./acuerdo.txt")

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
    contenido = [str(nombre),str(agente.so),str(agente.tiempoActividad),str(dt.datetime.today())[:19],str(agente.comunidad)]
    
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