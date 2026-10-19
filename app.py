import streamlit as st
import pandas as pd
import cloudinary
import cloudinary.uploader
import requests
import json

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Ventas Inmuebles Venezuela",
    page_icon="🏢",
    layout="centered"
)

st.title("🏢 Ventas Inmuebles Venezuela")
st.caption("Conectando compradores, propietarios y asesores en Isla de Margarita, Gran Caracas y La Guaira.")

# --- CONFIGURACIÓN Y CONEXIÓN DE CLOUDINARY ---
try:
    cloudinary.config(
        cloud_name=st.secrets["CLOUDINARY_CLOUD_NAME"],
        api_key=st.secrets["CLOUDINARY_API_KEY"],
        api_secret=st.secrets["CLOUDINARY_API_SECRET"]
    )
    CLOUDINARY_ACTIVO = True
except Exception:
    CLOUDINARY_ACTIVO = False

# --- CONFIGURACIÓN DE GOOGLE SHEETS Y APPS SCRIPT ---
SHEET_URL = "https://docs.google.com/spreadsheets/d/1vT7Uv5J-z0K8mR... (tu enlace de hoja)"
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/1vT7Uv5J-z0K8mR.../gviz/tq?tqx=out:csv"
GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbz0orGQEFva4bPfWajY72CWUv-5vM1YgZd_yGYZYB-FCdeTUhJMVe9xj6WcvvBDbhM1/exec"

@st.cache_data(ttl=10)
def cargar_inventario(url):
    try:
        df = pd.read_csv(url)
        return df
    except Exception:
        return None

df_inmuebles = cargar_inventario(SHEET_CSV_URL)

# --- CONFIGURACIÓN DE CONTACTOS Y GRUPOS ---
MI_NUMERO_WA = "584124792652"
ENLACE_GRUPO_WA = "https://chat.whatsapp.com/DR5lqu5ibyb7yO60BryXJf?s=cl&p=a&mlu=4&ilr=4"  # Reemplaza con el enlace real de tu grupo

# --- CREACIÓN DE TABS / PESTAÑAS ---
tab1, tab2, tab3 = st.tabs(["📝 Registrar Inmueble", "📂 Inventario Google Sheets", "💬 Grupo y Contacto WhatsApp"])

with tab1:
    st.subheader("Registro de Nuevo Inmueble")
    
    titulo_prop = st.text_input("Título de la Propiedad (ej: Espectacular apartamento en Chacao)")
    nicho = st.selectbox("Nicho / Región:", ["Isla de Margarita", "Gran Caracas", "La Guaira"])
    operacion = st.selectbox("Tipo de Operación:", ["Venta", "Alquiler", "Traspaso"])
    tipo_inm = st.selectbox("Tipo de Inmueble:", ["Apartamento", "Casa", "Townhouse", "Local Comercial", "Terreno"])
    precio = st.text_input("Precio (ej: $85,000 USD o Bs.)")
    
    st.markdown("### 📸 Evidencia Fotográfica")
    fotos_tasacion = st.file_uploader(
        "Sube fotos del inmueble desde tu celular (puedes seleccionar varias):",
        type=["jpg", "png", "jpeg", "heic"],
        accept_multiple_files=True,
        key="tasacion_files"
    )
    
    st.markdown("---")
    nombre_t = st.text_input("Nombre del Propietario / Asesor Inmobiliario:")
    whatsapp_t = st.text_input("WhatsApp de Contacto (ej: 0412...):")
    
    # Botón estándar sin riesgo de AttributeError
    btn_ejecutar = st.button("📦 Procesar Inmueble y Subir Fotos a la Nube", use_container_width=True)

    if btn_ejecutar:
        if not titulo_prop or not precio:
            st.error("Por favor completa al menos el título y el precio del inmueble.")
        else:
            enlaces_fotos = []
            if fotos_tasacion and CLOUDINARY_ACTIVO:
                with st.spinner("Subiendo fotos optimizadas a Cloudinary..."):
                    for idx, archivo in enumerate(fotos_tasacion):
                        try:
                            upload_result = cloudinary.uploader.upload(archivo)
                            enlaces_fotos.append(upload_result.get("secure_url"))
                        except Exception as e:
                            st.warning(f"No se pudo subir la foto {idx+1}: {e}")
            
            # Preparar mensaje para WhatsApp
            texto_wa = f"Hola, nuevo inmueble registrado:\nPropiedad: {titulo_prop}\nTransacción: {operacion} ({tipo_inm})\nRegión: {nicho}\nPrecio: {precio}\n"
            if enlaces_fotos:
                texto_wa += f"Fotos en la Nube ({len(enlaces_fotos)}):\n"
                for i, link in enumerate(enlaces_fotos):
                    texto_wa += f"📷 Foto {i+1}: {link}\n"
            
            # Enviar datos a Google Sheets vía Apps Script
            datos_google = {
                "titulo": titulo_prop,
                "nicho": nicho,
                "operacion": operacion,
                "tipo": tipo_inm,
                "precio": precio,
                "enlace_foto": enlaces_fotos[0] if enlaces_fotos else "Sin foto"
            }
            
            try:
                response = requests.post(GOOGLE_SCRIPT_URL, json=datos_google)
                if response.status_code == 200:
                    st.success("¡Propiedad procesada y fotos subidas a la nube con éxito!")
                else:
                    st.info("El registro fue enviado a la base de datos.")
            except Exception as ex:
                st.warning(f"Procesado localmente. Error al sincronizar tabla: {ex}")
            
            # Botón de envío directo a WhatsApp
            import urllib.parse
            mensaje_encoded = urllib.parse.quote(texto_wa)
            url_wa_directo = f"https://wa.me/{MI_NUMERO_WA}?text={mensaje_encoded}"
            st.link_button("📱 Toca aquí para Enviar Notificación con Fotos a WhatsApp", url_wa_directo, use_container_width=True)

with tab2:
    st.subheader("Inventario Conectado")
    if df_inmuebles is not None:
        st.dataframe(df_inmuebles)
    else:
        st.info("Cargando inventario o la tabla se encuentra vacía actualmente.")
        st.markdown(f"[Abrir Google Sheets directamente]({SHEET_URL})")

with tab3:
    st.subheader("Comunidad y Canales de WhatsApp")
    st.write("Únete a nuestra comunidad de asesores e inversores para recibir captaciones en tiempo real.")
    
    st.link_button("👉 Unirse al Grupo de WhatsApp", ENLACE_GRUPO_WA, use_container_width=True)
    st.link_button("💬 Contactar al Administrador por WhatsApp", f"https://wa.me/{MI_NUMERO_WA}", use_container_width=True)
