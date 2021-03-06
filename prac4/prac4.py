from inicio import *
from telnet_ftp import *
from rendimiento import *
from os import system
from crearPDF import *
from updateRRD import *
from graphRRD import grafica, trendGraph, trendRAMGraph
from claseAgente import Agente, obtenerAgentes, eliminarAgente, mostrarAgentes, agregarAgente
import threading

agentes = obtenerAgentes()

print(f"""
INICIO

    *El numero de agentes en monitoreo es {len(agentes)}
""")
#mostrarAgentes(agentes)

""" i=0
for agente in agentes:
    print(f"Interfaces agente {i+1}\n{agente.tablaInterfaces}")
    interfaz = int(input("Selecciona la interfaz a monitorizar: "))
    agente.interfazSelec = interfaz
    t = threading.Thread(name="Hilo "+str(i+1),target=update, args=(agente,interfaz), daemon=True)
    t.start()
    t = threading.Thread(name="Hilo "+str(i+1),target=trendUpdate, args=(agente,), daemon=True)
    t.start()
    i = i+1 """


while True:
    opcion = 0
    opcion = int(input(
        "Indique la acción que quiere hacer:\n1. Agregar agente\n2. Eliminar agente\n3. Obtener reporte\n4. Mostrar agentes\n5. Monitorizar el rendimiento de los agentes\n6. Facturacion\n7. Modulo configuracion\nPresione cualquier otro para cerrar el programa\n"))
    if opcion == 1:
        host = input("Indique el nombre del host o ip del dispositivo: ")
        snmp_v = input("Indique la versión de snmp a utilizar:\n1. v1\n2. v2c\n")
        snmp_v = "v1" if snmp_v == '1' else "v2"
        comunidad = input("Indique la comunidad a la que pertenece el agente: ")
        puerto = input("Indique el puerto de snmp del agente: ")
        agente = Agente(host, snmp_v, comunidad, puerto)
        agregarAgente(agente, agentes)
        print(f"Interfaces agente {len(agentes)}\n{agente.tablaInterfaces}")
        interfaz = int(input("Selecciona la interfaz a monitorizar: "))
        agentes[len(agentes)-1].interfazSelec = interfaz
        """ t = threading.Thread(name="Hilo "+str(len(agentes)),target=update, args=(agentes[len(agentes)-1],interfaz), daemon=True)
        t.start() """


    elif opcion == 2:
        host = input("Indique el nombre del host o ip del dispositivo a eliminar: ")
        eliminarAgente(host,agentes)

    elif opcion == 3:
        i=0
        print("Seleccione un agente:")
        for agente in agentes:
            print(f"Agente {i+1}: {agente.desc}")
            i = i+1
        op = int(input())
        tiempo_inicial = input("Indique el tiempo inicial con formato dd-mm-yyyy HH:MM: ")
        tiempo_final = input("Indique el tiempo final con formato dd-mm-yyyy HH:MM: ")
        
        grafica(agentes[op-1],tiempo_inicial,tiempo_final,agentes[op-1].interfazSelec)


        generaReporte(agentes[op-1])
        print("Reporte generado exitosamente\n")

    elif opcion == 4:
        mostrarAgentes(agentes)

    elif opcion == 5:
        system("clear")
        for agente in agentes:
            mostrarAcuerdo(agente)

        threads =[]
        for i,agente in enumerate(agentes):
            t = threading.Thread(name="Hilo "+str(i+1),target=trendUpdate, args=(agente,), daemon=True)
            threads.append(t)
            t.start()
        for i in range(len(threads)):
            threads[i].join()
        print("""Inventario de la configuracion
        """)
        for agente in agentes:
            tablaInventario(agente)
            trendGraph(agente,300)
            trendRAMGraph(agente,300)
            trendHDDGraph(agente,300)
            generaReporte(agente)
            #genericaCPU(agente, 300)
            #genericaRAM(agente, 300)
            #genericaHDD(agente, 300)
    elif opcion == 6:
        system("clear")
        threads = []
        for i,agente in enumerate(agentes):
            t = threading.Thread(name="Hilo "+str(i+1),target=udpUpdate, args=(agente,), daemon=True)
            threads.append(t)
            t.start()
        for i in range(len(threads)):
            threads[i].join()


        tiempo_inicial = input("Indique el tiempo inicial con formato dd-mm-yyyy HH:MM: ")
        tiempo_final = input("Indique el tiempo final con formato dd-mm-yyyy HH:MM: ")
        
        """ tiempo_inicial = "26-10-2021 13:35"
        tiempo_final = "26-10-2021 13:41" """
        for agente in agentes:
            tablaInventario(agente)
            dataFactura = graficaUDP(agente,tiempo_inicial,tiempo_final)
            dataFactura.append(tiempo_inicial)
            dataFactura.append(tiempo_final)
            generaFactura(agente, dataFactura)
        exit(0)
    elif opcion == 7:
        system("clear")
        routers = ["30.30.30.1","192.168.1.2"]
        for agente in agentes:
            tablaInventario(agente)

        opcion = input("¿Desea usar el protocolo Telnet para guardar los archivos de configuracion? [s/n]")
        if(opcion == 's'):
            for host in routers:
                genera_archivo_conf(host)

        print("""\nSeleccione un router para trabajar:
        1. RPClive-3 (30.30.30.1)
        2. RPClive-1 (192.168.1.2)
        """)
        opcion = int(input())

        cliente_ftp(routers[opcion-1])

        exit(0)
    else:
        print("El programa finalizo")
        exit(0)