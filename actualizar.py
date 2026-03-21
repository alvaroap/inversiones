import json
import yfinance as yf
import os
import sys
from datetime import datetime

DIRECTORIO = os.path.dirname(os.path.abspath(__file__))
ARCHIVO_JSON = os.path.join(DIRECTORIO, "datos.json")

# Diccionario para comparar meses
MESES_MAP = {"Ene": 1, "Feb": 2, "Mar": 3, "Abr": 4, "May": 5, "Jun": 6, 
             "Jul": 7, "Ago": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dic": 12}

# --- CONFIGURACIÓN DE TUS TÍTULOS ---
MIS_TITULOS = {
    "bbva": {"ticker": "BBVA.MC", "titulos": 735},
    "vanguard": {"ticker": "IE00B03HCZ61", "titulos": 130.46}, 
    "quality": {"ticker": "ES0157663008", "titulos": 124.118},
    "redeia": {"ticker": "RED.MC", "titulos": 122},
    "mega": {"ticker": "ES0147711032", "titulos": 115.537}
}

def actualizar():
    with open(ARCHIVO_JSON, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # --- LÓGICA DE DETECCIÓN DE MODO (AUTO O MANUAL) ---
    es_auto = "--auto" in sys.argv
    
    if es_auto:
        # El robot detecta el mes solo
        meses_lista = ["", "Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
        mes_dest = meses_lista[datetime.now().month]
    else:
        # A ti te pregunta como siempre
        mes_dest = input("¿Qué mes quieres actualizar? (Ene/Feb/Mar/Abr...): ")

    if mes_dest not in MESES_MAP:
        print(f"❌ Mes '{mes_dest}' no válido.")
        return

    num_mes_dest = MESES_MAP[mes_dest]
    print(f"\n--- 🚀 Iniciando actualización de {mes_dest} {'(MODO AUTOMÁTICO)' if es_auto else ''} ---")

    for activo in data["activos"]:
        id_act = activo["id"]
        inicio = MESES_MAP[activo["desdeMes"]]
        fin = MESES_MAP[activo["hastaMes"]]

        # Solo procesar si el activo está vigente en este mes
        if inicio <= num_mes_dest <= fin:
            print(f"\n📦 {activo['nombre'].upper()}")
            
            # 1. Obtener precio de Yahoo Finance
            info = MIS_TITULOS.get(id_act)
            precio_mercado = 0
            
            try:
                ticker_yf = yf.Ticker(info["ticker"])
                hist = ticker_yf.history(period="5d")
                if not hist.empty:
                    precio_mercado = hist['Close'].tail(1).values[0]
                else:
                    raise Exception("No hay datos")
            except:
                if es_auto:
                    # Si el robot falla, mantiene el valor que ya había para no poner 0
                    print(f"   ⚠️ Error en Yahoo para {id_act}. Saltando...")
                    continue
                else:
                    print(f"   ⚠️ No pude conectar con Yahoo para {id_act}. Introduce valor manual.")
                    val_manual = input(f"   Valor total mercado (Enter para saltar): ")
                    if val_manual: precio_mercado = float(val_manual) / info["titulos"]

            # 2. Calcular y Guardar Valor
            tits = info["titulos"]
            valor_total = round(precio_mercado * tits)
            data["datos"][mes_dest][id_act]["valor"] = valor_total
            print(f"   ✅ Precio: {precio_mercado:.2f}€ | Total: {valor_total}€")

            # 3. Aportación (Solo pregunta si NO es automático)
            if not es_auto:
                apor = input(f"   💸 Aportación de este mes (Enter para 0): ")
                data["datos"][mes_dest][id_act]["aportacion"] = round(float(apor)) if apor else 0
            # Si es auto, NO tocamos la aportación para no borrar lo que tú pongas manual
        
        else:
            # Activo fuera de rango -> Todo a 0
            data["datos"][mes_dest][id_act]["valor"] = 0
            data["datos"][mes_dest][id_act]["aportacion"] = 0
            print(f"\n⏭️  {activo['nombre'].upper()} omitido (fuera de fecha).")

    # Guardar cambios
    with open(ARCHIVO_JSON, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✨ ¡Listo! Datos de {mes_dest} guardados.")

if __name__ == "__main__":
    actualizar()