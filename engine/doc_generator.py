from datetime import datetime
import io

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
    try:
        from fpdf import FPDF
        
        class ComexPDF(FPDF):
            def header(self):
                self.set_font("Helvetica", "B", 11)
                self.set_text_color(15, 23, 42)
                self.cell(0, 8, "NOTA FORMAL DE COMERCIO EXTERIOR Y CAMBIOS", border=False, align="R")
                self.ln(4)
                self.set_draw_color(203, 213, 225)
                self.line(10, 18, 200, 18)
                self.ln(10)

            def footer(self):
                self.set_y(-18)
                self.set_font("Helvetica", "I", 8)
                self.set_text_color(148, 163, 184)
                self.cell(0, 10, f"Generado conforme normativa BCRA de Exterior y Cambios | Pagina {self.page_no()}", align="C")

        pdf = ComexPDF(orientation="P", unit="mm", format="A4")
        pdf.set_auto_page_break(auto=True, margin=20)
        pdf.add_page()
        
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(30, 41, 59)
        today_str = datetime.now().strftime("%d de %B de %Y")
        pdf.cell(0, 6, f"Buenos Aires, {today_str}", align="R")
        pdf.ln(8)
        
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(0, 5, "Senores de la Mesa de Comercio Exterior y Cambios", ln=True)
        pdf.cell(0, 5, f"{bank_name.upper()}", ln=True)
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(0, 5, "Presente.-", ln=True)
        pdf.ln(6)
        
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_fill_color(241, 245, 249)
        pdf.multi_cell(0, 7, f"REF: {ref_text}", fill=True, border="L")
        pdf.ln(6)
        
        pdf.set_font("Helvetica", "", 10)
        for p in body_paragraphs:
            pdf.multi_cell(0, 6, p)
            pdf.ln(4)
            
        pdf.ln(8)
        pdf.multi_cell(0, 6, "Sin otro particular, saluda a Uds. muy atentamente,")
        pdf.ln(18)
        
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(90, 5, "________________________________________", ln=True)
        pdf.cell(90, 5, f"{signer_name} - {signer_role}", ln=True)
        pdf.cell(90, 5, f"{company_name} (CUIT: {cuit})", ln=True)
        
        return bytes(pdf.output()), "pdf"
    except Exception:
        return generate_text_document(title, ref_text, body_paragraphs, company_name, cuit, bank_name, signer_name, signer_role), "txt"

def generate_prorroga_sepaimpo_pdf(company_name, cuit, bank_name, op_number, amount_usd, bl_number, reason_text, signer_name, signer_role):
    ref = f"SEPAIMPO - Solicitud de Prorroga de Plazo de Demostracion de Ingreso Aduanero | Op. N° {op_number}"
    paragraphs = [
        f"Por la presente nos dirigimos a Uds. en nuestro caracter de titulares de la razon social {company_name}, CUIT {cuit}, con relacion al pago de importacion de bienes cursado oportunamente bajo el concepto BCRA B05 por el importe de USD {amount_usd:,.2f} mediante la operacion de referencia.",
        f"Al respecto, venimos a solicitar formalmente la EXTENSION DEL PLAZO DE DEMOSTRACION DEL REGISTRO DE INGRESO ADUANERO ante el Banco Central de la Republica Argentina, motivado en demoras logisticas y de navegacion internacional ajenas a nuestra voluntad, segun se detalla a continuacion:",
        f"MOTIVO: {reason_text}",
        f"A tal efecto, adjuntamos como constancia documental copia del Conocimiento de Embarque / Documento de Transporte Internacional N° {bl_number} ('Shipped on Board'), acreditando que la mercaderia se encuentra en transito con destino final a la Republica Argentina.",
        "Declaramos bajo juramento que los fondos transferidos se encuentran efectivamente afectados a la importacion de los bienes consignados y solicitamos la actualizacion correspondiente en el sistema SEPAIMPO del BCRA para evitar observaciones registrales."
    ]
    return build_pdf_document("PRORROGA SEPAIMPO", ref, paragraphs, company_name, cuit, bank_name, signer_name, signer_role)

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
    return build_pdf_document("DESCARGO MERMAS SECOEXPO", ref, paragraphs, company_name, cuit, bank_name, signer_name, signer_role)

def generate_zona_primaria_pdf(company_name, cuit, bank_name, pe_number, buyer_name, local_invoice, signer_name, signer_role):
    ref = f"SECOEXPO - Solicitud de Desafectacion por Venta en Zona Primaria Aduanera | PE N° {pe_number}"
    paragraphs = [
        f"Nos dirigimos a Uds. con relacion al Permiso de Embarque N° {pe_number} registrado en el sistema SECOEXPO a nombre de {company_name} (CUIT {cuit}).",
        f"Venimos a poner en vuestro conocimiento que la mercaderia amparada en dicha destinacion aduanera fue objeto de TRANSFERENCIA Y CESION DE DERECHOS EN ZONA PRIMARIA ADUANERA con anterioridad a su libramiento/embarque efectivo, habiendo sido adquirida en plaza local por la firma {buyer_name}.",
        "Por tal motivo, la operacion fue facturada y cancelada localmente en moneda nacional, no correspondiendo el ingreso de divisas desde el exterior a traves del Mercado Libre de Cambios.",
        f"Acompanamos a la presente:\n1. Copia del Contrato de Cesion de Derechos Aduaneros con certificacion de firmas.\n2. Factura comercial local N° {local_invoice}.\n3. Constancia de rectificacion / anulacion aduanera en el Sistema Informatico Malvina (SIM).",
        "Por todo lo expuesto, solicitamos se registre la desafectacion de la obligacion de ingreso de divisas y el cierre del mencionado Permiso de Embarque en el sistema SECOEXPO del BCRA."
    ]
    return build_pdf_document("VENTA ZONA PRIMARIA", ref, paragraphs, company_name, cuit, bank_name, signer_name, signer_role)

def generate_imputacion_b02_pdf(company_name, cuit, bank_name, pe_number, b02_boleto, amount_usd, signer_name, signer_role):
    ref = f"SECOEXPO - Instruccion de Afectacion de Permiso de Embarque a Boleto de Anticipo B02 | PE N° {pe_number}"
    paragraphs = [
        f"Por medio de la presente, {company_name} (CUIT {cuit}) solicita a esa entidad bancaria tenga a bien proceder a la AFECTACION Y CANCELACION del Permiso de Embarque cumplido N° {pe_number} por el importe de USD {amount_usd:,.2f}.",
        f"Dicho Permiso de Embarque debe ser imputado al Boleto de Compra de Cambio liquidado con anterioridad bajo el concepto BCRA B02 (Cobro anticipado de exportaciones de bienes) con numero de operacion / boleto N° {b02_boleto}.",
        "Adjuntamos al presente pedido copia del Permiso de Embarque cumplido en el SIM, Factura Comercial 'E' y Documento de Transporte Internacional.",
        "Solicitamos se asiente la imputacion en el sistema SECOEXPO del BCRA para cancelar el saldo pendiente a la fecha."
    ]
    return build_pdf_document("IMPUTACION B02", ref, paragraphs, company_name, cuit, bank_name, signer_name, signer_role)
