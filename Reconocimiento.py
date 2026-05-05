import cv2               # libreria para la captura de video y procesamiento de imagenes
import face_recognition  # libreria para el reconocimiento facial
import os                # libreria para interactuar con el sistema operativo
from Seguridad import Seguridad   # Del archivo Seguridad.py importamos la clase Seguridad
import shutil            # libreria para gestionar archivos y directorios (mover, copiar, eliminar)
import hashlib           # libreria para el cifrado de contraseñas           
from fpdf import FPDF    # libreria para crear archivos PDF
from PIL import Image   # libreria para la manipulación de imágenes
import numpy as np       # libreria para el manejo de arreglos y matrices
import tkinter as tk     # libreria para la creación de ventanas interactivas
from tkinter import messagebox    # complementos de tkinter (messagebox para ventanas emergentes)
import folium   # libreria para la creación de un mapa interactivo
import webbrowser   # libreria para poder abrir el mapa generado
import subprocess   # libreria para poder ejecutar otro script (Reportes)
from dotenv import load_dotenv  # libreria para el almacenamiento de claves en archivos .env
from io import BytesIO # libreria para comprimir y descomprimir imagenes

os.makedirs("Users", exist_ok=True) # crea la carpeta Users si no existe para almacenar las imagenes

dotenv_path = os.path.join("Claves", ".env")    # guardamos en una variable la ruta del archivo .env
load_dotenv(dotenv_path=dotenv_path)    # se carga el archivo .env

def directory_env():    # función para crear la carpeta claves y el arvhivo .env
    os.makedirs("Claves", exist_ok=True)    # crea la carpeta claves
    if not os.path.exists(dotenv_path): # verifica que no haya un archivo .env 
        with open(dotenv_path, "w") as f:   # abre el archivo en modo de escritura
            f.write("")  # crea un .env vacío

def write_env(clave_env, text): # función para escribir las claves cuando son escritas por primera vez
    clave_hash = hashlib.sha256(text.encode()).hexdigest()  # se encripta la clave
    with open(dotenv_path, "a") as f:   # se abre el archivo
        f.write(f"{clave_env}={clave_hash}\n")  # escribe en el .env clave del admin/operador y la clave encriptada

# mensaje de bienvenida
welcome = """¡Bienvenido al sistema de reconocimiento facial!   

📌 Con este programa puedes hacer:

- Reconocimientos faciales en tiempo real
- Agregar rostros para luego ser reconocidos
- Ver nuestro lugar de ubicación
- Generar reportes con los datos de ingreso 
"""
messagebox.showinfo("Bienvenida", welcome)  #muestra el mensaje de vienvenida en una ventana emergente

def limpiar_pantalla():   # función para eliminar el texto en la terminal
    os.system('cls' if os.name == 'nt' else 'clear')    # limpia la consola

load_dotenv()  # carga las variables del .env

class Usuario:
    def __init__(self, rol):
            self.rol = rol
            self.env_key = "CLAVE_ADMIN" if rol == "Admin" else "CLAVE_OPERADOR"

    def verificar_clave(self, clave):   # método para verificar la clave
        directory_env()   # llamado a la función para crear el directorio y el archivo .env
        clave_env = os.getenv(self.env_key)   # obtiene el rol que esta ingresando
        if not clave_env: # si no hay aún una clave del rol a ingresar
            write_env(self.env_key, clave)    # se llama a la función para escribir la clave
            messagebox.showinfo("Clave creada", f"[🔐] No se encontró una clave de {self.rol}. Estableciendo nueva clave.")   # notificación de la creación de una nuveva clave cuando sed inicia por primera vez
            return True   # devuelve true para poder continuar con el programa
        return clave_env == hashlib.sha256(clave.encode()).hexdigest()  # hace una compración entre la clave ingresada y la guardada, si es correcta true, si no false

class Admin(Usuario):  #hereda de la clase Usuario
    def __init__(self, clave, rol):  # constructor de la clase admin
        super().__init__(clave, "Admin")  # llama al constructor de la clase padre (Usuario) y le pasa la clave y el rol

    def añadir_persona(nombre): # método para añadir un nuevo rostro al programa
        ruta = f"Users/{nombre}"    # establecemos la ruta donde se guardará la imagen
        os.makedirs(ruta, exist_ok=True) # crea un directorio para la nueva persona
        cap = cv2.VideoCapture(0)   # inicia la cámara predeterminada
        messagebox.showinfo("Capturar imagen","[📸😁] Presione 'c' para capturar imagen...")
        while True:
            ret, frame = cap.read() # verifica si se pudo capturar el frame - ret es un booleano que indica si la captura se esta haciendo
            if not ret:     # si no se pudo hacer la captura sale
                messagebox.showerror("Error de captura", "[❌] No se pudo capturar la imagen. Verifique la cámara.") # muestra un mensaje de error
                break
            cv2.imshow("Captura", frame)    # muestra la imagen capturada en una ventana
            if cv2.waitKey(1) & 0xFF == ord('c'):   # verifica si la tecla pulsada es la c, de ser asi toma la captura   -ord('c'): devuelve el valor ASCII de la tecla 'c'
                #cv2.waitKey(1) devuelve el valor ASCII de la tecla presionada (si no se presiona ninguna tecla, devuelve -1)
                cv2.imwrite(f"{ruta}/{nombre}.jpg", frame)  # guarda la imagen en la ruta establecida
                break
        cap.release()   # libera la cámara
        cv2.destroyAllWindows() # cierra todas las ventanas abiertas por OpenCV
        print(f"\n [👍 ] Imagen guardada en {ruta}/{nombre}.jpg")    # muestra un mensaje indicando dónde se guardó la imagen.
        carpeta_users = os.path.join('Users')
        rf = Reconocimiento_Facial(carpeta_users)  #se hace esto para que se actualicen los rostros conocidos con el nuevo rostro agregado
        rf.generar_pdf(nombre) # genera el PDF de la persona agregada

class Camara:
    def __init__(self, camera=0):  # el número indica la cámara que se va a usar (0 es la cámara principal por defecto)
        self.camera = camera 
        self.cap = None   # inicializa la variable cap que se usara para almacenar la captura de video
        self.iniciar_camara()   

    def iniciar_camara(self):            
        self.cap = cv2.VideoCapture(self.camera)     # inicia la captura de video
        if not self.cap.isOpened():             # verifica si la cámara se abrió 
            messagebox.showerror("[😥 ] No se pudo abrir la cámara después de varios intentos.")
            exit()   # termina la ejecucion del programa

class Reconocimiento_Facial:
    def __init__(self, carpeta_personas):
        self.encodings_caras_conocidas = []    # lista para almacenar las codificaciones de los rostros conocidos
        self.nombres_caras_conocidas = []      # lista para almacenar los nombres de los rostros conocidos
        self.seguridad = Seguridad()           # clase de seguridad para el encriptamiento
        self.archivo_rostros = "rostros_encriptados.dat"    # se crea un archivo con los rostros encriptados
        self.nombres_vistos_actuales = set()    # crea un conjunto vacío para registrar los nombres de personas detectadas
        
        if os.path.exists(self.archivo_rostros):    # se verifica la existencia del archivo con rostros encriptados
            print("\n[🔐 ] Cargando rostros desde archivo encriptado...")
            try:
                datos = self.seguridad.cargar_encriptado(self.archivo_rostros)  # se crea el objeto con los rostros encriptados
                self.encodings_caras_conocidas = datos["encodings"]     # se crea una lista con los encodings de la persona
                self.nombres_caras_conocidas = datos["nombres"]     # se crea una lista con los nombres de la persona
            except PermissionError as e:
                messagebox.showerror(f"Permiso denegado.", "[❌] No se puede acceder al archivo de rostros encriptados: {self.archivo_rostros}. {e}")
            except Exception as e:  # captura cualquier otro error
                messagebox.showerror(f"Error al cargar rostros encriptados.", "[❌] Error al cargar los rostros encriptados: {self.archivo_rostros}. {e}")  # si ocurre un error al cargar los rostros

        self.cargar_rostros(carpeta_personas)   # carga los archivos en la carpeta donde se almacenan los rostros
        self.seguridad.guardar_encriptado({ # guardamos los rostros encriptados
            "encodings": self.encodings_caras_conocidas,
            "nombres": self.nombres_caras_conocidas
        }, self.archivo_rostros)    # se guardan en el archivo "rostros_encriptados.dat"
        print("\n[👌 ] Rostros procesados y encriptados exitosamente.")
            
        if self.encodings_caras_conocidas:    # guardamos los datos encriptados después de cargar
            imagenes_bytes = []     # crea una lista para almacenar los bytes de las imagenes
            for nombre in self.nombres_caras_conocidas: # recorre la lista que contiene los nombres
                imagen_path = os.path.join('Users', nombre, f"{nombre}.jpg")    # creamos un objeto que ingresa donde esta la imagen de la persona
                try:    # se intenta comprimir la imagen para ahorro de memoria
                    with Image.open(imagen_path) as img:    # se abre la imagen 
                        img = img.convert("RGB")  # convertimos a rbg para asegura formato compatible con jpeg
                        buffer = BytesIO()  # creamos el objeto para poder hacer la compresión
                        img.save(buffer, format="JPEG", quality=70)  # comprime a jpeg con calidad 70%
                        imagenes_bytes.append(buffer.getvalue())    # se añaden los bytes de la imagen comprimida a la lista
                except PermissionError as e:
                    messagebox.showerror("Permiso denegado", f"[❌] No se puede acceder a la imagen de {nombre}: {imagen_path}. {e}")
                except Exception as e:
                    imagenes_bytes.append(b'')  # bytes vacíos si hay error
                
            datos = {   # diccionario con los datos a encriptar
                "encodings": self.encodings_caras_conocidas,
                "nombres": self.nombres_caras_conocidas,
                "imagenes": imagenes_bytes
            }
            
            self.seguridad.guardar_encriptado(datos, self.archivo_rostros)  # hacemos llamado a seguridad para guardar y encriptar las imagenes 
            print("\n[👌 ] Rostros procesados y encriptados exitosamente.")
        else:
            print("\n[⚠️ ] No se encontraron rostros válidos para procesar.")
            
    def cargar_rostros(self, carpeta):
        print(f"[💾] Cargando rostros desde la carpeta: {carpeta}")  
        try:
            for persona in os.listdir(carpeta):  # devuelve una lista con los nombres de las carpetas dentro de la carpeta Users
                persona_dir = os.path.join(carpeta, persona)  # crea la ruta completa de la carpeta de la persona
                if os.path.isdir(persona_dir):  # Verifica que sea una carpeta
                    for archivo in os.listdir(persona_dir):  # Busca imágenes en la subcarpeta
                        if archivo.endswith('.jpg') or archivo.endswith('.png'): #verifica la extensión de la imagen
                            ruta_imagen = os.path.join(persona_dir, archivo) # crea la ruta completa de la imagen
                            print(f"[🤔 ] Procesando imagen: {ruta_imagen}")
                            try: 
                                imagen = face_recognition.load_image_file(ruta_imagen)  # carga la imagen
                                encodings = face_recognition.face_encodings(imagen)  # obtiene los encodings faciales
                                if encodings: #si hay encodings
                                    encoding = encodings[0] # toma el primer encoding
                                    self.encodings_caras_conocidas.append(encoding)  # añade el encoding a la lista de encodings
                                    self.nombres_caras_conocidas.append(persona)  # Usa el nombre de la carpeta como nombre de la persona
                                    print(f"[✅ ] Rostro cargado: {persona}")
                                else:
                                    messagebox.showwarning("Advertencia de archivos", f"[⚠️] No se detectó rostro en {ruta_imagen}")
                            except PermissionError as e:
                                messagebox.showerror(f"Permiso denegado", f"[❌]  No se puede acceder al archivo {ruta_imagen}. {e}")
                            except Exception as e:  # captura cualquier otro error
                                messagebox.showerror(f"Error en el procesamiento",f"[⚠️] Error al procesar la imagen: {ruta_imagen}. {e}")
        except FileNotFoundError as e:
            messagebox.showerror("Carpeta no encontrada:", f"[❌] No se encontró la carpeta: {carpeta}. {e}")  # si no se encuentra la carpeta
        except PermissionError as e:
            messagebox.showerror("Permiso denegado:", f"[❌] No se puede acceder a la carpeta: {carpeta}. {e}")
        except Exception as e:  # captura cualquier otro error
            messagebox.showerror("Error al cargar rostros:", f"[❌] Error al cargar rostros desde la carpeta: {carpeta}. {e}")  # si ocurre un error al cargar los rostros

    def generar_pdf(self, nombre):  # método para generar el pdf 
        #hacemos la comprobación de que existan datos en las listas de nombres y encondings
        if not self.encodings_caras_conocidas or not self.nombres_caras_conocidas:  
            print("\n[❌] No hay rostros cargados en el sistema")
            return

        nombre_busqueda = nombre.strip().lower()  # creamos una variable que almacene el nombre solicitado en minuscuas y sin espacios
        encontrado = False  # establecemos que aún no se ha encontrado
        
        for i, nombre_guardado in enumerate(self.nombres_caras_conocidas):  # itera sobre la lista de nombres guardados
            if nombre_busqueda == nombre_guardado.strip().lower():  # verifica que el el nombre buscado sea el mismo a de algun elemento de la lista
                imagen_path = os.path.join('Users', nombre_guardado, f"{nombre_guardado}.jpg")  #definir la ruta de la imagen temporal
                
                if os.path.exists(imagen_path): # verifica la existencia de la imagen temporal
                    try:
                        pdf = FPDF()   # se crea una instancia de la función de la libreria fpdf
                        pdf.add_page()  # crea una nueva pagina en blanco
                        
                        pdf.set_font("Arial", "B", 16)  # estilos para el título
                        pdf.cell(200, 10, f"Reporte de {nombre_guardado}", ln=True, align="C")  # ln=True salta de línea
                        pdf.ln(10)  # salto de línea de 10 unidades (mm por defecto)
                        
                        try:    # estilos para la imagen
                            img = Image.open(imagen_path)
                            img.thumbnail((100, 100))   # cambia el tamaño de la imagen 
                            temp_path = f"temp_{nombre_guardado}.jpg"  # crea un archivo temporal para guardar la imagen redimensionada
                            img.save(temp_path)   # guarda la imagen redimensionada
                            
                            pdf.image(temp_path, x=60, w=80)  # coloca la imagen en el PDF 
                            pdf.ln(90)  # salto de línea
                            os.remove(temp_path)  # elimina el archivo temporal
                        except FileNotFoundError as e:
                            print(f"[❌ ] Imagen no encontrada: {imagen_path}. {e}")
                            pdf.cell(0, 10, "Imagen no disponible", ln=True)  # si no se encuentra la imagen, se coloca un mensaje en el PDF
                        except PermissionError as e:
                            print(f"[❌ ] Permiso denegado al acceder a la imagen: {imagen_path}. {e}")
                            pdf.cell(0, 10, "Permiso denegado para acceder a la imagen", ln=True)
                        except Exception as e:
                            print(f"Error al procesar imagen: {e}")
                            pdf.cell(0, 10, "Imagen no disponible", ln=True)  # si no se puede cargar la imagen, se coloca un mensaje en el PDF
                        
                        pdf.set_font("Arial", "B", 12)  # estilos para los encodings
                        pdf.cell(0, 10, "Encodings faciales:", ln=True)   # título de la sección de encodings
                        pdf.set_font("Arial", size=8)
                        
                        encoding_str = np.array2string(
                            self.encodings_caras_conocidas[i],  # selecciona el enconding a estilizar
                            precision=4,    # aproxima con 4 decimales
                            separator=', ', # separa los encondiings por comas
                            suppress_small=True #evita notación científica para números muy pequeños
                        )
                        
                        pdf.multi_cell(0, 5, encoding_str)  # coloca el texto en el PDF
                        
                        os.makedirs("PDFs", exist_ok=True) # crea la carpeta PDFs si no existe
                        pdf_name = f"PDFs/{nombre_guardado}_reporte.pdf"
                        try:
                            pdf.output(pdf_name)  # guarda el PDF en la carpeta PDFs
                            print(f"\n[✅ ] PDF generado: {pdf_name}")
                        except PermissionError as e:
                            print(f"[❌] Permiso denegado al guardar el PDF: {pdf_name}. {e}")
                        except Exception as e:  # captura cualquier otro error
                            print(f"[❌] Error al guardar el PDF: {pdf_name}. {e}")
                        # definimos la ruta de la carpeta raiz para luego eliminar las subcarpetas como y solo tener los encodings como método de seguridad
                        carpeta_raiz = os.path.join('Users')    
                        eliminar_subcarpetas(carpeta_raiz)  # llamado a la función que elimina las carpetas
                        encontrado = True   # se actualiza que fue encontradoe el nombre
                        break
                    except Exception as e:  
                        print(f"[❌ ] Error al generar el PDF: {str(e)}")
                else:
                    print(f"[❌ ] Imagen no encontrada para {nombre_guardado}")

        if not encontrado:  # en caso de no encontrar a la persona 
            print(f"\n[❌ ] No se encontró a '{nombre}'")
            print("[👥 ] Personas registradas:", self.nombres_caras_conocidas)    # se muestra la lista con las personas registradas

    def reconocer(self, frame):
        try:
            # convertir de BGR a RGB ya que face_recognition usa RGB y cv2 usa BGR
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # detecta la ubicacion del rostro dentro del frame
            localizacion_cara = face_recognition.face_locations(rgb_frame)
            if not localizacion_cara:
                # si no hay caras en el cuadro, reiniciamos nombres vistos
                self.nombres_vistos_actuales = set()
                return  

            # obtiene las codificaciones faciales 
            encodings_cara = face_recognition.face_encodings(
                rgb_frame,  #toma la imagen RGB
                localizacion_cara,  #usa la unicación de los rostros detectados
                num_jitters=4   # controla cuántas veces se perturba ligeramente (jitter) una imagen antes de calcular el encoding del rostro. Es decir, genera variaciones artificiales del rostro (como leves desplazamientos o ruidos) y promedia los resultados para obtener un encoding más robusto.
                )

            for (top, right, bottom, left), face_encoding in zip(localizacion_cara, encodings_cara):
                # el zip combina la ubicacion del rostro y sus codificaciones en una tupla
                # top, right, bottom, left son las coordenadas del rectángulo que rodea el rostro
                # con el bucle for itera sobre las coordenadas y las codificaciones de los rostros detectados
                # comparar con rostros conocidos
                coincidencias = face_recognition.compare_faces( #devuelve una lista de booleanos que indica si cada rostro conocido coincide con el rostro detectado
                    self.encodings_caras_conocidas, 
                    face_encoding,  # compara la codificación del rostro detectado con las codificaciones de los rostros conocidos
                    tolerance=0.4   # valor de tolerancia para la comparación
                    )
                nombre = "Desconocido"  # nombre por defecto si no se encuentra coincidencia

                if True in coincidencias:   # si hay coincidencias, usa el primer rostro conocido que coincida
                    primer_coincidencia_indice = coincidencias.index(True)  # verifica si hay alguna coincidencia
                    # .index(True) devuelve la posición de la primera coincidencia encontrada en la lista de coincidencias
                    nombre = self.nombres_caras_conocidas[primer_coincidencia_indice]   # obtiene el índice (posicion) de la primera coincidencia
                    
                    if nombre not in self.nombres_vistos_actuales:  # comprobación para que salga únicamente el nombre de la persona cuando este en cámara
                        print(f"[👤 ] Persona reconocida: {nombre}")
                        # guarda el nombre para que solo aparezca una sola vez 
                        self.nombres_vistos_actuales.add(nombre)

                # dibujar rectángulo y etiqueta
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                # color verde (0, 255, 0) (BGR) y grosor de 2
                # requiere 2 puntos: la esquina superior izquierda (left, top) y la esquina inferior derecha (right, bottom) para dibujar el rectángulo
                cv2.putText(
                    frame,  # lugar donde se dibujara el texto
                    nombre,     # texto a escribir
                    (left, top - 10), # posición del texto (justo encima del rectángulo)
                    cv2.FONT_HERSHEY_SIMPLEX,   # tipo de letra
                    0.9,    # tamaño
                    (0, 255, 0), # color
                    2)  # grosor

        except Exception as e:
            print(f"[ ERROR ❌💀 ] en reconocimiento facial: {str(e)}")   

class Popups:
    def __init__(self): # constructor de la clase
        self.usuario = None     
        self.rol_actual = None  # ventanas de rol actual
        self.vLogin = None  # ventanas para logearse
        self.admin_menu = None  # ventanas del menu del admin
        self.admin_frame = None    # frame para el menu del admin 
        self.newP = None    # ventanas para el registro de una persona
        self.name = None    # variable para almacenar el nombre 
        self.intentos = 0   # contador de intentos

    def login(self, rol):   # método de ventanas para el ingreso de contraseñas
        self.usuario = Usuario(rol)
        self.rol_actual = rol   # establecemos el rol actual
        vRol.withdraw() # escondemos la ventana principal
        self.vLogin = tk.Toplevel() # se crea la ventana de login como una superpuesta de la ventana principal
        self.vLogin.title(f"Ingreso como {rol}")    # titulo y tamaño de la ventana
        self.vLogin.geometry("300x200")
        tk.Label(self.vLogin, text=f"Ingresa la clave del {rol}:", pady=10).pack()  # información
        self.contra = tk.Entry(self.vLogin, show="*")   # espacio donde se colocará la contraseña
        self.contra.pack()   
        # boton para ingresar que toma el rol y la contraseña para luego hacer la verificación
        self.clave = self.contra.get()
        tk.Button(self.vLogin, text="Ingresar", pady=10,
                  command=lambda: self.callMenu(self.rol_actual, self.clave)).pack() 

    def callMenu(self, rol, clave):     #método para llamar el menu del usuario que esta ingresando
        if self.usuario.verificar_clave(clave): # si la comprobación de la contraseña fue exitosa
            messagebox.showinfo("Acceso concedido", f"[😎] Acceso concedido como {rol}.")   # mensaje de acceso concedido
            if rol == "Admin":  # se verifica que rol esta ingresando
                info_adm = """ 
Bienvenido Administrador

Aqui podras: 

🔷 Iniciar el reconocimiento facial
🔷 Agregar a nuevas personas para posterior reconocimiento
🔷 Enviar por correo un reporte de la información recopilada

Opciones:

🔶 Si deseas salir del reconocimiento presiona q"""
                messagebox.showinfo("Información de administrador", info_adm)   # se muestra la información del admin
                self.menu_admin()   # llamado al método del menu del admin
            else:
                info_ope = """ 
Bienvenido operador

Aqui podras: 

🔷 Iniciar el reconocimiento facial

Opciones:

🔶 Si deseas salir del reconocimiento presiona q"""
                messagebox.showinfo("Información de operador", info_ope) # se muestra la información del operador
                self.vLogin.destroy()   # se destruye la ventana de contraseñas
                iniciar_programa(self.rol_actual)   # se llama a la función de iniciar el programa 
        else:
            self.intentos += 1  # si la contraseña es erronea se suma uno a los intentos
            if self.intentos >= 3:  # si se superan los 3 intentos el programa se cierra
                messagebox.showerror("Acceso bloqueado", "[🚫] Demasiados intentos. Cerrando la aplicación.")
                exit()
            else:   # se notifica el numero de intentos restantes
                messagebox.showwarning("Acceso denegado", f"[❌] Clave incorrecta. Intento #{self.intentos} de 3")

    def callReport(self):   # método para ejecutar el archivo que genera los reportes
        # ya que es una acción que implica a terceros hacemos una verificación si la accion se desea realizar 
        conf = messagebox.askyesno("Confirmación","¿Estas seguro que deseas generar el reporte y enviarlo por correo?") # si es yes retorna true, si no retorna false
        if conf:    # verifica que opción se eligio
            subprocess.Popen(["python", "Reportes.py"]) # abre el archivo desde la terminal 

    def show_map(self):
        mapa = folium.Map(location=[3.353846, -76.521280], zoom_start=18)   # creaa un mapa centrado en la universidad autonoma, en aulas 3
        folium.Marker([3.353846, -76.521280], popup="Universida Autonoma de occidente").add_to(mapa)    # agregamos el marcador de la ubicación especifica
        os.makedirs("Mapa", exist_ok=True)  # creamos una carpeta para guardar el archivo del mapa
        archivo_mapa = "Mapa/mapa_interactivo.html" # ruta del archivo
        mapa.save(archivo_mapa) # se guarda en la ruta establecida
        webbrowser.open('file://' + os.path.realpath(archivo_mapa)) # abre el mapa en el navegador predeterminado

    def newPerson(self):    # método para registrar a una nueva persona
        self.newP = tk.Toplevel(self.admin_menu)    # creación de la ventana
        self.newP.title("Registro de nueva persona")    # titulo y tamaño
        self.newP.geometry("300x200")
        tk.Label(self.newP, text="Ingrese el nombre de la nueva persona:").pack()   #información
        self.name = tk.Entry(self.newP) # campo donde se coloca el nombre de la persona
        self.name.pack()
        tk.Button(self.newP, text="Aceptar", pady=10, command=self.callNewPerson).pack()    # boton de ok

    def callNewPerson(self):
        self.nombre = self.name.get()   # se obtiene el nombre ingresado de la persona
        self.newP.destroy() # se destruye la ventana 
        Admin.añadir_persona(self.nombre)   # llamado a la función para registrar a la persona

    def menu_admin(self):   # método del menu del admin
        self.vLogin.destroy()   # destrye la ventana de las contraseñas
        self.admin_menu = tk.Toplevel() # creación de la ventana 
        self.admin_menu.geometry("400x300") # tamaño y titulo
        self.admin_menu.title("Menú de Administrador")
        tk.Label(self.admin_menu, text="Bienvenido al menú de administrador", pady=10).pack()   #información
        tk.Label(self.admin_menu, text="Selecciona la opción deseada", pady=10).pack()
        self.admin_frame = tk.Frame(self.admin_menu)    # creación del frame para más organización
        self.admin_frame.pack(pady=10, fill="x")
        tk.Button(self.admin_frame, text="Registrar a una nueva persona", pady=10,   # opciones elegibles
                  command=self.newPerson).pack()
        tk.Button(self.admin_frame, text="Iniciar reconocimiento", pady=10,
                  command=lambda: iniciar_programa(self.rol_actual)).pack()
        tk.Button(self.admin_frame, text="Generar y enviar reporte", pady=10,
                  command=self.callReport).pack()
        tk.Button(self.admin_frame, text="Regresar al menú de roles", pady=10,
                  command=lambda: (self.admin_menu.destroy(), main())).pack()

def eliminar_subcarpetas(carpeta_raiz):  # función para eliminar las imagenes tomadas y solo quedarnos con los encodings
    if not os.path.exists(carpeta_raiz):    # verifica que exista la carpeta donde se almacenana las imagenes
        messagebox.showwarning("Aviso de carpeta", f"[😲] La carpeta {carpeta_raiz} no existe")
        return

    for nombre in os.listdir(carpeta_raiz): # recorre las carpetas con el nombre guardado
        ruta = os.path.join(carpeta_raiz, nombre)   # se crea el objeto y se ingresa a las subcarpetas  
        if os.path.isdir(ruta): # se verifica la existencia de las subcarpetas
            try:
                print("\n[🗑️ ] Eliminando las carpetas con las imagenes por seguridad")    # se notifica la eliminación
                shutil.rmtree(ruta) # se eliminan las subcarpetas
                print(f"[✔ ] Subcarpeta eliminada: {ruta}")
            except Exception as e:
                print(f"\n[❌ ] No se pudo eliminar {ruta}: {e}")  # si no se puede eliminar o si no existen
 
def iniciar_programa(rol_act): # función para iniciar el reconocimiento
    try:
        cam = Camara()    # crea un objeto de la clase Camara
        carpeta_users = os.path.join('Users')   # guardamos la uta de las imagenes en una instancia
        reconocimiento = Reconocimiento_Facial(carpeta_users) # crea un objeto de la clase Reconocimiento y le pasa la ruta de la carpeta donde se encuentran las fotos
        print("\n[😀 ] Sistema iniciado. Presione ''q'' para salir.")
        
        while True:  
            ret, frame = cam.cap.read()  # cam.cap.read() es un método que devuelve dos valores: un booleano (ret) 
            if not ret:
                print("[😥 ] No se pudo recibir el frame")  # si no se pudo leer el frame, imprime un mensaje de error
                continue

            reconocimiento.reconocer(frame)  # llama al método reconocer de la clase Reconocimiento_Facial y le pasa el frame leído de la cámara
            # (reconocimiento es un objeto de la clase Reconocimiento_Facial)
            cv2.imshow("Reconocimiento Facial", frame)  # muestra el frame con el reconocimiento facial en una ventana llamada "Reconocimiento Facial".

            # Salir con "q"
            if cv2.getWindowProperty("Reconocimiento Facial", cv2.WND_PROP_VISIBLE) < 1 or cv2.waitKey(1) == ord("q"):
                                #ord("q") devuelve el valor ASCII de la tecla "q"
                #cv2.waitKey(1) devuelve el valor ASCII de la tecla presionada (si no se presiona ninguna tecla, devuelve -1)
                print("\n[👋 ] Terminando reconocimiento...\n")
                break

    except Exception as e:
        print(f"[❌ ] Error en la aplicación: {str(e)}")
    finally:    # se ejecuta siempre al final, independientemente de si hubo un error o no
        if "cam" in locals():  # verifica si la variable cam existe
            cam.cap.release()  # si existe, libera la cámara
        cv2.destroyAllWindows() # cierra todas las ventanas abiertas por OpenCV
        if rol_act == "Operador":
            main()  # si el rol actual es operador, llama al menú principal para que no se cierre el programa

popup = Popups()    # instacia para el posterior llamado a las ventanas desde main

def main(): # función del menu inicial
    global vRol # se define global para luego hacer cambios en otras clases
    vRol = tk.Tk()   # creación de la ventana con sus respectivos nombres y tañano
    vRol.title("Opciones de ingreso")
    vRol.geometry("300x300")
    infoI = tk.Label(vRol, text="¡Bienvenido al programa de reconocimiento facial!").pack() # información para ingresar
    info_I = tk.Label(vRol, text="¿Quien esta intentando ingresar?", pady = 10).pack()
    main_frame = tk.Frame(vRol) # creación de un frame para mejor organización
    main_frame.pack(pady=10, fill="x")
    adm = tk.Button(main_frame, text="Ingresar como administrador", pady = 10, command = lambda: popup.login("Admin")).pack()  # vopciones elegibles
    ope = tk.Button(main_frame, text="Ingresar como operador", pady = 10, command = lambda: popup.login("Operador")).pack()
    mapa = tk.Button(main_frame, text="Ver nuestra ubicación", pady = 10,  command = popup.show_map).pack()
    close = tk.Button(main_frame, text="Salir del programa", pady = 10, command = exit).pack()    # en caso de querer salir del programa
    vRol.mainloop()

if __name__ == "__main__":  #apenas se inicia el programa llama a la función main
    main()