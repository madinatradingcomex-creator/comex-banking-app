import pandas as pd
from datetime import datetime, date
from engine.rules_engine import evaluate_semaphore

def normalize_column_name(col):
    c = str(col).strip().upper()
    c = c.replace("N°", "NUMERO").replace("NRO", "NUMERO").replace("Nº", "NUMERO")
    c = c.replace("Á", "A").replace("É", "E").replace("Í", "I").replace("Ó", "O").replace("Ú", "U")
    return c

def parse_sabana_dataframe(df, regime_hint="AUTO"):
    if df.empty:
        return pd.DataFrame(), "DESCONOCIDO", {}
        
    col_map = {col: normalize_column_name(col) for col in df.columns}
    df_clean = df.rename(columns=col_map).copy()
    
    text_corpus = " ".join([str(c) for c in df_clean.columns])
    is_secoexpo = any(k in text_corpus for k in ["EMBARQUE", "SECOEXPO", "PERMISO", "FOB", "EXPORTAC"])
    
    if regime_hint == "SECOEXPO" or (regime_hint == "AUTO" and is_secoexpo):
        regime = "SECOEXPO"
    else:
        regime = "SEPAIMPO"
        
    enriched_rows = []
    today = datetime.now().date()
    
    for idx, row in df_clean.iterrows():
        op_id = "N/D"
        for k in ["NUMERO DE PERMISO", "NUMERO PERMISO", "PERMISO DE EMBARQUE", "PERMISO", "DESPACHO", "NUMERO DE DESPACHO", "OPERACION"]:
            if k in row and pd.notna(row[k]) and str(row[k]).strip():
                op_id = str(row[k]).strip()
                break
                
        banco = "Banco Principal"
        for k in ["BANCO", "BANCO NOMINADO", "BANCO SEGUIMIENTO", "ENTIDAD"]:
            if k in row and pd.notna(row[k]):
                banco = str(row[k]).strip()
                break
                
        monto_str = 0.0
        for k in ["SALDO PENDIENTE", "SALDO", "MONTO PENDIENTE", "IMPORTE PENDIENTE", "VALOR FOB", "MONTO", "IMPORTE"]:
            if k in row and pd.notna(row[k]):
                try:
                    val = str(row[k]).replace("$", "").replace("USD", "").replace(".", "").replace(",", ".").strip()
                    monto_str = float(val)
                    break
                except:
                    pass
                    
        fecha_limite = None
        for k in ["FECHA LIMITE", "FECHA VENCIMIENTO", "VENCIMIENTO", "FECHA PLAZO", "FECHA LIMITE DEMOSTRACION"]:
            if k in row and pd.notna(row[k]):
                try:
                    if isinstance(row[k], (datetime, date)):
                        fecha_limite = row[k].date() if isinstance(row[k], datetime) else row[k]
                    else:
                        fecha_limite = pd.to_datetime(row[k], dayfirst=True).date()
                    break
                except:
                    pass
                    
        fecha_op = None
        for k in ["FECHA CUMPLIDO", "FECHA PAGO", "FECHA OFICIALIZACION", "FECHA"]:
            if k in row and pd.notna(row[k]):
                try:
                    if isinstance(row[k], (datetime, date)):
                        fecha_op = row[k].date() if isinstance(row[k], datetime) else row[k]
                    else:
                        fecha_op = pd.to_datetime(row[k], dayfirst=True).date()
                    break
                except:
                    pass

        if fecha_limite:
            days_left = (fecha_limite - today).days
        elif fecha_op:
            fecha_limite = fecha_op + pd.Timedelta(days=180)
            days_left = (fecha_limite - today).days
        else:
            fecha_limite = today + pd.Timedelta(days=30)
            days_left = 30
            
        sem = evaluate_semaphore(days_left)
        
        enriched_rows.append({
            "Identificador": op_id,
            "Banco Nominado": banco,
            "Monto Pendiente (USD)": monto_str,
            "Fecha Inicio": str(fecha_op) if fecha_op else "N/D",
            "Fecha Límite": str(fecha_limite),
            "Días Restantes": days_left,
            "Estado Semáforo": f"{sem['color']} {sem['estado']}",
            "Nivel Riesgo": sem["nivel"],
            "Acción Sugerida": sem["accion"]
        })
        
    res_df = pd.DataFrame(enriched_rows)
    
    stats = {
        "total_operaciones": len(res_df),
        "monto_total_usd": res_df["Monto Pendiente (USD)"].sum() if not res_df.empty else 0.0,
        "en_mora": len(res_df[res_df["Días Restantes"] < 0]) if not res_df.empty else 0,
        "en_riesgo_alto": len(res_df[(res_df["Días Restantes"] >= 0) & (res_df["Días Restantes"] <= 15)]) if not res_df.empty else 0,
        "en_plazo": len(res_df[res_df["Días Restantes"] > 15]) if not res_df.empty else 0
    }
    
    return res_df, regime, stats

def get_demo_secoexpo_data():
    data = [
        {"Numero Permiso": "26001EC01004567Z", "Banco": "Santander", "Fecha Cumplido": "15/04/2026", "Fecha Limite": "15/10/2026", "Saldo Pendiente": "45000.00"},
        {"Numero Permiso": "26001EC01007890B", "Banco": "Galicia", "Fecha Cumplido": "10/01/2026", "Fecha Limite": "10/07/2026", "Saldo Pendiente": "18500.00"},
        {"Numero Permiso": "26001EC01009911C", "Banco": "BBVA", "Fecha Cumplido": "01/08/2026", "Fecha Limite": "01/02/2027", "Saldo Pendiente": "82000.00"},
        {"Numero Permiso": "26001EC01003322D", "Banco": "Macro", "Fecha Cumplido": "01/09/2026", "Fecha Limite": "15/09/2026", "Saldo Pendiente": "30000.00"}
    ]
    return pd.DataFrame(data)

def get_demo_sepaimpo_data():
    data = [
        {"Numero Despacho": "26001IC04001234A", "Banco": "Santander", "Concepto": "B05", "Fecha Pago": "01/06/2026", "Fecha Limite": "01/09/2026", "Monto Pendiente": "50000.00"},
        {"Numero Despacho": "26001IC04008877B", "Banco": "Galicia", "Concepto": "B12", "Fecha Pago": "15/02/2026", "Fecha Limite": "15/02/2027", "Monto Pendiente": "120000.00"},
        {"Numero Despacho": "26001IC04009944C", "Banco": "ICBC", "Concepto": "B05", "Fecha Pago": "10/07/2026", "Fecha Limite": "10/10/2026", "Monto Pendiente": "25000.00"}
    ]
    return pd.DataFrame(data)
