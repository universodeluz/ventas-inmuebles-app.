import streamlit as st
import pandas as pd

# Configuración de la página
st.set_page_config(
    page_title="Ventas Inmuebles Venezuela | Hub Digital",
    page_icon="🏢",
    layout="centered"
)

st.title("🏢 Ventas Inmuebles Venezuela")
st.caption("Conectando compradores, propietarios y tecnología inmobiliaria en Isla de Margarita y Gran Caracas.")

# --- CONEXIÓN A GOOGLE SHEETS ---
# Reemplaza con el enlace CSV público de tu Google Sheet de inventario
SHEET_URL = "https://docs.google.com/spreadsheets/d/1AkLUKg1FgjgEPeJmSY9oE-1v2Sgld8-4wsu8og3XMEU/edit/export?format=csv"

@st.cache_data(ttl=300)
def cargar_inventario(url):
    try:
        df = pd.read_csv(url)
        return df
    except Exception as e:
        return None

df_inmuebles = cargar_inventario(SHEET_URL)

# Enlace de WhatsApp principal
MI_NUMERO_WA = "584120000000"  # Cambia por tu número real

# CREACIÓN DE PESTAÑAS (TABS)
tab_comprador, tab_vendedor, tab_ia = st.tabs([
    "🔍 Buscar Inmueble", 
    "📝 Publicar Inmueble", 
    "🤖 Tasación e Inspección IA"
])

# =========================================================
# PESTAÑA 1: COMPRADORES (BÚSQUEDA Y REQUERIMIENTO)
# =========================================================
with tab_comprador:
    st.subheader("Búsqueda de Inmuebles y Registro de Requerimiento")
    st.markdown("Filtra las opciones disponibles o registra tu solicitud exacta para recibir propuestas personalizadas.")
    
    with st.form("form_comprador"):
        nicho = st.selectbox(
            "Selecciona la ubicación:",
            ["Isla de Margarita", "Gran Caracas (Caracas, Miranda, La Guaira)"]
        )
        operacion = st.radio("Operación:", ["Comprar", "Alquilar"])
        tipo_inmueble = st.selectbox(
            "Tipo de propiedad:",
            ["Apartamento", "Casa", "Townhouse", "Local Comercial", "Terreno", "Oficina"]
        )
        presupuesto_max = st.number_input("Presupuesto máximo ($):", min_value=0, value=50000, step=2500)
        
        st.markdown("---")
        st.markdown("**Datos de Contacto**")
        nombre_c = st.text_input("Nombre y Apellido:", key="nombre_c")
        telefono_c = st.text_input("WhatsApp (ej: +58412...):", key="tel_c")
        
        btn_comprador = st.form_submit_button("🔍 Ver Coincidencias y Enviar Requerimiento")

    if btn_comprador:
        if not nombre_c or not telefono_c:
            st.error("Por favor ingresa tu nombre y teléfono de contacto.")
        else:
            inmuebles_compatibles = []
            if df_inmuebles is not None and not df_inmuebles.empty:
                # Filtrado en la base de datos
                filtrados = df_inmuebles[
                    (df_inmuebles['nicho'].str.contains(nicho, case=False, na=False)) &
                    (df_inmuebles['operacion'].str.contains(operacion, case=False, na=False)) &
                    (df_inmuebles['tipo'].str.contains(tipo_inmueble, case=False, na=False)) &
                    (df_inmuebles['precio'] <= presupuesto_max)
                ]
                
                if not filtrados.empty:
                    st.success("✨ ¡Encontramos propiedades coincidentes!")
                    for idx, row in filtrados.iterrows():
                        st.markdown(f"**🏠 {row['titulo']}**")
                        st.markdown(f"💰 **Precio:** ${row['precio']} | 📍 **Zona:** {row['nicho']}")
                        if 'enlace_foto_o_info' in row and pd.notna(row['enlace_foto_o_info']):
                            st.markdown(f"[📷 Ver Galería / Ficha Técnica]({row['enlace_foto_o_info']})")
                        st.markdown("---")
                        inmuebles_compatibles.append(str(row['titulo']))
                else:
                    st.info("No tenemos una coincidencia exacta de inmediato, pero guardamos tu requerimiento para avisarte en cuanto ingrese una opción.")
            else:
                st.info("Requerimiento registrado. Estamos actualizando el inventario digital.")

            # Formatear mensaje para WhatsApp
            msg_wa = (
                f"Hola, nuevo requerimiento de comprador:%0A"
                f"*Cliente:* {nombre_c} ({telefono_c})%0A"
                f"*Zona:* {nicho}%0A"
                f"*Operación:* {operacion} - {tipo_inmueble}%0A"
                f"*Presupuesto Máx:* ${presupuesto_max}%0A"
                f"*Opciones vistas:* {', '.join(inmuebles_compatibles) if inmuebles_compatibles else 'Ninguna inmediata'}"
            )
            link_wa = f"https://wa.me/{584124792652}?text={msg_wa}"
            
            st.markdown(
                f'<a href="{link_wa}" target="_blank" style="display:inline-block;padding:12px 20px;font-size:15px;font-weight:bold;color:white;background-color:#25D366;text-align:center;text-decoration:none;border-radius:8px;">📱 Enviar Requerimiento a WhatsApp</a>',
                unsafe_allow_html=True
            )

# =========================================================
# PESTAÑA 2: VENDEDORES / ALIADOS (REGISTRO DE INMUEBLE)
# =========================================================
with tab_vendedor:
    st.subheader("Publica o Registra tu Inmueble")
    st.markdown("Si eres propietario o corredor aliado, registra las características de tu propiedad para conectarte con compradores activos.")
    
    with st.form("form_vendedor"):
        nicho_v = st.selectbox(
            "Ubicación del inmueble:",
            ["Isla de Margarita", "Gran Caracas (Caracas, Miranda, La Guaira)"],
            key="nicho_v"
        )
        titulo_v = st.text_input("Título o breve descripción (ej: Apto 2Hab en Pampatar vista al mar):")
        tipo_v = st.selectbox("Tipo:", ["Apartamento", "Casa", "Townhouse", "Local Comercial", "Terreno", "Oficina"], key="tipo_v")
        operacion_v = st.radio("Operación:", ["Venta", "Alquiler"], key="op_v")
        precio_v = st.number_input("Precio ($ USD):", min_value=0, value=30000, step=1000)
        habitaciones_v = st.number_input("Habitaciones:", min_value=0, value=2)
        enlace_fotos = st.text_input("Enlace a fotos / Google Drive / Instagram / Dropbox:")
        
        st.markdown("---")
        nombre_v = st.text_input("Nombre del Propietario / Agente:", key="nombre_v")
        telefono_v = st.text_input("WhatsApp de Contacto:", key="tel_v")
        
        btn_vendedor = st.form_submit_button("📤 Registrar Inmueble para Inventario")
        
    if btn_vendedor:
        if not titulo_v or not telefono_v:
            st.error("Por favor completa al menos el título de la propiedad y tu número de teléfono.")
        else:
            st.success("¡Información procesada exitosamente!")
            
            msg_prop = (
                f"Hola, deseo publicar/registrar un inmueble:%0A"
                f"*Propiedad:* {titulo_v}%0A"
                f"*Ubicación:* {nicho_v}%0A"
                f"*Operación:* {operacion_v} | *Precio:* ${precio_v}%0A"
                f"*Habitaciones:* {habitaciones_v}%0A"
                f"*Fotos/Info:* {enlace_fotos}%0A"
                f"*Contacto:* {nombre_v} ({telefono_v})"
            )
            link_wa_v = f"https://wa.me/{584125792652}?text={msg_prop}"
            
            st.markdown(
                f'<a href="{link_wa_v}" target="_blank" style="display:inline-block;padding:12px 20px;font-size:15px;font-weight:bold;color:white;background-color:#25D366;text-align:center;text-decoration:none;border-radius:8px;">📱 Validar Publicación vía WhatsApp</a>',
                unsafe_allow_html=True
            )

# =========================================================
# PESTAÑA 3: ASISTENTE DE TASACIÓN E INSPECCIÓN VISUAL POR IA
# =========================================================
with tab_ia:
    st.subheader("🤖 Asistente de Tasación e Inspección Visual por IA")
    st.markdown("""
    Herramienta exclusiva impulsada por Inteligencia Artificial para **analizar fotos de inmuebles, evaluar el estado de conservación e inspección visual, y calcular la banda de precios sugerida** ajustada al mercado venezolano.
    """)
    
    st.info("💡 **Beneficio para Propietarios y Corredores:** Obtén una estimación de precio objetiva respaldada por datos antes de salir al mercado.")
    
    st.markdown("### ¿Cómo solicitar una prueba de Tasación por IA?")
    st.markdown("""
    1. Haz clic en el botón inferior para solicitar tu análisis.
    2. Envía las fotos principales del inmueble (fachada, cocina, baños, vista).
    3. Nuestro modelo de **Visión Artificial e Inspección Visual** procesará los detalles y te entregará el reporte estimado con la banda de precio sugerida para *Margarita* o *Gran Caracas*.
    """)
    
    # Enlace a WhatsApp o a tu modulo desplegado de Streamlit de Tasación
    msg_ia = "Hola, me interesa solicitar una Tasación e Inspección Visual por IA para evaluar mi inmueble."
    link_wa_ia = f"https://wa.me/{MI_NUMERO_WA}?text={msg_ia.replace(' ', '%20')}"
    
    st.markdown(
        f'<a href="{link_wa_ia}" target="_blank" style="display:inline-block;padding:14px 24px;font-size:16px;font-weight:bold;color:white;background-color:#007BFF;text-align:center;text-decoration:none;border-radius:8px;">🤖 Solicitar Tasación e Inspección Visual por IA</a>',
        unsafe_allow_html=True
          )
          
