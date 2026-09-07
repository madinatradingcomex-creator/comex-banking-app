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


def diagnose_import_operation(
    estado_mercaderia,
    docs_disponibles,
    concepto_propuesto,
    monto_usd,
    fecha_operacion,
    empresa_mep_ccl,
    socios_mep_ccl,
    activos_externos_100k,
    arca_cuit_activa,
    sedi_estado="SALIDA / APROBADA",
    es_bien_capital=False
):
    """
    Ejecuta el análisis técnico de encuadre normativo y validación de candados (BCRA + ARCA)
    para una operación de importación de bienes.
    """
    bloqueos = []
    observaciones = []
    
    # 1. Auditoría de Candados Cruzados (Empresa + Dueños/Socios)
    if empresa_mep_ccl:
        bloqueos.append({
            "origen": "BCRA - Mercado Financiero (Empresa)",
            "detalle": "La empresa registra operaciones con títulos valores (MEP / CCL / CEDEARs / Canje) en los últimos 90/180 días. Inhabilitada para cursar pagos con acceso al MLC (Comunicación 'A' 7030 y modificatorias)."
        })
        
    if socios_mep_ccl:
        bloqueos.append({
            "origen": "BCRA - Candado Cruzado Directores/Accionistas",
            "detalle": "Accionistas directos, directores o controlantes de la sociedad operaron títulos valores en los últimos 90/180 días. La normativa del BCRA (Com. 'A' 7030 punto 2 y modif.) bloquea el acceso de la persona jurídica si sus personas humanas vinculadas operaron en el mercado bursátil."
        })
        
    if not arca_cuit_activa:
        bloqueos.append({
            "origen": "ARCA / AFIP - Estado Tributario",
            "detalle": "La CUIT de la empresa no se encuentra en estado plenamente activo o presenta inconsistencias registrales/fiscales ante ARCA."
        })
        
    if sedi_estado == "BLOQUEADA / OBSERVADA":
        bloqueos.append({
            "origen": "ARCA / Aduana - Estado SEDI",
            "detalle": "La declaración SEDI presenta bloqueos u observaciones de organismos intervinientes (ej. Bloqueo F49). El banco no puede procesar giros al exterior hasta su levantamiento."
        })
    elif sedi_estado == "OFICIALIZADA":
        observaciones.append({
            "origen": "ARCA / Aduana - Estado SEDI",
            "detalle": "La SEDI está en estado 'Oficializada' pero aún no alcanzó estado 'SALIDA'. El banco exigirá estado SALIDA definitivo para ejecutar el giro."
        })
        
    if activos_externos_100k:
        observaciones.append({
            "origen": "BCRA - Activos Externos Líquidos",
            "detalle": "La empresa o el grupo poseen más de USD 100.000 disponibles en el exterior. Conforme Com. 'A' 7030, debe comprometerse a pagar con dichos fondos o encuadrar en alguna de las excepciones reglamentarias."
        })
        
    # 2. Análisis de Encuadre Normativo Cambiario
    if estado_mercaderia == "NO_EMBARCADA":
        concepto_correcto = "B12" if es_bien_capital else "B05"
        nombre_concepto = "B12 - Pago anticipado de bienes de capital (BK)" if es_bien_capital else "B05 - Pago anticipado de importaciones de bienes"
        plazo_demostracion = 270 if es_bien_capital else 90
        
        if concepto_propuesto in ["B06", "B07"]:
            observaciones.append({
                "origen": "Inconsistencia de Concepto Propuesto",
                "detalle": f"El cliente o banco sugirió usar '{concepto_propuesto}'. Es técnicamente INVIABLE porque la mercadería aún no cuenta con documento de transporte emitido ni ingreso aduanero. El encuadre legal obligado es {concepto_correcto}."
            })
            
        fundamento = (
            f"Al tratarse de una transferencia al exterior previa al embarque y al despacho a plaza, "
            f"el encuadre legal obligatorio conforme Texto Ordenado de Exterior y Cambios es {concepto_correcto}. "
            f"La empresa asume la obligación de demostrar el registro de ingreso aduanero definitivo (Despacho SIM) "
            f"dentro de los {plazo_demostracion} días corridos posteriores a la fecha de acceso al mercado para no quedar en mora en SEPAIMPO."
        )
        docs_necesarios = [
            "Factura Proforma u Orden de Compra formal emitida por el proveedor del exterior.",
            "Declaración Jurada de Acceso al MLC (Candados de Títulos Valores Empresa + Declaraciones Juradas de los Socios/Directores).",
            "SEDI en estado SALIDA definitiva.",
            "Certificación contable de no tenencia de activos externos > USD 100k (si aplica).",
            "Contrato comercial o especificaciones técnicas de maquinaria (si es Bien de Capital B12)."
        ]
        
    elif estado_mercaderia == "EN_VIAJE":
        concepto_correcto = "B07"
        nombre_concepto = "B07 - Pago a la vista de importaciones de bienes"
        plazo_demostracion = 90
        
        if concepto_propuesto in ["B05", "B06"]:
            observaciones.append({
                "origen": "Inconsistencia de Concepto Propuesto",
                "detalle": f"Habiéndose embarcado la mercadería con documento de transporte emitido, el encuadre exacto es B07 (A la vista). El código B05 no corresponde porque ya fue embarcada, y B06 no corresponde porque aún no fue nacionalizada."
            })
            
        fundamento = (
            f"Dado que la mercadería ya fue embarcada en el país de origen y se encuentra respaldada por documento de transporte "
            f"internacional (Bill of Lading, Carta de Porte CRT o Guía Aérea), corresponde cursar la operación bajo el concepto {concepto_correcto}. "
            f"Se dispone de un plazo de {plazo_demostracion} días corridos para nacionalizar la mercadería y presentar el Despacho SIM ante el banco."
        )
        docs_necesarios = [
            "Documento de Transporte Internacional (B/L, CRT o AWB original o copia certificada).",
            "Factura Comercial definitiva del proveedor exterior.",
            "SEDI en estado SALIDA.",
            "Declaración Jurada de Acceso al MLC (Empresa y Socios)."
        ]
        
    else:  # NACIONALIZADA
        concepto_correcto = "B06"
        nombre_concepto = "B06 - Pago diferido de importaciones de bienes"
        plazo_demostracion = 0
        
        if concepto_propuesto in ["B05", "B07"]:
            observaciones.append({
                "origen": "Inconsistencia de Concepto Propuesto",
                "detalle": f"La mercadería ya se encuentra nacionalizada en el país con registro aduanero oficializado. No debe cursarse como anticipo ni vista; el concepto correspondiente es B06 (Diferido)."
            })
            
        fundamento = (
            f"Habiéndose nacionalizado la mercadería con registro aduanero oficializado en el Sistema Informático Malvina (SIM), "
            f"la operación califica como Pago Diferido ({concepto_correcto}). El pago cancela la obligación aduanera "
            f"y no genera deudas pendientes de demostración en SEPAIMPO."
        )
        docs_necesarios = [
            "Despacho de Importación SIM oficializado y cancelado en Aduana.",
            "Factura Comercial definitiva.",
            "Documento de Transporte Internacional vinculado al despacho.",
            "Declaración Jurada de Acceso al MLC."
        ]
        
    # 3. Determinación de Viabilidad y Semáforo
    if len(bloqueos) > 0:
        semaforo = {
            "estado": "BLOQUEADO POR NORMATIVA",
            "color": "🔴",
            "nivel": "CRITICO",
            "resumen": "La operación no puede cursarse actualmente por el Mercado Libre de Cambios oficial. Existen bloqueos normativos que generarán rechazo bancario o sumario penal cambiario."
        }
    elif len(observaciones) > 0:
        semaforo = {
            "estado": "OBSERVADO / VIABLE CONDICIONADO",
            "color": "🟡",
            "nivel": "MEDIO",
            "resumen": "La operación es factible siempre que se subsanen las observaciones documentales y se encuadre en el concepto correcto."
        }
    else:
        semaforo = {
            "estado": "OPERACIÓN VIABLE EN EL MLC",
            "color": "🟢",
            "nivel": "NORMAL",
            "resumen": "La operación cumple plenamente con las exigencias del BCRA y ARCA. Lista para presentar legajo ante la mesa de Comex del banco."
        }
        
    return {
        "tipo_operacion": "IMPORTACION",
        "monto_usd": monto_usd,
        "fecha_operacion": fecha_operacion,
        "concepto_correcto": concepto_correcto,
        "nombre_concepto": nombre_concepto,
        "plazo_demostracion_dias": plazo_demostracion,
        "fundamento_normativo": fundamento,
        "semaforo": semaforo,
        "bloqueos": bloqueos,
        "observaciones": observaciones,
        "checklist_documental": docs_necesarios
    }


def diagnose_export_operation(
    momento_fondos,
    docs_disponibles,
    concepto_propuesto,
    monto_usd,
    fecha_cumplido_o_ingreso,
    categoria_ncm_key="MANUFACTURAS_MOI_PYME",
    is_related=False
):
    """
    Ejecuta el análisis técnico de encuadre normativo y compromisos SECOEXPO
    para una operación de exportación de bienes.
    """
    bloqueos = []
    observaciones = []
    
    if momento_fondos == "FONDOS_ANTES_DE_EMBARCAR":
        concepto_correcto = "B02"
        nombre_concepto = "B02 - Cobros anticipados de exportaciones de bienes"
        
        if concepto_propuesto == "B01":
            observaciones.append({
                "origen": "🚨 ERROR GRAVE EVITADO: Intento de uso de B01",
                "detalle": "El cliente o banco sugirió usar B01. Esto causaría un RECHAZO BANCARIO inmediato o apertura errónea en SECOEXPO porque B01 exige Permiso de Embarque cumplido preexistente. El encuadre normativo obligado es B02."
            })
            
        fundamento = (
            "Los fondos del comprador exterior ingresan al país con anterioridad al embarque de la mercadería. "
            "Conforme el Texto Ordenado de Exterior y Cambios y la Comunicación 'A' 6808 del BCRA (Régimen Informativo SECOEXPO), "
            "el único concepto cambiario aplicable es B02 (Anticipo de Exportación). "
            "Esta operación genera la apertura formal de una obligación en el sistema SECOEXPO a cargo de la entidad financiera nominada: "
            "la empresa exportadora cuenta con un plazo máximo legal de hasta 365 días corridos para realizar el embarque y, "
            "una vez cumplido el Permiso de Embarque en Aduana (SIM), deberá presentar formalmente ante este banco la Nota de Imputación "
            "del Permiso al Boleto de Anticipo B02 para cancelar el saldo y evitar ser intimada bajo apercibimiento del Régimen Penal Cambiario (Ley 19.359)."
        )
        plazo_embarque_dias = 365
        fecha_limite = fecha_cumplido_o_ingreso + timedelta(days=plazo_embarque_dias)
        
        docs_necesarios = [
            "Factura Proforma u Orden de Compra emitida al cliente exterior.",
            "Contrato comercial, orden de pedido formal o intercambio de correos que acredite la relación comercial.",
            "Instrucción de liquidación al banco especificando Concepto B02.",
            "Boleto de liquidación oficial de divisas emitido por la entidad bancaria (a archivar para futura imputación)."
        ]
        
        semaforo = {
            "estado": "VIABLE CON COMPROMISO POSTERIOR SECOEXPO (COM. A 6808)",
            "color": "🟢",
            "nivel": "NORMAL",
            "resumen": "Operación liquidable bajo B02. Se activa seguimiento normativo en SECOEXPO (Com. 'A' 6808) para futuro embarque e imputación de Permiso aduanero."
        }
        
        plazo_info = {
            "tipo_plazo": "Plazo máximo para cumplir embarque e imputar",
            "dias": plazo_embarque_dias,
            "fecha_limite": fecha_limite
        }
        
    else:  # FONDOS_DESPUES_DE_EMBARCAR
        concepto_correcto = "B01"
        nombre_concepto = "B01 - Cobros de exportaciones de bienes"
        
        if concepto_propuesto == "B02":
            observaciones.append({
                "origen": "Inconsistencia de Concepto",
                "detalle": "Habiéndose ya cumplido el embarque en Aduana, no debe utilizarse B02 (Anticipo) sino B01 (Cobro). El concepto B01 imputará y cancelará el Permiso en SECOEXPO conforme Com. 'A' 6808."
            })
            
        # Cálculo de plazos por NCM
        plazo_calc = calculate_expo_deadline(fecha_cumplido_o_ingreso, categoria_ncm_key, is_related)
        
        fundamento = (
            f"Habiéndose cumplido el embarque de los bienes con registro aduanero formal en el SIM, el ingreso de divisas debe "
            f"liquidarse bajo el concepto B01 conforme lo estipulado por la Comunicación 'A' 6808 y el Texto Ordenado de Exterior y Cambios del BCRA. "
            f"La liquidación bancaria imputará y cancelará el Permiso de Embarque en el sistema de seguimiento SECOEXPO. "
            f"El plazo legal exigible según la posición arancelaria NCM y la condición de venta es de {plazo_calc['plazo_dias_aplicado']} días "
            f"corridos contados desde la fecha del cumplido aduanero. Su vencimiento sin liquidación obligará a la entidad nominada a intimar "
            f"a la empresa y reportarla ante la Gerencia Principal de Control Cambiario del BCRA bajo el Régimen Penal Cambiario (Com. 'A' 6808)."
        )
        
        docs_necesarios = [
            "Permiso de Embarque (PE) cumplido en el Sistema Informático Malvina (SIM).",
            "Factura de Exportación Electrónica 'E' (ARCA / WSFEX).",
            "Documento de Transporte Internacional (Bill of Lading, CRT o Guía Aérea).",
            "Instrucción de liquidación indicando N° de Permiso de Embarque para su imputación directa."
        ]
        
        semaforo = plazo_calc["semaforo"]
        plazo_info = {
            "tipo_plazo": "Plazo legal de liquidación desde cumplido aduanero",
            "dias": plazo_calc["plazo_dias_aplicado"],
            "fecha_limite": plazo_calc["fecha_limite"],
            "dias_restantes": plazo_calc["dias_restantes"]
        }
        
    return {
        "tipo_operacion": "EXPORTACION",
        "monto_usd": monto_usd,
        "fecha_base": fecha_cumplido_o_ingreso,
        "concepto_correcto": concepto_correcto,
        "nombre_concepto": nombre_concepto,
        "fundamento_normativo": fundamento,
        "plazo_info": plazo_info,
        "semaforo": semaforo,
        "bloqueos": bloqueos,
        "observaciones": observaciones,
        "checklist_documental": docs_necesarios
    }

