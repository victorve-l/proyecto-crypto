import os
import time
from datetime import datetime
import mysql.connector # Conector oficial de MySQL para Python
import requests # Librería para hacer peticiones HTTP

# URL de la API de CoinGecko para obtener precios de BTC, ETH y SOL en USD
API_URL = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,solana&vs_currencies=usd&include_24hr_vol=true&include_24hr_change=true"


# Funcion para consultar la API, extraer los datos y guardarlos en la base de datos MySQL
def guardar_precios():
  try:
    headers = {"User-Agent": "Mozilla/5.0"}
    # 1. Petición HTTP a la API externa
    res = requests.get(API_URL, headers=headers, timeout=10)
    res.raise_for_status() # Si la respuesta no es 200, lanza una excepción
    datos = res.json() # Convertir la respuesta JSON en un diccionario de Python




    # 2. Conexión a la base de datos MySQL (dentro de la red Docker)
    conexion = mysql.connector.connect(
        host=os.environ.get("DB_HOST", "mysql"), # Si existe DB_HOST en Docker, úsalo; si no, usa "mysql" como host por defecto
        port=int(os.environ.get("DB_PORT", "3306")), # Si existe DB_PORT en Docker, úsalo; si no, usa 3306 como puerto por defecto
        user=os.environ.get("DB_USER", "dash_user"), 
        password=os.environ.get("DB_PASSWORD", "DashDemo2026_local"),
        database=os.environ.get("DB_NAME", "agricultura"), # user, password y database son credenciales defeinidas en el archivo externo .env
    )

    with conexion.cursor() as cursor: # Abrir un cursor para ejecutar consultas SQL
      sql = """
            INSERT INTO precios_crypto (fecha, criptomoneda, precio_usd, volumen_24h, cambio_24h)
            VALUES (%s, %s, %s, %s, %s)
            """
      ahora = datetime.now()

      # 3. Recorrer la respuesta de la API e insertar cada criptomoneda
      for crypto, info in datos.items(): # crypto será "bitcoin", "ethereum" o "solana"; info será un diccionario con los datos de cada criptomoneda
        cursor.execute(
            sql,
            (
                ahora,
                crypto,
                info.get("usd", 0.0), # Si no existe la clave "usd", se asigna 0.0 como valor por defecto
                info.get("usd_24h_vol", 0.0), # Si no existe la clave "usd_24h_vol", se asigna 0.0 como valor por defecto
                info.get("usd_24h_change", 0.0), # Si no existe la clave "usd_24h_change", se asigna 0.0 como valor por defecto
            ),
        )

      conexion.commit()
      print(f"[{ahora}] Datos insertados exitosamente para BTC, ETH y SOL.")

    conexion.close()
  except Exception as e:
    print(f"Error en la ingesta: {e}")


if __name__ == "__main__": # Si este script se ejecuta directamente (no se importa como módulo), entonces se ejecuta el siguiente bloque de código
  # Espera 15 segundos al inicio para que MySQL termine de inicializar
  print("Esperando a que la base de datos esté lista...")
  time.sleep(15) # Espera 15 segundos para que MySQL termine de inicializar antes de hacer la primera consulta a la API

  # Bucle infinito para consultar la API periódicamente
  while True:
    guardar_precios() # Llamada a la función que consulta la API y guarda los datos en la base de datos
    time.sleep(30)  # Consulta cada 30 segundos