from flask import Flask, render_template, request
from collections import deque, defaultdict
import csv
import requests

app = Flask(__name__)

# ---- Configs y constantes ----
DEFAULT_IMAGE_URL = "https://thypix.com/wp-content/uploads/sad-cat-41.jpg"
USER_AGENT = "MiAppDeActores/1.0 (https://tu-proyecto-ejemplo.com)"

# ---- Cargar datos UNA VEZ al inicio ----
entradas = {}
with open("static/imdb_movies.csv", newline='', encoding="utf8") as csvfile:
    reader = csv.reader(csvfile)
    next(reader, None)
    for i in reader:
        title = i[0]
        actores_field = i[5] if len(i) > 5 else ""
        descripcion = i[4] if len(i) > 4 else ""
        entradas[title] = [[n for n in actores_field.split(",")], descripcion]

grafo = defaultdict(set)
descripcion_peliculas = {}
def norm(s): return s.lower().strip()

for pelicula, personas in entradas.items():
    reparto = [p.lower().strip() for p in personas[0] if p.strip() != pelicula]
    reparto = reparto[::2]  # mantenemos tu lógica original
    pelicula_norm = norm(pelicula)
    descripcion_peliculas[pelicula_norm] = personas[1]
    for actor in reparto:
        actor_norm = norm(actor)
        grafo[pelicula_norm].add(actor_norm)
        grafo[actor_norm].add(pelicula_norm)

grafo = dict(grafo)

# Generamos lista de actores para autocompletar (solo nodos que no son películas)
actores_list = sorted([nodo for nodo in grafo.keys() if nodo not in descripcion_peliculas])

def encontrar_camino_corto(grafo, inicio, fin):
    inicio = inicio.lower().strip()
    fin = fin.lower().strip()
    visitados = set()
    cola = deque([(inicio, [inicio])])
    visitados.add(inicio)
    while cola:
        nodo, camino = cola.popleft()
        if nodo == fin:
            return camino
        for vecino in grafo.get(nodo, []):
            if vecino not in visitados:
                visitados.add(vecino)
                cola.append((vecino, camino + [vecino]))
    return None

# ---- Búsqueda de imágenes con cache ----
cache_fotos = {}
session = requests.Session()
session.headers.update({"User-Agent": USER_AGENT})

from urllib.parse import urlparse
import os

# ---- filtros ----
BAD_KEYWORDS = ("commons-logo", "logo", "wikimedia", "badge", "icon", "placeholder", "no_image", "default", "sprite")
PREFERRED_MIMES = ("image/jpeg", "image/jpg", "image/png", "image/webp")

def _is_bad_filename(url):
    """Rechaza URLs cuyos nombres contengan palabras indicadoras de logo/placeholder."""
    try:
        path = urlparse(url).path.lower()
        fname = os.path.basename(path)
        if not fname:
            return True
        for bad in BAD_KEYWORDS:
            if bad in fname:
                return True
        # evita svg (suelen logos, vectores, íconos)
        if fname.endswith(".svg"):
            return True
        return False
    except Exception:
        return True

def _is_acceptable_image(info_url=None, mime=None, width=None, height=None):
    """
    Decide si una imagen es aceptable:
    - mime debe estar en PREFERRED_MIMES (si está disponible)
    - no aceptar SVGs ni nombres con BAD_KEYWORDS
    - si width/height están disponibles, evitar imágenes extremadamente pequeñas
    """
    if not info_url:
        return False
    if _is_bad_filename(info_url):
        return False
    if mime:
        mime = mime.lower()
        if mime not in PREFERRED_MIMES:
            return False
    # si hay dimensiones, exigir al menos 60px en ancho o alto
    try:
        if width is not None and height is not None:
            if int(width) < 60 or int(height) < 60:
                return False
    except Exception:
        pass
    return True


def buscar_imagen_nodo(nodo_name, idioma='es'):
    """
    Busca la imagen principal de la página de Wikipedia del nodo (actor o película).
    Retorna (url, None) si se encontró una imagen aceptable, o (DEFAULT_IMAGE_URL, mensaje).
    Rechaza logos/placeholder y SVGs; prioriza original/thumbnail en formatos jpg/png/webp.
    """
    try:
        url_search = f"https://{idioma}.wikipedia.org/w/api.php"

        pruebas = [nodo_name, nodo_name.title()]

        for q in pruebas:
            params_search = {
                "action": "query",
                "list": "search",
                "srsearch": q,
                "format": "json",
                "srlimit": 1,
            }
            r = session.get(url_search, params=params_search, timeout=10)
            r.raise_for_status()
            data = r.json()
            if not data.get("query", {}).get("search"):
                continue

            page = data["query"]["search"][0]
            pageid = page["pageid"]

            # 1) intentar pageimages -> original / thumbnail (mejor camino)
            params_image = {
                "action": "query",
                "pageids": pageid,
                "prop": "pageimages",
                "piprop": "original|thumbnail",
                "pithumbsize": 600,
                "format": "json",
            }
            r2 = session.get(url_search, params=params_image, timeout=10)
            r2.raise_for_status()
            data2 = r2.json()
            pageinfo = data2.get("query", {}).get("pages", {}).get(str(pageid), {})

            # original (si existe) — validamos nombre/mime/dimensiones si es posible
            original = pageinfo.get("original")
            if original and original.get("source"):
                orig_url = original.get("source")
                mime = original.get("mime") if isinstance(original, dict) else None
                # pageimages original a veces no trae mime/dims; validamos por filename y evitar SVGs/logos
                if _is_acceptable_image(orig_url, mime=mime,
                                        width=original.get("width") if isinstance(original, dict) else None,
                                        height=original.get("height") if isinstance(original, dict) else None):
                    return orig_url, None

            # thumbnail (más seguro para navegadores)
            thumb = pageinfo.get("thumbnail")
            if thumb and thumb.get("source"):
                thumb_url = thumb.get("source")
                # thumbnail normalmente es jpg/png, validamos filename
                if _is_acceptable_image(thumb_url,
                                       mime=thumb.get("mime") if isinstance(thumb, dict) else None,
                                       width=thumb.get("width") if isinstance(thumb, dict) else None,
                                       height=thumb.get("height") if isinstance(thumb, dict) else None):
                    return thumb_url, None

            # 2) fallback: listar imágenes de la página y pedir imageinfo
            params_images_list = {
                "action": "query",
                "pageids": pageid,
                "prop": "images",
                "format": "json",
            }
            r3 = session.get(url_search, params=params_images_list, timeout=10)
            r3.raise_for_status()
            data3 = r3.json()
            imgs = data3.get("query", {}).get("pages", {}).get(str(pageid), {}).get("images", []) or []

            # recorrer imágenes en orden; pedir imageinfo y validar mime/size/filename
            for img in imgs:
                title = img.get("title", "")
                # pedimos imageinfo (url, mime, size, width/height si está)
                params_file = {
                    "action": "query",
                    "titles": title,
                    "prop": "imageinfo",
                    "iiprop": "url|mime|size|metadata",
                    "format": "json",
                }
                try:
                    r4 = session.get(url_search, params=params_file, timeout=10)
                    r4.raise_for_status()
                    data4 = r4.json()
                except requests.RequestException:
                    continue

                pages = data4.get("query", {}).get("pages", {}).values()
                for p in pages:
                    info = p.get("imageinfo")
                    if not info:
                        continue
                    info0 = info[0]
                    img_url = info0.get("url")
                    mime = info0.get("mime")
                    # algunos imageinfo contienen 'width'/'height' en metadata; a veces 'size' solo indica bytes.
                    width = info0.get("width")
                    height = info0.get("height")
                    # si width/height no están, verificar en metadata (p.ej. metadata puede contener "Width" "Height")
                    if not width or not height:
                        meta = info0.get("metadata", [])
                        for m in meta:
                            k = m.get("name", "").lower()
                            if k in ("width", "image width"):
                                try:
                                    width = int(m.get("value"))
                                except Exception:
                                    pass
                            if k in ("height", "image height"):
                                try:
                                    height = int(m.get("value"))
                                except Exception:
                                    pass

                    if _is_acceptable_image(img_url, mime=mime, width=width, height=height):
                        return img_url, None

        # si nada válido fue encontrado -> fallback al DEFAULT_IMAGE_URL
        return DEFAULT_IMAGE_URL, f"No se encontró imagen aceptable en Wikipedia para '{nodo_name}'."

    except requests.RequestException as e:
        return DEFAULT_IMAGE_URL, f"Error de conexión: {e}"
    except Exception as e:
        return DEFAULT_IMAGE_URL, f"Error inesperado: {e}"


def obtener_foto_con_cache(nodo, idioma='es'):
    """
    Retorna la URL de la foto usando cache. `nodo` debe ser la cadena normalizada (lower).
    Si no hay imagen o hay error, devuelve DEFAULT_IMAGE_URL.
    """
    nodo_key = nodo.lower().strip()
    if nodo_key in cache_fotos:
        return cache_fotos[nodo_key]

    # probamos con el nodo tal como está y con versión title() dentro de la función buscar_imagen_nodo
    url, err = buscar_imagen_nodo(nodo_key, idioma=idioma)
    cache_fotos[nodo_key] = url or DEFAULT_IMAGE_URL
    return cache_fotos[nodo_key]

# ---- Rutas ----
@app.route("/", methods=["GET", "POST"])
def index():
    camino = []
    fotos = []
    if request.method == "POST":
        actor1 = request.form.get("actor1")
        actor2 = request.form.get("actor2")
        if actor1 and actor2:
            camino = encontrar_camino_corto(grafo, actor1, actor2)
            if camino:
                # Para cada nodo del camino: pedimos foto (actor o película)
                for nodo in camino:
                    fotos.append(obtener_foto_con_cache(nodo))
            else:
                camino = []
                fotos = []

    return render_template(
        "grafo.html",
        camino=camino,
        descripcion_peliculas=descripcion_peliculas,
        actores_list=actores_list,
        fotos=fotos
    )

if __name__ == "__main__":
    app.run(debug=True)


