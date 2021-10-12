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

                         "CDEF:umbral15=cargaRAM,15,LT,0,cargaRAM,IF",
                         "CDEF:umbral60=cargaRAM,60,LT,0,cargaRAM,IF",
                         "CDEF:umbral80=cargaRAM,80,LT,0,cargaRAM,IF",

                         "AREA:cargaRAM#0000FF:Carga de la RAM",
                         "AREA:umbral15#CCFFCC:Carga RAM mayor que 15%",
                         "AREA:umbral60#FFE0B3:Carga RAM mayor que 60%",
                         "AREA:umbral80#FFB3B3:Carga RAM mayor que 80%",
                         "HRULE:15#00FF00:Umbral 1 - 15%",
                         "HRULE:60#FF9900:Umbral 16 - 60%",
                         "HRULE:80#FF0000:Umbral 61 - 80%",

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
    if 15 < valor <= 60 and banderas[0]:
        banderas[0] = False
        t = threading.Thread(target=send_alert_attached,args=("Se sobrepaso el umbral READY en RAM",imgpath+"deteccionRAM.png"),daemon=True)
        t.start()
    if 60 < valor <= 80 and banderas[1]:
        banderas[1] = False
        t = threading.Thread(target=send_alert_attached,args=("Se sobrepaso el umbral SET en RAM",imgpath+"deteccionRAM.png"),daemon=True)
        t.start()
    if valor > 80 and banderas[2]:
        banderas[2] = False
        t = threading.Thread(target=send_alert_attached,args=("Se sobrepaso el umbral GO en RAM",imgpath+"deteccionRAM.png"),daemon=True)
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

                         "CDEF:umbral15=cargaCPU,15,LT,0,cargaCPU,IF",
                         "CDEF:umbral60=cargaCPU,60,LT,0,cargaCPU,IF",
                         "CDEF:umbral80=cargaCPU,80,LT,0,cargaCPU,IF",

                         "AREA:cargaCPU#0000FF:Carga del CPU",
                         "AREA:umbral15#CCFFCC:Carga CPU mayor que 15%",
                         "AREA:umbral60#FFE0B3:Carga CPU mayor que 60%",
                         "AREA:umbral80#FFB3B3:Carga CPU mayor que 80%",
                         "HRULE:15#00FF00:Umbral 1 - 15%",
                         "HRULE:60#FF9900:Umbral 16 - 60%",
                         "HRULE:80#FF0000:Umbral 61 - 80%",

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
    if 15 < valor <= 60 and banderas[0]:
        banderas[0] = False
        t = threading.Thread(target=send_alert_attached,args=("Se sobrepaso el umbral READY en CPU",imgpath+"deteccionCPU.png"),daemon=True)
        t.start()
    if 60 < valor <= 80 and banderas[1]:
        banderas[1] = False
        t = threading.Thread(target=send_alert_attached,args=("Se sobrepaso el umbral SET en CPU",imgpath+"deteccionCPU.png"),daemon=True)
        t.start()
    if valor > 80 and banderas[2]:
        banderas[2] = False
        t = threading.Thread(target=send_alert_attached,args=("Se sobrepaso el umbral GO en CPU",imgpath+"deteccionCPU.png"),daemon=True)
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
    mailsender = "sburkok@gmail.com"
    mailreceip = "sburkok@gmail.com"
    mailserver = 'smtp.gmail.com: 587'
    password = 'Secreto123!'
    """ Envía un correo electrónico adjuntando la imagen en IMG
    """
    msg = MIMEMultipart()
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

""" import threading, time

vmas_hilos=False
def contar(segundos):
    global vmas_hilos
    inicial = time.time()
    limite = inicial + segundos
    while inicial<=limite:
        inicial = time.time()
    vmas_hilos = True
    
def accion():
    global vmas_hilos
    while not vmas_hilos:
        print("Hola")
    

segundos = 300
hilo = threading.Thread(name='contador',
                            target=accion, 
                            args=())
hilo2 = threading.Thread(name='contador',
                            target=contar, 
                            args=(segundos,))
hilo.start()
hilo2.start() """
