# Catálogo Oficial de Códigos de Concepto BCRA y Reglas por Posición Arancelaria

CONCEPTOS_SERIE_B = {
    # --- EXPORTACIONES (Cobros / Ingresos) ---
    "B01": {
        "codigo": "B01",
        "tipo": "EXPO",
        "descripcion": "Cobros de exportaciones de bienes",
        "momento": "Post-embarque (mercadería cumplida en Aduana)",
        "plazo_adicional_dias": 5,
        "docs_requeridos": [
            "Permiso de Embarque (PE) cumplido en SIM",
            "Factura de Exportación E (WSFEX / ARCA)",
            "Documento de transporte internacional (B/L, AWB o CRT)"
        ],
        "impacto_bancario": "Imputa y cancela el saldo del Permiso de Embarque en SECOEXPO."
    },
    "B02": {
        "codigo": "B02",
        "tipo": "EXPO",
        "descripcion": "Cobros anticipados de exportaciones de bienes",
        "momento": "Previo al embarque de la mercadería",
        "plazo_imputacion_meses": 12,
        "docs_requeridos": [
            "Factura Proforma u Orden de Compra del exterior",
            "Contrato comercial o intercambio probatorio"
        ],
        "impacto_bancario": "Abre obligación en SECOEXPO. Requiere posterior afectación de PE cumplido."
    },
    "B03": {
        "codigo": "B03",
        "tipo": "EXPO",
        "descripcion": "Financiaciones del exterior por exportaciones de bienes",
        "momento": "Crédito pre-embarque o post-embarque otorgado desde el exterior",
        "docs_requeridos": [
            "Contrato de financiamiento del exterior",
            "Comprobante de ingreso de divisas Swift MT103"
        ],
        "impacto_bancario": "Genera pasivo a cancelar con la presentación de futuros PEs cumplidos."
    },
    "B04": {
        "codigo": "B04",
        "tipo": "EXPO",
        "descripcion": "Financiación de bancos locales por exportaciones de bienes",
        "momento": "Préstamo en moneda extranjera otorgado por banco local",
        "docs_requeridos": [
            "Pagaré / Acuerdo de línea crediticia comex local"
        ],
        "impacto_bancario": "Se liquida localmente a pesos y se cancela con las divisas del PE."
    },
    "B09": {
        "codigo": "B09",
        "tipo": "CROSS_TRADE",
        "descripcion": "Compraventa de bienes sin paso por el país y vendidos a terceros países",
        "momento": "Operación Triangular / Tráfico Internacional / Cross-Trade",
        "docs_requeridos": [
            "Factura Comercial de Compra (Proveedor país origen)",
            "Factura Comercial de Venta (Cliente país destino final)",
            "Documento de Transporte Internacional (B/L internacional origen-destino)",
            "Declaración Jurada de No Ingreso Aduanero a territorio argentino",
            "Cuadro de calce financiero demostrando margen comercial positivo"
        ],
        "impacto_bancario": "No abre SECOEXPO ni SEPAIMPO tradicional (sin SIM). Control de calce de divisas."
    },

    # --- IMPORTACIONES (Pagos / Egresos) ---
    "B05": {
        "codigo": "B05",
        "tipo": "IMPO",
        "descripcion": "Pagos anticipados de importaciones de bienes (excepto bienes de capital)",
        "momento": "Previo al embarque de la mercadería",
        "plazo_demostracion_dias": 90,
        "docs_requeridos": [
            "Factura Proforma o Contrato de Compraventa internacional",
            "Declaración SEDI oficializada en estado de salida (si aplica)",
            "Aval o garantía bancaria si supera los montos normativos"
        ],
        "impacto_bancario": "Abre registro pendiente en SEPAIMPO. Obliga a demostrar despacho en 90/180 días."
    },
    "B06": {
        "codigo": "B06",
        "tipo": "IMPO",
        "descripcion": "Pagos diferidos de importaciones de bienes",
        "momento": "Mercadería ya nacionalizada en Argentina",
        "docs_requeridos": [
            "Despacho de Importación a Plaza (SIM) oficializado y cancelado",
            "Factura Comercial definitiva del proveedor del exterior"
        ],
        "impacto_bancario": "Imputa y cancela el despacho en SEPAIMPO de forma directa."
    },
    "B07": {
        "codigo": "B07",
        "tipo": "IMPO",
        "descripcion": "Pagos a la vista de importaciones de bienes (excepto bienes de capital)",
        "momento": "Mercadería embarcada con B/L emitido, previo a nacionalización",
        "plazo_demostracion_dias": 90,
        "docs_requeridos": [
            "Factura Comercial definitiva",
            "Documento de Transporte Internacional (B/L 'Shipped on Board', AWB o CRT)"
        ],
        "impacto_bancario": "Abre registro en SEPAIMPO sujeto a demostración posterior del despacho a plaza."
    },
    "B08": {
        "codigo": "B08",
        "tipo": "IMPO",
        "descripcion": "Pagos por otras compras de bienes al exterior / Deudas comerciales con bancos",
        "momento": "Financiamiento bancario de importaciones",
        "docs_requeridos": ["Contrato de financiamiento", "Despacho o B/L"],
        "impacto_bancario": "Cancela deuda financiera de importación."
    },
    "B10": {
        "codigo": "B10",
        "tipo": "IMPO",
        "descripcion": "Pagos de deudas comerciales por importación sin registro de ingreso aduanero",
        "momento": "Cancelación de pasivos comerciales del exterior",
        "docs_requeridos": ["Contrato comercial", "Constancia Com. A 6401", "Estados contables"],
        "impacto_bancario": "Cancela pasivo comercial registrado."
    },
    "B12": {
        "codigo": "B12",
        "tipo": "IMPO",
        "descripcion": "Pagos anticipados de importaciones de bienes de capital (BK)",
        "momento": "Previo al embarque de maquinaria / Bienes de Capital",
        "plazo_demostracion_dias": 365,
        "docs_requeridos": [
            "Factura Proforma identificando posición arancelaria BK",
            "Garantía bancaria o contrato de suministro de maquinaria"
        ],
        "impacto_bancario": "Abre SEPAIMPO con plazo extendido de 365 días para demostrar despacho."
    }
}

CONCEPTOS_SERIE_S = {
    "S13": {
        "codigo": "S13",
        "tipo": "SERVICIOS_IMPO",
        "descripcion": "Servicios de fletes por transporte internacional de bienes",
        "docs_requeridos": ["Factura del transportista/armador exterior", "B/L (Freight Prepaid/Collect)"]
    },
    "S14": {
        "codigo": "S14",
        "tipo": "SERVICIOS_IMPO",
        "descripcion": "Servicios de seguros de transporte de mercaderías",
        "docs_requeridos": ["Póliza de seguro internacional", "Factura de la compañía aseguradora"]
    },
    "S22": {
        "codigo": "S22",
        "tipo": "SERVICIOS_EXPO",
        "descripcion": "Servicios jurídicos, contables, gerenciales y de consultoría",
        "plazo_dias_habiles": 5,
        "docs_requeridos": ["Factura E de exportación de servicios", "Contrato de prestación / Orden de servicio"]
    },
    "S24": {
        "codigo": "S24",
        "tipo": "SERVICIOS_EXPO",
        "descripcion": "Servicios de informática, software y tecnología",
        "plazo_dias_habiles": 5,
        "docs_requeridos": ["Factura E de exportación de servicios", "Comprobante de cobro internacional"]
    }
}

CATEGORIAS_NCM_EXPO = {
    "GRANOS_COMMODITIES": {
        "nombre": "Granos, Cereales, Oleaginosas y Subproductos (Cap. 10, 12, 15, 23)",
        "plazo_dias": 15,
        "tipo_dias": "corridos",
        "descripcion": "Plazo ultracorto regulado por el BCRA (o desde DJVE)."
    },
    "ECONOMIAS_REGIONALES": {
        "nombre": "Economías Regionales / Alimentos Elaborados / Carnes / Vinos / Frutas",
        "plazo_dias": 180,
        "tipo_dias": "corridos",
        "descripcion": "Plazo general para productos de agroindustria y manufacturas de origen agropecuario."
    },
    "MANUFACTURAS_MOI_PYME": {
        "nombre": "Manufacturas de Origen Industrial (MOI) / Bienes de Capital / PyMEs",
        "plazo_dias": 365,
        "tipo_dias": "corridos",
        "descripcion": "Plazo extendido de 365 días corridos para bienes industriales o empresas con Certificado MiPyME."
    },
    "EMPRESAS_VINCULADAS": {
        "nombre": "Operaciones entre Empresas Vinculadas (Cualquier NCM)",
        "plazo_dias": 60,
        "tipo_dias": "corridos",
        "descripcion": "Plazo recortado normativamente para evitar financiamiento intragrupo."
    }
}
