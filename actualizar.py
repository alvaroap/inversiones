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

MIS_TITULOS = {
    "bbva": {"ticker": "BBVA.MC", "titulos": 735},
    "vanguard": {"ticker": "0P00000RQC.F", "titulos": 137.54},
    "fidelity": {"ticker": "IE00BYX5NX33", "titulos": 0.00},
    "quality": {"ticker": "ES0157663008", "titulos": 124.118},
    "redeia": {"ticker": "RED.MC", "titulos": 122},
    "mega": {"ticker": "ES0147711032", "titulos": 115.537}
}

def obtener_precio(ticker_str):
    try:
        t = yf.Ticker(ticker_str)
        # Intentamos obtener un historial más amplio para asegurar que haya datos
        hist = t.history(period="1mo") 
        if not hist.empty:
            # Cogemos el último valor que NO sea NaN
            precio = hist['Close'].dropna().iloc[-1]
            return float(precio)
    except:
        pass
    return None

def actualizar():
    with open(ARCHIVO_JSON, 'r', encoding='utf-8') as f:
        data = json.load(f)

    es_auto = "--auto" in sys.argv
    if es_auto:
        meses_lista = ["", "Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
        mes_dest = meses_lista[datetime.now().month]
    else:
        mes_dest = input("¿Qué mes quieres actualizar? (Ene/Feb/Mar/Abr...): ")

    if mes_dest not in MESES_MAP: return
    num_mes_dest = MESES_MAP[mes_dest]

    for activo in data["activos"]:
        id_act = activo["id"]
        if MESES_MAP[activo["desdeMes"]] <= num_mes_dest <= MESES_MAP[activo["hastaMes"]]:
            info = MIS_TITULOS.get(id_act)
            precio = obtener_precio(info["ticker"])
            
            if precio and not math.isnan(precio):
                valor_total = round(precio * info["titulos"])
                data["datos"][mes_dest][id_act]["valor"] = valor_total
                print(f"✅ {id_act}: {valor_total}€")
            else:
                print(f"⚠️ {id_act}: No se pudo obtener precio")
            
            if not es_auto:
                apor = input(f"   💸 Aportación para {id_act} (Enter para 0): ")
                data["datos"][mes_dest][id_act]["aportacion"] = round(float(apor)) if apor else 0
            
            time.sleep(2) # Pausa generosa para evitar bloqueos de Yahoo

    with open(ARCHIVO_JSON, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    actualizar()
