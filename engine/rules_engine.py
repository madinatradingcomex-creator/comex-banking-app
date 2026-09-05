from datetime import datetime, timedelta, date
from engine.concepts_db import CONCEPTOS_SERIE_B, CONCEPTOS_SERIE_S, CATEGORIAS_NCM_EXPO

def evaluate_semaphore(days_remaining):
    if days_remaining < 0:
        return {
            "estado": "VENCIDO / EN MORA",
            "color": "🔴",
            "nivel": "CRITICO",
            "accion": "🚨 ACCIÓN URGENTE: Presentar legajo de descargo o regularización para evitar reporte al BCRA y sumario penal cambiario (Ley 19.359)."
        }
    elif days_remaining <= 15:
        return {
            "estado": "RIESGO ALTO (< 15 días)",
            "color": "🔴",
            "nivel": "ALTO",
            "accion": "⚠️ Vencimiento inminente: Gestionar de inmediato la prórroga bancaria o la afectación de fondos."
        }
    elif days_remaining <= 35:
        return {
            "estado": "ATENCIÓN / PREVENTIVO",
            "color": "🟡",
            "nivel": "MEDIO",
            "accion": "⏳ Plazo en cuenta regresiva: Reclamar pago al cliente exterior o solicitar documentación de embarque."
        }
    else:
        return {
            "estado": "EN REGLA / EN PLAZO",
            "color": "🟢",
            "nivel": "NORMAL",
            "accion": "✅ Operación en curso regular dentro de los plazos normativos."
        }

def calculate_expo_deadline(cumplido_date, category_key="MANUFACTURAS_MOI_PYME", is_related=False):
    if is_related:
        base_days = CATEGORIAS_NCM_EXPO["EMPRESAS_VINCULADAS"]["plazo_dias"]
    else:
        base_days = CATEGORIAS_NCM_EXPO.get(category_key, {}).get("plazo_dias", 365)
    
    deadline = cumplido_date + timedelta(days=base_days)
    today = datetime.now().date()
    if isinstance(deadline, datetime):
        deadline = deadline.date()
    days_remaining = (deadline - today).days
    
    semaphore = evaluate_semaphore(days_remaining)
    return {
        "fecha_cumplido": cumplido_date,
        "plazo_dias_aplicado": base_days,
        "fecha_limite": deadline,
        "dias_restantes": days_remaining,
        "semaforo": semaphore
    }

def calculate_sepaimpo_deadline(payment_date, concept_code="B05"):
    concept_info = CONCEPTOS_SERIE_B.get(concept_code, {})
    days = concept_info.get("plazo_demostracion_dias", 90)
    
    deadline = payment_date + timedelta(days=days)
    today = datetime.now().date()
    if isinstance(deadline, datetime):
        deadline = deadline.date()
    days_remaining = (deadline - today).days
    
    semaphore = evaluate_semaphore(days_remaining)
    return {
        "fecha_pago": payment_date,
        "concepto": concept_code,
        "plazo_dias_otorgado": days,
        "fecha_limite_demostracion": deadline,
        "dias_restantes": days_remaining,
        "semaforo": semaphore
    }

def validate_candados_access(operated_mep_ccl_last_90d=False, liquid_assets_over_100k=False, com_6401_ok=True):
    inconsistencias = []
    
    if operated_mep_ccl_last_90d:
        inconsistencias.append({
            "candado": "TÍTULOS VALORES (MEP / CCL)",
            "estado": "BLOQUEANTE",
            "detalle": "Registra operaciones con títulos valores en los últimos 90/180 días. Inhabilitado para comprar divisas en el MLC (Com. 'A' 7030 y compl.)."
        })
        
    if liquid_assets_over_100k:
        inconsistencias.append({
            "candado": "ACTIVOS EXTERNOS LÍQUIDOS",
            "estado": "CONDICIONANTE",
            "detalle": "Posee más de USD 100.000 líquidos en el exterior. Debe aplicar dichos fondos al pago antes de solicitar divisas al BCRA."
        })
        
    if not com_6401_ok:
        inconsistencias.append({
            "candado": "RELEVAMIENTO ACTIVOS Y PASIVOS (COM. A 6401)",
            "estado": "BLOQUEANTE",
            "detalle": "Falta presentación de trimestres vencidos ante el BCRA. El banco no cursará la transferencia hasta regularizar la presentación."
        })
        
    return {
        "apto_para_acceder_mlc": len(inconsistencias) == 0,
        "cantidad_inconsistencias": len(inconsistencias),
        "inconsistencias": inconsistencias
    }
