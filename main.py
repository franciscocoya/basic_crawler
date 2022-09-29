"""
author: Francisco Coya Abajo
description: Práctica 2 SIW: Crawler básico.
version: v1.0.1
"""
from datetime import datetime
import logging
import sys
import requests
import time
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import re
import os

# import urllib.robotparser

max_downloads = 5  # Número máximo de archivos a descargar
DEFAULT_SECONDS = 5;
target_type = 'text/html'  # Solo va a buscar páginas HTML
visited_urls = []  # Lista de URLs visitadas
not_visited_urls = []  # Lista de URLs por visitar
url_seed = []  # Lista de semillas de URL para realizar la búsqueda
seed_index = 1  # Indice para distinguir entre los ficheros semilla generados
last_visited_seed = 0;  # Posición de la última URL de la lista visitada

"""
Función principal del programa.
A partir de una URL dada el tiempo de espera entre petición, realiza un escaneo y descarga de tantos archivos
como especifique max_downloads
"""


def crawl(url, seconds):
    global max_downloads
    global last_visited_seed
    global not_visited_urls

    # Si se ha utilizado la última URL de las semillas, inicializar en la primera
    if last_visited_seed == len(url_seed):
        last_visited_seed = 0

    if max_downloads == 0:
        sys.exit()
        return

    else:
        processUrl(url, seconds)


"""
Para una URL determinada, descarga el contenido HTML y explora todos los enlaces que contiene.
Los enlaces extraidos los añade a la lista de URLs visitadas.
"""


def processUrl(url, seconds):
    global max_downloads
    global visited_urls

    addLinkToExisingList(url, visited_urls)
    not_visited_urls.pop(0)

    # visited_urls.append(url)
    print(str(max_downloads) + " :::: " + str(datetime.now().strftime("%H:%M:%S")) + " :::: Explorando " + str(
        url) + "\n");
    # print("\nDescargas: " + str(max_downloads))
    try:
        r = requests.get(url, headers={"Content-Type": "html"}, timeout=seconds)

        if (r.status_code != 200):
            return

        # Contenido de la pagina
        html_content = r.content
        soup = BeautifulSoup(html_content, 'html.parser')

        # Obtener todos los enlaces que contiene la página
        links = soup.find_all('a')

        # Añadir los nuevos enlaces a los enlaces no visitados
        for link in links:
            normalized_link = normalize_link(url, link)
            addLinkToExisingList(normalized_link, not_visited_urls)

            #TODO: Explorar el link si no ha sido explorado aun
            if normalized_link and len(normalized_link) > 0 \
                    and not normalized_link in visited_urls:
                crawl(normalized_link, seconds)

    except requests.exceptions.Timeout:
        logging.error("La URL no puede ser explorada");


"""
Elimina las slashes de una cadena dada.
"""


def replaceBackSlashesFromWord(word):
    return str(word).replace("/", "")


"""
Comprueba que la URL pasada como parametro es válida
"""


def isURLWellFormed(urlToCheck):
    return len(urlToCheck.path) > 0 and len(urlToCheck.netloc) > 0


"""
Normaliza un link pasado como parámetro. Para ello, diferencia los links relativos de los absolutos
"""


def normalize_link(url, linkToNormalize):
    link_href = str(linkToNormalize.get('href'))

    if len(link_href) < 2 or link_href == "" or len(urlparse(url).scheme) == 0:
        return

    elif link_href.startswith('/'):
        # Si el link es relativo, se une con la url
        parsedUrl = urlparse(link_href)
        originalUrlScheme = urlparse(url).scheme;

        if isURLWellFormed(parsedUrl):
            # Construcción de la url a partir del path relativo y la url original
            return replaceBackSlashesFromWord(originalUrlScheme) + "://" \
                   + replaceBackSlashesFromWord(parsedUrl.netloc)

    else:
        parsedCorrectUrl = urlparse(link_href)
        if len(parsedCorrectUrl.scheme) > 0 and parsedCorrectUrl.scheme == "http" \
                or parsedCorrectUrl.scheme == "https":
            return replaceBackSlashesFromWord(parsedCorrectUrl.scheme) + "://" \
                   + replaceBackSlashesFromWord(parsedCorrectUrl.netloc) + "/"


"""
Añade una URL pasada como parámetro a la lista indicada.
"""


def addLinkToExisingList(urlToAdd, list):
    if urlToAdd and not urlToAdd in list:
        list.append(urlToAdd)


"""
Lee un fichero de texto con el nombre especificado como parámetro y carga en una 
lista las URL semilla leídas.
"""


def readTextFile(filename):
    # if not isValidFilename(filename):
    #   return
    global not_visited_urls

    file_abs_path = os.path.abspath(filename)
    with open(file_abs_path) as f:
        not_visited_urls = f.read().splitlines()
        f.close()


"""
Comprueba que un nombre de fichero pasado como parámetro es válido.
"""


def isValidFilename(filenameToCheck):
    return len(str(filenameToCheck)) > 0 and re.search(".txt$", filenameToCheck)


"""
Crea un fichero de URLs semilla con los elementos de la lista de URL.
"""


def generateSeedFile():
    global seed_index

    with open(os.path.abspath(generateFilename()), 'w') as f:
        for url in url_seed:
            f.write(url + "\n")
        f.close()

    seed_index = seed_index + 1


"""
Función auxiliar a @generateSeedFile que genera un nuevo nombre para el fichero de semillas a generar.
"""


def generateFilename():
    return "seed".join(str(seed_index)).join(".txt")


def main():
    global not_visited_urls
    global visited_urls

    # url_seed = [] # Para iteración, la lista ha de inicializarse
    readTextFile(os.path.abspath("seed.txt"))
    if len(not_visited_urls) == 0:
        print("No se puede realizar la búsqueda")
    else:
        crawl(not_visited_urls[0], DEFAULT_SECONDS)
    # generateSeedFile()

    print("URLS NO VISITADAS: " + str(len(not_visited_urls)))
    print(not_visited_urls)

    print("\n\nURLS VISITADAS")
    print(visited_urls)


# crawl("http://www.ingenieriainformatica.uniovi.es", 5)
# print("URLS: \n")
# print(visited_urls)

main()
