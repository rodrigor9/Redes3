from ftplib import FTP
import getpass
import telnetlib


def genera_archivo_conf(HOST: str):

    user = input(f"Ingresa el nombre de usuario para el host {HOST}: ")
    password = getpass.getpass()

    tn = telnetlib.Telnet(HOST)
    tn.read_until(b"User: ")
    tn.write(user.encode('ascii') + b"\n")
    if password:
        tn.read_until(b"Password: ")
        tn.write(password.encode('ascii') + b"\n")

    tn.write(b"en\n")
    tn.write(b"dir\n")
    tn.write(b"show running-config\n")
    tn.write(b"show startup-config\n")
    tn.write(b"copy running-config startup-config\n")
    tn.write(b"show startup-config\n")
    tn.write(b"exit\n")

    print(tn.read_all().decode('ascii'))
    print("\nConfiguracion generada exitosamente")

def cliente_ftp(host: str):
    # Datos
    user = input("Ingresa el usuario: ")
    password = input("Ingresa la contraseña: ")
    # Realizar la conexion
    try:
        ftp = FTP(host)  # connect to host, default port
        ftp.login(user=user, passwd=password)  # user anonymous, passwd anonymous@
        print("Conexion establecida con el host", host)
        # Mostramos el directorio
        ftp.dir()

        #Menu de opcion
        print("""¿Qué desea hacer?
        1.Extraer un archivo de configuracion
        2.Enviar un archivo de configuracion
        """)

        opcion = input("Seleccione una opcion: ")
        while(opcion not in '1' and opcion not in '2'):
            print("""¿Qué desea hacer?
            1.Extraer un archivo de configuracion
            2.Enviar un archivo de configuracion
            """)
            opcion = input("Seleccione una opcion: ")
        #FIN de menu

        if opcion in '1':
            archivo = open("startup-config", 'wb')  # Se crea el archivo
            if ftp.retrbinary("RETR startup-config", archivo.write): #Se guarda el archivo extraido en variable archivo
                print("Archivo recibido exitosamente...\n")
            archivo.close()
        else:
            archivo = open("startup-config",'rb') #Se abre el archivo
            # La funcion storbinary() recibe como primer parametro el nombre del archivo que se va a crear
            # y como segundo el archivo que se va a enviar
            if ftp.storbinary('STOR startup-config',archivo):
                print("\nArchivo enviado exitosamente...\n")
        # ftp.delete("startup-config2")
    except Exception as e:
        # Si ocurre un fallo entonces:
        print("Conexion errada:", str(e))
