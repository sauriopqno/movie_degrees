# 🎬 Movie Degrees — Conecta Actores a Través de Películas
<p align="center">
  <a href="https://movie-degrees-2.onrender.com/" target="_blank">
    <img src="https://img.shields.io/badge🎬/%20Probar%20la%20App%20en%20Render-blue?style=for-the-badge" alt="Probar en Render">
  </a>
</p>

**Movie Degrees** es una aplicación web desarrollada con **Flask** que encuentra la conexión más corta entre dos actores a través de las películas en las que han participado juntos.  
Además, muestra imágenes reales (obtenidas desde Wikipedia) y descripciones de las películas, todo con una interfaz visual moderna y responsive.

---

## 🌟 Vista previa
<img width="1900" height="898" alt="image" src="https://github.com/user-attachments/assets/397989cb-1318-407b-be86-ca7402c32316" />


---

## 🧠 ¿Cómo funciona?

1. Carga un archivo CSV (`imdb_movies.csv`) con películas y su reparto.  
2. Construye un **grafo** donde los nodos son actores y películas.  
   - Los actores se conectan con las películas en las que participaron.  
3. Cuando el usuario busca dos actores, la app usa **BFS (Breadth-First Search)** para encontrar el camino más corto que los une.  
4. Por cada nodo (actor o película) del camino, la app obtiene:
   - 📸 Imagen desde **Wikipedia API**
   - 📝 Descripción (para las películas)
5. Finalmente, renderiza el resultado en una línea temporal visual que alterna entre actores 🎭 y películas 🎥.

---

## 🚀 Características principales

✅ Encuentra la conexión más corta entre dos actores.  
✅ Muestra imágenes y descripciones reales desde Wikipedia.  
✅ Interfaz elegante, moderna y responsive (HTML + CSS puros).  
✅ Autocompletado de actores.  
✅ Cache local de imágenes para mejorar el rendimiento.  
✅ Código claro y modular en Python + Flask.

---

## 🧩 Tecnologías utilizadas

| Tipo | Tecnología |
|------|-------------|
| Backend | [Python 3](https://www.python.org/), [Flask](https://flask.palletsprojects.com/) |
| Frontend | HTML5, CSS3 (vanilla) |
| Data | Archivo CSV (`imdb_movies.csv`) con títulos, descripción y elenco |
| APIs externas | [Wikipedia REST API](https://www.mediawiki.org/wiki/API:Main_page) |
| Librerías Python | `requests`, `collections`, `csv` |

---

## ⚙️ Instalación y uso

### 1️⃣ Clona el repositorio
```bash
git clone https://github.com/sauriopqno/movie_degrees.git
cd movie_degrees
```



### 2️⃣ (Opcional) Crea un entorno virtual

```bash
python -m venv venv
source venv/bin/activate   # En Linux/macOS
venv\Scripts\activate      # En Windows
```

### 3️⃣ Instala las dependencias necesarias

```bash
pip install flask requests
```

### 4️⃣ Prepara los datos

Asegúrate de tener el archivo **`imdb_movies.csv`** dentro de la carpeta `static/`.

Debe contener al menos las siguientes columnas:

| Título | Año | Género | Descripción | Elenco |
| ------ | --- | ------ | ----------- | ------ |

**Ejemplo de línea:**

```
Titanic,1997,Drama,Una joven de clase alta se enamora de un artista pobre...,Leonardo DiCaprio, Kate Winslet, Billy Zane
```

> 🗂️ Este archivo se utiliza para crear el grafo de conexiones entre actores y películas.

---

### 5️⃣ Ejecuta la aplicación

```bash
python main.py
```

La app se ejecutará en modo desarrollo (`debug=True`) y podrás acceder a ella desde tu navegador en:

```
http://localhost:5000
```

---

### 6️⃣ Uso de la aplicación

1. Ingresa dos actores en los campos de texto (ejemplo: “Leonardo DiCaprio” y “Tom Hanks”).
2. Presiona el botón **Conectar**.
3. La aplicación buscará el **camino más corto** que conecta a esos actores mediante las películas en las que participaron juntos.
4. Por cada nodo del camino (actor 🎭 o película 🎥), se mostrará:

   * Su nombre.
   * Una imagen (obtenida automáticamente desde Wikipedia).
   * En el caso de las películas, una breve descripción.

**Ejemplo visual del resultado:**

```
Leonardo DiCaprio 🎭  
↓  
Inception 🎥  
↓  
Tom Hardy 🎭  
↓  
Dunkerque 🎥  
↓  
Tom Hanks 🎭
```

---

## 🧠 Estructura del proyecto

```
movie_degrees/
├── main.py                 # Lógica principal Flask + BFS + carga CSV
├── templates/
│   └── grafo.html          # Interfaz web (HTML + CSS)
├── static/
│   └── imdb_movies.csv     # Dataset base
└── README.md               # Este archivo
```

---

## 🧰 Funciones clave

| Función                    | Descripción                                                                            |
| -------------------------- | -------------------------------------------------------------------------------------- |
| `encontrar_camino_corto()` | Aplica BFS (Breadth-First Search) para hallar la conexión mínima entre actores.        |
| `buscar_imagen_nodo()`     | Busca imágenes de actores/películas usando la API de Wikipedia, evitando logos o SVGs. |
| `obtener_foto_con_cache()` | Cachea imágenes localmente para optimizar el rendimiento.                              |
| `index()`                  | Controlador Flask que procesa la búsqueda y renderiza el resultado.                    |

---

## 💡 Ejemplo práctico

1. En el campo “Actor 1”, escribe **Leonardo DiCaprio**.
2. En el campo “Actor 2”, escribe **Tom Hanks**.
3. La aplicación mostrará la secuencia de películas y actores que los conectan.

Cada actor y película aparece en tarjetas alternadas con sus imágenes y descripciones, formando una “línea” visual de conexión.

---

## 🧑‍💻 Contribuir

¿Quieres mejorar esta app? ¡Genial!
Sigue estos pasos:

1. Haz un **fork** del repositorio.
2. Crea una nueva rama para tu mejora:

   ```bash
   git checkout -b feature/nueva-funcionalidad
   ```
3. Realiza tus cambios y pruébalos localmente.
4. Haz commit con un mensaje claro:

   ```bash
   git commit -m "Agrega nueva funcionalidad X"
   ```
5. Envía un **Pull Request** para revisión.

---

## 🗺 Roadmap (futuras mejoras)

* [ ] Añadir visualización de grafo interactivo (D3.js o vis.js).
* [ ] Guardar resultados en caché persistente.
* [ ] Implementar una API REST para consultas externas.
* [ ] Filtros por año, género o país.
* [ ] Selector de tema claro/oscuro.

---


## 💬 Autores

**[@sauriopqno](https://github.com/sauriopqno)**
, Victor Javier Garcia y
Armando Cortez
📫 Si te gusta este proyecto, ¡deja una ⭐ en el repositorio!





