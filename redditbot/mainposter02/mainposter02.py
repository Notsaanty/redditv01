import os
import json
import csv
import time
import random
from datetime import datetime, timedelta

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
            writer.writerow(['r/test', 'Test Post 1', 'image1.jpg'])
            writer.writerow(['r/test', 'Test Post 2', 'image2.jpg'])
    
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
    
    # Archivo agents.json
    agents_path = os.path.join(DATA_DIR, 'agents.json')
    if not os.path.exists(agents_path):
        agents_data = {
            "user_agents": [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.85 Safari/537.36",
                "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:57.0) Gecko/20100101 Firefox/57.0"
            ]
        }
        with open(agents_path, 'w', encoding='utf-8') as f:
            json.dump(agents_data, f, indent=4)

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

def obtener_user_agent():
    agents_path = os.path.join(DATA_DIR, 'agents.json')
    agents_data = cargar_json(agents_path)
    user_agents = agents_data.get("user_agents", [])
    if not user_agents:
        log("No se encontraron user agents en agents.json.")
        return None
    user_agent = random.choice(user_agents)
    log("Obteniendo un nuevo user agent...")
    return user_agent

# Tiempos de espera aleatorios entre las acciones

def esperar_aleatorio(min_segundos, max_segundos):
    espera = random.randint(min_segundos, max_segundos)
    log(f"Esperando {espera} segundos...")
    time.sleep(espera)

# Main script

def main():
    # Crear archivos base si no existen
    crear_archivos_base()

    # Preguntar si desea comenzar
    input("Presiona Enter para comenzar...")

    # Preguntar si desea trabajar con las tandas programadas o hacer una tanda manual
    opcion = input("¿Deseas trabajar con las tandas programadas o hacer una tanda manual ahora mismo?\n1. Tandas programadas\n2. Hacer una tanda manual\nElige una opción (1 o 2): ")

    if opcion == '1':
        cuentas_path = os.path.join(DATA_DIR, 'cuentas.json')
        config_path = os.path.join(DATA_DIR, 'config.json')
        estado_path = os.path.join(DATA_DIR, 'estado.json')

        cuentas = cargar_json(cuentas_path)
        config = cargar_json(config_path)
        estado = cargar_json(estado_path)
        posts = leer_posts_csv()

        if not cuentas:
            log("No se encontraron cuentas en cuentas.json")
            return
        if not posts:
            log("No hay publicaciones disponibles. Por favor actualice el archivo posts.csv")
            return

        start_times = config.get("start_times", ["08:00", "14:00", "20:00"])
        proximo_horario = obtener_proximo_horario(start_times)
        esperar_hasta(proximo_horario)

        for idx, cuenta in enumerate(cuentas):
            log(f"\nLogueando cuenta {cuenta['username']} ({idx+1}/{len(cuentas)})...")

            # Obtener user agent aleatorio
            log("Obteniendo un nuevo user agent...")
            user_agent = obtener_user_agent()
            log(f"Usando user agent: {user_agent}")

            time.sleep(2)
            log(f"Cuenta {cuenta['username']} logueada exitosamente.")

            for i in range(5):
                # Espera aleatoria entre acciones
                esperar_aleatorio(5, 15)  # Tiempo aleatorio entre 5 y 15 segundos para simular escribir el título
                log(f"Configurando título del post {i+1}/5...")

                esperar_aleatorio(5, 15)  # Espera aleatoria para subir la imagen
                log(f"Subiendo imagen del post {i+1}/5...")

                esperar_aleatorio(10, 20)  # Espera aleatoria antes de hacer la publicación
                log(f"Publicando el post {i+1}/5...")

                delay = random.randint(60, 420)
                log(f"Publicado exitosamente en subreddit simulado. (delay: {delay}s)")
                time.sleep(delay)

            total_delay = sum(delays)
            restante = max(0, 3420 - total_delay)
            log(f"Cuenta {cuenta['username']} finalizó sus publicaciones. Total: {int(total_delay/60)} min. Esperando {int(restante/60)} min restantes...")
            time.sleep(restante)

            input(f"\nPor favor cambie la IP antes de continuar con la siguiente cuenta. Presione ENTER para continuar...")

        log("\nTanda completada. Esperando al próximo horario programado...")

    elif opcion == '2':
        cuentas_path = os.path.join(DATA_DIR, 'cuentas.json')
        cuentas = cargar_json(cuentas_path)

        if not cuentas:
            log("No se encontraron cuentas en cuentas.json")
            return

        # Hacer tanda manual ahora mismo
        for idx, cuenta in enumerate(cuentas):
            log(f"\nLogueando cuenta {cuenta['username']} ({idx+1}/{len(cuentas)})...")

            # Obtener user agent aleatorio
            log("Obteniendo un nuevo user agent...")
            user_agent = obtener_user_agent()
            log(f"Usando user agent: {user_agent}")

            time.sleep(2)
            log(f"Cuenta {cuenta['username']} logueada exitosamente.")

            for i in range(5):
                # Espera aleatoria entre acciones
                esperar_aleatorio(5, 15)  # Tiempo aleatorio entre 5 y 15 segundos para simular escribir el título
                log(f"Configurando título del post {i+1}/5...")

                esperar_aleatorio(5, 15)  # Espera aleatoria para subir la imagen
                log(f"Subiendo imagen del post {i+1}/5...")

                esperar_aleatorio(10, 20)  # Espera aleatoria antes de hacer la publicación
                log(f"Publicando el post {i+1}/5...")

                delay = random.randint(60, 420)
                log(f"Publicado exitosamente en subreddit simulado. (delay: {delay}s)")
                time.sleep(delay)

            log(f"Cuenta {cuenta['username']} finalizó sus publicaciones.")

        log("\nTanda manual completada. El proceso ha finalizado.")
    else:
        log("Opción no válida. El proceso ha terminado.")

if __name__ == "__main__":
    main()
