from cryptography.fernet import Fernet  # libreria para la encriptación y desencriptación de los datos
import rostros_pb2  # generado por protoc
import os   # sistema operativo para manejo de archivos
import numpy as np  # libreria para el manejo de encodings

# para el cambio a protobuf me apoye de la IA ya que a pesar de encontrar repositorios con ejemplos se me dificulto mucho la implementación al proyecto

class Seguridad:
    def __init__(self, key_path="clave.key"):
        self.key_path = key_path    # es la ruta donde se guardará o leerá la clave de cifrado
        self.fernet = self.cargar_o_crear_clave()   # guarda el objeto necesario para cifrar y descifrar

    def cargar_o_crear_clave(self):  # método para cargar o generar una clave
        if os.path.exists(self.key_path):   # se verifica si la clave ya existe
            with open(self.key_path, "rb") as f:  # se obtiene la clave según la ruta establecida 
                key = f.read()  # lee la clave generada 
        else:   # si no hay una clave establecida
            key = Fernet.generate_key()   # genera la clave en la variable key
            with open(self.key_path, "wb") as f:    # se va a la ruta establecida
                f.write(key)    # genera la clave 
        return Fernet(key)  # retorna la clave guardada o una nueva generada

    def encriptar_objeto(self, obj_bytes):  # método para encriptar los datos
        return self.fernet.encrypt(obj_bytes)   # retorna encriptados los bytes que se les ingresaron

    def desencriptar_objeto(self, datos_encriptados):   # método para desencriptar los datos
        return self.fernet.decrypt(datos_encriptados)   # retorna desencriptados los bytes que se le ingresaron

    def guardar_encriptado(self, datos_dict, archivo):  # método para guardar los encriptados
        mensaje = rostros_pb2.DatosRostros()    # crea un mensaje protobuf
        mensaje.nombres.extend(datos_dict["nombres"])   # se agregan directamente los nombres
        mensaje.encodings.extend([e.tobytes() for e in datos_dict["encodings"]]) # recorre todos los encodings, los convierte a bytes y luego los agrega 
        
        if "imagenes" in datos_dict:    # se verifica si el diccionario tiene imagenes
            mensaje.imagenes.extend(datos_dict["imagenes"]) # si hay imagenes las agrega
        
        datos_bytes = mensaje.SerializeToString()   # se serializa el mensaje con todo lo agregado anteriormente
        with open(archivo, "wb") as f:  # se abre el archivo en escritura binaria
            f.write(self.encriptar_objeto(datos_bytes)) # escribe en el archivo los datos serializados y los encripta

    def cargar_encriptado(self, archivo):   # método para cargar los encriptados 
        with open(archivo, "rb") as f:  # se abre el archivo en lectura binaria
            datos = self.desencriptar_objeto(f.read())  # se guardan los datos desencriptados en la variable

        mensaje = rostros_pb2.DatosRostros()    # creamos un objeto protobuf
        mensaje.ParseFromString(datos)  # lo llemanos con los datos desencriptados

        encodings_np = [np.frombuffer(enc, dtype=np.float64) for enc in mensaje.encodings]  # convierte los bytes a arrays de numpy

        return {    # retorna los datos como un diccionario (exactamente el mismo que se tenia antes de la ecriptación)
            "nombres": list(mensaje.nombres),
            "encodings": encodings_np,
            "imagenes": list(mensaje.imagenes)
        }