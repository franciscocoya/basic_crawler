# author: Francisco Coya Abajo
# description: Práctica 2 SIW: Crawler básico.
# version: v1.0.3

from datetime import datetime
import logging
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import re
import os

# import urllib.robotparser


max_downloads = 5  # Número máximo de archivos a descargar
DEFAULT_SECONDS = 5
target_type = 'text/html'  # Solo va a buscar páginas HTML
visited_urls = []  # Lista de URLs visitadas
not_visited_urls = []  # Lista de URLs por visitar


def crawl(url, seconds):
    """
    Crawl de una URL.

    Invoca a #processUrl(). Si el número de descargas llega a su límite, se finaliza la búsqueda.

    :param url: URL a explorar.
    :param seconds: Tiempo en segundos a esperar.
    :return: void
    """
    global max_downloads
    global not_visited_urls

    # Condicion de parada: Límite de descargas establecido
    if max_downloads == 0:
        return

    else:
        processUrl(url, seconds)


def processUrl(url, seconds):
    """
    Procesamiento de una URL.

    Para realizar el procesamiento de la url :url se realiza:

        1. Decremento del número de decargas realizadas.
        2. Inserción de :url dentro de la lista :visited_urls de URLs visitadas.
        3. Descarga del contenido HTML de la página con URL :url.
        4. Obtención de todos los enlaces(Absolutos y relativos) de dicha URL. Utilización de la libraría BeautifulSoap.
        5. Para cada enlace obtenido:
            5.1. Normalización del enlace normalize_link()
            5.2. Añadirlo a la lista :not_visited_urls , de enlaces no visitados aún.

    :param url: URL a procesar.
    :param seconds: Tiempo de espera entre descargas, expresado en segundos.

    :return: void
    """
    global max_downloads
    global visited_urls

    max_downloads -= 1
    addLinkToExisingList(url, visited_urls)

    print(str(max_downloads + 1) + " :::: " + str(datetime.now().strftime("%H:%M:%S")) + " :::: Explorando " + str(
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

    except requests.exceptions.Timeout:
        logging.error("La URL no puede ser explorada")
        return


def replace_slash_from_word(word):
    """
    Elimina los slashes("/")

    :param word: Palabra a formatear.
    :return: Nueva palabra sin slashes ("/")
    """
    return str(word).replace("/", "")


def isURLWellFormed(urlToCheck):
    """
    Validación de una URL.

    :param urlToCheck: URL a comprobar.
    :return: True si está bien formada y False en caso contrario.
    """
    return len(urlToCheck.path) > 0 and len(urlToCheck.netloc) > 0


def normalize_link(url, url_to_normalize):
    """
    Normalización de una URL.

    Se distinguen dos escenaarios:
        - URL absoluta: Se devuelve igual a como se pasa por parámetro.
        -  URL relativa: Se realiza un procesamiento previo:
            1. Validación de la URL.
            2. Reemplazo de las slashes.
            3. Concatenacion de la :url con la url relativa.

    :param url: URL semilla.
    :param url_to_normalize: URL a normalizar.
    :return: void
    """
    link_href = str(url_to_normalize.get('href'))

    if len(link_href) < 2 or link_href == "" or len(urlparse(url).scheme) == 0:
        return

    elif link_href.startswith('/'):
        # Si el link es relativo, se une con la url
        parsedUrl = urlparse(link_href)
        originalUrlScheme = urlparse(url).scheme;

        if isURLWellFormed(parsedUrl):
            # Construcción de la url a partir del path relativo y la url original
            return replace_slash_from_word(originalUrlScheme) + "://" \
                   + replace_slash_from_word(parsedUrl.netloc)

    else:
        parsedCorrectUrl = urlparse(link_href)
        if len(parsedCorrectUrl.scheme) > 0 and parsedCorrectUrl.scheme == "http" \
                or parsedCorrectUrl.scheme == "https":
            return replace_slash_from_word(parsedCorrectUrl.scheme) + "://" \
                   + replace_slash_from_word(parsedCorrectUrl.netloc) + "/"


def addLinkToExisingList(urlToAdd, list):
    """
    Añadir una URL a una lista.

    :param urlToAdd: URL a añadir a la lista :list
    :param list: Lista de elementos donde se añadirá :urlToAdd

    :return: void
    """
    if urlToAdd and not urlToAdd in list:
        list.append(urlToAdd)


def readTextFile(filename):
    """
    Lectura de fichero.

    Lee el fichero con el nombre pasado como parámetro y vuelca las URLs semilla a
    la lista.

    :param filename: Nombre del fichero a leer.
    """
    global not_visited_urls

    file_abs_path = os.path.abspath(filename)
    with open(file_abs_path) as f:
        not_visited_urls = f.read().splitlines()
        f.close()


def isValidFilename(filenameToCheck):
    """
    Comprueba que un nombre de fichero pasado como parámetro es válido.

    :param filenameToCheck:
    """
    return len(str(filenameToCheck)) > 0 and re.search(".txt$", filenameToCheck)


def main(seed_filename="seed.txt", max_downloads_limit=10, seconds=5):
    """
    Programa que ejecuta el Crawler.

    :param seed_filename: Nombre del fichero de semillas.
    :param max_downloads_limit: Número máximo de archivos a descargar.
    :param seconds: Tiempo de espera entre descargas (En segundos).
    """
    global not_visited_urls
    global visited_urls
    global max_downloads

    max_downloads = max_downloads_limit

    readTextFile(os.path.abspath(seed_filename))
    if len(not_visited_urls) == 0:
        print("No se puede realizar la búsqueda")
    else:
        for seed_url in not_visited_urls:
            crawl(seed_url, seconds)

    print("URLS NO VISITADAS: " + str(len(not_visited_urls)))
    print(not_visited_urls)

    print("\n\nURLS VISITADAS: " + str(len(visited_urls)))
    print(visited_urls)


# TODO: Prueba de ejecución. BORRAR
main("seed.txt", 10, DEFAULT_SECONDS)
