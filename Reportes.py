import random, faker, pandas as pd    #importar random para generar numeros aleatorios, faker para generar datos falsos y pandas para manejar los datos
from faker import Faker   #importar Faker para generar datos falsos
from datetime import timedelta    #importar timedelta para manejar el tiempo
import matplotlib.pyplot as plt    #importar matplotlib para graficar
import seaborn as sns   #importar seaborn para graficar
import os  #importar os para manejar archivos
from staticmap import StaticMap, CircleMarker #importar staticmap para graficar mapas y circlemarker para marcar puntos en el mapa
from PIL import Image  #importar PIL para manejar imagenes
from fpdf import FPDF  #importar fpdf para crear pdfs
from email.mime.multipart import MIMEMultipart  # Estructura de email con múltiples partes
from email.mime.text import MIMEText  # Cuerpo de texto del email
from email.mime.base import MIMEBase  # Permite adjuntar archivos al correo
from email import encoders  # Codifica archivos adjuntos para el envío
import smtplib  # Protocolo SMTP para enviar correos
#import folium as fm   #importar folium para graficar mapas
import tkinter as tk     # libreria para la creación de ventanas interactivas
from tkinter import ttk, messagebox    # complementos de tkinter
import shutil #import shutil para eliminar carpeta y archivos

ruta_py = os.path.dirname(os.path.abspath(__file__))   #ruta donde se encuentra el archivo python
#os.path.abspath(__file__) devuelve la ruta absoluta del archivo python
#os.path.dirname(__file__) devuelve la ruta del directorio donde se encuentra el archivo python (sin el nombre del archivo)
ruta_carpeta = os.path.join(ruta_py, "Reportes")  #ruta donde se guardaran los reportes - une la ruta del archivo python con Reportes
os.makedirs(ruta_carpeta, exist_ok=True)  #crea la carpeta si no existe

fake = Faker("es_CO")   #crear un objeto Faker para generar datos en español - Colombia

hora_ingreso = [fake.date_time_this_year() for _ in range(150)]     #generar 150 fechas y horas aleatorias de este año

hora_salida = [
    ingreso + timedelta(hours=random.randint(1, 8),     #timedelta sirve para sumar tiempo
                         minutes=random.randint(0, 59), 
                         seconds=random.randint(0, 60))  
    for ingreso in hora_ingreso   #hora de salida es la hora de ingreso + un tiempo aleatorio entre 1 y 8 horas, 0 y 59 minutos y 0 y 60 segundos
]

tiempo_transcurrido = [hora_salida[i] - hora_ingreso[i] for i in range(len(hora_ingreso))]   #calcula el tiempo transcurrido restando la hora de salida a la hora de ingreso

nombre = [fake.name() for _ in range(150)]   #generar 150 nombres aleatorios

edades = [random.randint(16,60) for _ in range(150)]   #generar 150 edades aleatorias entre 16 y 60 años

data = {    #datos a guardar en el dataframe
    "Nombre" : nombre,     #columna de nombres
    "Edad" : edades,    #columna de edades
    "Correo" : [f"{i.split()[0].lower()}.{i.split()[-1].lower()}@uao.edu.co".replace("á", "a")  #dividimos el nombre en partes, tomamos la primera y la ultima palabra, las ponemos en minuscula, las unimos con un punto y añadimos el dominio
                .replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")  #cambiamos caracteres especiales
                for i in nombre],  #lo hacemos con un f string que sirve para formatear  e insertar texto en cadenas de texto
    "Telefono" : [fake.phone_number() for _ in range(150)],  #generar 150 telefonos aleatorios
    "Direccion" : [fake.address() for _ in range(150)],  #generar 150 direcciones aleatorias
    "Ciudad" : [fake.city() for _ in range(150)],   #generar 150 ciudades colombianas aleatorias 
    "Carrera" : [random.choice(["Ingenieria ambiental", "Ingenieria biomedica", "Ingenieria mecanica", "Ingenieria mecatronica", 
                                "Ingenieria electrica", "Ingenieria industrial", "Ingenieria informatica", "Ingenieria multimedia", 
                                "Ingenieria de datos e ia", "Administracion", "Contaduria", "Derecho", "Mercadeo", "Publicidad", 
                                "Arquitectura", "Diseño", "Cine", "Comunicacion", "Narrativas" ]) for _ in range(150)],   #elige una carrera aleatoria 150 veces

    "Tipo de documento" : ["T.I." if edad < 18 else "C.C." for edad in edades],   #tipo de documento, si la edad es menor a 18 es T.I. sino C.C.
    "Numero de documento" : random.sample(range(10000000, 99999999), 150),  #generar 150 numeros de documento aleatorios sin repetirse
    "Hora de ingreso:" : hora_ingreso,  #columna de hora de ingreso
    "Hora de salida" : hora_salida,   #columna de hora de salida
    "Tiempo transcurrido" : tiempo_transcurrido,   #columna de tiempo transcurrido
    "Total entradas semanales" : [random.randint(0, 14) for _ in range(150)],   #generar 150 entradas semanales aleatorias entre 0 y 14
    "Horas de clase semanales" : [random.randint(2, 48) for _ in range(150)],   #generar 150 horas de clase semanales aleatorias entre 2 y 48
    "Promedio de notas" : [round(random.uniform(0, 5), 3) for _ in range(150)], #generar 150 promedios de notas aleatorias entre 0 y 5 con 3 decimales
    "Encodings faciales" : [[fake.pyfloat(left_digits=1, right_digits=4, max_value=1, min_value=-1, positive=False) for _ in range(128)]for _ in range(150)]
    #generar 150 listas de 128 numeros aleatorios entre -1 y 1 con 4 decimales  - positive= false para que pueda generar numeros negativos
}

dataframe = pd.DataFrame(data)  #se crea un dataframe con los datos generados
dataframe["Tiempo transcurrido"] = dataframe["Tiempo transcurrido"].apply(str)  #convertir a string los datos de la columna para que no de error al exportar a excel por el formato de timedelta

#lista de graficos a generar
#eje x , eje y, tipo de grafico, titulo           #la ia me recomendo los mejores tipos de graficos a usar para cada caso
graficos = [
    ("Edad", "Carrera", "boxplot", "Distribución de edad por carrera"),
    ("Edad", "Promedio de notas", "regplot", "Edad vs promedio de notas"),
    ("Horas de clase semanales", "Promedio de notas", "regplot", "Horas de clase semanales vs promedio de notas"),
    ("Carrera", "Promedio de notas", "boxplot", "Distribución de promedio de notas por carrera"),
    ("Carrera", None, "histplot", "Distribucón de personas por carrera"),
    ("Carrera", "Tiempo transcurrido seg", "boxplot", "Distribución de tiempo transcurrido por carrera"),
    ("Total entradas semanales", "Horas de clase semanales", "regplot", "Total entradas semanales vs horas de clase semanales"),
]

# Antes de graficar, convierte "Tiempo transcurrido" a segundos para graficar bien
dataframe["Tiempo transcurrido seg"] = pd.to_timedelta(dataframe["Tiempo transcurrido"]).dt.total_seconds()  
#convertir la columna de tiempo transcurrido a segundos, porque el formato timedelta no se puede graficar
#se pasa de string a timedelta y luego a segundos

mapa = StaticMap(800, 500)  #crea el mapa con un tamaño de 800x500
latitud = 3.353666    #latitud de la ubicacion
longitud = -76.523119  #longitud de la ubicacion
marker = CircleMarker((longitud, latitud), "red", 12)  #crea un marcador en el mapa con la latitud y longitud especificadas, color rojo y tamaño 12
mapa.add_marker(marker)  #añade el marcador al mapa
imagen = mapa.render()  #renderiza el mapa (lo convierte en una imagen)
mapa_png = os.path.join(ruta_carpeta, "mapa.png")  #ruta donde se guardara el mapa
imagen.save(mapa_png)  #guarda el mapa en la ruta especificada

def hacer_grafico(x, y, tipo, titulo, dataframe, nombre_archivo):   #funcion para hacer los graficos
    plt.figure(figsize=(12, 6))  #se define el tamaño de la grafica
    if tipo == "boxplot":   #según el tipo de grafico se hace una cosa u otra
        sns.boxplot(data=dataframe, x=x, y=y)   #crea un boxplot con los datos del dataframe y los ejes x e y
        plt.xticks(rotation=45, ha="right")   #recomendacion de la ia para que no se junten los nombres
    elif tipo == "regplot":   
        sns.regplot(data=dataframe, x=x, y=y, line_kws={'color':'red'}) #crea un regplot con los datos del dataframe y los ejes x e y
        #sns.scatterplot pero con una linea de regresion 
        #line_kws={'color':'red'} para definir el color de la linea
    elif tipo == "histplot":
        #sns.countplot(data=dataframe, x=x)  #crea un countplot con los datos del dataframe y el eje x (la variable a contar) kde=True para que dibuje la densidad de la variable
        sns.histplot(data=dataframe, x=x, kde=True)
        plt.xticks(rotation=45, ha="right")
    else:
        print(f"[🥵] Tipo de gráfico '{tipo}' no disponible.")   #en caso de que el tipo de grafico solicitado no establecido en la función 
        return
    
    plt.title(titulo)   #titulo de la grafica
    plt.tight_layout()   #recomendacion de la ia para que no se junten las cosas
    plt.grid(True)   #crea las cuadriculas de la grafica
    plt.savefig(nombre_archivo)  #guarda la grafica en un archivo
    plt.close()   #cierra la grafica 
    
imagenes = []  #lista para guardar los nombres de las graficas y sus archivos
for i, (x, y, tipo, titulo) in enumerate(graficos):  #recorre la lista de graficos
    nombre_archivo = f"grafico_{i+1}.png"  #nombre del archivo de la grafica
    hacer_grafico(x, y, tipo, titulo, dataframe, nombre_archivo)  #llama a la funcion para hacer el grafico
    imagenes.append((f"Gráfico {i+1}", nombre_archivo))   #añade el nombre del grafico y el archivo a la lista de imagenes como tupla

with pd.ExcelWriter(os.path.join(ruta_carpeta, "data.xlsx"), engine="xlsxwriter") as writer:   #crea un archivo excel en la ruta especificada utilizando xlsxwriter
    #as writer objeto que se crea a partir de la clase ExcelWriter
    dataframe.to_excel(writer, index=False, sheet_name="Datos")  #convierte el dataframe a excel y lo guarda en la hoja Datos
    resumen = dataframe.describe().round(2)   #crea un resumen estadistico del dataframe - redondea a 2 decimales
    resumen.to_excel(writer, sheet_name="Resumen estadístico")   #añade el resumen estadistico a la hoja Resumen estadístico
    workbook = writer.book  #workbook representa el libro de excel que se esta creando - es el objeto que se crea a partir del excelwriter
    hoja_graficos = workbook.add_worksheet("Gráficos")   #crea una hoja nueva para los graficos
    hoja_ubicacion = workbook.add_worksheet("Ubicación")  #crea una hoja nueva para la ubicacion
    hoja_ubicacion.insert_image("B2", mapa_png)  #inserta el mapa en la hoja de ubicacion en la celda B2
    hoja_ubicacion.write("F1", "Ubicación:")  #escribe el texto Ubicación en la celda F1
    enlace_mapa = f"https://www.google.com/maps?q={latitud},{longitud}"  #crea un enlace al mapa interactivo con la latitud y longitud especificadas
    hoja_ubicacion.write_url("B27", enlace_mapa, string="Ver mapa interactivo")  #escribe el enlace al mapa interactivo en la celda B27
    
    fila = 1  #inicia la fila en 1 (deja una celda vacia arriba) (la primera fila es la 0)
    columna = 1 #inicia la columna en 1 (deja una celda vacia a la izquierda) (la primera columna es la 0)
    for nombre_grafico, archivo_img in imagenes:  #recorre la lista de imagenes y guarda el nombre y el archivo de cada tupla
        hoja_graficos.write(fila, columna, nombre_grafico)   #escribe el nombre del grafico
        hoja_graficos.insert_image(fila + 1, 1, archivo_img, {'x_scale': 0.7, 'y_scale': 0.7})  #inserta la imagen en la hoja de excel reduciendo su tamaño en un 70%
        fila += 25  # espacio vertical entre gráficos

numericas = dataframe.select_dtypes(include="number").columns   #crea una lista seleccionando las columnas numericas del dataframe
valores_max = dataframe[numericas].idxmax()  #obtiene el indice del valor maximo de cada columna numerica - devuelve el indice y el valor maximo (serie de pandas) 
valores_min = dataframe[numericas].idxmin()  #obtiene el indice del valor minimo de cada columna numerica - devuelve el indice y el valor minimo (serie de pandas)
#df_max = dataframe.loc[valores_max]  #crea un nuevo dataframe con los valores maximos accediendo al dataframe original por medio de los indices obtenidos
#df_min = dataframe.loc[valores_min]  #crea un nuevo dataframe con los valores minimos accediendo al dataframe original por medio de los indices obtenidos

class PDF(FPDF):       #clase para crear el pdf
    def header(self):      #metodo para crear el encabezado
        self.set_font("Arial", "B", 14)  
        self.set_text_color(0,0,255)  #se establece la fuente a Arial, negrita, tamaño 14
        self.cell(0, 10, "Reporte de Datos y Gráficos", ln=True, align='C')   #añade una celda con el texto Reporte de Datos y Graficos, ln=True para que salte a la siguiente linea, align='C' para centrar el texto
        self.ln(10)  #salta 10 lineas para dejar espacio entre el encabezado y el contenido
    
    def footer(self):    #metodo para crear el pie de pagina
        self.set_y(-17)    #se establece la posicion y= -15 para que quede 15mm arriba del borde inferior
        self.set_font("Arial", "I", 8)  #se establece la fuente a Arial, Italica, tamaño 8
        self.cell(0, 10, f"Página {self.page_no()}", align="C")  #añade una celda con el texto Página y el numero de pagina, alineado al centro - cuando el ancho es 0 ocupa todo el ancho de la pagina disponible
        self.set_y(-13)
        self.cell(0, 10, f"Juan David Lasso & Emmanuel Escobar", align="C")
#estos metos se llaman automaticamente en cada pagina del pdf

pdf = PDF()  #crea un objeto PDF a partir de la clase PDF
pdf.add_page()   #añade una pagina al pdf

# Página con el mapa
pdf.set_font("Arial", "B", 14)
pdf.set_text_color(0,0,255)  #el color se define en RGB (cada componente va de 0 a 255)
pdf.cell(0, 10, "Ubicación", ln=True, align="C") #añade una celda con el texto Ubicación
pdf.ln(10)

epw = pdf.w - 2 * pdf.l_margin    #recomendacion de la ia para que el mapa no quede pegado a los bordes  epw = ancho efectivo de la pagina    
pdf.image(mapa_png, x=pdf.l_margin, w=epw) #añade el mapa a la pagina, x=pdf.l_margin para que quede pegado al margen izquierdo, w=epw para que ocupe todo el ancho utilizable de la pagina
pdf.ln(10)

# Añadir el enlace como texto
#crea un enlace al mapa interactivo con la latitud y longitud especificadas
pdf.set_font("Arial", "U", 12) 
pdf.cell(0, 10, "Ver mapa interactivo", ln=True, link=enlace_mapa) #añade una celda con el texto Ver mapa interactivo y le añade el enlace al texto

pdf.add_page(orientation="L") #añade una nueva pagina al pdf en orientacion horizontal (landscape)
pdf.set_font("Arial", "B", 14) 
pdf.cell(0, 10, "Resumen Estadístico", ln=True, align="C") #añade una celda con el texto Resumen Estadistico
pdf.ln(10)

ancho_columnas = [
    16,  # Estadistica
    10,  # Edad
    33,  # Numero de documento
    43,  # Hora de ingreso
    43,  # Hora de salida
    35,  # Total entradas semana
    36,  # Horas de clase semana
    26,  # Promedio de nota
    35   # Tiempo transcurrido seg
]
altura_fila = 6

analisis_graficos = [
    "Espacio de relleno para evitar errores al agregar la imagen y el texto",
    "Este gráfico muestra la distribución de edades por carrera. Permite identificar si hay carreras con estudiantes significativamente más jóvenes o mayores. Es útil para entender el perfil demográfico por programa académico.",
    "Se analiza la relación entre la edad y el promedio de notas. Puede sugerir si los estudiantes más jóvenes o mayores tienden a obtener mejores calificaciones. La línea de regresión muestra la tendencia general de cómo el promedio de notas varía con la edad de los estudiantes. Si la pendiente es positiva, indica que a mayor edad, los estudiantes tienden a obtener mejores notas; si es negativa, que las notas disminuyen con la edad. Una línea casi horizontal sugiere que no hay una relación lineal clara entre edad y rendimiento académico.",
    "Compara el número de horas de clase semanales con el promedio de notas. Es útil para explorar si una mayor carga académica se relaciona con un mejor o peor desempeño. La línea de regresión refleja cómo el promedio de notas cambia según las horas de clase que asiste un estudiante semanalmente. Una pendiente positiva indica que asistir a más horas de clase se asocia con mejores notas, mientras que una pendiente negativa o cercana a cero señala poca o ninguna relación lineal entre las horas de clase y el rendimiento académico.",
    "Permite observar cómo varía el promedio de notas entre diferentes carreras. Ayuda a detectar si hay programas con un rendimiento académico superior o inferior.",
    "Cuenta cuántos estudiantes hay por carrera. Es clave para ver la distribución de la muestra y posibles sesgos por número de estudiantes. La la curva de densidad de probabilidad representa una estimación suave de la distribución de probabilidad de una variable numérica. A diferencia del histograma (que muestra frecuencias por intervalos), la curva de densidad de probabilidad intenta suavizar la forma general de los datos para mostrar cómo se distribuyen.",
    "Analiza el tiempo de permanencia (en segundos) por carrera. Ayuda a entender si ciertas carreras demandan más tiempo presencial en la universidad.",
    "Relaciona las entradas semanales al campus con las horas de clase. Busca patrones de comportamiento según la carga académica. La línea de regresión muestra la relación entre la cantidad total de entradas semanales (por ejemplo, accesos o asistencias) y las horas de clase que un estudiante toma semanalmente. Si la pendiente es positiva, indica que a mayor número de entradas semanales, generalmente se asocian más horas de clase, sugiriendo un patrón consistente de asistencia y dedicación. Por otro lado, una pendiente negativa o cercana a cero indicaría poca relación entre estos dos factores."
]
#lista de analisis de graficos

# titulos de las columnas
pdf.set_font("Arial", "B", 8)
pdf.set_fill_color(200, 220, 255)   #color de fondo de las celdas
pdf.cell(ancho_columnas[0], altura_fila, "Estadística", border=1, fill=True, align="C")  #toca añadir el nombre de la columna a mano porque no se puede obtener por medio del metodo columns
for i, columna in enumerate(resumen.columns):   #resumen.columns devuelve los nombres de las columnas del dataframe resumen - for i, columna devuelve el indice y columa el nombre de la columna
    pdf.cell(ancho_columnas[i+1], altura_fila, columna, border=1, fill=True, align="C") # añade el nombre de la columna a la celda
pdf.ln(altura_fila) #deja un espacio entre filas (la altura de la fila) 

# filas del resumen estadistico
pdf.set_font("Arial", size=8)  
pdf.set_fill_color(245, 245, 245)
fill = False
for indice, fila in resumen.iterrows():  #iterrows devuelve el indice (el nombre de la fila) y la fila del dataframe resumen (los valores de la fila) (serie de pandas)
    pdf.cell(ancho_columnas[0], altura_fila, str(indice), border=1, fill=fill)
    for i, valor in enumerate(fila): #recorre la fila y devuelve el indice y el valor de cada celda
        pdf.cell(ancho_columnas[i+1], altura_fila, str(valor), border=1, fill=fill)  #convierte el valor a string y lo añade a la celda
    pdf.ln(altura_fila) 
    fill = not fill  #toque decorativo para que las filas alternen de color 

pdf.ln(20)
pdf.set_font("Arial", "B", 14)  #cambia la fuente a itálica
texto_est = "La tabla muestra estadísticas descriptivas de una muestra de 150 personas, incluyendo edad, número de documento, horarios de ingreso y salida," \
    "entradas semanales, horas de clase, promedio de notas y tiempo total invertido. Se presentan medidas como promedio, mínimos, máximos, percentiles y desviación estándar," \
        "lo que permite analizar la distribución, participación y desempeño de los individuos. Esta información es útil para evaluar el comportamiento general, la asistencia y el rendimiento académico del grupo."
pdf.multi_cell(0, 6, texto_est) 
      
#añadir valores maximos y minimos
pdf.add_page()    #crea una nueva pagina
pdf.set_font('Arial', 'B', 14)   
pdf.cell(0, 10, "Estudiantes con valores máximos:", ln=True)    #añade una celda con el texto Estudiantes con valores maximos:
pdf.set_font("Arial", "", 10)  
for columna in numericas:
    indice = valores_max[columna]   #obtiene el indice del valor maximo de la columna  - lo saca de la serie de pandas (es la etiqueta (indice) la columna y la fila es el indice del valor maximo) (2xn)
    estudiante = dataframe.loc[indice]  #obtiene el estudiante con el indice del valor maximo  
    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 8, f"{columna} - Máximo: {estudiante[columna]}", ln=True)  #añade una celda con la columna y el valor maximo
    pdf.set_font("Arial", "", 9)
    pdf.multi_cell(0, 5, f'Nombre: {estudiante["Nombre"]}\nEdad: {estudiante["Edad"]}\nCarrera: {estudiante["Carrera"]}\nCiudad: {estudiante["Ciudad"]}\n')
    #añade una celda con el nombre, edad, carrera y ciudad del estudiante con un salto de linea entre cada dato
    pdf.ln(1)    

pdf.add_page()   
pdf.set_font("Arial", "B", 14)
pdf.cell(0, 10, "Estudiantes con valores mínimos:", ln=True)
pdf.set_font("Arial", "", 10)
                          
for columna in numericas:
    indice = valores_min[columna]
    estudiante = dataframe.loc[indice]         #hace lo mismo de arriba pero con los valores minimos
    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 8, f"{columna} - Mínimo: {estudiante[columna]}", ln=True)
    pdf.set_font("Arial", "", 9)
    pdf.multi_cell(0, 5, f'Nombre: {estudiante["Nombre"]}\nEdad: {estudiante["Edad"]}\nCarrera: {estudiante["Carrera"]}\nCiudad: {estudiante["Ciudad"]}\n')
    pdf.ln(1)

#añadir gráficos
for i in range(1, 8):  #de 1 a 8 (7) porque asi se enumeran los graficos
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, f"Gráfico {i}", ln=True, align="C")  #agrega el numero - nombre del grafico
    pdf.ln(10)
    ruta_img = f"grafico_{i}.png" #ruta de la imagen
    try:
        pdf.image(ruta_img, x=pdf.l_margin, w=epw) #intenta agregar la imagen al pdf - epw es el ancho efectivo de la pagina esta definido arriba
    except FileNotFoundError:
        pdf.cell(0, 10, f"[X] No se encontró la imagen {ruta_img}.", ln=True)  #si no se encuentra la imagen, agrega un texto indicando que no se encontro la imagen
    pdf.ln(17) #deja un espacio entre la imagen y el texto
    if i < len(analisis_graficos): #si el indice es menor al tamaño de la lista de analisis de graficos (tamaño 8)
        pdf.multi_cell(0, 10, analisis_graficos[i])  #agrega el analisis del grafico
    else:   #si no
        pdf.multi_cell(0, 10, "Análisis no disponible para este gráfico.")    #agrega un texto indicando que no hay analisis disponible

pdf.output(os.path.join(ruta_carpeta, "reporte.pdf")) #ruta donde se guardara el pdf - se guarda el pdf
print("[😎] PDF generado con éxito.") 


archivos_a_borrar = [archivo_img for _, archivo_img in imagenes] + [mapa_png] #lista de archivos a borrar - solo toma las rutas de los archivos y las concatena con la ruta del mapa (sale 1 sola lista)
os.makedirs("carp_temporal", exist_ok=True)  #crea una carpeta temporal para mover los archivos a borrar

for archivo in archivos_a_borrar:  #recorre la lista de archivos a borrar
    try:
        if os.path.exists(archivo):    #verifica si el archivo existe
            nombre_archivo = os.path.basename(archivo)    #obtiene el nombre del archivo sin la ruta
            destino = os.path.join("carp_temporal", nombre_archivo)  #crea la ruta de destino donde se movera el archivo
            shutil.move(archivo, destino)  #mueve el archivo a la carpeta temporal
            print(f"Se movio {archivo} a {destino} para su posterior eliminación.")    #imprime un mensaje indicando que se movio el archivo
        else:
            print(f"Archivo {archivo} no existe, no se puede mover.")
    except Exception as e:  #si ocurre un error al mover el archivo
        print(f"[🥵] Error al mover el archivo {archivo}: {str(e)}")  #imprime un mensaje de error si no se pudo mover el archivo

# Luego, elimina toda la carpeta 
try: 
    if os.path.exists("carp_temporal") and os.path.isdir("carp_temporal"):  #verifica si la carpeta temporal existe y es un directorio
        shutil.rmtree("carp_temporal")  #elimina la carpeta temporal y todo su contenido
        print("Carpeta temporal eliminada con éxito junto con todos los archivos temporales.")
    else:
        print(f"No se encontró la carpeta temporal para eliminar.")
except Exception as e:  #si ocurre un error al eliminar la carpeta
    print(f"[🥵] Error al eliminar la carpeta temporal: {str(e)}")  #imprime un mensaje de error si no se pudo eliminar la carpeta

#print(valores_max)
#print(df_max)
class EmailSender:
    def __init__(self, sender_email, sender_password, receiver_emails, subject, body, attachment):
        """Inicializa la clase con los datos del correo electrónico."""
        self.sender_email = sender_email  # Correo del remitente
        self.sender_password = sender_password  # Contraseña del remitente (contraseña de aplicación)
        self.receiver_emails = receiver_emails  # Correo del destinatario
        self.subject = subject  # Asunto del correo
        self.body = body  # Contenido del mensaje
        self.attachment = attachment  # Archivo adjunto

    def send_email(self):
        """Envía un correo con el archivo adjunto."""
        msg = MIMEMultipart()  # Crea la estructura del mensaje
        msg["From"] = self.sender_email  # Define el remitente
        msg["To"] = ", ".join(self.receiver_emails)  # Define el destinatario
        msg["Subject"] = self.subject  # Establece el asunto del mensaje
        msg.attach(MIMEText(self.body, "plain"))  # Agrega el cuerpo del mensaje en texto plano

        # Adjuntar el archivo PDF al correo
        with open(self.attachment, "rb") as file:  # Abre el archivo en modo binario
            part = MIMEBase("application", "octet-stream")  # Define el tipo de archivo adjunto
            part.set_payload(file.read())  # Carga el archivo en el correo
            encoders.encode_base64(part)  # Codifica el archivo para envío seguro
            part.add_header("Content-Disposition", f"attachment; filename={os.path.basename(self.attachment)}")  # Define el nombre del archivo
            msg.attach(part)  # Adjunta el archivo al email

        # Configurar el servidor SMTP de Gmail
        server = smtplib.SMTP("smtp.gmail.com", 587)  # Configura el servidor SMTP con el puerto adecuado
        server.starttls()  # Activa el modo seguro (TLS) para el envío del correo
        server.login(self.sender_email, self.sender_password)  # Inicia sesión con las credenciales del remitente
        server.sendmail(self.sender_email, self.receiver_emails, msg.as_string())  # Envía el correo con el adjunto
        server.quit()  # Cierra la conexión con el servidor SMTP

        print(f"\nEmail enviado a {', '.join(self.receiver_emails)} con el análisis adjunto.")  # Mensaje de confirmación
        messagebox.showinfo("Correo enviado exitosamente!!!","Email enviado correctamente a los destinatarios con el análisis adjunto")
pdf_filename = os.path.join(ruta_carpeta, "reporte.pdf")  # Ruta del archivo PDF generado

# Configurar y enviar el email desde Colab
email_token = os.getenv("EMAIL_TOKEN")  #obtiene el token de la variable de entorno EMAIL_TOKEN
sender_email = "emmanuel.escobar@uao.edu.co"  # Reemplazar con el correo remitente
sender_password = email_token  # Usar la contraseña de aplicación de Gmail
receiver_emails = [""] # Lista de correos destinatarios

email_sender = EmailSender(sender_email, sender_password, receiver_emails,
                           "Informe de análisis de datos",
                           "Adjunto el reporte generado en PDF.",
                           pdf_filename)
try:
    email_sender.send_email()  # Envía el correo con el archivo adjunto
except Exception as e:
    print(f"[😥] Error al enviar el correo: {str(e)}")
    messagebox.showerror(f"Error al enviar el correo", f"Hubo un problema al enviar el correo: {str(e)}")  #muestra un mensaje de error si falla el envío