import threading
from graphRRD import *
from claseAgente import Agente
import time
import rrdtool
from getSNMP import consultaSNMP
import logging

logging.basicConfig(level=logging.INFO,
                    format='[%(levelname)s] (%(threadName)-s) %(message)s')


def update(agente: Agente, interfaz: int):
    logging.info("Monitorizando para el host " +
                 agente.host+" e interfaz "+str(interfaz))
    ifInNUcastPkts = 0
    ipOutRequests = 0
    icmpInMsgs = 0
    tcpRetransSegs = 0
    udpOutDatagrams = 0

    while 1:

        ifInNUcastPkts = int(
            consultaSNMP(agente.comunidad, agente.host,
                         "1.3.6.1.2.1.2.2.1.12."+str(interfaz), agente.puerto, agente.version))
        ipOutRequests = int(
            consultaSNMP(agente.comunidad, agente.host,
                         "1.3.6.1.2.1.4.10.0", agente.puerto, agente.version))
        icmpInMsgs = int(
            consultaSNMP(agente.comunidad, agente.host,
                         "1.3.6.1.2.1.5.1.0", agente.puerto, agente.version))
        tcpRetransSegs = int(
            consultaSNMP(agente.comunidad, agente.host,
                         "1.3.6.1.2.1.6.12.0", agente.puerto, agente.version))
        udpOutDatagrams = int(
            consultaSNMP(agente.comunidad, agente.host,
                         "1.3.6.1.2.1.7.4.0", agente.puerto, agente.version))

        valor = "N:" + str(ifInNUcastPkts) + ':' + \
            str(ipOutRequests)+":"+str(icmpInMsgs)+":" + \
            str(tcpRetransSegs)+":"+str(udpOutDatagrams)

        rrdtool.update("datosGenerados/agente_"+agente.host +
                       "/RRDagente_"+agente.host+".rrd", valor)
        rrdtool.dump("datosGenerados/agente_"+agente.host+"/RRDagente_"+agente.host +
                     ".rrd", "datosGenerados/agente_"+agente.host+"/RRDagente_"+agente.host+".xml")
        time.sleep(1)


def trendUpdate(agente: Agente):

    banderas = {}
    banderas["cpu"] = [True, True, True]
    banderas["ram"] = [True, True, True]
    banderas["hdd"] = [True, True, True]
    logging.info("Monitorizando para el host " + agente.host)
    rrdpath = "datosGenerados/agente_"+agente.host
    carga_CPU = 0
    carga_RAM = 0
    carga_HDD = 0
    oidCPU = ""

    if "Windows" in agente.desc:
        oidCPU = "1.3.6.1.2.1.25.3.3.1.2.4"
    else:
        oidCPU = "1.3.6.1.2.1.25.3.3.1.2.196608"

    inicial = time.time()
    limite = time.time() + 300

    while inicial <= limite:
        carga_CPU = int(consultaSNMP(agente.comunidad, agente.host,
                                     oidCPU, agente.puerto, agente.version))
        carga_RAM = calculoCargaRamWindows(agente) if "Windows" in agente.desc else calculoCargaRamLinux(agente)
        carga_HDD = calculoCargaHDDWindows(agente) if "Windows" in agente.desc else calculoCargaHDDLinux(agente)
        valor = "N:" + str(carga_CPU)+":"+str(carga_RAM)+":"+str(carga_HDD)
        # print(valor)
        rrdtool.update(rrdpath+"/RRDagenteTrend_" +
                       agente.host+".rrd", valor)
        rrdtool.dump(rrdpath+"/RRDagenteTrend_"+agente.host +
                     ".rrd", rrdpath+"/RRDagenteTrend_"+agente.host+".xml")
        time.sleep(1)
        trendGraph(agente, 60, banderas["cpu"])
        trendRAMGraph(agente, 60, banderas["ram"])
        trendHDDGraph(agente,60,banderas["hdd"])
        inicial = time.time()

    print("Finalizo el "+str(threading.current_thread().getName()))


def calculoCargaRamWindows(agente: Agente):
    """ unidadEnBytes = int(consultaSNMP(agente.comunidad, agente.host,
                                 "1.3.6.1.2.1.25.2.3.1.4.3", agente.puerto, agente.version)) # Bytes de una unidad """

    hrStorageUsed = int(consultaSNMP(agente.comunidad, agente.host,
                                     "1.3.6.1.2.1.25.2.3.1.6.3", agente.puerto, agente.version))  # En unidades
    hrStorageSize = int(consultaSNMP(agente.comunidad, agente.host,
                                     "1.3.6.1.2.1.25.2.3.1.5.3", agente.puerto, agente.version))  # En unidades
    # Regla de 3 para sacar porcentaje
    cargaRAM = hrStorageUsed*100/hrStorageSize
    return cargaRAM

def calculoCargaHDDLinux(agente: Agente):
    cargaHDD = int(consultaSNMP(
            agente.comunidad, agente.host, "1.3.6.1.4.1.2021.9.1.9.1", agente.puerto, agente.version))
    return cargaHDD

def calculoCargaHDDWindows(agente: Agente):
    """ unidadEnBytes = int(consultaSNMP(agente.comunidad, agente.host,
                                 "1.3.6.1.2.1.25.2.3.1.4.1", agente.puerto, agente.version)) # Bytes de una unidad """

    hrStorageUsed = int(consultaSNMP(agente.comunidad, agente.host,
                                     "1.3.6.1.2.1.25.2.3.1.6.1", agente.puerto, agente.version))  # En unidades
    hrStorageSize = int(consultaSNMP(agente.comunidad, agente.host,
                                     "1.3.6.1.2.1.25.2.3.1.5.1", agente.puerto, agente.version))  # En unidades
    # Regla de 3 para sacar porcentaje
    cargaHDD = hrStorageUsed*100/hrStorageSize
    return cargaHDD


def calculoCargaRamLinux(agente: Agente):
    memTotalReal = int(consultaSNMP(agente.comunidad, agente.host,
                                    "1.3.6.1.4.1.2021.4.5.0", agente.puerto, agente.version))  # En kB's
    memUsed = int(consultaSNMP(agente.comunidad, agente.host,
                               "1.3.6.1.4.1.2021.4.6.0", agente.puerto, agente.version))  # En kB's

    cargaRAM = memUsed*100/memTotalReal
    return cargaRAM
