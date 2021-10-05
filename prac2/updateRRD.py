from claseAgente import Agente
import time
import rrdtool
from getSNMP import consultaSNMP
import logging

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] (%(threadName)-s) %(message)s')

def update(agente: Agente, interfaz: int):
    logging.info("Monitorizando para el host "+agente.host+" e interfaz "+str(interfaz))
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
        
        rrdtool.update("datosGenerados/agente_"+agente.host+"/RRDagente_"+agente.host+".rrd", valor)
        rrdtool.dump("datosGenerados/agente_"+agente.host+"/RRDagente_"+agente.host+".rrd", "datosGenerados/agente_"+agente.host+"/RRDagente_"+agente.host+".xml")
        time.sleep(1)
