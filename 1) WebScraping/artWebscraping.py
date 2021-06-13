# By Cristian Beltran , Maria Paula Peña y Alejandro Aponte
from selenium import webdriver
from selenium.webdriver.common import service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
import time
import pandas as pd
import requests

#Function to remove 'url:(..)' from links
def cleanUrl(urllink):
    return urllink[5:-2] 

#Descargar imagen a traves de link, dando el nombre como segundo parametro   
def downloadImageFromLink(urllink,filename):
    if len(urllink)!=0:
        img_data = requests.get(urllink).content
        with open(filename, 'wb') as handler:
            handler.write(img_data)
        return True
    else:
        return False


#Ruta para el controlador de chrome 
path = r'D:\Descargas\chromedriver_win32\chromedriver.exe'
#Cargar el controlador en python
driver = webdriver.Chrome(executable_path = path)

#Paginas target para webscraping
baseColorsUrl = ["WHITE","PINK","YELLOW","PURPLE","BLUE","TEAL","GREEN","ORANGE","RED","BROWN","BLACK"]
#Preparar diccionario de los datos recolectados
data = {"filename":[],"title":[],"autor":[],"date":[],"place":[],"category":[]}

#Webscraping para todas las paginas 
for basecolor in baseColorsUrl:
    driver.get("https://artsandculture.google.com/color?col="+basecolor)
    time.sleep(5)
    #Moverse hacia abajo de la pagina para cargar mas resultados y repetir el proceso n_scroll veces
    n_scrolls = 20
    for j in range(0, n_scrolls):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(4)


    
    js1 ="var containers = [...document.querySelectorAll('.DuHQbc')];"
    js2 ="var as = containers.map(contain => contain.firstElementChild);"
    js3 ="return as.map(a => a.href)" #To get image pages
    js4 = "return as.map(a =>window.getComputedStyle(a, false).backgroundImage);" #To get image files
    
    jsimagePages = js1+js2+js3# js que me extrae todos los links de las paginas de cada obra
    jsimagefile= js1+js2+js4 # js que retorna la ubicacion de las imagenes

    imagePages = driver.execute_script(jsimagePages) # Guardar paginas de las images en lista
    imagefiles = driver.execute_script(jsimagefile) # Guardar links crudos de la ubicacion de las imagenes

    #Inspeccionar los datos
    print("longitud: ",len(imagePages),len(imagefiles))
    print("Vacios ",imagePages.count("none"),imagefiles.count("none"))
    
    #Limpiar los datos crudos de la ubicacion de las imagenes
    imagefiles = list(map(cleanUrl, imagefiles))
    indexImageFiles = 0
    #WebScraping para la imagen para la seccion de color actual
    for page in imagePages:
        #Cargar pagina
        driver.get(page)
        time.sleep(0.3)

        #Retornar si la pagina no tiene mas archivos encontrados 
        if len(imagefiles[indexImageFiles])==0:
            break
        #Js para capturar los contenedores donde esta la informacion de la obra
        jsdetailsContainer = 'var detailsContainer = document.querySelector(".ve9nKb");'
        jsSubtitlesLi = 'var SubtitlesLi = [...detailsContainer.firstElementChild.querySelectorAll("li")];'

        #Js para obtener el titulo, devuelve null sino existe
        jsTitle = 'var title = SubtitlesLi.filter(subtitle => subtitle.textContent.startsWith("Título")|| subtitle.textContent.startsWith("Title"));'
        jsTitle = jsTitle + "title =(title.length==0)?'null':title[0].textContent;"
        
        #Js para obtener el artista, devuelve null sino existe
        jsArtist = 'var artist = SubtitlesLi.filter(subtitle => subtitle.textContent.startsWith("Creador")||subtitle.textContent.startsWith("Painter")||subtitle.textContent.startsWith("Illustrator"));'
        jsArtist = jsArtist + "artist= (artist.length==0)?'null':artist[0].textContent;"
        
        #Js para obtener la fecha, devuelve null sino existe
        jsDate = 'var date = SubtitlesLi.filter(subtitle => subtitle.textContent.startsWith("Fecha"));'
        jsDate = jsDate + "date=(date.length==0)?'null':date[0].textContent;"
        
        #Js para obtener el lugar, devuelve null sino existe
        jsPlace= 'var place = document.querySelector(".WrfKPd");'
        jsPlace = jsPlace +"place = (place==undefined)?'null': place.innerText;  "

        #Concatenar diferentes js para un script completo
        jsinfo = jsdetailsContainer+jsSubtitlesLi
        jsGetTitle = jsinfo+jsTitle+"return title"
        jsGetArtist = jsinfo+jsArtist+"return artist"
        jsGetDate = jsinfo+jsDate+"return date"
        #jsGetType = jsinfo+jsType+"return type"
        jsGetPlace = jsPlace+"return place"

        #Obtener datos crudos de la ejecucion del script
        RawTitle = driver.execute_script(jsGetTitle)
        RawArtist = driver.execute_script(jsGetArtist)
        RawDate = driver.execute_script(jsGetDate)
        RawPlace = driver.execute_script(jsGetPlace)

        #Adicionar datos a diccionario
        data["title"].append(RawTitle)
        data["autor"].append(RawArtist)
        data["date"].append(RawDate)
        data["place"].append(RawPlace)

        data["filename"].append(imagefiles[indexImageFiles])
        data["category"].append(basecolor)
        
        indexImageFiles=indexImageFiles+1

#Convertir datos en dataframe y exportarlo
df= pd.DataFrame.from_dict(data)
df.to_csv(r'googleartWebScraping.csv', index = False)
