from pysnmp.hlapi import *

def consultaSNMP(comunidad,host,oid, puerto, version):
    model = 0 if "v1" in version else 1
    tuplaConsulta = next(
        getCmd(SnmpEngine(),
               CommunityData(comunidad,mpModel=model),
               UdpTransportTarget((host, puerto)),
               ContextData(),
               ObjectType(ObjectIdentity(oid))))

    errorIndication, errorStatus, errorIndex, varBinds = tuplaConsulta

    if errorIndication:
        print(errorIndication)
    elif errorStatus:
        print('%s at %s' % (errorStatus.prettyPrint(),errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
    else:
        for varBind in varBinds:
            varB=(' = '.join([x.prettyPrint() for x in varBind]))
            resultado= varB.split(sep=" ",maxsplit=2)[2]
    return resultado