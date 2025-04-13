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
        cuentas_ejemplo = [
            {"username": "usuario1", "password": "pass1", "client_id": "id1", "client_secret": "secret1"},
            {"username": "usuario2", "password": "pass2", "client_id": "id2", "client_secret": "secret2"},
            {"username": "usuario3", "password": "pass3", "client_id": "id3", "client_secret": "secret3"}
        ]
        with open(cuentas_path, 'w', encoding='utf-8') as f:
            json.dump(cuentas_ejemplo, f, indent=4)

    # Archivo posts.csv
    posts_path = os.path.join(DATA_DIR, 'posts.csv')
    if not os.path.exists(posts_path):
        with open(posts_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['subreddit', 'title', 'img'])
            writer.writerow(['funny', 'Este es un título de ejemplo', 'ruta/a/imagen1.jpg'])
            writer.writerow(['pics', 'Otro título reemplazable', 'ruta/a/imagen2.png'])

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
            time.sleep(2)
            log(f"Cuenta {cuenta['username']} logueada exitosamente.")

            delays = []
            for i in range(5):
                delay = random.randint(60, 420)
                delays.append(delay)
                log(f"Cuenta {idx+1}/{len(cuentas)} publicando post {i+1}/5 en {int(delay / 60)} minutos...")
                time.sleep(delay)
                log(f"Publicado exitosamente en subreddit simulado. (delay: {delay}s)")

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
            time.sleep(2)
            log(f"Cuenta {cuenta['username']} logueada exitosamente.")

            delays = []
            for i in range(5):
                delay = random.randint(60, 420)
                delays.append(delay)
                log(f"Cuenta {idx+1}/{len(cuentas)} publicando post {i+1}/5 en {int(delay / 60)} minutos...")
                time.sleep(delay)
                log(f"Publicado exitosamente en subreddit simulado. (delay: {delay}s)")

            total_delay = sum(delays)
            log(f"Cuenta {cuenta['username']} finalizó sus publicaciones. Total: {int(total_delay/60)} min.")

        log("\nTanda manual completada. El proceso ha finalizado.")
    else:
        log("Opción no válida. El proceso ha terminado.")

if __name__ == "__main__":
    main()
