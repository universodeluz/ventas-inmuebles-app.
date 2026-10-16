import streamlit as st
import pandas as pd

# Configuración de la página
st.set_page_config(
    page_title="Ventas Inmuebles Venezuela | Hub Digital",
    page_icon="🏢",
    layout="centered"
)

st.title("🏢 Ventas Inmuebles Venezuela")
st.caption("Conectando compradores, propietarios y tecnología inmobiliaria en Nueva Esparta y Región Capital/La Guaira.")

# --- CONEXIÓN A GOOGLE SHEETS ---
SHEET_URL = "https://docs.google.com/spreadsheets/d/1AkLUKg1FgjgEPeJmSY9oE-1v2Sgld8-4wsu8og3XMEU/export?format=csv"

# --- CONFIGURACIÓN DE CONTACTOS Y GRUPOS ---
# Tu número de WhatsApp de contacto privado (sin el +)
MI_NUMERO_WA = "584124792652" 

# PEGA AQUÍ LOS ENLACES DE INVITACIÓN REALES DE TUS GRUPOS DE WHATSAPP
LINK_GRUPO_MARGARITA = "https://chat.whatsapp.com/TU_ENLACE_MARGARITA_AQUI"
LINK_GRUPO_CARACAS = "https://chat.whatsapp.com/TU_ENLACE_CARACAS_AQUI"

@st.cache_data(ttl=300)
def cargar_inventario(url):
    try:
        df = pd.read_csv(url)
        return df
    except Exception as e:
        return None

df_inmuebles = cargar_inventario(SHEET_URL)

# --- BANNER SUPERIOR DE GRUPOS DE WHATSAPP ---
st.info("💬 **¿Quieres unirte a nuestras comunidades activas en WhatsApp?**")
col_top1, col_top2 = st.columns(2)
with col_top1:
    st.markdown(
        f'<a href="{LINK_GRUPO_MARGARITA}" target="_blank" style="display:block;padding:10px;font-size:13px;font-weight:bold;color:white;background-color:#25D366;text-align:center;text-decoration:none;border-radius:6px;">🌴 Grupo Margarita</a>',
        unsafe_allow_html=True
    )
with col_top2:
    st.markdown(
        f'<a href="{LINK_GRUPO_CARACAS}" target="_blank" style="display:block;padding:10px;font-size:13px;font-weight:bold;color:white;background-color:#25D366;text-align:center;text-decoration:none;border-radius:6px;">🏢 Grupo Caracas/La Guaira</a>',
        unsafe_allow_html=True
    )

st.markdown("---")

# LISTAS DE LOCALIDADES POR REGIÓN
LOCALIDADES_MARGARITA = [
    "Porlamar (Municipio Mariño)",
    "Pampatar (Municipio Maneiro)",
    "La Asunción (Municipio Arismendi)",
    "Juan Griego (Municipio Marcano)",
    "El Valle del Espíritu Santo (Municipio García)",
    "Playa El Agua / Manzanillo (Municipio Antolín del Campo)",
    "Punta de Piedras (Municipio Tubores)",
    "Boca de Pozo / San Francisco (Municipio Península de Macanao)",
    "Coche (Municipio Villalba)",
    "Otra localidad de Nueva Esparta"
]

LOCALIDADES_MIRANDA_BARLOVENTO = [
    "Andrés Bello: San José de Barlovento",
    "Páez: Río Chico",
    "Buroz: Mamporal",
    "Pedro Gual: Cúpira",
    "Área Metropolitana de Caracas / Miranda (Chacao, Baruta, El Hatillo, Sucre, etc.)",
    "Otra zona de Miranda"
]

LOCALIDADES_LA_GUAIRA = [
    "Catia La Mar",
    "Maiquetía",
    "La Guaira",
    "Macuto",
    "Caraballeda",
    "Naiguatá",
    "Caruao",
    "Otras localidades y sectores del Estado La Guaira"
]

# OPCIONES DE TIPOS DE INMUEBLES (INCLUYE POSADA / HOTEL)
TIPOS_INMUEBLES = [
    "Apartamento", 
    "Casa", 
    "Townhouse", 
    "Posada / Hotel", 
    "Local Comercial", 
    "Terreno", 
    "Oficina", 
    "Fondo de Comercio"
]

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
    
    with st.form("form_comprador"):
        nicho = st.selectbox(
            "Selecciona el Estado o Región principal:",
            ["Isla de Margarita (Nueva Esparta)", "Miranda (Eje Barlovento / Caracas)", "Estado La Guaira"]
        )
        
        if "Margarita" in nicho:
            localidad = st.selectbox("Selecciona la localidad o municipio:", LOCALIDADES_MARGARITA)
        elif "Miranda" in nicho:
            localidad = st.selectbox("Selecciona la localidad o municipio:", LOCALIDADES_MIRANDA_BARLOVENTO)
        else:
            localidad = st.selectbox("Selecciona la parroquia o sector:", LOCALIDADES_LA_GUAIRA)

        operacion = st.radio("Operación:", ["Comprar", "Alquilar"])
        tipo_inmueble = st.selectbox("Tipo de propiedad:", TIPOS_INMUEBLES)
        presupuesto_max = st.number_input("Presupuesto máximo ($):", min_value=0, value=50000, step=2500)
        
        st.markdown("---")
        st.markdown("**Datos de Contacto**")
        nombre_c = st.text_input("Nombre y Apellido:", key="nombre_c")
        telefono_c = st.text_input("WhatsApp (ej: 0412...):", key="tel_c")
        
        btn_comprador = st.form_submit_button("🔍 Ver Coincidencias y Enviar Requerimiento")

    if btn_comprador:
        if not nombre_c or not telefono_c:
            st.error("Por favor ingresa tu nombre y teléfono de contacto.")
        else:
            inmuebles_compatibles = []
            if df_inmuebles is not None and not df_inmuebles.empty:
                filtrados = df_inmuebles[
                    (df_inmuebles['operacion'].str.contains(operacion, case=False, na=False)) &
                    (df_inmuebles['tipo'].str.contains(tipo_inmueble, case=False, na=False)) &
                    (df_inmuebles['precio'] <= presupuesto_max)
                ]
                
                if not filtrados.empty:
                    st.success("✨ ¡Encontramos propiedades coincidentes!")
                    for idx, row in filtrados.iterrows():
                        st.markdown(f"**🏠 {row['titulo']}**")
                        st.markdown(f"💰 **Precio:** ${row['precio']} | 📍 **Zona:** {row['nicho']}")
                        if 'enlace_foto_o_info' in row and pd.notna(row['enlace_foto_o_info']) and str(row['enlace_foto_o_info']).strip() != "":
                            st.markdown(f"[📷 Ver Galería / Ficha Técnica]({row['enlace_foto_o_info']})")
                        st.markdown("---")
                        inmuebles_compatibles.append(str(row['titulo']))
                else:
                    st.info("No tenemos una coincidencia exacta de inmediato, pero guardamos tu requerimiento.")
            else:
                st.info("Requerimiento registrado con éxito.")

            msg_wa = (
                f"Hola, nuevo requerimiento de comprador:%0A"
                f"*Cliente:* {nombre_c} ({telefono_c})%0A"
                f"*Región:* {nicho}%0A"
                f"*Localidad/Sector:* {localidad}%0A"
                f"*Operación:* {operacion} - {tipo_inmueble}%0A"
                f"*Presupuesto Máx:* ${presupuesto_max}%0A"
                f"*Opciones vistas:* {', '.join(inmuebles_compatibles) if inmuebles_compatibles else 'Ninguna inmediata'}"
            )
            link_wa = f"https://wa.me/{MI_NUMERO_WA}?text={msg_wa}"
            
            st.markdown(
                f'<a href="{link_wa}" target="_blank" style="display:inline-block;padding:12px 20px;font-size:15px;font-weight:bold;color:white;background-color:#25D366;text-align:center;text-decoration:none;border-radius:8px;">📱 Enviar Requerimiento a WhatsApp</a>',
                unsafe_allow_html=True
            )

# =========================================================
# PESTAÑA 2: VENDEDORES / ALIADOS (REGISTRO DE INMUEBLE)
# =========================================================
with tab_vendedor:
    st.subheader("Publica o Registra tu Inmueble")
    
    with st.form("form_vendedor"):
        región_v = st.selectbox(
            "Estado o Región:",
            ["Isla de Margarita (Nueva Esparta)", "Miranda (Eje Barlovento / Caracas)", "Estado La Guaira"],
            key="reg_v"
        )
        
        if "Margarita" in región_v:
            localidad_v = st.selectbox("Localidad / Municipio:", LOCALIDADES_MARGARITA, key="loc_v_marg")
        elif "Miranda" in región_v:
            localidad_v = st.selectbox("Localidad / Municipio:", LOCALIDADES_MIRANDA_BARLOVENTO, key="loc_v_mir")
        else:
            localidad_v = st.selectbox("Localidad / Parroquia:", LOCALIDADES_LA_GUAIRA, key="loc_v_lag")

        titulo_v = st.text_input("Título o breve descripción (ej: Posada 8 hab en Playa El Agua):")
        tipo_v = st.selectbox("Tipo:", TIPOS_INMUEBLES, key="tipo_v")
        operacion_v = st.radio("Operación:", ["Venta", "Alquiler"], key="op_v")
        precio_v = st.number_input("Precio ($ USD):", min_value=0, value=30000, step=1000)
        enlace_fotos = st.text_input("Enlace a fotos / Google Drive / Instagram:")
        
        st.markdown("---")
        nombre_v = st.text_input("Nombre del Propietario / Agente:", key="nombre_v")
        telefono_v = st.text_input("WhatsApp de Contacto:", key="tel_v")
        
        btn_vendedor = st.form_submit_button("📤 Registrar Inmueble en el Inventario")
        
    if btn_vendedor:
        if not titulo_v or not telefono_v:
            st.error("Por favor completa el título de la propiedad y tu teléfono.")
        else:
            st.success("¡Información procesada exitosamente!")
            
            msg_prop = (
                f"Hola, deseo publicar un inmueble:%0A"
                f"*Propiedad:* {titulo_v}%0A"
                f"*Tipo:* {tipo_v}%0A"
                f"*Región:* {región_v} ({localidad_v})%0A"
                f"*Operación:* {operacion_v} | *Precio:* ${precio_v}%0A"
                f"*Fotos/Info:* {enlace_fotos}%0A"
                f"*Contacto:* {nombre_v} ({telefono_v})"
            )
            link_wa_v = f"https://wa.me/{MI_NUMERO_WA}?text={msg_prop}"
            
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
    
    msg_ia = "Hola, me interesa solicitar una Tasación e Inspección Visual por IA para evaluar mi inmueble."
    link_wa_ia = f"https://wa.me/{MI_NUMERO_WA}?text={msg_ia.replace(' ', '%20')}"
    
    st.markdown(
        f'<a href="{link_wa_ia}" target="_blank" style="display:inline-block;padding:14px 24px;font-size:16px;font-weight:bold;color:white;background-color:#007BFF;text-align:center;text-decoration:none;border-radius:8px;">🤖 Solicitar Tasación e Inspección Visual por IA</a>',
        unsafe_allow_html=True
    )

# =========================================================
# SECCIÓN FINAL: GRUPOS DE WHATSAPP
# =========================================================
st.markdown("---")
st.subheader("💬 Únete a nuestras comunidades en WhatsApp")
col_g1, col_g2 = st.columns(2)

with col_g1:
    st.markdown("##### 🌴 Margarita")
    st.markdown(
        f'<a href="{LINK_GRUPO_MARGARITA}" target="_blank" style="display:inline-block;padding:10px 14px;font-size:14px;font-weight:bold;color:white;background-color:#25D366;text-align:center;text-decoration:none;border-radius:6px;">Unirme al Grupo Margarita</a>',
        unsafe_allow_html=True
    )

with col_g2:
    st.markdown("##### 🏢 Gran Caracas / La Guaira")
    st.markdown(
        f'<a href="{LINK_GRUPO_CARACAS}" target="_blank" style="display:inline-block;padding:10px 14px;font-size:14px;font-weight:bold;color:white;background-color:#25D366;text-align:center;text-decoration:none;border-radius:6px;">Unirme al Grupo Caracas</a>',
        unsafe_allow_html=True
            )
                        
