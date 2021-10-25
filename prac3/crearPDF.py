import os
import pathlib

from jinja2 import Template
from xhtml2pdf import pisa

from claseAgente import Agente


def convertHtmlToPdf(data, sourceHtml, outputFilename, base_dir):
    resultFile = open(outputFilename, "w+b")
    template = Template(open(os.path.join(base_dir, sourceHtml)).read())
    html = template.render(data)
    pisaStatus = pisa.CreatePDF(html, dest=resultFile)
    resultFile.close()
    return pisaStatus.err


def generaReporte(agente: Agente):
    carpetaImagenes = "datosGenerados/agente_"+agente.host
    base_dir = pathlib.Path().parent.absolute()
    sourceHtml = os.path.join(base_dir, 'index.html')
    outputFilename = carpetaImagenes+"/reporte.pdf"
    lista = []

    archivos = os.listdir(os.path.join(base_dir, carpetaImagenes))
    for f in archivos:
        name, ext = os.path.splitext(f)
        if ext == '.png':
            lista.append(f)
    lista = sorted(lista)
    data = {'imagen1': lista, 'carpeta': carpetaImagenes, 'so': agente.so,
            'desc': agente.desc, 'comunidad': agente.comunidad, 'host': agente.host, 'tiempoActividad': agente.tiempoActividad, 'puerto': agente.puerto, 'ubicacion': agente.ubicacion}  # Nuevo!
    pisa.showLogging()
    convertHtmlToPdf(data, sourceHtml, outputFilename, base_dir)
