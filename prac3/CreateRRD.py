#!/usr/bin/env python

import rrdtool

def crearRRD(host:str):
    ret = rrdtool.create("datosGenerados/agente_"+host+"/RRDagente_"+host+".rrd",
                     "--start",'N',
                     "--step",'60',
                     "DS:ifInNUcastPkts:COUNTER:600:U:U", #1) Paquetes multicast que ha enviado una interfaz:
                     "DS:ipOutRequests:COUNTER:600:U:U",  #2) Paquetes IPv4 que los protocolos locales de usuarios de IPv4 suministraron a IPv4 en las solicitudes de transmisión
                     "DS:icmpInMsgs:COUNTER:600:U:U",  #3) Mensajes ICMP que ha recibido el agente
                     "DS:tcpRetransSegs:COUNTER:600:U:U",  # 4) Segmentos retransmitidos; es decir, el número de segmentos TCP transmitidos que contienen uno o más octetos transmitidos previamente
                     "DS:udpOutDatagrams:COUNTER:600:U:U",  # 5) Datagramas enviados por el dispositivo
                     "RRA:AVERAGE:0.5:6:5",
                     "RRA:AVERAGE:0.5:1:20")

    if ret:
        print (rrdtool.error())

def trendCreate(host: str):
    ret = rrdtool.create("datosGenerados/agente_"+host+"/RRDagenteTrend_"+host+".rrd",
                     "--start",'N',
                     "--step",'60',
                     "DS:CPUload:GAUGE:600:U:U",
                     "DS:RAMload:GAUGE:600:U:U",
                     "DS:HDDload:GAUGE:600:U:U",
                     "RRA:AVERAGE:0.5:1:24")
    if ret:
        print (rrdtool.error())