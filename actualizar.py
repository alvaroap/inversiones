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
            return float(hist['Close'].dropna().iloc[-1])
    except: pass
    return None

def actualizar():
    with open(ARCHIVO_JSON, 'r', encoding='utf-8') as f:
        data = json.load(f)

    es_auto = "--auto" in sys.argv
    meses_lista = ["", "Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
    mes_dest = meses_lista[datetime.now().month] if es_auto else input("¿Mes a actualizar? (Ene/Feb...): ")

    if mes_dest not in MESES_MAP: return
    num_mes_dest = MESES_MAP[mes_dest]

    # Creamos un diccionario auxiliar para saber si un activo está activo este mes
    # basándonos en la lista 'activos' del JSON
    activos_vigentes = {}
    for a in data["activos"]:
        inicio = MESES_MAP[a["desdeMes"]]
        fin = MESES_MAP[a["hastaMes"]]
        if inicio <= num_mes_dest <= fin:
            activos_vigentes[a["id"]] = True

    print(f"\n--- ACTUALIZANDO {mes_dest.upper()} ---")

    for id_act, config in data["config_inversiones"].items():
        # FILTRO: Si el activo no está vigente este mes, lo saltamos completamente
        if id_act not in activos_vigentes:
            continue

        print(f"\n[{id_act.upper()}]")
        
        # 1. Gestión de Títulos
        titulos = config["titulos"]
        if not es_auto:
            nuevo_tits = input(f"   🔢 Participaciones actuales ({titulos}): ")
            if nuevo_tits:
                titulos = float(nuevo_tits.replace(",", "."))
                data["config_inversiones"][id_act]["titulos"] = titulos

        # 2. Obtener precio y calcular valor
        precio = obtener_precio(config["ticker"])
        if precio:
            valor_mercado = round(precio * titulos)
            data["datos"][mes_dest][id_act]["valor"] = valor_mercado
            print(f"   ✅ Precio: {precio:.2f} | Valor: {valor_mercado}€")
        
        # 3. Aportación (Solo manual)
        if not es_auto:
            apor = input(f"   💸 Aportación este mes: ")
            if apor:
                data["datos"][mes_dest][id_act]["aportacion"] = round(float(apor.replace(",", ".")))

        time.sleep(1.5)

    with open(ARCHIVO_JSON, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print("\n🚀 Actualización completada.")

if __name__ == "__main__":
    actualizar()
