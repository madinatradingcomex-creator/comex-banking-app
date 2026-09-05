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

st.set_page_config(
    page_title="COMEX Asistente Bancario | BCRA & ARCA",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header {
        font-size: 26px;
        font-weight: 700;
        color: #0F172A;
        margin-bottom: 2px;
    }
    .sub-header {
        font-size: 14px;
        color: #64748B;
        margin-bottom: 20px;
    }
    .metric-card {
        background: #FFFFFF;
        padding: 16px;
        border-radius: 10px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/bank-building.png", width=64)
    st.markdown("### **COMEX Asistente Bancario**")
    st.caption("Régimen Informativo BCRA & ARCA | Para PyMEs")
    st.divider()
    
    menu = st.radio(
        "Navegación del Sistema:",
        [
            "🏠 Asistente Rápido (TurboTax Comex)",
            "📊 Traductor de Sábana Bancaria",
            "📦 Asistente de Importaciones (Impo)",
            "🚢 Asistente de Exportaciones (Expo & B09)",
            "📝 Generador de Notas y Descargos",
            "🌐 Publicar en un Link Web (Guía)"
        ]
    )
    
    st.divider()
    st.markdown("**Datos de la Empresa / Consultora:**")
    default_empresa = st.text_input("Razón Social:", value="Mi Empresa S.A.", key="side_empresa")
    default_cuit = st.text_input("CUIT:", value="30-71234567-8", key="side_cuit")
    default_firmante = st.text_input("Firmante / Apoderado:", value="Juan Perez", key="side_firmante")
    default_cargo = st.text_input("Cargo:", value="Socio Gerente / Apoderado", key="side_cargo")

if menu == "🏠 Asistente Rápido (TurboTax Comex)":
    st.markdown('<div class="main-header">🏠 Asistente Guiado de Comercio Exterior</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Respondé 3 preguntas simples y te decimos qué concepto aplicar, qué plazos tenés y qué documentación te pedirá el banco.</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1.2, 1])
    
    with col1:
        st.markdown("#### **Paso 1: ¿Qué tipo de operación estás realizando?**")
        tipo_op = st.selectbox(
            "Seleccioná la operación:",
            [
                "🚢 Exportación de Bienes (Venta de productos al exterior)",
                "📦 Importación de Bienes (Compra de mercadería al exterior)",
                "💻 Exportación de Servicios (Factura E / Software, Consultoría, etc.)",
                "🌐 Tráfico Internacional / Cross-Trade (Venta directa de un país a otro sin pasar por Argentina - B09)"
            ]
        )
        
        if "Exportación de Bienes" in tipo_op:
            st.markdown("#### **Paso 2: ¿En qué momento se encuentra el cobro?**")
            momento_expo = st.radio(
                "Momento del cobro:",
                [
                    "Cobro luego de haber embarcado (Tengo Permiso de Embarque cumplido)",
                    "Cobro por anticipado (Aún no embarqué la mercadería)",
                    "Crédito / Financiación del exterior para exportar"
                ]
            )
            
            cat_ncm = st.selectbox(
                "¿Qué tipo de producto es?",
                options=list(CATEGORIAS_NCM_EXPO.keys()),
                format_func=lambda x: CATEGORIAS_NCM_EXPO[x]["nombre"]
            )
            
            es_vinculada = st.checkbox("¿El comprador del exterior es una empresa vinculada / del mismo grupo?", value=False)
            fecha_cumplido = st.date_input("Fecha de Cumplido de Embarque en Aduana:", value=date.today())
            res_expo = calculate_expo_deadline(fecha_cumplido, cat_ncm, es_vinculada)
            
        elif "Importación de Bienes" in tipo_op:
            st.markdown("#### **Paso 2: ¿En qué momento se paga al proveedor?**")
            momento_impo = st.radio(
                "Momento del pago:",
                [
                    "Pago Anticipado (Antes de que la mercadería llegue o se embarque)",
                    "Pago A la Vista (Mercadería embarcada con B/L en mano, antes de nacionalizar)",
                    "Pago Diferido (Mercadería ya nacionalizada con Despacho a Plaza SIM)",
                    "Pago de Bienes de Capital (Maquinaria / Equipamiento BK)"
                ]
            )
            fecha_pago = st.date_input("Fecha de pago / transferencia:", value=date.today())
            
        elif "Servicios" in tipo_op:
            concepto_serv = st.selectbox(
                "Tipo de servicio prestado:",
                ["S24 - Informática, software y tecnología", "S22 - Consultoría, jurídica, contable y administración"]
            )
            
        elif "Cross-Trade" in tipo_op:
            st.info("💡 **Operación B09 (Compraventa de bienes sin paso por el país)**: La mercadería viaja directo entre terceros países. No hay Despacho ni Permiso SIM en Argentina.")

    with col2:
        st.markdown("#### 📋 **Dictamen y Diagnóstico Instantáneo**")
        
        if "Exportación de Bienes" in tipo_op:
            if "Cobro luego de haber embarcado" in momento_expo:
                cod = "B01"
            elif "Cobro por anticipado" in momento_expo:
                cod = "B02"
            else:
                cod = "B03"
                
            info = CONCEPTOS_SERIE_B[cod]
            sem = res_expo["semaforo"]
            
            st.markdown(f"""
            <div class="metric-card">
                <h4 style="margin:0; color:#0B5ED7;">Concepto BCRA sugerido: <strong>{cod}</strong></h4>
                <p style="margin:4px 0; color:#475569;">{info['descripcion']}</p>
                <hr style="margin:8px 0;"/>
                <p><strong>Plazo normativo base:</strong> {res_expo['plazo_dias_aplicado']} días corridos.</p>
                <p><strong>Fecha límite de liquidación:</strong> <span style="font-weight:bold; color:#B91C1C;">{res_expo['fecha_limite']}</span></p>
                <p><strong>Días restantes:</strong> {res_expo['dias_restantes']} días ({sem['color']} {sem['estado']})</p>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(f"**{sem['accion']}**")
            st.markdown("**Documentos que te va a pedir el banco:**")
            for d in info["docs_requeridos"]:
                st.markdown(f"- 📄 {d}")
                
        elif "Importación de Bienes" in tipo_op:
            if "Pago Anticipado" in momento_impo:
                cod = "B05"
            elif "Pago A la Vista" in momento_impo:
                cod = "B07"
            elif "Pago Diferido" in momento_impo:
                cod = "B06"
            else:
                cod = "B12"
                
            info = CONCEPTOS_SERIE_B[cod]
            res_impo = calculate_sepaimpo_deadline(fecha_pago, cod)
            sem = res_impo["semaforo"]
            
            st.markdown(f"""
            <div class="metric-card">
                <h4 style="margin:0; color:#0B5ED7;">Concepto BCRA sugerido: <strong>{cod}</strong></h4>
                <p style="margin:4px 0; color:#475569;">{info['descripcion']}</p>
                <hr style="margin:8px 0;"/>
                <p><strong>Plazo para demostrar ingreso aduanero:</strong> {res_impo['plazo_dias_otorgado']} días.</p>
                <p><strong>Fecha límite en SEPAIMPO:</strong> <span style="font-weight:bold; color:#B91C1C;">{res_impo['fecha_limite_demostracion']}</span></p>
                <p><strong>Días restantes:</strong> {res_impo['dias_restantes']} días ({sem['color']} {sem['estado']})</p>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(f"**{sem['accion']}**")
            st.markdown("**Documentos que te va a pedir el banco:**")
            for d in info["docs_requeridos"]:
                st.markdown(f"- 📄 {d}")
                
        elif "Cross-Trade" in tipo_op:
            info = CONCEPTOS_SERIE_B["B09"]
            st.markdown(f"""
            <div class="metric-card">
                <h4 style="margin:0; color:#0B5ED7;">Concepto BCRA: <strong>B09</strong></h4>
                <p style="margin:4px 0; color:#475569;">{info['descripcion']}</p>
                <hr style="margin:8px 0;"/>
                <p><strong>Plazo de liquidación del cobro:</strong> 5 días hábiles desde acreditación en el exterior.</p>
                <p><strong>Control bancario clave:</strong> Demostrar que el cobro es mayor a la compra (margen comercial positivo).</p>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("**Documentos que te va a pedir el banco:**")
            for d in info["docs_requeridos"]:
                st.markdown(f"- 📄 {d}")
                
        elif "Servicios" in tipo_op:
            st.markdown("""
            <div class="metric-card">
                <h4 style="margin:0; color:#0B5ED7;">Régimen de Exportación de Servicios</h4>
                <p><strong>Plazo legal de liquidación:</strong> 5 días hábiles desde la percepción en cuenta bancaria del exterior o billetera.</p>
                <p><strong>Documentos exigidos:</strong> Factura E emitida en ARCA + Comprobante de cobro internacional.</p>
            </div>
            """, unsafe_allow_html=True)

elif menu == "📊 Traductor de Sábana Bancaria":
    st.markdown('<div class="main-header">📊 Traductor de Sábanas de Banco (SEPAIMPO / SECOEXPO)</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Subí el Excel que te mandó el oficial de Comex de tu banco (Galicia, Santander, Macro, BBVA, etc.) y te decimos exactamente qué tenés que hacer fila por fila.</div>', unsafe_allow_html=True)
    
    col_up, col_demo = st.columns([2, 1])
    with col_up:
        uploaded_file = st.file_uploader("Arrastrá o seleccioná tu archivo Excel (.xlsx / .xls) o CSV:", type=["xlsx", "xls", "csv"])
    with col_demo:
        st.markdown("**¿No tenés un archivo a mano?**")
        use_demo_expo = st.button("Cargar Ejemplo SECOEXPO (Expo)")
        use_demo_impo = st.button("Cargar Ejemplo SEPAIMPO (Impo)")
        
    df_raw = None
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith(".csv"):
                df_raw = pd.read_csv(uploaded_file)
            else:
                df_raw = pd.read_excel(uploaded_file)
            st.success(f"✅ Archivo cargado con éxito: {uploaded_file.name}")
        except Exception as e:
            st.error(f"Error al leer el archivo: {e}")
    elif use_demo_expo:
        df_raw = get_demo_secoexpo_data()
        st.info("ℹ️ Cargando sábana de demostración de SECOEXPO.")
    elif use_demo_impo:
        df_raw = get_demo_sepaimpo_data()
        st.info("ℹ️ Cargando sábana de demostración de SEPAIMPO.")
        
    if df_raw is not None and not df_raw.empty:
        processed_df, regime_detected, stats = parse_sabana_dataframe(df_raw)
        st.divider()
        st.markdown(f"### **Régimen Identificado:** `{regime_detected}`")
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Operaciones", stats["total_operaciones"])
        m2.metric("Monto Total Pendiente", f"USD {stats['monto_total_usd']:,.2f}")
        m3.metric("🚨 En Mora / Vencidas", stats["en_mora"], delta_color="inverse")
        m4.metric("⚠️ Riesgo Alto (< 15 días)", stats["en_riesgo_alto"], delta_color="inverse")
        
        st.markdown("#### **Tabla de Operaciones Traducida a Lenguaje Simple**")
        st.dataframe(
            processed_df[["Identificador", "Banco Nominado", "Monto Pendiente (USD)", "Fecha Límite", "Días Restantes", "Estado Semáforo", "Acción Sugerida"]],
            use_container_width=True,
            hide_index=True
        )
        
        csv_data = processed_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Descargar Informe de Diagnóstico en CSV",
            data=csv_data,
            file_name=f"diagnostico_{regime_detected.lower()}_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

elif menu == "📦 Asistente de Importaciones (Impo)":
    st.markdown('<div class="main-header">📦 Asistente y Auditor de Importaciones</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Validación de requisitos documentarios, candados de acceso al MLC y fletes conexos.</div>', unsafe_allow_html=True)
    
    tab_calc, tab_candados, tab_fletes = st.tabs(["🗓️ Calculador de Pagos Impo", "🔒 Candados de Acceso al MLC (DDJJ)", "🚢 Fletes y Seguros (S13/S14)"])
    
    with tab_calc:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### Datos de la Importación")
            despacho_nro = st.text_input("N° de Despacho SIM (si tiene):", value="26001IC04001234A")
            concepto_impo = st.selectbox("Concepto de Pago:", ["B05 (Anticipado)", "B06 (Diferido)", "B07 (A la vista)", "B12 (Bienes de Capital)"])
            monto_impo = st.number_input("Monto en Divisa (USD):", value=50000.0, step=1000.0)
            fecha_giro = st.date_input("Fecha de Giro / Transferencia:", value=date.today())
            
        with c2:
            cod = concepto_impo.split(" ")[0]
            info = CONCEPTOS_SERIE_B.get(cod, {})
            res = calculate_sepaimpo_deadline(fecha_giro, cod)
            sem = res["semaforo"]
            
            st.markdown(f"""
            <div class="metric-card">
                <h4 style="color:#0B5ED7;">Estado SEPAIMPO: {cod}</h4>
                <p>{info.get('descripcion', '')}</p>
                <hr/>
                <p><strong>Plazo de Demostración:</strong> {res['plazo_dias_otorgado']} días corridos.</p>
                <p><strong>Fecha Límite para Demostrar Despacho:</strong> <span style="color:#B91C1C; font-weight:bold;">{res['fecha_limite_demostracion']}</span></p>
                <p><strong>Días Restantes:</strong> {res['dias_restantes']} días ({sem['color']} {sem['estado']})</p>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(f"**{sem['accion']}**")
            
    with tab_candados:
        st.markdown("#### Validación de 'Candados' y Declaraciones Juradas")
        st.caption("Los bancos no transfieren si alguno de estos puntos está en rojo.")
        
        mep_check = st.checkbox("¿La empresa, socios o directores vendieron títulos con liquidación en moneda extranjera (Dólar MEP / CCL) en los últimos 90/180 días?", value=False)
        activos_check = st.checkbox("¿La empresa tiene más de USD 100.000 líquidos disponibles en cuentas del exterior?", value=False)
        com6401_check = st.checkbox("¿Tiene al día las presentaciones del Relevamiento de Activos y Pasivos Externos (Com. A 6401)?", value=True)
        
        val_res = validate_candados_access(mep_check, activos_check, com6401_check)
        if val_res["apto_para_acceder_mlc"]:
            st.success("✅ **APTO PARA ACCEDER AL MERCADO LIBRE DE CAMBIOS**: Cumple con todas las declaraciones juradas normativas.")
        else:
            st.error(f"❌ **NO APTO PARA ACCEDER AL MLC ({val_res['cantidad_inconsistencias']} inconsistencias detectadas)**")
            for inc in val_res["inconsistencias"]:
                st.warning(f"**{inc['candado']} ({inc['estado']}):** {inc['detalle']}")

    with tab_fletes:
        st.markdown("#### Tratamiento de Fletes y Seguros Conexos")
        incoterm = st.selectbox("Incoterm de la Factura Comercial:", ["FOB / FCA (Flete NO incluido)", "CFR / CIF (Flete incluido en el precio)"])
        if "FOB" in incoterm:
            st.info("💡 **Factura FOB:** El flete internacional se paga aparte. Si se paga al armador exterior, se utiliza el concepto **S13** con factura de flete y B/L. Si se paga a una agencia marítima local en pesos, no requiere acceso al MLC del importador.")
        else:
            st.success("💡 **Factura CFR / CIF:** El flete ya está incluido en el valor del bien y se paga todo junto bajo el concepto B de la mercadería.")

elif menu == "🚢 Asistente de Exportaciones (Expo & B09)":
    st.markdown('<div class="main-header">🚢 Asistente de Exportaciones & Operaciones Especiales</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Cálculo de plazos legales de liquidación, gestión de cobros anticipados B02 y cross-trade B09.</div>', unsafe_allow_html=True)
    
    tab_expo_calc, tab_b09, tab_mermas = st.tabs(["🗓️ Calculador de Plazos SECOEXPO", "🌐 Tráfico Triangular (B09)", "⚖️ Mermas y Descuentos"])
    
    with tab_expo_calc:
        c1, c2 = st.columns(2)
        with c1:
            pe_input = st.text_input("N° de Permiso de Embarque:", value="26001EC01004567Z")
            fob_monto = st.number_input("Valor FOB en Dólares (USD):", value=80000.0, step=1000.0)
            fecha_cumplido_input = st.date_input("Fecha de Cumplido de Embarque:", value=date.today())
            cat_selected = st.selectbox("Categoría NCM:", options=list(CATEGORIAS_NCM_EXPO.keys()), format_func=lambda x: CATEGORIAS_NCM_EXPO[x]["nombre"])
            es_vinc = st.checkbox("¿Comprador vinculado?", value=False)
            
        with c2:
            res_e = calculate_expo_deadline(fecha_cumplido_input, cat_selected, es_vinc)
            sem_e = res_e["semaforo"]
            
            st.markdown(f"""
            <div class="metric-card">
                <h4 style="color:#0B5ED7;">Estado SECOEXPO: {pe_input}</h4>
                <p><strong>Valor FOB:</strong> USD {fob_monto:,.2f}</p>
                <hr/>
                <p><strong>Plazo legal aplicable:</strong> {res_e['plazo_dias_aplicado']} días corridos.</p>
                <p><strong>Fecha Límite Improrrogable:</strong> <span style="color:#B91C1C; font-weight:bold;">{res_e['fecha_limite']}</span></p>
                <p><strong>Días Restantes:</strong> {res_e['dias_restantes']} días ({sem_e['color']} {sem_e['estado']})</p>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(f"**{sem_e['accion']}**")
            
    with tab_b09:
        st.markdown("#### Operaciones Triangulares / Cross-Trade (Concepto B09)")
        st.write("La mercadería no ingresa físicamente a Argentina (compra en país A, venta en país B).")
        
        c_buy, c_sell = st.columns(2)
        with c_buy:
            monto_compra = st.number_input("Monto Factura de Compra (USD):", value=60000.0)
            pais_origen = st.text_input("País de Origen de la Mercadería:", value="China")
        with c_sell:
            monto_venta = st.number_input("Monto Factura de Venta (USD):", value=75000.0)
            pais_destino = st.text_input("País de Destino Final:", value="Chile")
            
        margen = monto_venta - monto_compra
        if margen > 0:
            st.success(f"✅ **Resultado Comercial Positivo:** Margen de USD {margen:,.2f} (+{(margen/monto_compra)*100:.1f}%). Apto para cursar bajo concepto B09.")
        else:
            st.error(f"❌ **Margen Negativo:** El monto de venta debe ser superior al de compra para justificar la operación ante el BCRA.")

    with tab_mermas:
        st.markdown("#### Ajustes sobre el Valor FOB por Mermas o Descuentos")
        fob_orig = st.number_input("Valor FOB Permiso SIM (USD):", value=50000.0)
        monto_rec = st.number_input("Monto cobrado/liquidado (USD):", value=45000.0)
        dif = fob_orig - monto_rec
        if dif > 0:
            st.warning(f"⚠️ **Diferencia abierta en SECOEXPO:** USD {dif:,.2f}. Requiere Nota de Crédito 'E' + Survey Report para cerrar el PE.")

elif menu == "📝 Generador de Notas y Descargos":
    st.markdown('<div class="main-header">📝 Generador de Notas Bancarias y Descargos</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Generá cartas con formato oficial listas para firmar y presentar en la Mesa de Comex de cualquier banco.</div>', unsafe_allow_html=True)
    
    banco_sel = st.selectbox("Banco Destinatario:", ["Banco Santander Argentina", "Banco Galicia", "Banco BBVA Argentina", "Banco Macro", "Banco de la Nacion Argentina", "Banco ICBC", "Otro"])
    tipo_nota = st.selectbox(
        "Tipo de Nota a Generar:",
        [
            "1. Solicitud de Prórroga de Plazo de Demostración (SEPAIMPO)",
            "2. Descargo por Mermas y Descuentos Comerciales (SECOEXPO)",
            "3. Solicitud de Desafectación por Venta en Zona Primaria Aduanera",
            "4. Instrucción de Afectación de Permiso a Boleto de Anticipo B02"
        ]
    )
    
    st.divider()
    
    if "1. Solicitud de Prórroga" in tipo_nota:
        col_a, col_b = st.columns(2)
        with col_a:
            op_nro = st.text_input("N° de Operación / Boleto BVC:", value="OP-2026-99482")
            monto_p = st.number_input("Importe Transferido (USD):", value=45000.0)
        with col_b:
            bl_nro = st.text_input("N° de Documento de Transporte (B/L):", value="MEDU12345678")
            motivo_p = st.text_area("Motivo de la demora:", value="Retraso logístico internacional en buque por congestión en puerto de transbordo.")
            
        if st.button("📄 Generar Nota de Prórroga", type="primary"):
            doc_bytes, ext = generate_prorroga_sepaimpo_pdf(
                default_empresa, default_cuit, banco_sel, op_nro, monto_p, bl_nro, motivo_p, default_firmante, default_cargo
            )
            mime_type = "application/pdf" if ext == "pdf" else "text/plain"
            st.download_button(f"📥 Descargar Nota Oficial ({ext.upper()})", data=doc_bytes, file_name=f"prorroga_sepaimpo_{op_nro}.{ext}", mime=mime_type)
            
    elif "2. Descargo por Mermas" in tipo_nota:
        col_a, col_b = st.columns(2)
        with col_a:
            pe_nro_m = st.text_input("N° de Permiso de Embarque:", value="26001EC01004567Z")
            fob_orig_m = st.number_input("Valor FOB Declarado (USD):", value=80000.0)
            monto_rec_m = st.number_input("Importe Cobrado (USD):", value=72000.0)
        with col_b:
            nc_nro = st.text_input("N° de Nota de Crédito E (ARCA):", value="00005-00001234")
            survey_nro = st.text_input("N° de Peritaje / Survey Report en Destino:", value="SURV-CHL-2026-88")
            
        if st.button("📄 Generar Descargo de Mermas", type="primary"):
            doc_bytes, ext = generate_descargo_mermas_pdf(
                default_empresa, default_cuit, banco_sel, pe_nro_m, fob_orig_m, monto_rec_m, nc_nro, survey_nro, default_firmante, default_cargo
            )
            mime_type = "application/pdf" if ext == "pdf" else "text/plain"
            st.download_button(f"📥 Descargar Descargo Oficial ({ext.upper()})", data=doc_bytes, file_name=f"descargo_mermas_{pe_nro_m}.{ext}", mime=mime_type)

    elif "3. Solicitud de Desafectación por Venta en Zona Primaria" in tipo_nota:
        col_a, col_b = st.columns(2)
        with col_a:
            pe_nro_z = st.text_input("N° de Permiso de Embarque:", value="26001EC01009988K")
            comprador_loc = st.text_input("Razón Social del Comprador Local:", value="Distribuidora Nacional S.R.L.")
        with col_b:
            factura_loc = st.text_input("N° Factura Comercial Local (ARCA):", value="00012-00004567")
            
        if st.button("📄 Generar Nota de Venta en Zona Primaria", type="primary"):
            doc_bytes, ext = generate_zona_primaria_pdf(
                default_empresa, default_cuit, banco_sel, pe_nro_z, comprador_loc, factura_loc, default_firmante, default_cargo
            )
            mime_type = "application/pdf" if ext == "pdf" else "text/plain"
            st.download_button(f"📥 Descargar Nota Oficial ({ext.upper()})", data=doc_bytes, file_name=f"descargo_zona_primaria_{pe_nro_z}.{ext}", mime=mime_type)

    elif "4. Instrucción de Afectación de Permiso a Boleto de Anticipo B02" in tipo_nota:
        col_a, col_b = st.columns(2)
        with col_a:
            pe_nro_b2 = st.text_input("N° de Permiso de Embarque Cumplido:", value="26001EC01003344J")
            monto_b2 = st.number_input("Monto a Afectar (USD):", value=30000.0)
        with col_b:
            boleto_b2 = st.text_input("N° de Boleto / Operación de Anticipo B02:", value="BCC-2026-004412")
            
        if st.button("📄 Generar Nota de Afectación B02", type="primary"):
            doc_bytes, ext = generate_imputacion_b02_pdf(
                default_empresa, default_cuit, banco_sel, pe_nro_b2, boleto_b2, monto_b2, default_firmante, default_cargo
            )
            mime_type = "application/pdf" if ext == "pdf" else "text/plain"
            st.download_button(f"📥 Descargar Nota Oficial ({ext.upper()})", data=doc_bytes, file_name=f"afectacion_b02_{pe_nro_b2}.{ext}", mime=mime_type)

elif menu == "🌐 Publicar en un Link Web (Guía)":
    st.markdown('<div class="main-header">🌐 Cómo Publicar este Sistema en un Link Web Gratuito</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Pasos para dejar activa tu aplicación con una dirección web pública permanente para acceder desde cualquier dispositivo.</div>', unsafe_allow_html=True)
    
    st.markdown("""
    ### 🚀 Paso a Paso de Publicación (en 3 minutos):

    1. **Crear una cuenta gratuita en GitHub:**
       * Entrá a [github.com](https://github.com) y creá una cuenta si no tenés una.
       * Creá un nuevo repositorio (ej. `comex-banking-app`) y subí esta carpeta con todos sus archivos.

    2. **Conectar con Streamlit Community Cloud (Gratis y Oficial):**
       * Entrá a [share.streamlit.io](https://share.streamlit.io) e iniciá sesión con tu cuenta de GitHub.
       * Hacé clic en **"New App"**.
       * Seleccioná tu repositorio `comex-banking-app` y como archivo principal elegí `app.py`.
       * Hacé clic en **"Deploy"**.

    3. **¡Listo! Tu Link Web está Activo:**
       * En 60 segundos la plataforma te otorga un link público (ej. `https://comex-consulting.streamlit.app`).
       * Podés compartir este link con tus clientes o usarlo vos mismo desde cualquier computadora, tablet o teléfono.
    """)
