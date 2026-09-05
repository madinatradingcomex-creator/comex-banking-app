# ⚖️ COMEX Asistente Bancario & Consultoría (BCRA & ARCA)

Sistema integral y tech-enabled de consultoría sobre el **Régimen Informativo Bancario y Cambiario** en Argentina, enfocado en PyMEs y personas físicas (importadores, exportadores y servicios).

---

## 📁 Estructura del Proyecto

```
comex-banking-app/
├── app.py                      # Interfaz Web Principal interactiva (Streamlit)
├── requirements.txt            # Dependencias del proyecto
├── .streamlit/
│   └── config.toml             # Configuración visual e institucional
├── engine/
│   ├── __init__.py
│   ├── concepts_db.py          # Catálogo Oficial Serie B (B01-B12, B09) y Serie S
│   ├── rules_engine.py         # Cómputo de plazos NCM, semáforo de riesgo y candados MLC
│   ├── sabana_parser.py        # Traductor de sábanas bancarias (SEPAIMPO / SECOEXPO)
│   └── doc_generator.py        # Generador de notas oficiales y descargos en PDF/TXT
├── sample_data/
│   ├── secoexpo_ejemplo.csv    # Sábana de prueba SECOEXPO
│   └── sepaimpo_ejemplo.csv    # Sábana de prueba SEPAIMPO
└── docs/
    ├── 1_MANUAL_OPERATIVO_Y_NORMATIVO.md   # Guía exhaustiva de regímenes cambiarios
    ├── 2_ESTRATEGIA_COMERCIAL_Y_PRICING.md # Modelo de negocio, tarifas y ventas B2B
    └── 3_ARQUITECTURA_APRENDIZAJE.md       # Los 4 motores de aprendizaje continuo
```

---

## 🚀 Inicio Rápido

### Ejecución Local:
```bash
streamlit run app.py
```

### Despliegue en la Nube (Link Público Permanente):
1. Subir este directorio a un repositorio en **GitHub**.
2. Conectar con **Streamlit Community Cloud** (share.streamlit.io).
3. Seleccionar `app.py` y hacer clic en **Deploy**.
