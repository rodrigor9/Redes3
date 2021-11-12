import logging
import threading
import smtplib
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from claseAgente import Agente
import rrdtool
import time

logging.basicConfig(level=logging.INFO,
                    format='[%(levelname)s] (%(threadName)-s) %(message)s')

def filtrarTiempoGraphV(data: str):
    tiempo = data.replace(" ", "-", 2)
    tiempo = tiempo.split(sep=" ", maxsplit=1)
    tiempo[1] = tiempo[1].replace(" ", ":")
    tiempo = " ".join(tiempo)
    return tiempo


def graficaUDP(agente: Agente, tiempoInicial, tiempoFinal):
    # Grafica desde el tiempo actual menos diez minutos

    tiempoInicial = time.strptime(tiempoInicial, "%d-%m-%Y %H:%M")
    tiempoInicial = int(time.mktime(tiempoInicial))

    tiempoFinal = time.strptime(tiempoFinal, "%d-%m-%Y %H:%M")
    tiempoFinal = int(time.mktime(tiempoFinal))


    rrdpath = "datosGenerados/agente_"+agente.host + \
        "/RRDagenteUDP_"+agente.host+".rrd"
    imgpath = "datosGenerados/agente_"+agente.host+"/"
    
    ret = rrdtool.graphv(imgpath+"paquetesEnviadosUDP.png",
                         "--start", str(tiempoInicial),
                         "--end", str(tiempoFinal),
                         "--vertical-label=Numero de datagramas",
                         "--title=Datagramas enviados por el host "+agente.host,

                         "DEF:protocoloUDP="+rrdpath+":protocoloUDP:AVERAGE",

                         "VDEF:cargaMAX=protocoloUDP,MAXIMUM",
                         "VDEF:cargaMIN=protocoloUDP,MINIMUM",
                         

                         "CDEF:antesLimite=protocoloUDP,750,GT,0,protocoloUDP,IF",
                         "CDEF:limite=protocoloUDP,750,LT,0,protocoloUDP,IF",
                         "CDEF:limite2=protocoloUDP,750,LT,INF,protocoloUDP,IF",

                         "VDEF:antesLimiteLAST=antesLimite,MAXIMUM",
                         "VDEF:limiteFIRST=limite2,MINIMUM",

                         "AREA:protocoloUDP#0000FF:Datagramas enviados",
                         "AREA:limite#FFB3B3:Datagramas enviados que pasaron el limite",
                         "HRULE:750#FF0000:Limite de datagramas [750]",

                         "PRINT:antesLimiteLAST:%0.0lf",
                         "PRINT:antesLimiteLAST:%d %m %Y %H %M:strftime",

                         "PRINT:limiteFIRST:%0.0lf",
                         "PRINT:limiteFIRST:%d %m %Y %H %M:strftime",

                         "GPRINT:cargaMIN:%6.0lf %SMIN",
                         "GPRINT:cargaMAX:%6.0lf %SMAX",

                         "GPRINT:antesLimiteLAST:%6.0lf %SUltimo Valor Cuota Regular",
                         "GPRINT:limiteFIRST:%6.0lf %SPrimer Valor Cuota Doble")
    lista = []
    for i in range(4):
        string = f"print[{i}]"
        lista.append(ret[string])

    
    lista[1] = filtrarTiempoGraphV(lista[1])
    lista[3] = filtrarTiempoGraphV(lista[3])
    return lista

def trendRAMGraph(agente: Agente, segundos: int, banderas = [False,False,False]):
    rrdpath = "datosGenerados/agente_"+agente.host + \
        "/RRDagenteTrend_"+agente.host+".rrd"
    imgpath = "datosGenerados/agente_"+agente.host+"/"

    ultima_lectura = int(rrdtool.last(rrdpath))
    tiempo_final = ultima_lectura
    tiempo_inicial = tiempo_final - segundos

    ret = rrdtool.graphv(imgpath+"deteccionRAM.png",
                         "--start", str(tiempo_inicial),
                         "--end", str(tiempo_final),
                         "--vertical-label=RAM load",
                         '--lower-limit', '0',
                         '--upper-limit', '100',
                         "--title=Uso de la RAM del host "+agente.host+"\n Detección de umbrales",

                         "DEF:cargaRAM="+rrdpath+":RAMload:AVERAGE",

                         "VDEF:cargaMAX=cargaRAM,MAXIMUM",
                         "VDEF:cargaMIN=cargaRAM,MINIMUM",
                         "VDEF:cargaSTDEV=cargaRAM,STDEV",
                         "VDEF:cargaLAST=cargaRAM,LAST",

                         "CDEF:umbral15=cargaRAM,"+str(agente.umbralRAM['ready'])+",LT,0,cargaRAM,IF",
                         "CDEF:umbral60=cargaRAM,"+str(agente.umbralRAM['set'])+",LT,0,cargaRAM,IF",
                         "CDEF:umbral80=cargaRAM,"+str(agente.umbralRAM['go'])+",LT,0,cargaRAM,IF",

                         "AREA:cargaRAM#0000FF:Carga de la RAM",
                         "AREA:umbral15#CCFFCC:Carga RAM mayor que "+str(agente.umbralRAM['ready'])+"%",
                         "AREA:umbral60#FFE0B3:Carga RAM mayor que "+str(agente.umbralRAM['set'])+"%",
                         "AREA:umbral80#FFB3B3:Carga RAM mayor que "+str(agente.umbralRAM['go'])+"%",
                         "HRULE:"+str(agente.umbralRAM['ready'])+"#00FF00:Umbral 1 - "+str(agente.umbralRAM['ready'])+"%",
                         "HRULE:"+str(agente.umbralRAM['set'])+"#FF9900:Umbral "+str(agente.umbralRAM['ready']+1)+" - "+str(agente.umbralRAM['set'])+"%",
                         "HRULE:"+str(agente.umbralRAM['go'])+"#FF0000:Umbral "+str(agente.umbralRAM['set']+1)+" - "+str(agente.umbralRAM['go'])+"%",

                         "PRINT:cargaMAX:%0.2lf",
                         "PRINT:cargaMAX:%Y %m %d %H %M:strftime",
                         "GPRINT:cargaMIN:%6.2lf %SMIN",
                         "GPRINT:cargaMAX:%6.2lf %SMAX",
                         "GPRINT:cargaSTDEV:%6.2lf %SSTDEV",
                         "GPRINT:cargaLAST:%6.2lf %SLAST")

    valor = ret["print[0]"]
    tiempo = ret["print[1]"].replace(" ", "-", 2)
    tiempo = tiempo.split(sep=" ", maxsplit=1)
    tiempo[1] = tiempo[1].replace(" ", ":")
    tiempo = " ".join(tiempo)

    #print(f"Valor: {valor}\nTiempo: {tiempo}")
    valor = float(ret['print[0]'])
    if agente.umbralRAM["ready"] < valor <= agente.umbralRAM["set"] and banderas[0]:
        banderas[0] = False
        t = threading.Thread(target=send_alert_attached,args=("Se sobrepaso el umbral READY en RAM con el valor "+str(valor)+" en el momento "+tiempo,imgpath+"deteccionRAM.png"),daemon=True)
        t.start()
    if agente.umbralRAM["set"] < valor <= agente.umbralRAM["go"] and banderas[1]:
        banderas[1] = False
        t = threading.Thread(target=send_alert_attached,args=("Se sobrepaso el umbral SET en RAM con el valor "+str(valor)+" en el momento "+tiempo,imgpath+"deteccionRAM.png"),daemon=True)
        t.start()
    if valor > agente.umbralRAM["go"] and banderas[2]:
        banderas[2] = False
        t = threading.Thread(target=send_alert_attached,args=("Se sobrepaso el umbral GO en RAM con el valor "+str(valor)+" en el momento "+tiempo,imgpath+"deteccionRAM.png"),daemon=True)
        t.start()

def trendGraph(agente: Agente, segundos: int, banderas = [False,False,False]):
    rrdpath = "datosGenerados/agente_"+agente.host + \
        "/RRDagenteTrend_"+agente.host+".rrd"
    imgpath = "datosGenerados/agente_"+agente.host+"/"

    ultima_lectura = int(rrdtool.last(rrdpath))
    tiempo_final = ultima_lectura
    tiempo_inicial = tiempo_final - segundos

    ret = rrdtool.graphv(imgpath+"deteccionCPU.png",
                         "--start", str(tiempo_inicial),
                         "--end", str(tiempo_final),
                         "--vertical-label=Cpu load",
                         '--lower-limit', '0',
                         '--upper-limit', '100',
                         "--title=Uso del CPU del host "+agente.host+"\n Detección de umbrales",

                         "DEF:cargaCPU="+rrdpath+":CPUload:AVERAGE",

                         "VDEF:cargaMAX=cargaCPU,MAXIMUM",
                         "VDEF:cargaMIN=cargaCPU,MINIMUM",
                         "VDEF:cargaSTDEV=cargaCPU,STDEV",
                         "VDEF:cargaLAST=cargaCPU,LAST",

                         "CDEF:umbral15=cargaCPU,"+str(agente.umbralCPU['ready'])+",LT,0,cargaCPU,IF",
                         "CDEF:umbral60=cargaCPU,"+str(agente.umbralCPU['set'])+",LT,0,cargaCPU,IF",
                         "CDEF:umbral80=cargaCPU,"+str(agente.umbralCPU['go'])+",LT,0,cargaCPU,IF",

                         "AREA:cargaCPU#0000FF:Carga del CPU",
                         "AREA:umbral15#CCFFCC:Carga CPU mayor que "+str(agente.umbralCPU['ready'])+"%",
                         "AREA:umbral60#FFE0B3:Carga CPU mayor que "+str(agente.umbralCPU['set'])+"%",
                         "AREA:umbral80#FFB3B3:Carga CPU mayor que "+str(agente.umbralCPU['go'])+"%",
                         "HRULE:"+str(agente.umbralCPU['ready'])+"#00FF00:Umbral 1 - "+str(agente.umbralCPU['ready'])+"%",
                         "HRULE:"+str(agente.umbralCPU['set'])+"#FF9900:Umbral "+str(agente.umbralCPU['ready']+1)+" - "+str(agente.umbralCPU['set'])+"%",
                         "HRULE:"+str(agente.umbralCPU['go'])+"#FF0000:Umbral "+str(agente.umbralCPU['set']+1)+" - "+str(agente.umbralCPU['go'])+"%",

                         "PRINT:cargaLAST:%0.2lf",
                         "PRINT:cargaLAST:%Y %m %d %H %M:strftime",
                         "GPRINT:cargaMIN:%6.2lf %SMIN",
                         "GPRINT:cargaMAX:%6.2lf %SMAX",
                         "GPRINT:cargaSTDEV:%6.2lf %SSTDEV",
                         "GPRINT:cargaLAST:%6.2lf %SLAST")

    valor = ret["print[0]"]
    tiempo = ret["print[1]"].replace(" ", "-", 2)
    tiempo = tiempo.split(sep=" ", maxsplit=1)
    tiempo[1] = tiempo[1].replace(" ", ":")
    tiempo = " ".join(tiempo)

    #print(f"Valor: {valor}\nTiempo: {tiempo}")
    valor = float(ret['print[0]'])
    if agente.umbralCPU["ready"] < valor <= agente.umbralCPU["set"] and banderas[0]:
        banderas[0] = False
        t = threading.Thread(target=send_alert_attached,args=("Se sobrepaso el umbral READY en CPU con el valor "+str(valor)+" en el momento "+tiempo,imgpath+"deteccionCPU.png"),daemon=True)
        t.start()
    if agente.umbralCPU["set"] < valor <= agente.umbralCPU["go"] and banderas[1]:
        banderas[1] = False
        t = threading.Thread(target=send_alert_attached,args=("Se sobrepaso el umbral SET en CPU con el valor "+str(valor)+" en el momento "+tiempo,imgpath+"deteccionCPU.png"),daemon=True)
        t.start()
    if valor > agente.umbralCPU["go"] and banderas[2]:
        banderas[2] = False
        t = threading.Thread(target=send_alert_attached,args=("Se sobrepaso el umbral GO en CPU con el valor "+str(valor)+" en el momento "+tiempo,imgpath+"deteccionCPU.png"),daemon=True)
        t.start()

def trendHDDGraph(agente: Agente, segundos: int, banderas = [False,False,False]):
    rrdpath = "datosGenerados/agente_"+agente.host + \
        "/RRDagenteTrend_"+agente.host+".rrd"
    imgpath = "datosGenerados/agente_"+agente.host+"/"

    ultima_lectura = int(rrdtool.last(rrdpath))
    tiempo_final = ultima_lectura
    tiempo_inicial = tiempo_final - segundos

    ret = rrdtool.graphv(imgpath+"deteccionHDD.png",
                         "--start", str(tiempo_inicial),
                         "--end", str(tiempo_final),
                         "--vertical-label=Disk load",
                         '--lower-limit', '0',
                         '--upper-limit', '100',
                         "--title=Uso del disco del host "+agente.host+"\n Detección de umbrales",

                         "DEF:cargaHDD="+rrdpath+":HDDload:AVERAGE",

                         "VDEF:cargaMAX=cargaHDD,MAXIMUM",
                         "VDEF:cargaMIN=cargaHDD,MINIMUM",
                         "VDEF:cargaSTDEV=cargaHDD,STDEV",
                         "VDEF:cargaLAST=cargaHDD,LAST",

                         "CDEF:umbral15=cargaHDD,"+str(agente.umbralHDD['ready'])+",LT,0,cargaHDD,IF",
                         "CDEF:umbral60=cargaHDD,"+str(agente.umbralHDD['set'])+",LT,0,cargaHDD,IF",
                         "CDEF:umbral80=cargaHDD,"+str(agente.umbralHDD['go'])+",LT,0,cargaHDD,IF",

                         "AREA:cargaHDD#0000FF:Carga del disco",
                         "AREA:umbral15#CCFFCC:Carga disco mayor que "+str(agente.umbralHDD['ready'])+"%",
                         "AREA:umbral60#FFE0B3:Carga disco mayor que "+str(agente.umbralHDD['set'])+"%",
                         "AREA:umbral80#FFB3B3:Carga disco mayor que "+str(agente.umbralHDD['go'])+"%",
                         "HRULE:"+str(agente.umbralHDD['ready'])+"#00FF00:Umbral 1 - "+str(agente.umbralHDD['ready'])+"%",
                         "HRULE:"+str(agente.umbralHDD['set'])+"#FF9900:Umbral "+str(agente.umbralHDD['ready']+1)+" - "+str(agente.umbralHDD['set'])+"%",
                         "HRULE:"+str(agente.umbralHDD['go'])+"#FF0000:Umbral "+str(agente.umbralHDD['set']+1)+" - "+str(agente.umbralHDD['go'])+"%",

                         "PRINT:cargaLAST:%0.2lf",
                         "PRINT:cargaLAST:%Y %m %d %H %M:strftime",
                         "GPRINT:cargaMIN:%6.2lf %SMIN",
                         "GPRINT:cargaMAX:%6.2lf %SMAX",
                         "GPRINT:cargaSTDEV:%6.2lf %SSTDEV",
                         "GPRINT:cargaLAST:%6.2lf %SLAST")

    valor = ret["print[0]"]
    tiempo = ret["print[1]"].replace(" ", "-", 2)
    tiempo = tiempo.split(sep=" ", maxsplit=1)
    tiempo[1] = tiempo[1].replace(" ", ":")
    tiempo = " ".join(tiempo)

    #print(f"Valor: {valor}\nTiempo: {tiempo}")
    valor = float(ret['print[0]'])
    if agente.umbralHDD["ready"] < valor <= agente.umbralHDD["set"] and banderas[0]:
        banderas[0] = False
        t = threading.Thread(target=send_alert_attached,args=("Se sobrepaso el umbral READY en disco con el valor "+str(valor)+" en el momento "+tiempo,imgpath+"deteccionHDD.png"),daemon=True)
        t.start()
    if agente.umbralHDD["set"] < valor <= agente.umbralHDD["go"] and banderas[1]:
        banderas[1] = False
        t = threading.Thread(target=send_alert_attached,args=("Se sobrepaso el umbral SET en disco con el valor "+str(valor)+" en el momento "+tiempo,imgpath+"deteccionHDD.png"),daemon=True)
        t.start()
    if valor > agente.umbralHDD["go"] and banderas[2]:
        banderas[2] = False
        t = threading.Thread(target=send_alert_attached,args=("Se sobrepaso el umbral GO en disco con el valor "+str(valor)+" en el momento "+tiempo,imgpath+"deteccionHDD.png"),daemon=True)
        t.start()

def grafica(agente: Agente, tiempoInicial, tiempoFinal, interfaz: int):
    # Grafica desde el tiempo actual menos diez minutos

    tiempoInicial = time.strptime(tiempoInicial, "%d-%m-%Y %H:%M")
    tiempoInicial = int(time.mktime(tiempoInicial))

    tiempoFinal = time.strptime(tiempoFinal, "%d-%m-%Y %H:%M")
    tiempoFinal = int(time.mktime(tiempoFinal))

    nombre = "datosGenerados/agente_"+agente.host+"/RRDagente_"+agente.host

    ret = rrdtool.graph("datosGenerados/agente_"+agente.host+"/"+"1"+".png",
                        "--start", str(tiempoInicial),
                        "--end", str(tiempoFinal),
                        "--vertical-label=Paquetes",
                        "--title=Paquetes de la interfaz\n" +
                        agente.descInterfaces[interfaz-1],
                        "DEF:ifInNUcastPkts="+nombre+".rrd:ifInNUcastPkts:AVERAGE",

                        "LINE2:ifInNUcastPkts#0000FF:Paquetes multicast enviados")
    ret = rrdtool.graph("datosGenerados/agente_"+agente.host+"/"+"2"+".png",
                        "--start", str(tiempoInicial),
                        "--end", str(tiempoFinal),
                        "--vertical-label=Paquetes",
                        "--title=Paquetes IPv4 que los protocolos locales\nde usuarios de IPv4 suministraron a IPv4\nen las solicitudes de transmisión.",
                        "DEF:ipOutRequests="+nombre+".rrd:ipOutRequests:AVERAGE",

                        "AREA:ipOutRequests#EE82EE:Paquetes IPv4")
    ret = rrdtool.graph("datosGenerados/agente_"+agente.host+"/"+"3"+".png",
                        "--start", str(tiempoInicial),
                        "--end", str(tiempoFinal),
                        "--vertical-label=Mensajes",
                        "--title=Mensajes ICMP que ha recibido el agente.",
                        "DEF:icmpInMsgs="+nombre+".rrd:icmpInMsgs:AVERAGE",

                        "AREA:icmpInMsgs#800000:Mensajes ICMP")
    ret = rrdtool.graph("datosGenerados/agente_"+agente.host+"/"+"4"+".png",
                        "--start", str(tiempoInicial),
                        "--end", str(tiempoFinal),
                        "--vertical-label=Segmentos",
                        "--title=Segmentos TCP transmitidos que contienen uno\no mas octetos transmitidos previamente.",
                        "DEF:tcpRetransSegs="+nombre+".rrd:tcpRetransSegs:AVERAGE",

                        "LINE2:tcpRetransSegs#FF9966:Segmentos retransmitidos")
    ret = rrdtool.graph("datosGenerados/agente_"+agente.host+"/"+"5"+".png",
                        "--start", str(tiempoInicial),
                        "--end", str(tiempoFinal),
                        "--vertical-label=Datagramas",
                        "--title=Datagramas enviados por el dispositivo.",
                        "DEF:udpOutDatagrams="+nombre+".rrd:udpOutDatagrams:AVERAGE",

                        "AREA:udpOutDatagrams#9400D3:Datagramas enviados.")

def send_alert_attached(subject,imgpath):
    mailsender = "luciaprueba027@gmail.com"
    mailreceip = " tanibet.escom@gmail.com"
    mailserver = 'smtp.gmail.com: 587'
    password = 'Secreto123!'
    """ Envía un correo electrónico adjuntando la imagen en IMG
    """
    msg = MIMEMultipart("Te mando este mensaje")
    msg['Subject'] = subject
    msg['From'] = mailsender
    msg['To'] = mailreceip
    fp = open(imgpath, 'rb')
    img = MIMEImage(fp.read())
    fp.close()
    msg.attach(img)
    s = smtplib.SMTP(mailserver)

    s.starttls()
    # Login Credentials for sending the mail
    s.login(mailsender, password)

    s.sendmail(mailsender, mailreceip, msg.as_string())
    s.quit()

def genericaCPU(agente: Agente, segundos: int):
    rrdpath = "datosGenerados/agente_"+agente.host + \
        "/RRDagenteTrend_"+agente.host+".rrd"
    imgpath = "datosGenerados/agente_"+agente.host+"/"

    ultima_lectura = int(rrdtool.last(rrdpath))
    tiempo_final = ultima_lectura
    tiempo_inicial = tiempo_final - segundos

    ret = rrdtool.graph(imgpath+"umbralCPU.png",
                         "--start", str(tiempo_inicial),
                         "--end", str(tiempo_final),
                         "--vertical-label=Cpu load",
                         '--lower-limit', '0',
                         '--upper-limit', '100',
                         "--title=Uso del CPU del host "+agente.host+"\n Detección de umbrales",

                         "DEF:cargaCPU="+rrdpath+":CPUload:AVERAGE",

                         "AREA:cargaCPU#0000FF:Carga del CPU")

def genericaRAM(agente: Agente, segundos: int):
    rrdpath = "datosGenerados/agente_"+agente.host + \
        "/RRDagenteTrend_"+agente.host+".rrd"
    imgpath = "datosGenerados/agente_"+agente.host+"/"

    ultima_lectura = int(rrdtool.last(rrdpath))
    tiempo_final = ultima_lectura
    tiempo_inicial = tiempo_final - segundos

    ret = rrdtool.graph(imgpath+"umbralRAM.png",
                         "--start", str(tiempo_inicial),
                         "--end", str(tiempo_final),
                         "--vertical-label=RAM load",
                         '--lower-limit', '0',
                         '--upper-limit', '100',
                         "--title=Uso de la RAM del host "+agente.host+"\n Detección de umbrales",

                         "DEF:cargaRAM="+rrdpath+":RAMload:AVERAGE",

                         "AREA:cargaRAM#0000FF:Carga de la RAM")

def genericaHDD(agente: Agente, segundos: int):
    rrdpath = "datosGenerados/agente_"+agente.host + \
        "/RRDagenteTrend_"+agente.host+".rrd"
    imgpath = "datosGenerados/agente_"+agente.host+"/"

    ultima_lectura = int(rrdtool.last(rrdpath))
    tiempo_final = ultima_lectura
    tiempo_inicial = tiempo_final - segundos

    ret = rrdtool.graph(imgpath+"umbralHDD.png",
                         "--start", str(tiempo_inicial),
                         "--end", str(tiempo_final),
                         "--vertical-label=Disk load",
                         '--lower-limit', '0',
                         '--upper-limit', '100',
                         "--title=Uso de disco del host "+agente.host+"\n Detección de umbrales",

                         "DEF:cargaHDD="+rrdpath+":HDDload:AVERAGE",

                         "AREA:cargaHDD#0000FF:Carga del disco")
