import json
import yfinance as yf
import os
import sys
import math
import time
from datetime import datetime

DIRECTORIO = os.path.dirname(os.path.abspath(__file__))
ARCHIVO_JSON = os.path.join(DIRECTORIO, "datos.json")

MESES_MAP = {"Ene": 1, "Feb": 2, "Mar": 3, "Abr": 4, "May": 5, "Jun": 6, 
             "Jul": 7, "Ago": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dic": 12}

def obtener_precio(ticker_str):
    try:
        t = yf.Ticker(ticker_str)
        hist = t.history(period="1mo") 
        if not hist.empty:
            precio = hist['Close'].dropna().iloc[-1]
            return float(precio)
    except: pass
    return None

def actualizar():
    if not os.path.exists(ARCHIVO_JSON):
        print(f"❌ Error: No se encuentra {ARCHIVO_JSON}")
        return

    with open(ARCHIVO_JSON, 'r', encoding='utf-8') as f:
        data = json.load(f)

    es_auto = "--auto" in sys.argv
    meses_lista = ["", "Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
    mes_dest = meses_lista[datetime.now().month] if es_auto else input("¿Mes a actualizar? (Ene/Feb...): ")

    if mes_dest not in MESES_MAP: 
        print("❌ Mes no válido")
        return

    print(f"\n--- ACTUALIZANDO {mes_dest.upper()} ---")

    for id_act, config in data["config_inversiones"].items():
        # 1. Gestión de Títulos (Manual vs Auto)
        titulos_actuales = config["titulos"]
        if not es_auto:
            print(f"\n[{id_act.upper()}]")
            nuevo_tits = input(f"   🔢 Participaciones actuales ({titulos_actuales}): ")
            if nuevo_tits:
                titulos_actuales = float(nuevo_tits.replace(",", "."))
                data["config_inversiones"][id_act]["titulos"] = titulos_actuales

        # 2. Cálculo de Valor de Mercado
        precio = obtener_precio(config["ticker"])
        if precio and not math.isnan(precio):
            valor_mercado = round(precio * titulos_actuales)
            data["datos"][mes_dest][id_act]["valor"] = valor_mercado
            print(f"   ✅ Precio: {precio:.2f} | Valor: {valor_mercado}€")
        else:
            print(f"   ⚠️ Error de conexión con Yahoo para {id_act}")

        # 3. Gestión de Aportaciones (Solo Manual)
        if not es_auto:
            apor = input(f"   💸 Aportación este mes: ")
            if apor:
                data["datos"][mes_dest][id_act]["aportacion"] = round(float(apor.replace(",", ".")))

        time.sleep(1.5) # Pausa para evitar bloqueos de Yahoo

    with open(ARCHIVO_JSON, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print("\n🚀 Proceso finalizado. datos.json actualizado.")

if __name__ == "__main__":
    actualizar()
