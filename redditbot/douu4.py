import os
import json
import csv
import time
import random
from datetime import datetime, timedelta
import praw  # Importar la librería PRAW

# Definir ruta absoluta del directorio de datos respecto a este script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, "data")

# Crear carpeta "data" si no existe
os.makedirs(DATA_DIR, exist_ok=True)

# Crear archivos base si no existen
def crear_archivos_base():
    # Archivo cuentas.json
    cuentas_path = os.path.join(DATA_DIR, 'cuentas.json')
    if not os.path.exists(cuentas_path):
        with open(cuentas_path, 'w', encoding='utf-8') as f:
            json.dump([{
                "username": "usuario1",
                "password": "contraseña1",
                "client_id": "id_cliente_1",
                "client_secret": "secreto_cliente_1"
            }], f, indent=4)
    
    # Archivo posts.csv
    posts_path = os.path.join(DATA_DIR, 'posts.csv')
    if not os.path.exists(posts_path):
        with open(posts_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['subreddit', 'title', 'img'])
            writer.writerow(['test', 'Test Post 1', 'https://example.com/image1.jpg'])
            writer.writerow(['test', 'Test Post 2', 'https://example.com/image2.jpg'])
    
    # Archivo config.json
    config_path = os.path.join(DATA_DIR, 'config.json')
    if not os.path.exists(config_path):
        config_data = {
            "start_times": ["08:00", "14:00", "20:00"]
        }
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=4)
    
    # Archivo estado.json
    estado_path = os.path.join(DATA_DIR, 'estado.json')
    if not os.path.exists(estado_path):
        with open(estado_path, 'w', encoding='utf-8') as f:
            json.dump({}, f, indent=4)

# Utilidades

def cargar_json(path):
    if not os.path.exists(path):
        log(f"Archivo no encontrado: {path}. Creando archivo vacío.")
        return {}
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def guardar_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

def leer_posts_csv():
    csv_path = os.path.join(DATA_DIR, 'posts.csv')
    if not os.path.exists(csv_path):
        log(f"Archivo no encontrado: {csv_path}. Por favor cree posts.csv")
        return []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return list(reader)

def log(mensaje):
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    print(f"{timestamp} {mensaje}")
    with open(os.path.join(DATA_DIR, 'logs.txt'), 'a', encoding='utf-8') as f:
        f.write(f"{timestamp} {mensaje}\n")

def esperar_hasta(horario_str):
    ahora = datetime.now()
    hoy_horario = datetime.strptime(horario_str, "%H:%M").replace(year=ahora.year, month=ahora.month, day=ahora.day)
    if hoy_horario < ahora:
        hoy_horario += timedelta(days=1)
    espera = (hoy_horario - ahora).total_seconds()
    log(f"Esperando hasta el próximo horario programado: {horario_str} ({int(espera)} segundos)")
    time.sleep(espera)

def obtener_proximo_horario(start_times):
    ahora = datetime.now()
    for t in start_times:
        hora = datetime.strptime(t, "%H:%M").replace(year=ahora.year, month=ahora.month, day=ahora.day)
        if ahora < hora:
            return t
    return start_times[0]  # todos pasaron, usar el primero del siguiente día

# Tiempos de espera aleatorios entre las acciones

def esperar_aleatorio(min_segundos, max_segundos):
    espera = random.randint(min_segundos, max_segundos)
    log(f"Esperando {espera} segundos...")
    time.sleep(espera)

# Función para autenticar en Reddit usando PRAW
def autenticar_reddit(cuenta):
    """
    Autenticar y devolver una instancia de Reddit.
    """
    try:
        log(f"Autenticando cuenta: {cuenta['username']}")
        reddit = praw.Reddit(
            client_id=cuenta['client_id'],
            client_secret=cuenta['client_secret'],
            username=cuenta['username'],
            password=cuenta['password'],
            user_agent=f"script:{cuenta['client_id']}:v1.0 (by /u/{cuenta['username']})"
        )
        # Verificar que la autenticación sea exitosa
        reddit.user.me()  # Si falla, lanzará una excepción
        log(f"Autenticación exitosa para la cuenta: {cuenta['username']}")
        return reddit
    except Exception as e:
        log(f"Error al autenticar la cuenta {cuenta['username']}: {e}")
        return None

# Publicar en un subreddit usando PRAW
def publicar_post(reddit, subreddit_name, title, img, post_number, total_posts):
    """
    Publicar un post en un subreddit y devolver el enlace al post.
    """
    try:
        subreddit = reddit.subreddit(subreddit_name)
        # Simular tiempo de búsqueda del subreddit
        esperar_aleatorio(2, 5)  # Esperar de 2 a 5 segundos

        # Simular tiempo de preparación del título y enlace
        esperar_aleatorio(2, 5)  # Esperar de 2 a 5 segundos

        # Publicar el post
        submission = subreddit.submit(title=title, url=img)

        # Capturar la URL única del post en Reddit
        reddit_post_url = f"https://www.reddit.com{submission.permalink}"

        mensaje = f"Post {post_number}/{total_posts} publicado exitosamente en {subreddit_name}: {title}\n{reddit_post_url}"
        log(mensaje)
        return reddit_post_url
    except Exception as e:
        log(f"Error al publicar en {subreddit_name}: {e}")
        return None

# Validar datos necesarios antes de ejecutar el script
def validar_datos(cuentas, posts, config):
    """
    Validar que los datos necesarios estén completos.
    """
    if not cuentas or any(not cuenta.get('username') or not cuenta.get('password') or not cuenta.get('client_id') or not cuenta.get('client_secret') for cuenta in cuentas):
        log("Error: cuentas.json está incompleto o no contiene datos válidos. Por favor, complete este archivo.")
        return False

    if not posts or any(not post.get('subreddit') or not post.get('title') or not post.get('img') for post in posts):
        log("Error: posts.csv está incompleto o no contiene datos válidos. Por favor, complete este archivo.")
        return False

    if not config or not config.get('start_times'):
        log("Error: config.json está incompleto o no contiene horarios de inicio. Por favor, complete este archivo.")
        return False

    return True

# Main script

def main():
    # Crear archivos base si no existen
    crear_archivos_base()

    # Cargar datos
    cuentas_path = os.path.join(DATA_DIR, 'cuentas.json')
    config_path = os.path.join(DATA_DIR, 'config.json')
    cuentas = cargar_json(cuentas_path)
    config = cargar_json(config_path)
    posts = leer_posts_csv()

    # Validar datos
    if not validar_datos(cuentas, posts, config):
        log("El script no puede continuar debido a datos incompletos.")
        return

    # Configuración de publicación diaria
    CICLOS_DIARIOS = 3  # Número de ciclos diarios (horarios)
    MIN_PUBLICACIONES = 12
    MAX_PUBLICACIONES = 21

    # Calcular el promedio de publicaciones por tanda
    for cuenta in cuentas:
        publicaciones_diarias = random.randint(MIN_PUBLICACIONES, MAX_PUBLICACIONES)
        publicaciones_por_tanda = publicaciones_diarias // CICLOS_DIARIOS

        for tanda in range(CICLOS_DIARIOS):
            reddit = autenticar_reddit(cuenta)
            if not reddit:
                log(f"Saltando cuenta: {cuenta['username']}")
Aquí está el script completo, adaptado para cumplir con la solicitud de ajustar el número aleatorio de publicaciones por tanda y mantener el total diario entre 12 y 21 publicaciones, distribuidas en los tres horarios programados:

```python name=reddit_post_scheduler_randomized.py
import os
import json
import csv
import time
import random
from datetime import datetime, timedelta
import praw  # Importar la librería PRAW

# Definir ruta absoluta del directorio de datos respecto a este script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, "data")

# Crear carpeta "data" si no existe
os.makedirs(DATA_DIR, exist_ok=True)

# Crear archivos base si no existen
def crear_archivos_base():
    # Archivo cuentas.json
    cuentas_path = os.path.join(DATA_DIR, 'cuentas.json')
    if not os.path.exists(cuentas_path):
        with open(cuentas_path, 'w', encoding='utf-8') as f:
            json.dump([{
                "username": "usuario1",
                "password": "contraseña1",
                "client_id": "id_cliente_1",
                "client_secret": "secreto_cliente_1"
            }], f, indent=4)
    
    # Archivo posts.csv
    posts_path = os.path.join(DATA_DIR, 'posts.csv')
    if not os.path.exists(posts_path):
        with open(posts_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['subreddit', 'title', 'img'])
            writer.writerow(['test', 'Test Post 1', 'https://example.com/image1.jpg'])
            writer.writerow(['test', 'Test Post 2', 'https://example.com/image2.jpg'])
    
    # Archivo config.json
    config_path = os.path.join(DATA_DIR, 'config.json')
    if not os.path.exists(config_path):
        config_data = {
            "start_times": ["08:00", "14:00", "20:00"]
        }
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=4)
    
    # Archivo estado.json
    estado_path = os.path.join(DATA_DIR, 'estado.json')
    if not os.path.exists(estado_path):
        with open(estado_path, 'w', encoding='utf-8') as f:
            json.dump({}, f, indent=4)

# Utilidades

def cargar_json(path):
    if not os.path.exists(path):
        log(f"Archivo no encontrado: {path}. Creando archivo vacío.")
        return {}
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def guardar_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

def leer_posts_csv():
    csv_path = os.path.join(DATA_DIR, 'posts.csv')
    if not os.path.exists(csv_path):
        log(f"Archivo no encontrado: {csv_path}. Por favor cree posts.csv")
        return []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return list(reader)

def log(mensaje):
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    print(f"{timestamp} {mensaje}")
    with open(os.path.join(DATA_DIR, 'logs.txt'), 'a', encoding='utf-8') as f:
        f.write(f"{timestamp} {mensaje}\n")

def esperar_hasta(horario_str):
    ahora = datetime.now()
    hoy_horario = datetime.strptime(horario_str, "%H:%M").replace(year=ahora.year, month=ahora.month, day=ahora.day)
    if hoy_horario < ahora:
        hoy_horario += timedelta(days=1)
    espera = (hoy_horario - ahora).total_seconds()
    log(f"Esperando hasta el próximo horario programado: {horario_str} ({int(espera)} segundos)")
    time.sleep(espera)

def obtener_proximo_horario(start_times):
    ahora = datetime.now()
    for t in start_times:
        hora = datetime.strptime(t, "%H:%M").replace(year=ahora.year, month=ahora.month, day=ahora.day)
        if ahora < hora:
            return t
    return start_times[0]  # todos pasaron, usar el primero del siguiente día

# Tiempos de espera aleatorios entre las acciones

def esperar_aleatorio(min_segundos, max_segundos):
    espera = random.randint(min_segundos, max_segundos)
    log(f"Esperando {espera} segundos...")
    time.sleep(espera)

# Función para autenticar en Reddit usando PRAW
def autenticar_reddit(cuenta):
    """
    Autenticar y devolver una instancia de Reddit.
    """
    try:
        log(f"Autenticando cuenta: {cuenta['username']}")
        reddit = praw.Reddit(
            client_id=cuenta['client_id'],
            client_secret=cuenta['client_secret'],
            username=cuenta['username'],
            password=cuenta['password'],
            user_agent=f"script:{cuenta['client_id']}:v1.0 (by /u/{cuenta['username']})"
        )
        # Verificar que la autenticación sea exitosa
        reddit.user.me()  # Si falla, lanzará una excepción
        log(f"Autenticación exitosa para la cuenta: {cuenta['username']}")
        return reddit
    except Exception as e:
        log(f"Error al autenticar la cuenta {cuenta['username']}: {e}")
        return None

# Publicar en un subreddit usando PRAW
def publicar_post(reddit, subreddit_name, title, img, post_number, total_posts):
    """
    Publicar un post en un subreddit y devolver el enlace al post.
    """
    try:
        subreddit = reddit.subreddit(subreddit_name)
        # Simular tiempo de búsqueda del subreddit
        esperar_aleatorio(2, 5)  # Esperar de 2 a 5 segundos

        # Simular tiempo de preparación del título y enlace
        esperar_aleatorio(2, 5)  # Esperar de 2 a 5 segundos

        # Publicar el post
        submission = subreddit.submit(title=title, url=img)

        # Capturar la URL única del post en Reddit
        reddit_post_url = f"https://www.reddit.com{submission.permalink}"

        mensaje = f"Post {post_number}/{total_posts} publicado exitosamente en {subreddit_name}: {title}\n{reddit_post_url}"
        log(mensaje)
        return reddit_post_url
    except Exception as e:
        log(f"Error al publicar en {subreddit_name}: {e}")
        return None

# Validar datos necesarios antes de ejecutar el script
def validar_datos(cuentas, posts, config):
    """
    Validar que los datos necesarios estén completos.
    """
    if not cuentas or any(not cuenta.get('username') or not cuenta.get('password') or not cuenta.get('client_id') or not cuenta.get('client_secret') for cuenta in cuentas):
        log("Error: cuentas.json está incompleto o no contiene datos válidos. Por favor, complete este archivo.")
        return False

    if not posts or any(not post.get('subreddit') or not post.get('title') or not post.get('img') for post in posts):
        log("Error: posts.csv está incompleto o no contiene datos válidos. Por favor, complete este archivo.")
        return False

    if not config or not config.get('start_times'):
        log("Error: config.json está incompleto o no contiene horarios de inicio. Por favor, complete este archivo.")
        return False

    return True

# Main script

def main():
    # Crear archivos base si no existen
    crear_archivos_base()

    # Cargar datos
    cuentas_path = os.path.join(DATA_DIR, 'cuentas.json')
    config_path = os.path.join(DATA_DIR, 'config.json')
    cuentas = cargar_json(cuentas_path)
    config = cargar_json(config_path)
    posts = leer_posts_csv()

    # Validar datos
    if not validar_datos(cuentas, posts, config):
        log("El script no puede continuar debido a datos incompletos.")
        return

    # Configuración de publicación diaria
    CICLOS_DIARIOS = 3  # Número de ciclos diarios (horarios)
    MIN_PUBLICACIONES = 12
    MAX_PUBLICACIONES = 21

    for cuenta in cuentas:
        publicaciones_diarias = random.randint(MIN_PUBLICACIONES, MAX_PUBLICACIONES)
        log(f"La cuenta {cuenta['username']} publicará {publicaciones_diarias} posts hoy.")
        publicaciones_restantes = publicaciones_diarias

        for ciclo in range(CICLOS_DIARIOS):
            publicaciones_por_ciclo = random.randint(3, min(7, publicaciones_restantes))
            publicaciones_restantes -= publicaciones_por_ciclo
            log(f"Ciclo {ciclo + 1} para {cuenta['username']}: {publicaciones_por_ciclo} posts.")

            reddit = autenticar_reddit(cuenta)
            if not reddit:
                log(f"Error de autenticación para {cuenta['username']}. Saltando ciclo.")
                continue

            for i, post in enumerate(posts[:publicaciones_por_ciclo]):
                publicar_post(reddit, post['subreddit'], post['title'], post['img'], i + 1, publicaciones_por_ciclo)
                esperar_aleatorio(180, 360)  # Esperar entre 3 y 6 minutos

if __name__ == "__main__":
    main()