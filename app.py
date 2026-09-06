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
from engine.sabana_parser import parse_sabana_dataframe, get_demo_secoexpo_data, get_demo_sepaimpo_data
from engine.doc_generator import (
    generate_prorroga_sepaimpo_pdf,
    generate_descargo_mermas_pdf,
    generate_zona_primaria_pdf,
    generate_imputacion_b02_pdf,
    generate_dictamen_tecnico_pdf
)

# Configuración de página
st.set_page_config(
    page_title="COMEX Consultoría | Dictamen Normativo BCRA & ARCA",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS Profesionales
st.markdown("""
<style>
    .main-title {
        font-size: 26px;
        font-weight: 800;
        color: #0F172A;
        margin-bottom: 2px;
    }
    .subtitle {
        font-size: 15px;
        color: #475569;
        margin-bottom: 20px;
    }
    .consulting-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 22px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
        margin-bottom: 16px;
    }
    .dictamen-box {
        background-color: #F8FAFC;
        border: 2px solid #CBD5E1;
        border-radius: 12px;
        padding: 22px;
        margin-bottom: 16px;
    }
    .badge-viable {
        background-color: #DCFCE7;
        color: #15803D;
        padding: 6px 14px;
        border-radius: 8px;
        font-weight: 700;
        font-size: 14px;
        display: inline-block;
    }
    .badge-observado {
        background-color: #FEF9C3;
        color: #A16207;
        padding: 6px 14px;
        border-radius: 8px;
        font-weight: 700;
        font-size: 14px;
        display: inline-block;
    }
    .badge-bloqueado {
        background-color: #FEE2E2;
        color: #B91C1C;
        padding: 6px 14px;
        border-radius: 8px;
        font-weight: 700;
        font-size: 14px;
        display: inline-block;
    }
    .concept-tag {
        background-color: #EFF6FF;
        color: #1D4ED8;
        padding: 6px 12px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 15px;
        display: inline-block;
        margin-bottom: 8px;
    }
</style>
""", unsafe_allow_html=True)

# Encabezado Institucional
st.markdown('<div class="main-title">🏛️ COMEX Consultoría Bancaria & Cambiaria</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Plataforma de Diagnóstico, Encuadre Normativo (BCRA) y Validación de Acceso al Mercado (ARCA)</div>', unsafe_allow_html=True)

# Navegación Principal en 3 Pilares Consultivos
modulo_opciones = [
    "📋 1. Dictamen de Importaciones (BCRA + ARCA)",
    "🚢 2. Dictamen de Exportaciones (BCRA)",
    "📑 3. Auditoría de Sábanas Bancarias (SEPAIMPO / SECOEXPO)"
]

modulo = st.segmented_control(
    "Seleccioná el Módulo de Asesoramiento:",
    options=modulo_opciones,
    default="📋 1. Dictamen de Importaciones (BCRA + ARCA)"
)
if not modulo:
    modulo = "📋 1. Dictamen de Importaciones (BCRA + ARCA)"

# Barra Lateral: Identificación del Cliente y Consultora
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/bank-building.png", width=52)
    st.markdown("### **Mesa de Consultoría**")
    st.caption("Régimen Informativo BCRA & ARCA")
    st.divider()
    
    st.markdown("**Datos del Cliente Evaluado:**")
    empresa_nombre = st.text_input("Razón Social:", value="Empresa Demo S.A.", key="cfg_empresa")
    empresa_cuit = st.text_input("CUIT:", value="30-71234567-8", key="cfg_cuit")
    empresa_firmante = st.text_input("Contacto / Apoderado:", value="Juan Pérez", key="cfg_firmante")
    
    st.divider()
    st.markdown("**Datos del Consultor / Asesor:**")
    consultor_nombre = st.text_input("Nombre del Asesor:", value="Lic. Asesor Comex", key="cfg_consultor")
    consultor_cargo = st.text_input("Cargo / Especialidad:", value="Consultor en Normativa Cambiaria", key="cfg_cargo_cons")
    st.info("💡 Completá los datos arriba para que salgan membretados en los Dictámenes en PDF.")


# ==============================================================================
# 📋 1. DICTAMEN DE IMPORTACIONES (BCRA + ARCA)
# ==============================================================================
if modulo == "📋 1. Dictamen de Importaciones (BCRA + ARCA)":
    st.markdown("### 📋 Relevamiento y Dictamen Técnico de Importación")
    st.caption("Evaluación de encuadre legal cambiario (B05 / B07 / B06 / B12), plazos aduaneros y candados de acceso al MLC.")
    
    col_input, col_output = st.columns([1.1, 1.3], gap="large")
    
    with col_input:
        st.markdown("#### 1. Relevamiento Operativo y Documental")
        
        estado_mercaderia_label = st.radio(
            "Estado físico de la mercadería y documentación disponible:",
            [
                "1. Pre-embarque: Aún NO embarcó en el país de origen (Pago por adelantado)",
                "2. En tránsito: Embarcada en origen con Documento de Transporte emitido (B/L, CRT o AWB)",
                "3. En plaza: Ya arribó al país y fue nacionalizada (Despacho a plaza oficializado)"
            ]
        )
        if "1. Pre-embarque" in estado_mercaderia_label:
            estado_mercaderia = "NO_EMBARCADA"
        elif "2. En tránsito" in estado_mercaderia_label:
            estado_mercaderia = "EN_VIAJE"
        else:
            estado_mercaderia = "NACIONALIZADA"
            
        es_bien_capital = st.checkbox("¿La mercadería califica como Bien de Capital / Maquinaria (BK)?", value=False)
        
        concepto_propuesto_impo = st.selectbox(
            "¿Qué código de pago sugirió el banco o intentaba usar el cliente?",
            [
                "No está seguro (Requiere encuadre del consultor)",
                "B05 - Pago anticipado de importaciones",
                "B07 - Pago a la vista de importaciones",
                "B06 - Pago diferido de importaciones",
                "B12 - Pago anticipado de bienes de capital"
            ]
        )
        cod_propuesto_limpio = concepto_propuesto_impo[:3] if "B" in concepto_propuesto_impo else "NO_SABE"
        
        monto_impo = st.number_input("Monto a transferir al exterior (USD):", value=45000.0, step=5000.0)
        fecha_giro_impo = st.date_input("Fecha estimada de acceso al mercado / giro:", value=date.today())
        
        st.divider()
        st.markdown("#### 2. Auditoría de Candados de Acceso al MLC (BCRA + ARCA)")
        
        empresa_mep = st.checkbox(
            "La EMPRESA operó títulos valores (MEP / CCL / CEDEARs / Canje) en los últimos 90 o 180 días",
            value=False
        )
        socios_mep = st.checkbox(
            "Los SOCIOS, directores, accionistas controlantes o apoderados operaron títulos valores en los últimos 90 o 180 días",
            value=False,
            help="Comunicación 'A' 7030 punto 2: el acceso de la sociedad se bloquea si las personas humanas vinculadas operaron en la bolsa."
        )
        activos_100k = st.checkbox(
            "Posee más de USD 100.000 líquidos disponibles en cuentas bancarias del exterior",
            value=False
        )
        
        c_arca1, c_arca2 = st.columns(2)
        with c_arca1:
            cuit_activa = st.selectbox("Estado del CUIT en ARCA:", ["Activo y regularizado", "Inconsistencias / Inactivo"]) == "Activo y regularizado"
        with c_arca2:
            sedi_opc = st.selectbox(
                "Estado de la SEDI:",
                ["SALIDA / APROBADA", "OFICIALIZADA", "BLOQUEADA / OBSERVADA", "NO_APLICA"]
            )
            
    with col_output:
        st.markdown("#### 3. Dictamen Técnico y Orientación Normativa")
        
        diag_impo = diagnose_import_operation(
            estado_mercaderia=estado_mercaderia,
            docs_disponibles=[],
            concepto_propuesto=cod_propuesto_limpio,
            monto_usd=monto_impo,
            fecha_operacion=fecha_giro_impo,
            empresa_mep_ccl=empresa_mep,
            socios_mep_ccl=socios_mep,
            activos_externos_100k=activos_100k,
            arca_cuit_activa=cuit_activa,
            sedi_estado=sedi_opc,
            es_bien_capital=es_bien_capital
        )
        
        sem = diag_impo["semaforo"]
        
        # Tarjeta de Estado
        if sem["nivel"] == "CRITICO":
            badge_html = f'<div class="badge-bloqueado">🔴 {sem["estado"]}</div>'
        elif sem["nivel"] == "MEDIO":
            badge_html = f'<div class="badge-observado">🟡 {sem["estado"]}</div>'
        else:
            badge_html = f'<div class="badge-viable">🟢 {sem["estado"]}</div>'
            
        st.markdown(f"""
        <div class="dictamen-box">
            <div style="margin-bottom: 12px;">{badge_html}</div>
            <div style="font-size: 14px; color: #334155; margin-bottom: 14px;">{sem["resumen"]}</div>
            <div class="concept-tag">📌 Concepto Oficial Dictaminado: {diag_impo["nombre_concepto"]}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Bloqueos detectados
        if diag_impo["bloqueos"]:
            st.error("🚨 **Bloqueos Normativos Detectados:**")
            for b in diag_impo["bloqueos"]:
                st.markdown(f"* **{b['origen']}:** {b['detalle']}")
                
        # Observaciones
        if diag_impo["observaciones"]:
            st.warning("⚠️ **Observaciones y Advertencias de Encuadre:**")
            for o in diag_impo["observaciones"]:
                st.markdown(f"* **{o['origen']}:** {o['detalle']}")
                
        # Fundamento Normativo
        with st.expander("📖 **Fundamento Normativo BCRA & Obligaciones Posteriores**", expanded=True):
            st.write(diag_impo["fundamento_normativo"])
            if diag_impo["plazo_demostracion_dias"] > 0:
                st.info(f"⏳ **Plazo de demostración aduanera (SEPAIMPO):** {diag_impo['plazo_demostracion_dias']} días corridos desde la fecha de transferencia para presentar el Despacho SIM cumplido.")
                
        # Checklist Documental
        with st.expander("📂 **Checklist Documental Exigible por la Mesa de Comex del Banco**", expanded=True):
            for idx, doc in enumerate(diag_impo["checklist_documental"], 1):
                st.markdown(f"**{idx}.** {doc}")
                
        # Botón de Descarga del Dictamen Técnico en PDF
        st.divider()
        pdf_bytes = generate_dictamen_tecnico_pdf(
            company_name=empresa_nombre,
            cuit=empresa_cuit,
            operation_type="IMPORTACIÓN DE BIENES",
            diagnosis_data=diag_impo,
            signer_name=consultor_nombre,
            signer_role=consultor_cargo
        )
        
        st.download_button(
            label="📥 Descargar Dictamen Técnico de Importación (PDF Membretado)",
            data=pdf_bytes,
            file_name=f"Dictamen_Impo_{empresa_cuit.replace('-', '')}_{datetime.now().strftime('%Y%m%d')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )


# ==============================================================================
# 🚢 2. DICTAMEN DE EXPORTACIONES (BCRA)
# ==============================================================================
elif modulo == "🚢 2. Dictamen de Exportaciones (BCRA)":
    st.markdown("### 🚢 Relevamiento y Dictamen Técnico de Exportación")
    st.caption("Evaluación de encuadre cambiario (B01 vs B02), plazos de liquidación obligatoria por NCM y seguimiento SECOEXPO.")
    
    col_input_exp, col_output_exp = st.columns([1.1, 1.3], gap="large")
    
    with col_input_exp:
        st.markdown("#### 1. Relevamiento del Cobro de Exportación")
        
        momento_fondos_label = st.radio(
            "¿En qué momento ingresan o se liquidan las divisas del exterior?",
            [
                "1. Pre-embarque: El comprador exterior transfiere ANTES de que la mercadería sea embarcada",
                "2. Post-embarque: Las divisas ingresan DESPUÉS de haber embarcado (con Permiso de Embarque cumplido)"
            ]
        )
        if "1. Pre-embarque" in momento_fondos_label:
            momento_fondos = "FONDOS_ANTES_DE_EMBARCAR"
        else:
            momento_fondos = "FONDOS_DESPUES_DE_EMBARCAR"
            
        concepto_propuesto_expo = st.selectbox(
            "¿Qué código de cobro pensaba declarar el exportador o sugirió el banco?",
            [
                "No está seguro (Requiere encuadre del consultor)",
                "B01 - Cobro de exportaciones de bienes",
                "B02 - Cobro anticipado de exportaciones",
                "B03 - Financiación del exterior"
            ]
        )
        cod_expo_limpio = concepto_propuesto_expo[:3] if "B" in concepto_propuesto_expo else "NO_SABE"
        
        monto_expo = st.number_input("Monto a liquidar en el mercado (USD):", value=65000.0, step=5000.0)
        
        if momento_fondos == "FONDOS_ANTES_DE_EMBARCAR":
            fecha_expo = st.date_input("Fecha de ingreso / liquidación del anticipo:", value=date.today())
            cat_ncm = "MANUFACTURAS_MOI_PYME"
            vinculada = False
        else:
            fecha_expo = st.date_input("Fecha del Cumplido Aduanero del Permiso de Embarque (SIM):", value=date.today())
            st.divider()
            st.markdown("#### Posición Arancelaria y Plazo Legal (BCRA)")
            cat_ncm = st.selectbox(
                "Rubro / Clasificación NCM de la mercadería exportada:",
                list(CATEGORIAS_NCM_EXPO.keys()),
                format_func=lambda k: f"{CATEGORIAS_NCM_EXPO[k]['nombre']} ({CATEGORIAS_NCM_EXPO[k]['plazo_dias']} días)",
                index=1
            )
            vinculada = st.checkbox("¿La venta se realiza a una empresa vinculada en el exterior?", value=False)
            
    with col_output_exp:
        st.markdown("#### 2. Dictamen Técnico y Encuadre Normativo")
        
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
            badge_exp = f'<div class="badge-bloqueado">🔴 {sem_exp.get("estado", "")}</div>'
        elif sem_exp.get("nivel") in ["ALTO", "MEDIO"]:
            badge_exp = f'<div class="badge-observado">🟡 {sem_exp.get("estado", "")}</div>'
        else:
            badge_exp = f'<div class="badge-viable">🟢 {sem_exp.get("estado", "")}</div>'
            
        st.markdown(f"""
        <div class="dictamen-box">
            <div style="margin-bottom: 12px;">{badge_exp}</div>
            <div style="font-size: 14px; color: #334155; margin-bottom: 14px;">{sem_exp.get("resumen", sem_exp.get("accion", ""))}</div>
            <div class="concept-tag">📌 Concepto Oficial Dictaminado: {diag_expo["nombre_concepto"]}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Alertas críticas
        if diag_expo["observaciones"]:
            for o in diag_expo["observaciones"]:
                st.warning(f"**{o['origen']}**: {o['detalle']}")
                
        # Detalle de Plazos
        pinfo = diag_expo.get("plazo_info", {})
        if pinfo:
            c_p1, c_p2 = st.columns(2)
            with c_p1:
                st.metric("Plazo Normativo:", f"{pinfo.get('dias', 0)} días")
            with c_p2:
                st.metric("Fecha Límite Exigible:", pinfo.get("fecha_limite", date.today()).strftime("%d/%m/%Y"))
                
        # Fundamento Normativo
        with st.expander("📖 **Fundamento Normativo BCRA & Obligaciones en SECOEXPO**", expanded=True):
            st.write(diag_expo["fundamento_normativo"])
            
        # Checklist Documental
        with st.expander("📂 **Checklist Documental Exigible por el Banco**", expanded=True):
            for idx, doc in enumerate(diag_expo["checklist_documental"], 1):
                st.markdown(f"**{idx}.** {doc}")
                
        # Botón de Descarga del Dictamen en PDF
        st.divider()
        pdf_bytes_exp = generate_dictamen_tecnico_pdf(
            company_name=empresa_nombre,
            cuit=empresa_cuit,
            operation_type="EXPORTACIÓN DE BIENES",
            diagnosis_data=diag_expo,
            signer_name=consultor_nombre,
            signer_role=consultor_cargo
        )
        
        st.download_button(
            label="📥 Descargar Dictamen Técnico de Exportación (PDF Membretado)",
            data=pdf_bytes_exp,
            file_name=f"Dictamen_Expo_{empresa_cuit.replace('-', '')}_{datetime.now().strftime('%Y%m%d')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )


# ==============================================================================
# 📑 3. AUDITORÍA DE SÁBANAS BANCARIAS (SEPAIMPO / SECOEXPO)
# ==============================================================================
else:
    st.markdown("### 📑 Auditoría y Regularización de Sábanas Bancarias")
    st.caption("Carga de planillas de seguimiento emitidas por entidades financieras (Santander, Galicia, Macro, BBVA, etc.) y generación de notas oficiales.")
    
    submodulo_sabana = st.radio(
        "Seleccioná el Régimen a Procesar:",
        ["SEPAIMPO (Seguimiento de Pagos de Importaciones)", "SECOEXPO (Seguimiento de Cobros de Exportaciones)"],
        horizontal=True
    )
    
    tipo_regimen = "SEPAIMPO" if "SEPAIMPO" in submodulo_sabana else "SECOEXPO"
    
    col_upload, col_view = st.columns([1, 1.8], gap="medium")
    
    with col_upload:
        st.markdown("#### 1. Carga de Sábana Bancaria")
        uploaded_file = st.file_uploader(
            f"Arrastrá el archivo Excel o CSV de {tipo_regimen} que te envió el banco:",
            type=["xlsx", "xls", "csv"]
        )
        
        usar_demo = st.button("🧪 Cargar Sábana de Prueba (Demostración)", use_container_width=True)
        
        df_raw = None
        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith(".csv"):
                    df_raw = pd.read_csv(uploaded_file)
                else:
                    df_raw = pd.read_excel(uploaded_file)
                st.success(f"Archivo cargado correctamente: {len(df_raw)} registros encontrados.")
            except Exception as e:
                st.error(f"Error al leer el archivo: {e}")
        elif usar_demo:
            if tipo_regimen == "SEPAIMPO":
                df_raw = get_demo_sepaimpo_data()
            else:
                df_raw = get_demo_secoexpo_data()
            st.info("Cargados datos de demostración con casos verde, amarillo y rojo.")
            
    with col_view:
        st.markdown("#### 2. Diagnóstico y Semáforo de Operaciones")
        if df_raw is not None:
            df_norm = parse_sabana_dataframe(df_raw, tipo_regimen)
            
            # Contadores
            c_v = len(df_norm[df_norm["Semáforo"].str.contains("🟢")])
            c_a = len(df_norm[df_norm["Semáforo"].str.contains("🟡")])
            c_r = len(df_norm[df_norm["Semáforo"].str.contains("🔴")])
            
            m1, m2, m3 = st.columns(3)
            m1.metric("En Plazo (🟢)", c_v)
            m2.metric("Atención (🟡)", c_a)
            m3.metric("Urgente / Vencido (🔴)", c_r)
            
            st.dataframe(
                df_norm[["Operación / Ref", "Fecha Base", "Fecha Límite", "Días Restantes", "Semáforo", "Diagnóstico Operativo"]],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("Subí una sábana del banco o tocá el botón 'Cargar Sábana de Prueba' para visualizar el diagnóstico.")
            
    # Sección de Generación de Notas Oficiales
    st.divider()
    st.markdown("#### 3. Centro de Emisión de Notas Formales de Descargo / Prórroga")
    
    if tipo_regimen == "SEPAIMPO":
        st.markdown("**Generar Solicitud de Prórroga Bancaria SEPAIMPO:**")
        cp1, cp2, cp3 = st.columns(3)
        with cp1:
            banco_sel = st.selectbox("Banco Interviniente:", ["Banco Santander", "Banco Galicia", "Banco BBVA", "Banco Macro", "Otro"])
            desp_num = st.text_input("N° Despacho / Registro:", value="26001IC04008899B")
        with cp2:
            dias_prorr = st.number_input("Días de prórroga a solicitar:", value=90, step=30)
            motivo_prorr = st.selectbox("Causal de Demora:", [
                "Demoras logísticas en flete internacional marítimo y congestión portuaria",
                "Retraso en la emisión de certificados técnicos / ensayos de laboratorio INTI",
                "Demora en la inspección aduanera y canal rojo de verificación"
            ])
        with cp3:
            st.write("")
            st.write("")
            pdf_prorr = generate_prorroga_sepaimpo_pdf(
                company_name=empresa_nombre,
                cuit=empresa_cuit,
                bank_name=banco_sel,
                operation_ref=desp_num,
                additional_days=dias_prorr,
                justification=motivo_prorr,
                signer_name=empresa_firmante,
                signer_role="Apoderado"
            )
            st.download_button(
                "📥 Descargar Solicitud de Prórroga en PDF",
                data=pdf_prorr,
                file_name=f"Prorroga_SEPAIMPO_{desp_num}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
    else:
        tab_mermas, tab_zona, tab_imp = st.tabs([
            "Descargo por Mermas / Descuentos",
            "Desafectación Venta en Zona Primaria",
            "Imputación de Permiso a Anticipo B02"
        ])
        
        with tab_mermas:
            cm1, cm2, cm3 = st.columns(3)
            with cm1:
                b_mer = st.selectbox("Banco:", ["Banco Santander", "Banco Galicia", "Banco BBVA", "Banco Macro"], key="b_mer")
                pe_mer = st.text_input("N° Permiso de Embarque:", value="26001EC01004455C", key="pe_mer")
            with cm2:
                fob_orig = st.number_input("FOB Original Aduanero (USD):", value=50000.0, key="fob_mer")
                fob_rec = st.number_input("Monto efectivamente cobrado (USD):", value=46500.0, key="rec_mer")
            with cm3:
                nc_num = st.text_input("N° Nota de Crédito 'E':", value="00001-00000045", key="nc_mer")
                surv_num = st.text_input("N° Certificado Peritaje / Survey:", value="SRV-2026-998", key="surv_mer")
                
            pdf_mer = generate_descargo_mermas_pdf(
                company_name=empresa_nombre,
                cuit=empresa_cuit,
                bank_name=b_mer,
                pe_number=pe_mer,
                original_fob=fob_orig,
                amount_received=fob_rec,
                nc_number=nc_num,
                survey_number=surv_num,
                signer_name=empresa_firmante,
                signer_role="Apoderado"
            )
            st.download_button(
                "📥 Descargar Descargo por Mermas en PDF",
                data=pdf_mer,
                file_name=f"Descargo_Mermas_{pe_mer}.pdf",
                mime="application/pdf"
            )
            
        with tab_zona:
            cz1, cz2 = st.columns(2)
            with cz1:
                b_zon = st.selectbox("Banco:", ["Banco Santander", "Banco Galicia", "Banco BBVA"], key="b_zon")
                pe_zon = st.text_input("N° Permiso de Embarque:", value="26001EC01003322A", key="pe_zon")
            with cz2:
                comprador_loc = st.text_input("Razón Social Comprador Local:", value="Compradora Local S.A.", key="comp_zon")
                fact_loc = st.text_input("Factura Comercial Local N°:", value="00005-00001234", key="fact_zon")
                
            pdf_zon = generate_zona_primaria_pdf(
                company_name=empresa_nombre,
                cuit=empresa_cuit,
                bank_name=b_zon,
                pe_number=pe_zon,
                buyer_name=comprador_loc,
                local_invoice=fact_loc,
                signer_name=empresa_firmante,
                signer_role="Apoderado"
            )
            st.download_button(
                "📥 Descargar Desafectación Zona Primaria en PDF",
                data=pdf_zon,
                file_name=f"Desafectacion_ZonaPrimaria_{pe_zon}.pdf",
                mime="application/pdf"
            )
            
        with tab_imp:
            ci1, ci2 = st.columns(2)
            with ci1:
                b_imp = st.selectbox("Banco:", ["Banco Santander", "Banco Galicia", "Banco BBVA"], key="b_imp")
                pe_imp = st.text_input("N° Permiso de Embarque cumplido a cancelar:", value="26001EC01007788D", key="pe_imp")
            with ci2:
                bol_imp = st.text_input("N° Boleto Cambio Anticipo B02:", value="BOL-2026-B02-0987", key="bol_imp")
                monto_imp = st.number_input("Monto a imputar (USD):", value=30000.0, key="monto_imp")
                
            pdf_imp = generate_imputacion_b02_pdf(
                company_name=empresa_nombre,
                cuit=empresa_cuit,
                bank_name=b_imp,
                pe_number=pe_imp,
                b02_boleto=bol_imp,
                amount_usd=monto_imp,
                signer_name=empresa_firmante,
                signer_role="Apoderado"
            )
            st.download_button(
                "📥 Descargar Nota de Imputación B02 en PDF",
                data=pdf_imp,
                file_name=f"Imputacion_B02_{pe_imp}.pdf",
                mime="application/pdf"
            )
