import streamlit as st
import pandas as pd
from datetime import datetime, date
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from engine.concepts_db import CONCEPTOS_SERIE_B, CONCEPTOS_SERIE_S, CATEGORIAS_NCM_EXPO
from engine.rules_engine import (
    calculate_expo_deadline,
    calculate_sepaimpo_deadline,
    validate_candados_access,
    diagnose_import_operation,
    diagnose_export_operation
)
from engine.doc_generator import generate_dictamen_tecnico_pdf

# Configuración de página
st.set_page_config(
    page_title="Consultoría Bancaria y Cambiaria | BCRA & ARCA",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS de Alta Gama - Tema Oscuro Profesional
st.markdown("""
<style>
    /* Fondo oscuro global y tipografía */
    .stApp {
        background-color: #070D18;
        color: #F8FAFC;
    }
    
    /* Titular Principal Superior */
    .header-main-title {
        font-size: 34px;
        font-weight: 800;
        color: #FFFFFF;
        letter-spacing: -0.5px;
        margin-top: 0px;
        margin-bottom: 4px;
    }
    .header-subtitle {
        font-size: 14px;
        color: #94A3B8;
        margin-bottom: 24px;
    }
    
    /* Banner de Operación Activa */
    .operation-banner {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
        border: 1px solid #334155;
        border-left: 5px solid #3B82F6;
        padding: 16px 20px;
        border-radius: 10px;
        margin-bottom: 24px;
    }
    .operation-title {
        font-size: 20px;
        font-weight: 700;
        color: #F8FAFC;
        margin: 0;
    }
    .operation-desc {
        font-size: 13px;
        color: #94A3B8;
        margin-top: 4px;
    }
    
    /* Tarjetas de Trabajo en Modo Oscuro */
    .dark-card {
        background-color: #0F172A;
        border: 1px solid #1E293B;
        border-radius: 12px;
        padding: 22px;
        margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
    }
    
    .section-title {
        font-size: 16px;
        font-weight: 700;
        color: #F1F5F9;
        margin-bottom: 14px;
    }
    
    /* Badges de Semáforo en Modo Oscuro */
    .badge-viable {
        background-color: #064E3B;
        color: #A7F3D0;
        border: 1px solid #059669;
        padding: 8px 16px;
        border-radius: 8px;
        font-weight: 700;
        font-size: 14px;
        display: inline-block;
    }
    .badge-observado {
        background-color: #451A03;
        color: #FDE68A;
        border: 1px solid #D97706;
        padding: 8px 16px;
        border-radius: 8px;
        font-weight: 700;
        font-size: 14px;
        display: inline-block;
    }
    .badge-bloqueado {
        background-color: #450A0A;
        color: #FECACA;
        border: 1px solid #DC2626;
        padding: 8px 16px;
        border-radius: 8px;
        font-weight: 700;
        font-size: 14px;
        display: inline-block;
    }
    
    .concept-tag-dark {
        background-color: #1E293B;
        color: #93C5FD;
        padding: 8px 14px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 14px;
        border-left: 4px solid #3B82F6;
        margin: 14px 0;
        display: block;
    }
    
    /* Alerta Antisumario */
    .alert-antisumario-dark {
        background-color: #3B0712;
        border: 1px solid #9F1239;
        border-left: 5px solid #F43F5E;
        padding: 14px 18px;
        border-radius: 8px;
        margin: 14px 0;
        color: #FFE4E6;
        font-size: 13.5px;
        line-height: 1.5;
    }
    
    /* Textos de Estado de Documentos */
    .doc-ok {
        color: #34D399;
        font-weight: 600;
        font-size: 13px;
    }
    .doc-pending {
        color: #FBBF24;
        font-weight: 600;
        font-size: 13px;
    }
    
    /* ===================================================================== */
    /* BOTONES DE ALTO CONTRASTE Y VISIBILIDAD (MODO OSCURO)                 */
    /* ===================================================================== */
    div[data-testid="stFileUploader"] button,
    button[data-testid="baseButton-secondary"],
    .stButton > button {
        background-color: #1E3A8A !important;
        color: #FFFFFF !important;
        border: 2px solid #3B82F6 !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        font-size: 14px !important;
        padding: 8px 20px !important;
        box-shadow: 0 0 14px rgba(59, 130, 246, 0.45) !important;
        transition: all 0.2s ease !important;
        cursor: pointer !important;
    }
    div[data-testid="stFileUploader"] button:hover,
    button[data-testid="baseButton-secondary"]:hover,
    .stButton > button:hover {
        background-color: #2563EB !important;
        border-color: #93C5FD !important;
        box-shadow: 0 0 22px rgba(96, 165, 250, 0.8) !important;
        transform: translateY(-1px) !important;
    }
    
    /* Botón de Descarga del Dictamen en PDF */
    div[data-testid="stDownloadButton"] > button,
    button[data-testid="baseButton-primary"] {
        background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%) !important;
        color: #FFFFFF !important;
        border: 2px solid #60A5FA !important;
        border-radius: 10px !important;
        font-weight: 800 !important;
        font-size: 16px !important;
        padding: 14px 28px !important;
        box-shadow: 0 4px 20px rgba(37, 99, 235, 0.6) !important;
        transition: all 0.2s ease !important;
        cursor: pointer !important;
    }
    div[data-testid="stDownloadButton"] > button:hover,
    button[data-testid="baseButton-primary"]:hover {
        background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%) !important;
        border-color: #BFDBFE !important;
        box-shadow: 0 6px 28px rgba(59, 130, 246, 0.9) !important;
        transform: translateY(-2px) !important;
    }
    
    /* Zona de arrastre de archivos (Dropzone) */
    div[data-testid="stFileUploaderDropzone"] {
        background-color: #0F172A !important;
        border: 2px dashed #3B82F6 !important;
        border-radius: 10px !important;
        padding: 14px !important;
    }
    div[data-testid="stFileUploaderDropzone"]:hover {
        background-color: #132142 !important;
        border-color: #60A5FA !important;
    }
    div[data-testid="stFileUploaderDropzone"] span {
        color: #CBD5E1 !important;
    }
    
    /* Textareas e Inputs en Modo Oscuro */
    div[data-baseweb="textarea"],
    div[data-testid="stTextArea"] textarea {
        background-color: #0F172A !important;
        color: #F8FAFC !important;
        border: 1.5px solid #334155 !important;
        border-radius: 8px !important;
        font-size: 13.5px !important;
    }
    div[data-baseweb="textarea"]:focus-within,
    div[data-testid="stTextArea"] textarea:focus {
        border-color: #3B82F6 !important;
        box-shadow: 0 0 10px rgba(59, 130, 246, 0.4) !important;
    }
    div[data-baseweb="input"],
    div[data-testid="stTextInput"] input {
        background-color: #0F172A !important;
        color: #F8FAFC !important;
        border: 1.5px solid #334155 !important;
        border-radius: 8px !important;
    }
    div[data-baseweb="input"]:focus-within,
    div[data-testid="stTextInput"] input:focus {
        border-color: #3B82F6 !important;
        box-shadow: 0 0 10px rgba(59, 130, 246, 0.4) !important;
    }
    
    /* Desplegables Selectbox Legibles */
    div[data-baseweb="select"] {
        border: 1.5px solid #334155 !important;
        border-radius: 8px !important;
        background-color: #0F172A !important;
    }
    div[data-baseweb="select"]:hover,
    div[data-baseweb="select"]:focus-within {
        border-color: #3B82F6 !important;
        box-shadow: 0 0 10px rgba(59, 130, 246, 0.4) !important;
    }
    div[data-baseweb="select"] * {
        color: #F8FAFC !important;
    }
    div[data-baseweb="popover"] {
        border: 1.5px solid #3B82F6 !important;
        border-radius: 10px !important;
        background-color: #0B1325 !important;
        box-shadow: 0 12px 32px rgba(0, 0, 0, 0.85) !important;
        max-width: 95vw !important;
    }
    div[data-baseweb="popover"] ul {
        background-color: #0B1325 !important;
        padding: 6px !important;
        white-space: normal !important;
    }
    div[data-baseweb="popover"] li {
        background-color: #0B1325 !important;
        color: #F8FAFC !important;
        white-space: normal !important;
        word-break: break-word !important;
        line-height: 1.4 !important;
        padding: 12px 14px !important;
        border-radius: 6px !important;
        margin-bottom: 4px !important;
        border-bottom: 1px solid #1E293B !important;
    }
    div[data-baseweb="popover"] li:hover,
    div[data-baseweb="popover"] li[aria-selected="true"] {
        background-color: #1E3A8A !important;
        color: #FFFFFF !important;
    }
</style>
""", unsafe_allow_html=True)


# ==============================================================================
# 🏛️ PANEL LATERAL IZQUIERDO: ÚNICAMENTE SELECCIÓN DE OPERACIÓN
# ==============================================================================
with st.sidebar:
    st.markdown("### **OPERACIÓN A REALIZAR**")
    operacion_seleccionada = st.radio(
        "Seleccioná la operación a gestionar:",
        [
            "🚢 Exportaciones",
            "📦 Importaciones"
        ],
        index=0,
        label_visibility="collapsed"
    )
    st.divider()
    st.caption("Normativa Cambiaria BCRA & ARCA")


# ==============================================================================
# 🏛️ TITULAR SUPERIOR PRINCIPAL
# ==============================================================================
st.markdown('<div class="header-main-title">Consultoría Bancaria y Cambiaria</div>', unsafe_allow_html=True)
st.markdown('<div class="header-subtitle">Régimen Informativo y Encuadre Normativo de Operaciones de Comercio Exterior (BCRA / ARCA)</div>', unsafe_allow_html=True)


# ==============================================================================
# 🚢 MÓDULO: EXPORTACIONES
# ==============================================================================
if "Exportaciones" in operacion_seleccionada:
    st.markdown("""
    <div class="operation-banner">
        <div class="operation-title">🚢 Mesa de Exportaciones | Análisis Técnico & Auditoría Documental</div>
        <div class="operation-desc">Encuadre legal de cobros (B01 vs B02), plazos de liquidación según NCM, consolidación de múltiples permisos y régimen SECOEXPO (Com. "A" 6808 BCRA).</div>
    </div>
    """, unsafe_allow_html=True)
    
    col_relev, col_dictamen = st.columns([1.15, 1.25], gap="large")
    
    # --------------------------------------------------------------------------
    # COLUMNA IZQUIERDA: RELEVAMIENTO OPERATIVO Y CARGA DE DOCUMENTOS
    # --------------------------------------------------------------------------
    with col_relev:
        st.markdown('<div class="section-title">📝 1. Relevamiento de la Operación de Exportación</div>', unsafe_allow_html=True)
        
        # Datos de la Empresa
        c_emp_ex, c_cuit_ex = st.columns([1.4, 1])
        with c_emp_ex:
            empresa_expo = st.text_input("Razón Social del Exportador:", value="Exportadora Argentina S.A.", key="emp_exp")
        with c_cuit_ex:
            cuit_expo = st.text_input("CUIT de la Empresa:", value="30-71234567-9", key="cuit_exp")
            
        momento_fondos_label = st.radio(
            "¿En qué momento ingresan o se liquidan las divisas del exterior?",
            [
                "1. Pre-embarque: El comprador exterior transfiere ANTES de embarcar la mercadería (Anticipo)",
                "2. Post-embarque: Las divisas ingresan DESPUÉS de haber embarcado (con Permiso de Embarque cumplido)"
            ]
        )
        es_anticipo = "1. Pre-embarque" in momento_fondos_label
        momento_fondos = "FONDOS_ANTES_DE_EMBARCAR" if es_anticipo else "FONDOS_DESPUES_DE_EMBARCAR"
        
        concepto_propuesto_expo = st.selectbox(
            "¿Qué código de cobro pensaba declarar el exportador o sugirió el banco?",
            [
                "No está seguro (A determinar por el dictamen técnico)",
                "B01 - Cobro de exportaciones de bienes",
                "B02 - Cobro anticipado de exportaciones",
                "B03 - Financiación del exterior"
            ]
        )
        cod_expo_limpio = concepto_propuesto_expo[:3] if "B" in concepto_propuesto_expo else "NO_SABE"
        
        c_monto, c_fecha = st.columns(2)
        with c_monto:
            monto_expo = st.number_input("Monto total a liquidar (USD):", value=65000.0, step=5000.0)
        with c_fecha:
            if es_anticipo:
                fecha_expo = st.date_input("Fecha estimada de cobro del anticipo:", value=date.today())
                cat_ncm = "MANUFACTURAS_MOI_PYME"
                vinculada = False
            else:
                fecha_expo = st.date_input("Fecha de Cumplido Aduanero del Permiso:", value=date.today())
                
        if not es_anticipo:
            st.markdown("---")
            NCM_LABELS = {
                "MANUFACTURAS_MOI_PYME": "🏭 Manufacturas Industriales / PyME (365 días)",
                "ECONOMIAS_REGIONALES": "🥩 Economías Regionales y Alimentos (180 días)",
                "GRANOS_COMMODITIES": "🌾 Granos, Cereales y Oleaginosas (15 días)",
                "EMPRESAS_VINCULADAS": "🔗 Operaciones entre Vinculadas (60 días)"
            }
            cat_ncm = st.selectbox(
                "Rubro / Clasificación NCM de la mercadería exportada:",
                list(NCM_LABELS.keys()),
                format_func=lambda k: NCM_LABELS[k],
                index=0
            )
            st.caption(f"ℹ️ **Normativa BCRA:** {CATEGORIAS_NCM_EXPO[cat_ncm]['nombre']} — {CATEGORIAS_NCM_EXPO[cat_ncm]['descripcion']}")
            vinculada = st.checkbox("¿La venta se realiza a una empresa vinculada en el exterior?", value=(cat_ncm == "EMPRESAS_VINCULADAS"))
            
        st.markdown("---")
        st.markdown('<div class="section-title">📂 2. Carga de Documentación Probatoria (Carga Masiva y Legajo Digital)</div>', unsafe_allow_html=True)
        st.caption("Podés declarar múltiples permisos y facturas correspondientes a una operación consolidada y adjuntar múltiples archivos digitalizados a la vez:")
        
        archivos_adjuntos = []
        declared_docs = {}
        
        if not es_anticipo:
            # 1. Permiso(s) de Embarque (Soporte Masivo)
            c_pe_txt, c_pe_file = st.columns([1.1, 1.2])
            with c_pe_txt:
                pe_raw = st.text_area(
                    "N° de Permiso(s) de Embarque (SIM):",
                    value="26001EC01004567A\n26001EC01004568B",
                    height=85,
                    help="Ingresá uno por línea o separados por coma si la operación ampara más de un permiso.",
                    key="pe_raw"
                )
                pe_list = [p.strip() for p in pe_raw.replace(",", "\n").splitlines() if p.strip()]
                declared_docs["Permisos de Embarque SIM"] = pe_list
                if pe_list:
                    st.caption(f"📑 **{len(pe_list)} Permiso(s) declarado(s):** " + ", ".join(f"`{p}`" for p in pe_list))
                else:
                    st.caption("⚠️ No se ingresaron números de permiso.")
            with c_pe_file:
                pe_uploads = st.file_uploader(
                    "📎 Adjuntar Permiso(s) SIM (.pdf/.jpg) [Múltiples]:",
                    type=["pdf", "jpg", "png"],
                    accept_multiple_files=True,
                    key="up_pe_multi",
                    help="Podés seleccionar o arrastrar todos los permisos digitalizados a la vez."
                )
                pe_files = [f.name for f in pe_uploads] if pe_uploads else []
                archivos_adjuntos.append({
                    "name": f"Permisos de Embarque SIM ({len(pe_list)} declarados)",
                    "attached": len(pe_files) > 0,
                    "count": len(pe_files),
                    "expected": len(pe_list),
                    "filename": ", ".join(pe_files) if pe_files else None
                })
                
            # 2. Factura(s) de Exportación E (Soporte Masivo)
            c_fac_txt, c_fac_file = st.columns([1.1, 1.2])
            with c_fac_txt:
                fac_raw = st.text_area(
                    "N° de Factura(s) Electrónica(s) 'E':",
                    value="00001-00000456\n00001-00000457",
                    height=85,
                    help="Ingresá una por línea o separadas por coma.",
                    key="fac_raw"
                )
                fac_list = [f.strip() for f in fac_raw.replace(",", "\n").splitlines() if f.strip()]
                declared_docs["Facturas Electrónicas 'E'"] = fac_list
                if fac_list:
                    st.caption(f"🧾 **{len(fac_list)} Factura(s) declarada(s):** " + ", ".join(f"`{f}`" for f in fac_list))
                else:
                    st.caption("⚠️ No se ingresaron números de factura.")
            with c_fac_file:
                fac_uploads = st.file_uploader(
                    "📎 Adjuntar Factura(s) 'E' (.pdf) [Múltiples]:",
                    type=["pdf"],
                    accept_multiple_files=True,
                    key="up_fac_multi",
                    help="Podés arrastrar o seleccionar todas las facturas 'E'."
                )
                fac_files = [f.name for f in fac_uploads] if fac_uploads else []
                archivos_adjuntos.append({
                    "name": f"Facturas Electrónicas 'E' ({len(fac_list)} declaradas)",
                    "attached": len(fac_files) > 0,
                    "count": len(fac_files),
                    "expected": len(fac_list),
                    "filename": ", ".join(fac_files) if fac_files else None
                })
                
            # 3. Documento(s) de Transporte
            c_bl_txt, c_bl_file = st.columns([1.1, 1.2])
            with c_bl_txt:
                bl_raw = st.text_area(
                    "Doc(s). de Transporte (B/L, CRT o AWB):",
                    value="BL-MEDU-9876543",
                    height=68,
                    help="Uno por línea si hay varios conocimientos de embarque.",
                    key="bl_raw"
                )
                bl_list = [b.strip() for b in bl_raw.replace(",", "\n").splitlines() if b.strip()]
                declared_docs["Documentos de Transporte"] = bl_list
                if bl_list:
                    st.caption(f"🚢 **{len(bl_list)} Documento(s) declarado(s):** " + ", ".join(f"`{b}`" for b in bl_list))
            with c_bl_file:
                bl_uploads = st.file_uploader(
                    "📎 Adjuntar Doc(s). Transporte (.pdf) [Múltiples]:",
                    type=["pdf"],
                    accept_multiple_files=True,
                    key="up_bl_multi"
                )
                bl_files = [f.name for f in bl_uploads] if bl_uploads else []
                archivos_adjuntos.append({
                    "name": f"Documentos de Transporte ({len(bl_list)} declarados)",
                    "attached": len(bl_files) > 0,
                    "count": len(bl_files),
                    "expected": len(bl_list),
                    "filename": ", ".join(bl_files) if bl_files else None
                })
        else:
            # 1. Proforma(s) u Orden(es) de Compra
            c_prof_txt, c_prof_file = st.columns([1.1, 1.2])
            with c_prof_txt:
                prof_raw = st.text_area(
                    "N° Proforma(s) u Orden(es) de Compra:",
                    value="PI-2026-EXPO-098",
                    height=68,
                    help="Una por línea si hay varias proformas vinculadas.",
                    key="prof_raw"
                )
                prof_list = [p.strip() for p in prof_raw.replace(",", "\n").splitlines() if p.strip()]
                declared_docs["Proformas / Órdenes"] = prof_list
                if prof_list:
                    st.caption(f"📋 **{len(prof_list)} Proforma(s) declarada(s):** " + ", ".join(f"`{p}`" for p in prof_list))
            with c_prof_file:
                prof_uploads = st.file_uploader(
                    "📎 Adjuntar Factura(s) Proforma (.pdf) [Múltiples]:",
                    type=["pdf"],
                    accept_multiple_files=True,
                    key="up_prof_multi"
                )
                prof_files = [f.name for f in prof_uploads] if prof_uploads else []
                archivos_adjuntos.append({
                    "name": f"Facturas Proforma ({len(prof_list)} declaradas)",
                    "attached": len(prof_files) > 0,
                    "count": len(prof_files),
                    "expected": len(prof_list),
                    "filename": ", ".join(prof_files) if prof_files else None
                })
                
            # 2. Contrato Comercial o Pedido
            c_cont_txt, c_cont_file = st.columns([1.1, 1.2])
            with c_cont_txt:
                cont_raw = st.text_area(
                    "Referencia Contrato(s) / Pedido(s):",
                    value="PO-BUYER-USA-441",
                    height=68,
                    key="cont_raw"
                )
                cont_list = [c.strip() for c in cont_raw.replace(",", "\n").splitlines() if c.strip()]
                declared_docs["Contratos / Pedidos"] = cont_list
                if cont_list:
                    st.caption(f"📄 **{len(cont_list)} Referencia(s) declarada(s):** " + ", ".join(f"`{c}`" for c in cont_list))
            with c_cont_file:
                cont_uploads = st.file_uploader(
                    "📎 Adjuntar Contrato(s) / Pedido(s) (.pdf) [Múltiples]:",
                    type=["pdf"],
                    accept_multiple_files=True,
                    key="up_cont_multi"
                )
                cont_files = [f.name for f in cont_uploads] if cont_uploads else []
                archivos_adjuntos.append({
                    "name": f"Contratos / Pedidos ({len(cont_list)} declarados)",
                    "attached": len(cont_files) > 0,
                    "count": len(cont_files),
                    "expected": len(cont_list),
                    "filename": ", ".join(cont_files) if cont_files else None
                })

    # --------------------------------------------------------------------------
    # COLUMNA DERECHA: DICTAMEN TÉCNICO Y AUDITORÍA EN TIEMPO REAL
    # --------------------------------------------------------------------------
    with col_dictamen:
        st.markdown('<div class="section-title">⚖️ 3. Dictamen Técnico y Orientación Normativa</div>', unsafe_allow_html=True)
        
        diag_expo = diagnose_export_operation(
            momento_fondos=momento_fondos,
            docs_disponibles=[],
            concepto_propuesto=cod_expo_limpio,
            monto_usd=monto_expo,
            fecha_cumplido_o_ingreso=fecha_expo,
            categoria_ncm_key=cat_ncm,
            is_related=vinculada
        )
        
        sem_exp = diag_expo["semaforo"]
        if sem_exp.get("nivel") == "CRITICO":
            badge_html = f'<div class="badge-bloqueado">🔴 {sem_exp.get("estado", "")}</div>'
        elif sem_exp.get("nivel") in ["ALTO", "MEDIO"]:
            badge_html = f'<div class="badge-observado">🟡 {sem_exp.get("estado", "")}</div>'
        else:
            badge_html = f'<div class="badge-viable">🟢 {sem_exp.get("estado", "")}</div>'
            
        st.markdown(f"""
        <div class="dark-card">
            <div style="margin-bottom: 12px;">{badge_html}</div>
            <div style="font-size: 14px; color: #CBD5E1; line-height: 1.5; margin-bottom: 14px;">
                {sem_exp.get("resumen", sem_exp.get("accion", ""))}
            </div>
            <div class="concept-tag-dark">📌 Concepto Oficial Dictaminado: {diag_expo["nombre_concepto"]}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Alerta antisumario si intentaban usar B01 antes de embarcar
        if es_anticipo and cod_expo_limpio == "B01":
            st.markdown("""
            <div class="alert-antisumario-dark">
                <strong>🚨 ERROR CRÍTICO EVITADO: Intento de uso de Concepto B01</strong><br>
                El cliente o banco sugirió liquidar bajo <strong>B01</strong>. Sin embargo, conforme la normativa del BCRA, el código B01 exige indefectiblemente un <strong>Permiso de Embarque ya oficializado y cumplido en Aduana</strong>. Liquidar un anticipo como B01 genera rechazo inmediato en la mesa de Comex o la apertura de un reclamo en SECOEXPO. <strong>El encuadre legal obligado es B02.</strong>
            </div>
            """, unsafe_allow_html=True)
            
        # Métricas de Plazos
        pinfo = diag_expo.get("plazo_info", {})
        if pinfo:
            c1, c2 = st.columns(2)
            with c1:
                st.metric("Plazo Legal Otorgado:", f"{pinfo.get('dias', 0)} días")
            with c2:
                f_limite = pinfo.get("fecha_limite")
                f_limite_str = f_limite.strftime("%d/%m/%Y") if hasattr(f_limite, "strftime") else str(f_limite)
                st.metric("Fecha Límite Exigible:", f_limite_str)
                
        # Auditoría del Legajo Documental Adjunto (Múltiples Archivos / Carga Masiva)
        st.markdown("---")
        st.markdown("**Auditoría del Legajo Digital y Comprobantes Adjuntados:**")
        docs_adjuntados_count = sum(1 for a in archivos_adjuntos if a["attached"])
        total_docs_count = len(archivos_adjuntos)
        total_files_uploaded = sum(a.get("count", 0) for a in archivos_adjuntos)
        
        st.progress(docs_adjuntados_count / max(total_docs_count, 1))
        st.caption(f"Solidez del Legajo: {docs_adjuntados_count} de {total_docs_count} categorías respaldadas ({total_files_uploaded} archivos cargados en total).")
        
        for item in archivos_adjuntos:
            cat_name = item["name"]
            att_count = item.get("count", 0)
            exp_count = item.get("expected", 1)
            if item["attached"]:
                if att_count >= exp_count:
                    st.markdown(f"✅ <span class='doc-ok'>{cat_name}:</span> {att_count} archivo(s) digitalizado(s) adjunto(s) (`{item['filename']}`)", unsafe_allow_html=True)
                else:
                    st.markdown(f"⚠️ <span class='doc-pending'>{cat_name}:</span> {att_count} de {exp_count} archivos adjuntos (Faltan {exp_count - att_count}) (`{item['filename']}`)", unsafe_allow_html=True)
            else:
                st.markdown(f"⏳ <span class='doc-pending'>{cat_name}:</span> 0 de {exp_count} archivos cargados (Pendiente de adjuntar)", unsafe_allow_html=True)
                
        # Fundamento Normativo
        with st.expander("📖 **Fundamento Normativo: Régimen Informativo SECOEXPO (Com. 'A' 6808 BCRA)**", expanded=True):
            st.write(diag_expo["fundamento_normativo"])
            
        # Botón de Descarga de Dictamen en PDF
        st.divider()
        pdf_bytes_exp = generate_dictamen_tecnico_pdf(
            company_name=empresa_expo,
            cuit=cuit_expo,
            operation_type="EXPORTACIÓN DE BIENES",
            diagnosis_data=diag_expo,
            signer_name="Consultor Responsable",
            signer_role="Asesor Normativo Comex",
            attached_files=archivos_adjuntos,
            declared_documents=declared_docs
        )
        
        clean_cuit_exp = cuit_expo.replace("-", "").strip()
        st.download_button(
            label="📥 Descargar Dictamen Técnico de Exportación (PDF)",
            data=pdf_bytes_exp,
            file_name=f"Dictamen_Expo_{clean_cuit_exp}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )


# ==============================================================================
# 📦 MÓDULO: IMPORTACIONES
# ==============================================================================
else:
    st.markdown("""
    <div class="operation-banner">
        <div class="operation-title">📦 Mesa de Importaciones | Encuadre Normativo & Acceso al MLC</div>
        <div class="operation-desc">Evaluación de transferencias al exterior (B05 / B07 / B06 / B12), consolidación de despachos y facturas, candados bursátiles y validaciones ARCA.</div>
    </div>
    """, unsafe_allow_html=True)
    
    col_relev_im, col_dictamen_im = st.columns([1.15, 1.25], gap="large")
    
    with col_relev_im:
        st.markdown('<div class="section-title">📝 1. Relevamiento Operativo y Estado de Mercadería</div>', unsafe_allow_html=True)
        
        # Datos de la Empresa
        c_emp_im, c_cuit_im = st.columns([1.4, 1])
        with c_emp_im:
            empresa_impo = st.text_input("Razón Social del Importador:", value="Importadora Industrial S.A.", key="emp_im")
        with c_cuit_im:
            cuit_impo = st.text_input("CUIT de la Empresa:", value="30-79876543-1", key="cuit_im")
            
        estado_label = st.radio(
            "Estado físico de la mercadería importada:",
            [
                "1. Pre-embarque: Aún NO embarcó en el país de origen (Pago por adelantado)",
                "2. En tránsito: Embarcada en origen con Documento de Transporte emitido (B/L, CRT o AWB)",
                "3. En plaza: Ya arribó al país y fue nacionalizada (Despacho a plaza oficializado)"
            ]
        )
        if "1. Pre-embarque" in estado_label:
            estado_impo = "NO_EMBARCADA"
        elif "2. En tránsito" in estado_label:
            estado_impo = "EN_VIAJE"
        else:
            estado_impo = "NACIONALIZADA"
            
        es_bien_capital = st.checkbox("¿La mercadería califica como Bien de Capital / Maquinaria (BK)?", value=False)
        
        concepto_propuesto_impo = st.selectbox(
            "¿Qué código de giro intentaba usar el cliente o sugirió el banco?",
            [
                "No está seguro (A determinar por el dictamen técnico)",
                "B05 - Pago anticipado de importaciones",
                "B07 - Pago a la vista de importaciones",
                "B06 - Pago diferido de importaciones",
                "B12 - Pago anticipado de bienes de capital"
            ]
        )
        cod_impo_limpio = concepto_propuesto_impo[:3] if "B" in concepto_propuesto_impo else "NO_SABE"
        
        c_monto_im, c_fecha_im = st.columns(2)
        with c_monto_im:
            monto_impo = st.number_input("Monto total a transferir (USD):", value=45000.0, step=5000.0, key="m_impo")
        with c_fecha_im:
            fecha_giro_impo = st.date_input("Fecha estimada de giro:", value=date.today(), key="f_impo")
            
        st.markdown("---")
        st.markdown('<div class="section-title">📂 2. Carga de Documentación de Importación (Carga Masiva y Legajo Digital)</div>', unsafe_allow_html=True)
        st.caption("Podés declarar múltiples facturas, B/Ls, despachos y SEDIs para operaciones consolidadas y adjuntar múltiples archivos:")
        
        archivos_impo = []
        declared_docs_im = {}
        
        # Factura(s) Exterior
        c_fac_im, c_fac_up = st.columns([1.1, 1.2])
        with c_fac_im:
            fac_im_raw = st.text_area(
                "N° Factura(s) Exterior (Proforma o Comercial):",
                value="INV-EXT-2026-99\nINV-EXT-2026-100",
                height=85,
                help="Una por línea o separadas por coma.",
                key="fac_im_raw"
            )
            fac_im_list = [f.strip() for f in fac_im_raw.replace(",", "\n").splitlines() if f.strip()]
            declared_docs_im["Facturas del Exterior"] = fac_im_list
            if fac_im_list:
                st.caption(f"🧾 **{len(fac_im_list)} Factura(s) declarada(s):** " + ", ".join(f"`{f}`" for f in fac_im_list))
        with c_fac_up:
            up_fac_im = st.file_uploader(
                "📎 Factura(s) Exterior (.pdf) [Múltiples]:",
                type=["pdf"],
                accept_multiple_files=True,
                key="up_fac_im_multi"
            )
            fac_im_files = [f.name for f in up_fac_im] if up_fac_im else []
            archivos_impo.append({
                "name": f"Facturas del Exterior ({len(fac_im_list)} declaradas)",
                "attached": len(fac_im_files) > 0,
                "count": len(fac_im_files),
                "expected": len(fac_im_list),
                "filename": ", ".join(fac_im_files) if fac_im_files else None
            })
            
        # Doc(s) de Transporte o Despacho
        if estado_impo in ["EN_VIAJE", "NACIONALIZADA"]:
            c_bl_im, c_bl_up = st.columns([1.1, 1.2])
            with c_bl_im:
                bl_im_raw = st.text_area(
                    "N° Conocimiento(s) de Embarque (B/L, CRT, AWB):",
                    value="MEDU98765432",
                    height=68,
                    help="Uno por línea si hay múltiples conocimientos de embarque.",
                    key="bl_im_raw"
                )
                bl_im_list = [b.strip() for b in bl_im_raw.replace(",", "\n").splitlines() if b.strip()]
                declared_docs_im["Documentos de Transporte B/L"] = bl_im_list
                if bl_im_list:
                    st.caption(f"🚢 **{len(bl_im_list)} B/L(s) declarado(s):** " + ", ".join(f"`{b}`" for b in bl_im_list))
            with c_bl_up:
                up_bl_im = st.file_uploader(
                    "📎 Conocimiento(s) de Embarque B/L (.pdf) [Múltiples]:",
                    type=["pdf"],
                    accept_multiple_files=True,
                    key="up_bl_im_multi"
                )
                bl_im_files = [f.name for f in up_bl_im] if up_bl_im else []
                archivos_impo.append({
                    "name": f"Conocimientos de Embarque B/L ({len(bl_im_list)} declarados)",
                    "attached": len(bl_im_files) > 0,
                    "count": len(bl_im_files),
                    "expected": len(bl_im_list),
                    "filename": ", ".join(bl_im_files) if bl_im_files else None
                })
                
        if estado_impo == "NACIONALIZADA":
            c_desp_im, c_desp_up = st.columns([1.1, 1.2])
            with c_desp_im:
                desp_raw = st.text_area(
                    "N° Despacho(s) de Importación SIM:",
                    value="26001IC04001234A\n26001IC04001235B",
                    height=85,
                    help="Uno por línea si se cancelan varios despachos a plaza.",
                    key="desp_raw"
                )
                desp_list = [d.strip() for d in desp_raw.replace(",", "\n").splitlines() if d.strip()]
                declared_docs_im["Despachos de Importación SIM"] = desp_list
                if desp_list:
                    st.caption(f"📑 **{len(desp_list)} Despacho(s) declarado(s):** " + ", ".join(f"`{d}`" for d in desp_list))
            with c_desp_up:
                up_desp = st.file_uploader(
                    "📎 Despacho(s) SIM Oficializado(s) (.pdf) [Múltiples]:",
                    type=["pdf"],
                    accept_multiple_files=True,
                    key="up_desp_multi"
                )
                desp_files = [f.name for f in up_desp] if up_desp else []
                archivos_impo.append({
                    "name": f"Despachos SIM Oficializados ({len(desp_list)} declarados)",
                    "attached": len(desp_files) > 0,
                    "count": len(desp_files),
                    "expected": len(desp_list),
                    "filename": ", ".join(desp_files) if desp_files else None
                })
                
        # Constancia(s) SEDI
        c_sedi_im, c_sedi_up = st.columns([1.1, 1.2])
        with c_sedi_im:
            sedi_raw = st.text_area(
                "N° Declaración(es) SEDI:",
                value="SEDI-2026-004455",
                height=68,
                help="Una por línea si hay múltiples declaraciones SEDI.",
                key="sedi_raw"
            )
            sedi_list = [s.strip() for s in sedi_raw.replace(",", "\n").splitlines() if s.strip()]
            declared_docs_im["Declaraciones SEDI"] = sedi_list
            if sedi_list:
                st.caption(f"📄 **{len(sedi_list)} SEDI(s) declarada(s):** " + ", ".join(f"`{s}`" for s in sedi_list))
        with c_sedi_up:
            up_sedi = st.file_uploader(
                "📎 Constancia(s) SEDI en estado SALIDA (.pdf) [Múltiples]:",
                type=["pdf"],
                accept_multiple_files=True,
                key="up_sedi_multi"
            )
            sedi_files = [f.name for f in up_sedi] if up_sedi else []
            archivos_impo.append({
                "name": f"Constancias SEDI ({len(sedi_list)} declaradas)",
                "attached": len(sedi_files) > 0,
                "count": len(sedi_files),
                "expected": len(sedi_list),
                "filename": ", ".join(sedi_files) if sedi_files else None
            })
            
        st.markdown("---")
        st.markdown('<div class="section-title">🔒 3. Auditoría de Candados Cruzados (BCRA + ARCA)</div>', unsafe_allow_html=True)
        
        empresa_mep = st.checkbox(
            "La EMPRESA operó títulos valores (MEP / CCL / CEDEARs) en los últimos 90 o 180 días",
            value=False,
            key="im_empresa_mep"
        )
        socios_mep = st.checkbox(
            "Los SOCIOS, directores o controlantes operaron títulos valores en los últimos 90 o 180 días",
            value=False,
            help="Comunicación 'A' 7030 punto 2: si los socios operaron en la bolsa, la empresa no puede acceder al MLC.",
            key="im_socios_mep"
        )
        activos_100k = st.checkbox(
            "Posee más de USD 100.000 líquidos disponibles en cuentas del exterior",
            value=False,
            key="im_activos_100k"
        )
        
        c_arc1, c_arc2 = st.columns(2)
        with c_arc1:
            cuit_activa = st.selectbox("Estado del CUIT en ARCA:", ["Activo y regularizado", "Inconsistencias / Inactivo"], key="cuit_arc") == "Activo y regularizado"
        with c_arc2:
            sedi_opc = st.selectbox(
                "Estado de la SEDI en Aduana:",
                ["SALIDA / APROBADA", "OFICIALIZADA", "BLOQUEADA / OBSERVADA", "NO_APLICA"],
                key="sedi_arc"
            )

    with col_dictamen_im:
        st.markdown('<div class="section-title">⚖️ 4. Dictamen Técnico y Viabilidad Cambiaria</div>', unsafe_allow_html=True)
        
        diag_impo = diagnose_import_operation(
            estado_mercaderia=estado_impo,
            docs_disponibles=[],
            concepto_propuesto=cod_impo_limpio,
            monto_usd=monto_impo,
            fecha_operacion=fecha_giro_impo,
            empresa_mep_ccl=empresa_mep,
            socios_mep_ccl=socios_mep,
            activos_externos_100k=activos_100k,
            arca_cuit_activa=cuit_activa,
            sedi_estado=sedi_opc,
            es_bien_capital=es_bien_capital
        )
        
        sem_im = diag_impo["semaforo"]
        if sem_im["nivel"] == "CRITICO":
            badge_html_im = f'<div class="badge-bloqueado">🔴 {sem_im["estado"]}</div>'
        elif sem_im["nivel"] == "MEDIO":
            badge_html_im = f'<div class="badge-observado">🟡 {sem_im["estado"]}</div>'
        else:
            badge_html_im = f'<div class="badge-viable">🟢 {sem_im["estado"]}</div>'
            
        st.markdown(f"""
        <div class="dark-card">
            <div style="margin-bottom: 12px;">{badge_html_im}</div>
            <div style="font-size: 14px; color: #CBD5E1; line-height: 1.5; margin-bottom: 14px;">
                {sem_im["resumen"]}
            </div>
            <div class="concept-tag-dark">📌 Concepto Oficial Dictaminado: {diag_impo["nombre_concepto"]}</div>
        </div>
        """, unsafe_allow_html=True)
        
        if diag_impo["bloqueos"]:
            st.error("🚨 **Bloqueos Normativos Detectados:**")
            for b in diag_impo["bloqueos"]:
                st.markdown(f"* **{b['origen']}:** {b['detalle']}")
                
        if diag_impo["observaciones"]:
            st.warning("⚠️ **Observaciones de Encuadre:**")
            for o in diag_impo["observaciones"]:
                st.markdown(f"* **{o['origen']}:** {o['detalle']}")
                
        # Auditoría de Legajo (Cargas Masivas)
        st.markdown("---")
        st.markdown("**Auditoría del Legajo Digital y Comprobantes Adjuntados:**")
        docs_impo_count = sum(1 for a in archivos_impo if a["attached"])
        total_impo_count = len(archivos_impo)
        total_files_impo = sum(a.get("count", 0) for a in archivos_impo)
        
        st.progress(docs_impo_count / max(total_impo_count, 1))
        st.caption(f"Solidez del Legajo: {docs_impo_count} de {total_impo_count} categorías respaldadas ({total_files_impo} archivos cargados en total).")
        
        for item in archivos_impo:
            cat_name = item["name"]
            att_count = item.get("count", 0)
            exp_count = item.get("expected", 1)
            if item["attached"]:
                if att_count >= exp_count:
                    st.markdown(f"✅ <span class='doc-ok'>{cat_name}:</span> {att_count} archivo(s) digitalizado(s) adjunto(s) (`{item['filename']}`)", unsafe_allow_html=True)
                else:
                    st.markdown(f"⚠️ <span class='doc-pending'>{cat_name}:</span> {att_count} de {exp_count} archivos adjuntos (Faltan {exp_count - att_count}) (`{item['filename']}`)", unsafe_allow_html=True)
            else:
                st.markdown(f"⏳ <span class='doc-pending'>{cat_name}:</span> 0 de {exp_count} archivos cargados (Pendiente de adjuntar)", unsafe_allow_html=True)
                
        with st.expander("📖 **Fundamento Normativo BCRA & Plazo SEPAIMPO**", expanded=True):
            st.write(diag_impo["fundamento_normativo"])
            if diag_impo["plazo_demostracion_dias"] > 0:
                st.info(f"⏳ **Plazo de Demostración Aduanera:** {diag_impo['plazo_demostracion_dias']} días corridos para presentar el Despacho SIM cumplido.")
                
        st.divider()
        pdf_bytes_im = generate_dictamen_tecnico_pdf(
            company_name=empresa_impo,
            cuit=cuit_impo,
            operation_type="IMPORTACIÓN DE BIENES",
            diagnosis_data=diag_impo,
            signer_name="Consultor Responsable",
            signer_role="Asesor Normativo Comex",
            attached_files=archivos_impo,
            declared_documents=declared_docs_im
        )
        
        clean_cuit_im = cuit_impo.replace("-", "").strip()
        st.download_button(
            label="📥 Descargar Dictamen Técnico de Importación (PDF)",
            data=pdf_bytes_im,
            file_name=f"Dictamen_Impo_{clean_cuit_im}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
