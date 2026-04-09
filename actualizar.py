import json
import yfinance as yf
import os
import sys
from datetime import datetime

DIRECTORIO = os.path.dirname(os.path.abspath(__file__))
ARCHIVO_JSON = os.path.join(DIRECTORIO, "datos.json")

MESES_MAP = {"Ene": 1, "Feb": 2, "Mar": 3, "Abr": 4, "May": 5, "Jun": 6, 
             "Jul": 7, "Ago": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dic": 12}

# Configuración actualizada de tus activos
MIS_TITULOS = {
    "bbva": {"ticker": "BBVA.MC", "titulos": 735},
    "vanguard": {"ticker": "0P00000RQC.F", "titulos": 137.54}, 
    "quality": {"ticker": "ES0157663008", "titulos": 124.118},
    "redeia": {"ticker": "RED.MC", "titulos": 122},
    "mega": {"ticker": "ES0147711032", "titulos": 115.537}
}

def actualizar():
    with open(ARCHIVO_JSON, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # DETECTAR SI ES EL ROBOT O ERES TÚ
    es_auto = "--auto" in sys.argv
    
    if es_auto:
        # El robot mira qué mes es hoy automáticamente
        meses_lista = ["", "Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
        mes_dest = meses_lista[datetime.now().month]
        print(f"🤖 Modo Automático: Actualizando {mes_dest}")
    else:
        mes_dest = input("¿Qué mes quieres actualizar? (Ene/Feb/Mar/Abr...): ")

    if mes_dest not in MESES_MAP: return

    num_mes_dest = MESES_MAP[mes_dest]
    for activo in data["activos"]:
        id_act = activo["id"]
        # Solo actualizar si el activo está en su rango de fechas
        if MESES_MAP[activo["desdeMes"]] <= num_mes_dest <= MESES_MAP[activo["hastaMes"]]:
            info = MIS_TITULOS.get(id_act)
            try:
                ticker_yf = yf.Ticker(info["ticker"])
                hist = ticker_yf.history(period="5d")
                precio = hist['Close'].tail(1).values[0] if not hist.empty else 0
            except: precio = 0

            # Guardar el valor total (Precio mercado * Tus títulos)
            valor_total = round(precio * info["titulos"])
            data["datos"][mes_dest][id_act]["valor"] = valor_total

            # Solo preguntar aportación si NO es el robot
            if not es_auto:
                apor = input(f"   💸 Aportación para {id_act} (Enter para 0): ")
                data["datos"][mes_dest][id_act]["aportacion"] = round(float(apor)) if apor else 0
        
    with open(ARCHIVO_JSON, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    actualizar()
