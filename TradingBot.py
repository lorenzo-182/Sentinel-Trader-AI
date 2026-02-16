import yfinance as yf
import pandas as pd
import os
from datetime import datetime
import requests
from dotenv import load_dotenv # Nueva librería para las variables


activos = ["^GSPC", "^IXIC", "BTC-USD"]

print("--- REPORTE MULTI-ACTIVO PROFESIONAL ---")
print("-" * 40)
resultados = []
dir_path = os.path.dirname(os.path.realpath(__file__))
load_dotenv(os.path.join(dir_path, '.env'))
def enviar_telegram(mensaje):
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_ID")
    if not token or not chat_id:
        print("❌ ERROR: No se cargaron las credenciales desde el archivo .env")
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={mensaje}"
    try:
        r = requests.get(url)
        if r.status_code == 200:
            print(f"✅ Mensaje enviado con éxito a las {datetime.now().strftime('%H:%M:%S')}")
        else:
            print(f"❌ Error de Telegram (Código {r.status_code}): {r.text}")
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
# 1. Configuración
for ticket in activos:
    # Descarga de datos
    data = yf.download(ticket, period="6mo", interval="1d", progress=False)
    
    # Cálculos Técnicos
    data['SMA20'] = data['Close'].rolling(window=20).mean()
    
    # RSI (Matemática manual)
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    data['RSI'] = 100 - (100 / (1 + rs))

    # Obtener últimos valores (usamos .values[0] porque yfinance a veces devuelve series complejas)
    ultimo_cierre = data['Close'].iloc[-1].item()
    ultima_sma = data['SMA20'].iloc[-1].item()
    ultimo_rsi = data['RSI'].iloc[-1].item()

    # Gestión de Riesgo (2% pérdida / 6% ganancia)
    stop_loss = ultimo_cierre * 0.98
    take_profit = ultimo_cierre * 1.06

    porcentaje_stop_loss = 0.02 
    porcentaje_take_profit = 0.06
     
    # 5. Determinar Estado
    if ultimo_cierre > ultima_sma and ultimo_rsi < 70:
        estado = "COMPRA (Alcista)"
    elif ultimo_rsi > 70:
        estado = "SOBRECOMPRA (Esperar)"
    else:
        estado = "BAJISTA (Resguardo)"
    if estado == "COMPRA (Alcista)":
       alerta = f"🚀 OPORTUNIDAD EN {ticket}\nPrecio: {ultimo_cierre:.2f}\nS.L: {stop_loss:.2f} | T.P: {take_profit:.2f}"
       enviar_telegram(alerta)
    elif estado == "SOBRECOMPRA (Esperar)":
         alerta = f"⚠️ ALERTA: {ticket} en SOBRECOMPRA ({ultimo_rsi:.2f}). No entrar."
         enviar_telegram(alerta)    

    # 6. Imprimir Reporte en Consola (DENTRO DEL BUCLE)
    print(f"ACTIVO: {ticket}")
    print(f"Precio: {ultimo_cierre:.2f} | RSI: {ultimo_rsi:.2f} | SMA20: {ultima_sma:.2f}")
    print(f"DIAGNÓSTICO: {estado}")
    if estado == "COMPRA (Alcista)":
        print(f" -> S.L: {stop_loss:.2f} | T.P: {take_profit:.2f}")
    print("-" * 30)

    # 7. Agregar a la lista para el CSV
    resultados.append({
        "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Activo": ticket,
        "Precio": round(ultimo_cierre, 2),
        "RSI": round(ultimo_rsi, 2),
        "Estado": estado
    })


if resultados:
    df_reporte = pd.DataFrame(resultados)
    nombre_archivo = "historial_trading.csv"
    archivo_existe = os.path.isfile(nombre_archivo)
    df_reporte.to_csv(nombre_archivo, mode='a', header=not archivo_existe, index=False)
    print("¡ÉXITO! Reporte guardado en 'historial_trading.csv'")

 