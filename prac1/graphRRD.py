from claseAgente import Agente
import rrdtool
import time
def grafica(agente: Agente, tiempoInicial, tiempoFinal, interfaz:int):
    #Grafica desde el tiempo actual menos diez minutos

    tiempoInicial = time.strptime(tiempoInicial, "%d-%m-%Y %H:%M")
    tiempoInicial = int(time.mktime(tiempoInicial))

    tiempoFinal = time.strptime(tiempoFinal, "%d-%m-%Y %H:%M")
    tiempoFinal = int(time.mktime(tiempoFinal))

    nombre = "datosGenerados/agente_"+agente.host+"/RRDagente_"+agente.host

    ret = rrdtool.graph("datosGenerados/agente_"+agente.host+"/"+"1"+".png",
                        "--start",str(tiempoInicial),
                        "--end",str(tiempoFinal),
                        "--vertical-label=Paquetes",
                        "--title=Paquetes de la interfaz\n"+agente.descInterfaces[interfaz-1],
                        "DEF:ifInNUcastPkts="+nombre+".rrd:ifInNUcastPkts:AVERAGE",
                        #"AREA:inoctets#00FF00:Tráfico de entrada",
                        "LINE2:ifInNUcastPkts#0000FF:Paquetes multicast enviados")
    ret = rrdtool.graph("datosGenerados/agente_"+agente.host+"/"+"2"+".png",
                        "--start",str(tiempoInicial),
                        "--end",str(tiempoFinal),
                        "--vertical-label=Paquetes",
                        "--title=Paquetes IPv4 que los protocolos locales\nde usuarios de IPv4 suministraron a IPv4\nen las solicitudes de transmisión.",
                        "DEF:ipOutRequests="+nombre+".rrd:ipOutRequests:AVERAGE",
                        #"AREA:inoctets#00FF00:Tráfico de entrada",
                        "AREA:ipOutRequests#EE82EE:Paquetes IPv4")
    ret = rrdtool.graph("datosGenerados/agente_"+agente.host+"/"+"3"+".png",
                        "--start",str(tiempoInicial),
                        "--end",str(tiempoFinal),
                        "--vertical-label=Mensajes",
                        "--title=Mensajes ICMP que ha recibido el agente.",
                        "DEF:icmpInMsgs="+nombre+".rrd:icmpInMsgs:AVERAGE",
                        #"AREA:inoctets#00FF00:Tráfico de entrada",
                        "AREA:icmpInMsgs#800000:Mensajes ICMP")
    ret = rrdtool.graph("datosGenerados/agente_"+agente.host+"/"+"4"+".png",
                        "--start",str(tiempoInicial),
                        "--end",str(tiempoFinal),
                        "--vertical-label=Segmentos",
                        "--title=Segmentos TCP transmitidos que contienen uno\no mas octetos transmitidos previamente.",
                        "DEF:tcpRetransSegs="+nombre+".rrd:tcpRetransSegs:AVERAGE",
                        #"AREA:inoctets#00FF00:Tráfico de entrada",
                        "LINE2:tcpRetransSegs#FF9966:Segmentos retransmitidos")
    ret = rrdtool.graph("datosGenerados/agente_"+agente.host+"/"+"5"+".png",
                        "--start",str(tiempoInicial),
                        "--end",str(tiempoFinal),
                        "--vertical-label=Datagramas",
                        "--title=Datagramas enviados por el dispositivo.",
                        "DEF:udpOutDatagrams="+nombre+".rrd:udpOutDatagrams:AVERAGE",
                        #"AREA:inoctets#00FF00:Tráfico de entrada",
                        "AREA:udpOutDatagrams#9400D3:Datagramas enviados.")