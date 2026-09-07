from datetime import datetime
import io

def sanitize_pdf_text(text):
    """
    Sanitiza el texto eliminando emojis y caracteres especiales incompatibles con
    fuentes estándar de FPDF (Latin-1 / ISO-8859-1), reemplazándolos por etiquetas
    legibles y profesionales.
    """
    if not text:
        return ""
    if not isinstance(text, str):
        text = str(text)
        
    replacements = {
        # Semáforos y estados
        "🟢": "[VIABLE]",
        "🟡": "[OBSERVADO]",
        "🔴": "[BLOQUEADO]",
        "🚨": "[ALERTA]",
        "⚠️": "[ADVERTENCIA]",
        "✅": "[ADJUNTADO]",
        "⏳": "[PENDIENTE]",
        "📌": "[*]",
        "📖": "[NORMATIVA]",
        "📂": "[LEGAJO]",
        "🏭": "[MOI/PyME]",
        "🥩": "[ALIMENTOS]",
        "🌾": "[GRANOS]",
        "🔗": "[VINCULADAS]",
        "⚖️": "[DICTAMEN]",
        "🚢": "[EXPO]",
        "📦": "[IMPO]",
        "🔒": "[CANDADO]",
        "🛡️": "[SEGURIDAD]",
        "🧾": "[FACTURA]",
        "📑": "[PERMISO]",
        "📝": "[REGISTRO]",
        "🏢": "[EMPRESA]",
        "🏦": "[BANCO]",
        "🏷️": "[DOC]",
        "❌": "[NO]",
        "✔️": "[SI]",
        
        # Símbolos tipográficos
        "—": "-",
        "–": "-",
        "“": '"',
        "”": '"',
        "‘": "'",
        "’": "'",
        "«": '"',
        "»": '"',
        "…": "...",
        "°": "o.",
        "º": "o.",
        "ª": "a.",
        "•": "*",
        "·": "*",
        "\u200b": "",
        "\xa0": " "
    }
    
    for k, v in replacements.items():
        text = text.replace(k, v)
        
    # latin-1 replace convierte cualquier carácter Unicode restante a '?'
    return text.encode("latin-1", "replace").decode("latin-1")


def generate_text_document(title, ref_text, body_paragraphs, company_name, cuit, bank_name, signer_name, signer_role):
    today_str = datetime.now().strftime("%d de %B de %Y")
    text = f"""================================================================================
{title}
================================================================================
Buenos Aires, {today_str}

Senores de la Mesa de Comercio Exterior y Cambios
{bank_name.upper()}
Presente.-

REF: {ref_text}

"""
    for p in body_paragraphs:
        text += f"{p}\n\n"
        
    text += f"""Sin otro particular, saluda a Uds. muy atentamente,


________________________________________
{signer_name} - {signer_role}
{company_name} (CUIT: {cuit})
================================================================================
"""
    return text.encode("utf-8")


def build_pdf_document(title, ref_text, body_paragraphs, company_name, cuit, bank_name, signer_name, signer_role):
    title = sanitize_pdf_text(title)
    ref_text = sanitize_pdf_text(ref_text)
    company_name = sanitize_pdf_text(company_name)
    cuit = sanitize_pdf_text(cuit)
    bank_name = sanitize_pdf_text(bank_name)
    signer_name = sanitize_pdf_text(signer_name)
    signer_role = sanitize_pdf_text(signer_role)
    clean_paragraphs = [sanitize_pdf_text(p) for p in body_paragraphs]
    
    try:
        from fpdf import FPDF
        
        class ComexPDF(FPDF):
            def __init__(self, doc_header_title="CONSULTORIA BANCARIA Y CAMBIARIA", *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.doc_header_title = sanitize_pdf_text(doc_header_title)

            def header(self):
                self.set_font("Helvetica", "B", 10)
                self.set_text_color(30, 41, 59)
                self.cell(0, 7, self.doc_header_title, border=False, align="R")
                self.ln(2)
                self.set_draw_color(203, 213, 225)
                self.line(10, 16, 200, 16)
                self.ln(8)

            def footer(self):
                self.set_y(-18)
                self.set_font("Helvetica", "I", 8)
                self.set_text_color(148, 163, 184)
                self.cell(0, 10, f"Consultoria Bancaria y Cambiaria | BCRA & ARCA | Pagina {self.page_no()}", align="C")

        pdf = ComexPDF(orientation="P", unit="mm", format="A4", doc_header_title=title)
        pdf.set_auto_page_break(auto=True, margin=20)
        pdf.add_page()
        
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(30, 41, 59)
        today_str = datetime.now().strftime("%d de %B de %Y")
        pdf.cell(0, 6, f"Buenos Aires, {today_str}", align="R")
        pdf.ln(6)
        
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(0, 5, "Senores de la Mesa de Comercio Exterior y Cambios", ln=True)
        pdf.cell(0, 5, f"{bank_name.upper()}", ln=True)
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(0, 5, "Presente.-", ln=True)
        pdf.ln(5)
        
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_fill_color(241, 245, 249)
        pdf.multi_cell(0, 7, f"REF: {ref_text}", fill=True, border="L")
        pdf.ln(5)
        
        pdf.set_font("Helvetica", "", 9.5)
        for p in clean_paragraphs:
            pdf.multi_cell(0, 5.5, p)
            pdf.ln(3.5)
            
        pdf.ln(6)
        pdf.multi_cell(0, 5.5, "Sin otro particular, saluda a Uds. muy atentamente,")
        pdf.ln(14)
        
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(90, 5, "________________________________________", ln=True)
        pdf.cell(90, 5, f"{signer_name} - {signer_role}", ln=True)
        pdf.cell(90, 5, f"{company_name} (CUIT: {cuit})", ln=True)
        
        return bytes(pdf.output()), "pdf"
    except Exception as e:
        print("FPDF Error (attempting fallback):", e)
        try:
            from fpdf import FPDF
            fallback_pdf = FPDF()
            fallback_pdf.set_auto_page_break(auto=True, margin=20)
            fallback_pdf.add_page()
            fallback_pdf.set_font("Helvetica", "B", 13)
            fallback_pdf.cell(0, 10, title, ln=True)
            fallback_pdf.set_font("Helvetica", "B", 10)
            fallback_pdf.multi_cell(0, 6, f"REF: {ref_text}")
            fallback_pdf.ln(4)
            fallback_pdf.set_font("Helvetica", "", 9.5)
            for p in clean_paragraphs:
                fallback_pdf.multi_cell(0, 5.5, p)
                fallback_pdf.ln(3)
            fallback_pdf.ln(6)
            fallback_pdf.set_font("Helvetica", "B", 10)
            fallback_pdf.cell(0, 5, f"{signer_name} - {signer_role} | {company_name} (CUIT: {cuit})", ln=True)
            return bytes(fallback_pdf.output()), "pdf"
        except Exception as e2:
            print("Fallback PDF error:", e2)
            return generate_text_document(title, ref_text, clean_paragraphs, company_name, cuit, bank_name, signer_name, signer_role), "txt"


def generate_prorroga_sepaimpo_pdf(company_name, cuit, bank_name, op_number, amount_usd, bl_number, reason_text, signer_name, signer_role):
    ref = f"SEPAIMPO - Solicitud de Prorroga de Plazo de Demostracion de Ingreso Aduanero | Op. N° {op_number}"
    paragraphs = [
        f"Por la presente nos dirigimos a Uds. en nuestro caracter de titulares de la razon social {company_name}, CUIT {cuit}, con relacion al pago de importacion de bienes cursado oportunamente bajo el concepto BCRA B05 por el importe de USD {amount_usd:,.2f} mediante la operacion de referencia.",
        f"Al respecto, venimos a solicitar formalmente la EXTENSION DEL PLAZO DE DEMOSTRACION DEL REGISTRO DE INGRESO ADUANERO ante el Banco Central de la Republica Argentina, motivado en demoras logisticas y de navegacion internacional ajenas a nuestra voluntad, segun se detalla a continuacion:",
        f"MOTIVO: {reason_text}",
        f"A tal efecto, adjuntamos como constancia documental copia del Conocimiento de Embarque / Documento de Transporte Internacional N° {bl_number} ('Shipped on Board'), acreditando que la mercaderia se encuentra en transito con destino final a la Republica Argentina.",
        "Declaramos bajo juramento que los fondos transferidos se encuentran efectivamente afectados a la importacion de los bienes consignados y solicitamos la actualizacion correspondiente en el sistema SEPAIMPO del BCRA para evitar observaciones registrales."
    ]
    data, _ = build_pdf_document("PRORROGA SEPAIMPO", ref, paragraphs, company_name, cuit, bank_name, signer_name, signer_role)
    return data


def generate_descargo_mermas_pdf(company_name, cuit, bank_name, pe_number, original_fob, amount_received, nc_number, survey_number, signer_name, signer_role):
    diff = original_fob - amount_received
    ref = f"SECOEXPO - Solicitud de Cierre y Afectacion por Mermas / Descuentos Comerciales | PE N° {pe_number}"
    paragraphs = [
        f"Por la presente nos dirigimos a Uds. en relacion al Permiso de Embarque cumplido N° {pe_number}, oficializado a nombre de {company_name} (CUIT {cuit}) con un valor FOB aduanero registrado de USD {original_fob:,.2f}.",
        f"Informamos que el cobro liquidado mediante boleto de cambio ascendio a la suma de USD {amount_received:,.2f}, registrandose una diferencia de USD {diff:,.2f} originada en mermas, averias y descuentos comerciales justificados conforme las previsiones normativas del Texto Ordenado de Exterior y Cambios del BCRA.",
        f"A fin de proceder al CIERRE DEFINITIVO DEL PERMISO DE EMBARQUE EN SECOEXPO por el 100% de su valor, adjuntamos al presente legajo la siguiente documentacion probatoria:",
        f"1. Nota de Credito Comercial 'E' N° {nc_number} emitida a traves de ARCA.\n2. Certificado de Peritaje / Survey Report en puerto de destino N° {survey_number}.\n3. Correspondencia comercial probatoria del reclamo de calidad/merma.",
        "Solicitamos a esa entidad bancaria tenga a bien registrar la afectacion del ajuste sobre el valor FOB y dar por cumplida la obligacion de liquidacion de divisas en el sistema del BCRA."
    ]
    data, _ = build_pdf_document("DESCARGO MERMAS SECOEXPO", ref, paragraphs, company_name, cuit, bank_name, signer_name, signer_role)
    return data


def generate_zona_primaria_pdf(company_name, cuit, bank_name, pe_number, buyer_name, local_invoice, signer_name, signer_role):
    ref = f"SECOEXPO - Solicitud de Desafectacion por Venta en Zona Primaria Aduanera | PE N° {pe_number}"
    paragraphs = [
        f"Nos dirigimos a Uds. con relacion al Permiso de Embarque N° {pe_number} registrado en el sistema SECOEXPO a nombre de {company_name} (CUIT {cuit}).",
        f"Venimos a poner en vuestro conocimiento que la mercaderia amparada en dicha destinacion aduanera fue objeto de TRANSFERENCIA Y CESION DE DERECHOS EN ZONA PRIMARIA ADUANERA con anterioridad a su libramiento/embarque efectivo, habiendo sido adquirida en plaza local por la firma {buyer_name}.",
        "Por tal motivo, la operacion fue facturada y cancelada localmente en moneda nacional, no correspondiendo el ingreso de divisas desde el exterior a traves del Mercado Libre de Cambios.",
        f"Acompanamos a la presente:\n1. Copia del Contrato de Cesion de Derechos Aduaneros con certificacion de firmas.\n2. Factura comercial local N° {local_invoice}.\n3. Constancia de rectificacion / anulacion aduanera en el Sistema Informatico Malvina (SIM).",
        "Por todo lo expuesto, solicitamos se registre la desafectacion de la obligacion de ingreso de divisas y el cierre del mencionado Permiso de Embarque en el sistema SECOEXPO del BCRA."
    ]
    data, _ = build_pdf_document("VENTA ZONA PRIMARIA", ref, paragraphs, company_name, cuit, bank_name, signer_name, signer_role)
    return data


def generate_imputacion_b02_pdf(company_name, cuit, bank_name, pe_number, b02_boleto, amount_usd, signer_name, signer_role):
    ref = f"SECOEXPO - Instruccion de Afectacion de Permiso de Embarque a Boleto de Anticipo B02 | PE N° {pe_number}"
    paragraphs = [
        f"Por medio de la presente, {company_name} (CUIT {cuit}) solicita a esa entidad bancaria tenga a bien proceder a la AFECTACION Y CANCELACION del Permiso de Embarque cumplido N° {pe_number} por el importe de USD {amount_usd:,.2f}.",
        f"Dicho Permiso de Embarque debe ser imputado al Boleto de Compra de Cambio liquidado con anterioridad bajo el concepto BCRA B02 (Cobro anticipado de exportaciones de bienes) con numero de operacion / boleto N° {b02_boleto}.",
        "Adjuntamos al presente pedido copia del Permiso de Embarque cumplido en el SIM, Factura Comercial 'E' y Documento de Transporte Internacional.",
        "Solicitamos se asiente la imputacion en el sistema SECOEXPO del BCRA para cancelar el saldo pendiente a la fecha."
    ]
    data, _ = build_pdf_document("IMPUTACION B02", ref, paragraphs, company_name, cuit, bank_name, signer_name, signer_role)
    return data


def generate_dictamen_tecnico_pdf(
    company_name,
    cuit,
    operation_type,
    diagnosis_data,
    signer_name="Consultor Responsable",
    signer_role="Asesor Normativo Comex",
    attached_files=None,
    declared_documents=None
):
    """
    Genera el Dictamen Técnico Oficial de Encuadre Normativo y Viabilidad Cambiaria en formato PDF.
    Contempla operaciones complejas y masivas con múltiples Permisos de Embarque, Facturas 'E',
    Documentos de Transporte, Despachos SIM y Declaraciones SEDI.
    """
    ref = f"DICTAMEN TECNICO DE ENCUADRE NORMATIVO Y FACTIBILIDAD CAMBIARIA ({operation_type.upper()})"
    
    monto_val = diagnosis_data.get("monto_usd", 0.0)
    concepto_txt = diagnosis_data.get("nombre_concepto", "N/A")
    fundamento = diagnosis_data.get("fundamento_normativo", "")
    semaforo = diagnosis_data.get("semaforo", {})
    estado_sem = f"{semaforo.get('color', '')} {semaforo.get('estado', '')}"
    
    paragraphs = []
    
    # 0. Encabezado Operativo
    paragraphs.append(
        f"EMPRESA TITULAR: {company_name} | CUIT: {cuit}\n"
        f"TIPO DE OPERACION EVALUADA: {operation_type.upper()} | MONTO TOTAL EVALUADO: USD {monto_val:,.2f}"
    )
    
    # Detalle de Documentación Declarada en Operaciones Consolidadas/Masivas
    if declared_documents:
        txt_decl = "CONSOLIDACION OPERATIVA - DOCUMENTOS DECLARADOS:\n"
        for cat_label, items in declared_documents.items():
            if items:
                if isinstance(items, list):
                    items_str = ", ".join(str(it) for it in items)
                    txt_decl += f"- {cat_label} ({len(items)} declarados): {items_str}\n"
                else:
                    txt_decl += f"- {cat_label}: {items}\n"
        paragraphs.append(txt_decl)
    
    # 1. Encuadre Cambiario y Plazos
    pinfo = diagnosis_data.get("plazo_info", {})
    plazo_txt = ""
    if pinfo:
        f_lim = pinfo.get("fecha_limite")
        f_lim_str = f_lim.strftime("%d/%m/%Y") if hasattr(f_lim, "strftime") else str(f_lim)
        plazo_txt = f"\nPlazo Legal Exigible: {pinfo.get('dias', 0)} dias corridos | Fecha Limite Exigible: {f_lim_str}"
    elif diagnosis_data.get("plazo_demostracion_dias", 0) > 0:
        plazo_txt = f"\nPlazo de Demostracion Aduanera (SEPAIMPO): {diagnosis_data.get('plazo_demostracion_dias')} dias corridos"
        
    paragraphs.append(
        f"1. ENCUADRE CAMBIARIO DICTAMINADO (BCRA):\n"
        f"Concepto Oficial Aplicable: {concepto_txt}{plazo_txt}\n\n"
        f"Fundamentacion Normativa (Com. 'A' 6808 / SECOEXPO / SEPAIMPO):\n{fundamento}"
    )
    
    # 2. Evaluación de Viabilidad y Candados
    paragraphs.append(
        f"2. EVALUACION DE VIABILIDAD Y CANDADOS REGULATORIOS:\n"
        f"Dictamen de Factibilidad: {estado_sem}"
    )
    
    bloqueos = diagnosis_data.get("bloqueos", [])
    if bloqueos:
        txt_b = "BLOQUEOS NORMATIVOS DETECTADOS:\n"
        for b in bloqueos:
            txt_b += f"- [{b.get('origen', 'Normativa')}]: {b.get('detalle', '')}\n"
        paragraphs.append(txt_b)
        
    observaciones = diagnosis_data.get("observaciones", [])
    if observaciones:
        txt_o = "OBSERVACIONES Y RECOMENDACIONES DE ENCUADRE:\n"
        for o in observaciones:
            txt_o += f"- [{o.get('origen', 'Normativa')}]: {o.get('detalle', '')}\n"
        paragraphs.append(txt_o)
        
    checklist = diagnosis_data.get("checklist_documental", [])
    if checklist:
        txt_c = "3. CHECKLIST DOCUMENTAL EXIGIBLE POR LA ENTIDAD BANCARIA:\n"
        for idx, doc in enumerate(checklist, 1):
            txt_c += f"{idx}. {doc}\n"
        paragraphs.append(txt_c)
        
    # 4. Estado del Legajo Digital y Comprobantes Adjuntados (Soporte Masivo)
    if attached_files and len(attached_files) > 0:
        txt_att = "4. ESTADO DEL LEGAJO DIGITAL Y COMPROBANTES ADJUNTADOS:\n"
        for idx, item in enumerate(attached_files, 1):
            cat = item.get("name", f"Documento {idx}")
            is_att = item.get("attached", False)
            count = item.get("count", 1 if is_att else 0)
            exp = item.get("expected", 1)
            fn = item.get("filename", "")
            
            if is_att:
                status_str = f"[ADJUNTADO Y VERIFICADO: {count} archivo(s)]" if count > 1 else "[ADJUNTADO Y VERIFICADO]"
                files_str = f" | Archivo(s): {fn}" if fn else ""
                txt_att += f"{idx}. {cat}: {status_str}{files_str}\n"
            else:
                txt_att += f"{idx}. {cat}: [PENDIENTE DE CARGA]\n"
        paragraphs.append(txt_att)
        
    paragraphs.append(
        "CONCLUSION:\n"
        "El presente informe tecnico constituye un dictamen profesional emitido conforme a las normas "
        "del Texto Ordenado de Exterior y Cambios del Banco Central de la Republica Argentina (Comunicacion 'A' 6808 "
        "y complementarias) y disposiciones vigentes de ARCA a la fecha de emision. "
        "Se instruye a la empresa archivar el presente dictamen junto al legajo integral de la operacion "
        "como respaldo ante auditorias bancarias o requerimientos de la autoridad de control cambiario."
    )
    
    data, _ = build_pdf_document(
        "DICTAMEN TECNICO COMEX",
        ref,
        paragraphs,
        company_name,
        cuit,
        "MESA DE COMERCIO EXTERIOR / LEGAJO BANCARIO",
        signer_name,
        signer_role
    )
    return data
