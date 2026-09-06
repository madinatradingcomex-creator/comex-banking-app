import streamlit as st
import pandas as pd
from datetime import datetime, date
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from engine.concepts_db import CONCEPTOS_SERIE_B, CONCEPTOS_SERIE_S, CATEGORIAS_NCM_EXPO
from engine.rules_engine import calculate_expo_deadline, calculate_sepaimpo_deadline, validate_candados_access
from engine.sabana_parser import parse_sabana_dataframe, get_demo_secoexpo_data, get_demo_sepaimpo_data
from engine.doc_generator import (
    generate_prorroga_sepaimpo_pdf,
    generate_descargo_mermas_pdf,
    generate_zona_primaria_pdf,
    generate_imputacion_b02_pdf
)

# Configuración de página
st.set_page_config(
    page_title="COMEX Asistente Bancario | BCRA & ARCA",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS Limpios e Institucionales
st.markdown("""
<style>
    .main-title {
        font-size: 28px;
        font-weight: 800;
        color: #0F172A;
        margin-bottom: 4px;
    }
    .subtitle {
        font-size: 15px;
        color: #475569;
        margin-bottom: 24px;
    }
    .card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        margin-bottom: 16px;
    }
    .badge-blue {
        background-color: #EFF6FF;
        color: #1D4ED8;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 13px;
    }
</style>
""", unsafe_allow_html=True)

# Encabezado Institucional
st.markdown('<div class="main-title">🏛️ COMEX Asistente Bancario & Cambiario</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Régimen Informativo Bancario BCRA / ARCA · SEPAIMPO · SECOEXPO · Acceso al MLC</div>', unsafe_allow_html=True)

# Selector de Módulos Principal (Visible y cómodo en Celulares, Tablets y Computadoras)
modulo_opciones = [
    "📦 1. Módulo Importaciones",
    "🚢 2. Módulo Exportaciones",
    "📑 3. Módulo SEPAIMPO (Bancos)",
    "📑 4. Módulo SECOEXPO (Bancos)"
]

modulo = st.segmented_control(
    "Seleccioná el Módulo Operativo:",
    options=modulo_opciones,
    default="📦 1. Módulo Importaciones"
)
if not modulo:
    modulo = "📦 1. Módulo Importaciones"

# Barra Lateral: Identificación y Perfil de Empresa
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/bank-building.png", width=56)
    st.markdown("### **COMEX Consultoría**")
    st.caption("Régimen Informativo Bancario (BCRA / ARCA)")
    st.divider()
    st.markdown("**Datos del Titular / Empresa:**")
    empresa_nombre = st.text_input("Razón Social:", value="Empresa Demo S.A.", key="cfg_empresa")
    empresa_cuit = st.text_input("CUIT:", value="30-71234567-8", key="cfg_cuit")
    empresa_firmante = st.text_input("Firmante:", value="Juan Pérez", key="cfg_firmante")
    empresa_cargo = st.text_input("Cargo:", value="Apoderado / Socio Gerente", key="cfg_cargo")
    st.divider()
    st.info("💡 Cambiá de módulo usando los botones superiores en pantalla.")


# ==============================================================================
# 📦 1. MÓDULO IMPORTACIONES
# ==============================================================================
if modulo == "📦 1. Módulo Importaciones":
    st.markdown('<div class="main-title">📦 Módulo de Importaciones</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Gestión de pagos al exterior, plazos de registro aduanero, candados de acceso al MLC y fletes conexos.</div>', unsafe_allow_html=True)
    
    tab_pagos, tab_candados, tab_fletes = st.tabs([
        "🗓️ Calculador de Pagos y Conceptos",
        "🔒 Auditor de Candados MLC (DDJJ)",
        "🚢 Fletes y Seguros Conexos (S13/S14)"
    ])
    
    with tab_pagos:
        c1, c2 = st.columns([1.1, 1])
        with c1:
            st.markdown("#### Datos de la Operación de Importación")
            despacho_ref = st.text_input("N° de Despacho SIM (opcional si es anticipado):", value="26001IC04001234A")
            momento_impo = st.selectbox(
                "Tipo de Pago que vas a realizar:",
                [
                    "B05 - Pago Anticipado (Antes de que se embarque la mercadería)",
                    "B07 - Pago A la Vista (Mercadería embarcada con B/L emitido)",
                    "B06 - Pago Diferido (Mercadería ya nacionalizada en el país)",
                    "B12 - Pago Anticipado de Bienes de Capital (Maquinaria BK)"
                ]
            )
            monto_impo = st.number_input("Monto a transferir (USD):", value=50000.0, step=1000.0)
            fecha_giro = st.date_input("Fecha de Giro / Transferencia:", value=date.today())
            
        with c2:
            cod_impo = momento_impo[:3]
            info_impo = CONCEPTOS_SERIE_B[cod_impo]
            res_impo = calculate_sepaimpo_deadline(fecha_giro, cod_impo)
            sem_impo = res_impo["semaforo"]
            
            st.markdown(f"""
            <div class="card">
                <span class="badge-blue">Concepto Oficial BCRA: {cod_impo}</span>
                <h4 style="margin:10px 0 4px 0; color:#0F172A;">{info_impo['descripcion']}</h4>
                <p style="color:#64748B; font-size:14px;">{info_impo['impacto_bancario']}</p>
                <hr style="border-color:#E2E8F0; margin:12px 0;"/>
                <p><strong>Plazo de Demostración Aduanera:</strong> {res_impo['plazo_dias_otorgado']} días corridos.</p>
                <p><strong>Fecha Límite de Despacho:</strong> <span style="color:#B91C1C; font-weight:bold;">{res_impo['fecha_limite_demostracion']}</span></p>
                <p><strong>Días Restantes:</strong> {res_impo['dias_restantes']} días ({sem_impo['color']} {sem_impo['estado']})</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.info(f"💡 {sem_impo['accion']}")
            
            st.markdown("**Documentación obligatoria que te exigirá el banco:**")
            for doc in info_impo["docs_requeridos"]:
                st.markdown(f"- 📄 {doc}")

    with tab_candados:
        st.markdown("#### Auditoría de Declaraciones Juradas y Candados de Acceso al MLC")
        st.write("Antes de cursar cualquier pago de importación, el banco valida estos requisitos bajo apercibimiento de la Ley Penal Cambiaria:")
        
        mep_check = st.checkbox("¿La empresa, directores o socios vendieron títulos valores en moneda extranjera (Dólar MEP / CCL) en los últimos 90/180 días?", value=False)
        activos_check = st.checkbox("¿La empresa posee más de USD 100.000 líquidos disponibles en cuentas del exterior no afectados al pago?", value=False)
        com6401_check = st.checkbox("¿Tiene al día las presentaciones del Relevamiento de Activos y Pasivos Externos (Com. 'A' 6401)?", value=True)
        
        val_candados = validate_candados_access(mep_check, activos_check, com6401_check)
        if val_candados["apto_para_acceder_mlc"]:
            st.success("✅ **APTO PARA ACCEDER AL MERCADO LIBRE DE CAMBIOS**: Cumple con todas las declaraciones juradas exigidas por el BCRA.")
        else:
            st.error(f"❌ **INHABILITADO PARA OPERAR ({val_candados['cantidad_inconsistencias']} bloqueo/s detectado/s):**")
            for inc in val_candados["inconsistencias"]:
                st.warning(f"**{inc['candado']}:** {inc['detalle']}")

    with tab_fletes:
        st.markdown("#### Fletes y Seguros Internacionales Conexos")
        incoterm_sel = st.selectbox("Incoterm de tu Factura de Importación:", ["FOB / FCA (Flete y seguro NO incluidos)", "CFR / CIF (Flete y seguro incluidos en el precio)"])
        
        if "FOB" in incoterm_sel:
            st.markdown("""
            <div class="card">
                <h4 style="color:#0F172A; margin:0 0 8px 0;">Pago de Flete Internacional (Concepto S13)</h4>
                <p>Al ser factura FOB, el flete debe pagarse de forma separada:</p>
                <ul>
                    <li><strong>Si se paga al armador/transportista exterior:</strong> Se cursa bajo el concepto <strong>S13</strong> presentando la factura de flete y el B/L (Freight Prepaid/Collect).</li>
                    <li><strong>Si se paga en Argentina a una agencia marítima local en pesos:</strong> No requiere acceso al MLC del importador. La agencia emite factura local con IVA y gestiona su propio giro.</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.success("💡 **Condición CFR / CIF:** El flete ya se encuentra subsumido en el valor comercial del bien y se paga todo junto bajo el código B correspondiente.")


# ==============================================================================
# 🚢 2. MÓDULO EXPORTACIONES
# ==============================================================================
elif modulo == "🚢 2. Módulo Exportaciones":
    st.markdown('<div class="main-title">🚢 Módulo de Exportaciones</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Determinación de plazos por posición arancelaria (NCM), cobros anticipados B02 y cross-trade B09.</div>', unsafe_allow_html=True)
    
    tab_expo_plazos, tab_cross_trade = st.tabs([
        "🗓️ Plazos de Liquidación por Posición Arancelaria",
        "🌐 Tráfico Internacional / Cross-Trade (Concepto B09)"
    ])
    
    with tab_expo_plazos:
        col_e1, col_e2 = st.columns([1.1, 1])
        with col_e1:
            pe_nro = st.text_input("N° de Permiso de Embarque (SIM):", value="26001EC01004567Z")
            tipo_cobro = st.selectbox(
                "Tipo de Cobro que se realiza:",
                [
                    "B01 - Cobro posterior al embarque (Con Permiso cumplido en mano)",
                    "B02 - Cobro anticipado de exportación (Previo a embarcar)",
                    "B03 - Financiación / Prefinanciación del exterior"
                ]
            )
            cat_ncm = st.selectbox(
                "Categoría del Producto exportado:",
                options=list(CATEGORIAS_NCM_EXPO.keys()),
                format_func=lambda x: CATEGORIAS_NCM_EXPO[x]["nombre"]
            )
            es_vinc = st.checkbox("¿El comprador exterior es una empresa vinculada?", value=False)
            fecha_cumplido = st.date_input("Fecha de Cumplido de Embarque en Aduana:", value=date.today())
            
        with col_e2:
            cod_e = tipo_cobro[:3]
            info_e = CONCEPTOS_SERIE_B[cod_e]
            res_e = calculate_expo_deadline(fecha_cumplido, cat_ncm, es_vinc)
            sem_e = res_e["semaforo"]
            
            st.markdown(f"""
            <div class="card">
                <span class="badge-blue">Concepto Oficial BCRA: {cod_e}</span>
                <h4 style="margin:10px 0 4px 0; color:#0F172A;">{info_e['descripcion']}</h4>
                <p style="color:#64748B; font-size:14px;">{info_e['impacto_bancario']}</p>
                <hr style="border-color:#E2E8F0; margin:12px 0;"/>
                <p><strong>Plazo Legal de Liquidación:</strong> {res_e['plazo_dias_aplicado']} días corridos.</p>
                <p><strong>Fecha Límite Improrrogable:</strong> <span style="color:#B91C1C; font-weight:bold;">{res_e['fecha_limite']}</span></p>
                <p><strong>Días Restantes:</strong> {res_e['dias_restantes']} días ({sem_e['color']} {sem_e['estado']})</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.info(f"💡 {sem_e['accion']}")
            
            st.markdown("**Documentación requerida para liquidar en el banco:**")
            for doc in info_e["docs_requeridos"]:
                st.markdown(f"- 📄 {doc}")

    with tab_cross_trade:
        st.markdown("#### Tráfico Triangular Internacional / Cross-Trade (Concepto B09)")
        st.caption("Aplica cuando la mercadería viaja directamente entre terceros países sin ingresar físicamente a la Argentina.")
        
        c_buy, c_sell = st.columns(2)
        with c_buy:
            compra_usd = st.number_input("Monto Factura de Compra al Proveedor (USD):", value=60000.0)
            origen_pais = st.text_input("País de Origen de los Bienes:", value="China")
        with c_sell:
            venta_usd = st.number_input("Monto Factura de Venta al Cliente Final (USD):", value=75000.0)
            destino_pais = st.text_input("País de Destino Final:", value="Chile")
            
        margen = venta_usd - compra_usd
        if margen > 0:
            pct = (margen / compra_usd) * 100
            st.success(f"✅ **Resultado Comercial Válido:** Margen positivo de USD {margen:,.2f} (+{pct:.1f}%). La operación cumple con la justificación cambiaria ante el BCRA.")
        else:
            st.error("❌ **Margen Comercial Negativo:** La venta debe superar a la compra para que el banco autorice la operación bajo concepto B09.")
            
        st.markdown("**Documentos que te va a pedir el banco para un B09:**")
        for d in CONCEPTOS_SERIE_B["B09"]["docs_requeridos"]:
            st.markdown(f"- 📄 {d}")


# ==============================================================================
# 📑 3. MÓDULO SEPAIMPO (Seguimiento Bancario de Importaciones)
# ==============================================================================
elif modulo == "📑 3. Módulo SEPAIMPO (Bancos)":
    st.markdown('<div class="main-title">📑 Módulo SEPAIMPO (Seguimiento Bancario)</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Control de pagos anticipados vs. despachos nacionalizados en el SIM y gestión preventiva de prórrogas.</div>', unsafe_allow_html=True)
    
    tab_sabana_impo, tab_prorroga = st.tabs([
        "📊 Traductor de Sábana Bancaria SEPAIMPO",
        "📝 Generar Solicitud de Prórroga Bancaria"
    ])
    
    with tab_sabana_impo:
        col_u, col_d = st.columns([2, 1])
        with col_u:
            up_impo = st.file_uploader("Subí tu archivo Excel o CSV de SEPAIMPO emitido por el banco:", type=["xlsx", "xls", "csv"], key="up_sepaimpo")
        with col_d:
            st.markdown("**¿No tenés un archivo a mano?**")
            btn_demo_impo = st.button("Probar con Datos de Ejemplo SEPAIMPO", key="demo_impo")
            
        df_impo = None
        if up_impo is not None:
            df_impo = pd.read_csv(up_impo) if up_impo.name.endswith(".csv") else pd.read_excel(up_impo)
        elif btn_demo_impo:
            df_impo = get_demo_sepaimpo_data()
            
        if df_impo is not None and not df_impo.empty:
            res_df_i, reg_i, stats_i = parse_sabana_dataframe(df_impo, regime_hint="SEPAIMPO")
            st.divider()
            
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Total Operaciones", stats_i["total_operaciones"])
            m2.metric("Saldo Total Pendiente", f"USD {stats_i['monto_total_usd']:,.2f}")
            m3.metric("🚨 En Mora / Vencidas", stats_i["en_mora"], delta_color="inverse")
            m4.metric("⚠️ Riesgo Alto (< 15 días)", stats_i["en_riesgo_alto"], delta_color="inverse")
            
            st.markdown("#### **Diagnóstico Detallado de Pagos de Importación:**")
            st.dataframe(
                res_df_i[["Identificador", "Banco Nominado", "Monto Pendiente (USD)", "Fecha Límite", "Días Restantes", "Estado Semáforo", "Acción Sugerida"]],
                use_container_width=True,
                hide_index=True
            )
            
            csv_exp_i = res_df_i.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Descargar Diagnóstico en CSV", data=csv_exp_i, file_name=f"diagnostico_sepaimpo_{date.today()}.csv", mime="text/csv")

    with tab_prorroga:
        st.markdown("#### Confección de Solicitud de Prórroga ante el Banco Nominado")
        st.write("Si el plazo de demostración está por vencer y la mercadería está en viaje, presentá esta nota antes de caer en mora automática.")
        
        cp1, cp2 = st.columns(2)
        with cp1:
            banco_prorroga = st.selectbox("Banco de Seguimiento:", ["Banco Santander", "Banco Galicia", "Banco BBVA", "Banco Macro", "Banco Nación", "Banco ICBC", "Otro"], key="bp_impo")
            op_prorroga = st.text_input("N° de Operación Bancaria / Boleto BVC:", value="OP-2026-99482")
            monto_prorroga = st.number_input("Monto Pendiente (USD):", value=45000.0)
        with cp2:
            bl_prorroga = st.text_input("N° de Documento de Transporte (B/L):", value="MEDU12345678")
            motivo_prorroga = st.text_area("Motivo fundado de la demora:", value="Retraso logístico internacional en navegación y congestión portuaria en puerto de transbordo.")
            
        if st.button("📄 Generar Solicitud de Prórroga en PDF", type="primary"):
            pdf_bytes_p, ext_p = generate_prorroga_sepaimpo_pdf(
                empresa_nombre, empresa_cuit, banco_prorroga, op_prorroga, monto_prorroga, bl_prorroga, motivo_prorroga, empresa_firmante, empresa_cargo
            )
            mime_p = "application/pdf" if ext_p == "pdf" else "text/plain"
            st.download_button(f"📥 Descargar Nota Oficial ({ext_p.upper()})", data=pdf_bytes_p, file_name=f"prorroga_sepaimpo_{op_prorroga}.{ext_p}", mime=mime_p)


# ==============================================================================
# 📑 4. MÓDULO SECOEXPO (Seguimiento Bancario de Exportaciones)
# ==============================================================================
elif modulo == "📑 4. Módulo SECOEXPO (Bancos)":
    st.markdown('<div class="main-title">📑 Módulo SECOEXPO (Seguimiento Bancario)</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Monitoreo de cumplidos de embarque, imputación de anticipos B02 y descargos por mermas o venta en zona primaria.</div>', unsafe_allow_html=True)
    
    tab_sabana_expo, tab_descargo_mermas, tab_zona_prim, tab_imputa_b02 = st.tabs([
        "📊 Traductor de Sábana Bancaria SECOEXPO",
        "⚖️ Descargo por Mermas / Descuentos",
        "🏛️ Desafectación por Venta en Zona Primaria",
        "🔗 Afectación de Permiso a Anticipo B02"
    ])
    
    with tab_sabana_expo:
        col_ue, col_de = st.columns([2, 1])
        with col_ue:
            up_expo = st.file_uploader("Subí tu archivo Excel o CSV de SECOEXPO emitido por el banco:", type=["xlsx", "xls", "csv"], key="up_secoexpo")
        with col_de:
            st.markdown("**¿No tenés un archivo a mano?**")
            btn_demo_expo = st.button("Probar con Datos de Ejemplo SECOEXPO", key="demo_expo")
            
        df_expo = None
        if up_expo is not None:
            df_expo = pd.read_csv(up_expo) if up_expo.name.endswith(".csv") else pd.read_excel(up_expo)
        elif btn_demo_expo:
            df_expo = get_demo_secoexpo_data()
            
        if df_expo is not None and not df_expo.empty:
            res_df_e, reg_e, stats_e = parse_sabana_dataframe(df_expo, regime_hint="SECOEXPO")
            st.divider()
            
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Total Permisos", stats_e["total_operaciones"])
            m2.metric("Saldo Total Pendiente", f"USD {stats_e['monto_total_usd']:,.2f}")
            m3.metric("🚨 En Mora Cambiaria", stats_e["en_mora"], delta_color="inverse")
            m4.metric("⚠️ Riesgo Alto (< 15 días)", stats_e["en_riesgo_alto"], delta_color="inverse")
            
            st.markdown("#### **Diagnóstico Detallado de Permisos de Embarque:**")
            st.dataframe(
                res_df_e[["Identificador", "Banco Nominado", "Monto Pendiente (USD)", "Fecha Límite", "Días Restantes", "Estado Semáforo", "Acción Sugerida"]],
                use_container_width=True,
                hide_index=True
            )
            
            csv_exp_e = res_df_e.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Descargar Diagnóstico en CSV", data=csv_exp_e, file_name=f"diagnostico_secoexpo_{date.today()}.csv", mime="text/csv")

    with tab_descargo_mermas:
        st.markdown("#### Descargo de SECOEXPO por Mermas, Averías o Descuentos Comerciales")
        st.write("Permite cerrar el 100% del valor FOB ante el banco cuando el cliente del exterior pagó de menos con motivo fundado.")
        
        cm1, cm2 = st.columns(2)
        with cm1:
            banco_m = st.selectbox("Banco Nominado:", ["Banco Santander", "Banco Galicia", "Banco BBVA", "Banco Macro", "Banco Nación", "Banco ICBC", "Otro"], key="bm_expo")
            pe_m = st.text_input("N° de Permiso de Embarque cumplido:", value="26001EC01004567Z")
            fob_m = st.number_input("Valor FOB Oficial en SIM (USD):", value=80000.0)
            cobrado_m = st.number_input("Monto efectivamente liquidado (USD):", value=72000.0)
        with cm2:
            nc_m = st.text_input("N° de Nota de Crédito 'E' en ARCA:", value="00005-00001234")
            survey_m = st.text_input("N° de Peritaje / Survey Report en Destino:", value="SURV-CHL-2026-88")
            
        if st.button("📄 Generar Descargo de Mermas en PDF", type="primary"):
            pdf_bytes_m, ext_m = generate_descargo_mermas_pdf(
                empresa_nombre, empresa_cuit, banco_m, pe_m, fob_m, cobrado_m, nc_m, survey_m, empresa_firmante, empresa_cargo
            )
            mime_m = "application/pdf" if ext_m == "pdf" else "text/plain"
            st.download_button(f"📥 Descargar Nota Oficial ({ext_m.upper()})", data=pdf_bytes_m, file_name=f"descargo_mermas_{pe_m}.{ext_m}", mime=mime_m)

    with tab_zona_prim:
        st.markdown("#### Solicitud de Desafectación por Venta en Zona Primaria Aduanera")
        st.write("Aplica cuando la mercadería amparada en un Permiso oficializado se cedió/vendió localmente en pesos antes de embarcar.")
        
        cz1, cz2 = st.columns(2)
        with cz1:
            banco_z = st.selectbox("Banco Nominado:", ["Banco Santander", "Banco Galicia", "Banco BBVA", "Banco Macro", "Banco Nación", "Banco ICBC", "Otro"], key="bz_expo")
            pe_z = st.text_input("N° de Permiso de Embarque oficializado:", value="26001EC01009988K")
        with cz2:
            comprador_z = st.text_input("Razón Social del Comprador Local:", value="Distribuidora Nacional S.R.L.")
            factura_z = st.text_input("N° Factura Comercial Local (ARCA):", value="00012-00004567")
            
        if st.button("📄 Generar Nota de Venta en Zona Primaria en PDF", type="primary"):
            pdf_bytes_z, ext_z = generate_zona_primaria_pdf(
                empresa_nombre, empresa_cuit, banco_z, pe_z, comprador_z, factura_z, empresa_firmante, empresa_cargo
            )
            mime_z = "application/pdf" if ext_z == "pdf" else "text/plain"
            st.download_button(f"📥 Descargar Nota Oficial ({ext_z.upper()})", data=pdf_bytes_z, file_name=f"descargo_zona_primaria_{pe_z}.{ext_z}", mime=mime_z)

    with tab_imputa_b02:
        st.markdown("#### Imputación de Permiso de Embarque a Boleto de Anticipo B02")
        st.write("Instruye al banco a cruzar un nuevo Permiso cumplido contra un cobro anticipado cobrado con anterioridad.")
        
        cb1, cb2 = st.columns(2)
        with cb1:
            banco_b = st.selectbox("Banco Nominado:", ["Banco Santander", "Banco Galicia", "Banco BBVA", "Banco Macro", "Banco Nación", "Banco ICBC", "Otro"], key="bb_expo")
            pe_b = st.text_input("N° de Permiso de Embarque Cumplido:", value="26001EC01003344J")
        with cb2:
            boleto_b = st.text_input("N° de Boleto / Operación de Anticipo B02:", value="BCC-2026-004412")
            monto_b = st.number_input("Monto a Afectar (USD):", value=30000.0)
            
        if st.button("📄 Generar Instrucción de Imputación B02 en PDF", type="primary"):
            pdf_bytes_b, ext_b = generate_imputacion_b02_pdf(
                empresa_nombre, empresa_cuit, banco_b, pe_b, boleto_b, monto_b, empresa_firmante, empresa_cargo
            )
            mime_b = "application/pdf" if ext_b == "pdf" else "text/plain"
            st.download_button(f"📥 Descargar Nota Oficial ({ext_b.upper()})", data=pdf_bytes_b, file_name=f"afectacion_b02_{pe_b}.{ext_b}", mime=mime_b)
