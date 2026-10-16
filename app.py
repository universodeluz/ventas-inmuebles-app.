import streamlit as st
import pandas as pd

# Configuración de la página
st.set_page_config(
    page_title="Ventas Inmuebles Venezuela | Hub Digital",
    page_icon="🏢",
    layout="centered"
)

st.title("🏢 Ventas Inmuebles Venezuela")
st.caption("Conectando compradores, propietarios y tecnología inmobiliaria en Nueva Esparta, Caracas, Miranda y La Guaira.")

# --- CONEXIÓN A GOOGLE SHEETS ---
SHEET_URL = "https://docs.google.com/spreadsheets/d/1AkLUKg1FgjgEPeJmSY9oE-1v2Sgld8-4wsu8og3XMEU/export?format=csv"

# --- CONFIGURACIÓN DE CONTACTOS Y GRUPOS ---
MI_NUMERO_WA = "584124792652" 

LINK_GRUPO_MARGARITA = "https://chat.whatsapp.com/DR5lqu5ibyb7yO60BryXJf?s=cl&p=a&mlu=4&ilr=4"
LINK_GRUPO_CARACAS = "https://chat.whatsapp.com/DR5lqu5ibyb7yO60BryXJf?s=cl&p=a&mlu=4&ilr=4"

@st.cache_data(ttl=300)
def cargar_inventario(url):
    try:
        df = pd.read_csv(url)
        return df
    except Exception as e:
        return None

df_inmuebles = cargar_inventario(SHEET_URL)

# --- BANNER SUPERIOR GRUPOS DE WHATSAPP ---
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

# --- LISTAS DE LOCALIDADES DEDICADAS ---
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

LOCALIDADES_CARACAS = [
    "Libertador (Centro, El Recreo, Candelaria, San Bernardino, etc.)",
    "Chacao",
    "Baruta",
    "El Hatillo",
    "Sucre (Petare)",
    "Otro sector de Caracas"
]

LOCALIDADES_MIRANDA = [
    "Andrés Bello: San José de Barlovento",
    "Páez: Río Chico",
    "Buroz: Mamporal",
    "Pedro Gual: Cúpira",
    "Guarenas / Guatire (Plaza y Zamora)",
    "Los Teques / Carrizal / Los Salias (Altos Mirandinos)",
    "Valles del Tuy (Cúa, Ocumare, Charallave, Santa Teresa)",
    "Otro sector de Miranda"
]

LOCALIDADES_LA_GUAIRA = [
    "Catia La Mar",
    "Maiquetía",
    "La Guaira",
    "Macuto",
    "Caraballeda",
    "Naiguatá",
    "Caruao",
    "Otras localidades del Estado La Guaira"
]

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
# PESTAÑA 1: COMPRADORES
# =========================================================
with tab_comprador:
    st.subheader("Búsqueda de Inmuebles y Registro de Requerimiento")
    
    # REGIONALIZACIÓN FUERA DEL FORMULARIO PARA REACTIVIDAD INMEDIATA
    nicho = st.selectbox(
        "1. Selecciona el Estado o Región principal:",
        [
            "Isla de Margarita (Nueva Esparta)", 
            "Caracas (Distrito Capital)", 
            "Estado Miranda", 
            "Estado La Guaira"
        ],
        key="nicho_c_reactivo"
    )
    
    # Determinar las localidades según la elección
    if "Margarita" in nicho:
        loc_opciones = LOCALIDADES_MARGARITA
    elif "Caracas" in nicho:
        loc_opciones = LOCALIDADES_CARACAS
    elif "Miranda" in nicho:
        loc_opciones = LOCALIDADES_MIRANDA
    else:
        loc_opciones = LOCALIDADES_LA_GUAIRA
        
    localidad = st.selectbox("2. Selecciona la localidad o sector:", loc_opciones, key="loc_c_reactivo")

    with st.form("form_comprador_detalles"):
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
# PESTAÑA 2: VENDEDORES / ALIADOS
# =========================================================
with tab_vendedor:
    st.subheader("Publica o Registra tu Inmueble")
    
    # REGIONALIZACIÓN FUERA DEL FORMULARIO
    región_v = st.selectbox(
        "1. Estado o Región de la propiedad:",
        [
            "Isla de Margarita (Nueva Esparta)", 
            "Caracas (Distrito Capital)", 
            "Estado Miranda", 
            "Estado La Guaira"
        ],
        key="reg_v_reactivo"
    )
    
    if "Margarita" in región_v:
        loc_v_opciones = LOCALIDADES_MARGARITA
    elif "Caracas" in región_v:
        loc_v_opciones = LOCALIDADES_CARACAS
    elif "Miranda" in región_v:
        loc_v_opciones = LOCALIDADES_MIRANDA
    else:
        loc_v_opciones = LOCALIDADES_LA_GUAIRA
        
    localidad_v = st.selectbox("2. Localidad o Sector:", loc_v_opciones, key="loc_v_reactivo")

    with st.form("form_vendedor_detalles"):
        titulo_v = st.text_input("Título o breve descripción (ej: Casa 3 hab en Río Chico):")
        tipo_v = st.selectbox("Tipo:", TIPOS_INMUEBLES, key="tipo_v")
        operacion_v = st.radio("Operación:", ["Venta", "Alquiler"], key="op_v")
        precio_v = st.number_input("Precio ($ USD):", min_value=0, value=30000, step=1000)
        
        fotos_cargadas = st.file_uploader(
            "Sube fotos de la propiedad desde tu celular:", 
            type=["jpg", "png", "jpeg"], 
            accept_multiple_files=True
        )
        
        st.markdown("---")
        nombre_v = st.text_input("Nombre del Propietario / Agente:", key="nombre_v")
        telefono_v = st.text_input("WhatsApp de Contacto:", key="tel_v")
        
        btn_vendedor = st.form_submit_button("📤 Registrar Inmueble y Notificar")
        
    if btn_vendedor:
        if not titulo_v or not telefono_v:
            st.error("Por favor completa el título de la propiedad y tu teléfono.")
        else:
            st.success("¡Fotos e información procesadas con éxito!")
            num_fotos = len(fotos_cargadas) if fotos_cargadas else 0
            
            msg_prop = (
                f"Hola, deseo publicar un inmueble:%0A"
                f"*Propiedad:* {titulo_v}%0A"
                f"*Tipo:* {tipo_v}%0A"
                f"*Región:* {región_v}%0A"
                f"*Localidad/Sector:* {localidad_v}%0A"
                f"*Operación:* {operacion_v} | *Precio:* ${precio_v}%0A"
                f"*Fotos adjuntas en app:* {num_fotos} foto(s)%0A"
                f"*Contacto:* {nombre_v} ({telefono_v})"
            )
            link_wa_v = f"https://wa.me/{MI_NUMERO_WA}?text={msg_prop}"
            
            st.markdown(
                f'<a href="{link_wa_v}" target="_blank" style="display:inline-block;padding:12px 20px;font-size:15px;font-weight:bold;color:white;background-color:#25D366;text-align:center;text-decoration:none;border-radius:8px;">📱 Enviar Publicación con Fotos a WhatsApp</a>',
                unsafe_allow_html=True
            )

# =========================================================
# PESTAÑA 3: TASACIÓN IA
# =========================================================
with tab_ia:
    st.subheader("🤖 Asistente de Tasación e Inspección Visual por IA")
    st.markdown("""
    Herramienta exclusiva impulsada por Inteligencia Artificial para **analizar fotos de inmuebles, evaluar el estado de conservación e inspección visual, y calcular la banda de precios sugerida** ajustada al mercado venezolano.
    """)
    
    st.info("💡 **Beneficio para Propietarios y Corredores:** Obtén una estimación de precio objetiva respaldada por datos antes de salir al mercado.")
    
    fotos_tasacion = st.file_uploader(
        "Sube fotos del inmueble para el análisis visual por IA:", 
        type=["jpg", "png", "jpeg"], 
        accept_multiple_files=True,
        key="tasacion_files"
    )
    
    msg_ia = "Hola, he subido fotos en la app y me interesa solicitar una Tasación e Inspección Visual por IA para evaluar mi inmueble."
    link_wa_ia = f"https://wa.me/{584124792652}?text={msg_ia.replace(' ', '%20')}"
    
    st.markdown(
        f'<a href="{link_wa_ia}" target="_blank" style="display:inline-block;padding:14px 24px;font-size:16px;font-weight:bold;color:white;background-color:#007BFF;text-align:center;text-decoration:none;border-radius:8px;">🤖 Procesar Tasación e Inspección Visual por IA</a>',
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
        f'<a href="{LINK_GRUPO_MARGARITA}" style="display:inline-block;padding:10px 14px;font-size:14px;font-weight:bold;color:white;background-color:#25D366;text-align:center;text-decoration:none;border-radius:6px;">Unirme al Grupo Margarita</a>',
        unsafe_allow_html=True
    )

with col_g2:
    st.markdown("##### 🏢 Gran Caracas / La Guaira")
    st.markdown(
        f'<a href="{LINK_GRUPO_CARACAS}" target="_blank" style="display:inline-block;padding:10px 14px;font-size:14px;font-weight:bold;color:white;background-color:#25D366;text-align:center;text-decoration:none;border-radius:6px;">Unirme al Grupo Caracas</a>',
        unsafe_allow_html=True
)
        
