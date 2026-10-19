import streamlit as st
import pandas as pd
import cloudinary
import cloudinary.uploader
import requests
import json
import urllib.parse

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Ventas Inmuebles Venezuela",
    page_icon="🏢",
    layout="centered"
)

st.title("🏢 Ventas Inmuebles Venezuela")
st.caption("Conectando compradores, propietarios y asesores en Isla de Margarita, Gran Caracas y La Guaira.")

# --- DICCIONARIO DE LOCALIDADES POR ESTADO, MUNICIPIO Y SECTOR ---
LOCALIDADES = {
    "Nueva Esparta (Isla de Margarita)": {
        "Maneiro": ["Pampatar", "Costa Azul", "Playa Moreno", "Los Naranjos", "Agua de Vaca", "Otro Sector"],
        "Mariño": ["Porlamar", "Bella Vista", "Los Campitos", "Genovés", "Playa El Ángel", "Otro Sector"],
        "Antolín del Campo": ["Playa El Agua", "Playa Guacuco", "El Cardón", "La Plaza", "Otro Sector"],
        "Arismendi": ["La Asunción", "Atamo Sur", "Atamo Norte", "Guacuco", "Otro Sector"],
        "García": ["Villa Rosa", "San Antonio", "El Valle del Espíritu Santo", "Otro Sector"],
        "Díaz": ["San Juan Bautista", "El Yaque", "La Guardia", "Otro Sector"],
        "Gómez": ["Santa Ana", "Altagracia", "Playa Zaragoza", "Otro Sector"],
        "Tubores": ["Punta de Piedras", "Las Cuotas", "Otro Sector"]
    },
    "Distrito Capital (Gran Caracas)": {
        "Libertador": ["El Paraíso", "La Candela", "San Bernardino", "Montalbán", "Catia", "Centro", "Otro Sector"]
    },
    "Miranda (Gran Caracas)": {
        "Chacao": ["Altamira", "La Castellana", "Los Palos Grandes", "El Rosal", "Chacao", "Campo Alegre", "Otro Sector"],
        "Baruta": ["Las Mercedes", "Prados del Este", "El Cafetal", "La Trinidad", "Cumbres de Curumo", "Colinas de Bello Monte", "Otro Sector"],
        "Sucre": ["Los Dos Caminos", "Santa Eduvigis", "Terrazas del Ávila", "La Urbina", "El Marqués", "Otro Sector"],
        "El Hatillo": ["La Lagunita", "El Hatillo", "Oripoto", "La Boyera", "Los Naranjos", "Otro Sector"]
    },
    "La Guaira": {
        "Vargas": ["Caraballeda", "Macuto", "Maiquetía", "Catia La Mar", "Tanaguarena", "Naiguatá", "Otro Sector"]
    }
}

# --- CONFIGURACIÓN Y CONEXIÓN DE CLOUDINARY ---
try:
    cloudinary.config(
        cloud_name=st.secrets.get("CLOUDINARY_CLOUD_NAME", ""),
        api_key=st.secrets.get("CLOUDINARY_API_KEY", ""),
        api_secret=st.secrets.get("CLOUDINARY_API_SECRET", "")
    )
    CLOUDINARY_ACTIVO = True
except Exception:
    CLOUDINARY_ACTIVO = False

# --- CONFIGURACIÓN DE GOOGLE SHEETS Y APPS SCRIPT ---
SHEET_URL = "https://docs.google.com/spreadsheets/d/1vT7Uv5J-z0K8mR..."
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
ENLACE_GRUPO_WA = "https://chat.whatsapp.com/DR5lqu5ibyb7yO60BryXJf?s=cl&p=a&mlu=4&ilr=4" 
# --- PESTAÑAS PRINCIPALES ---
tab1, tab2, tab3 = st.tabs(["📝 Registrar Inmueble / Tasación", "📂 Inventario Google Sheets", "💬 Grupo y Contacto WhatsApp"])

with tab1:
    st.subheader("Registro y Tasación de Propiedad")
    
    titulo_prop = st.text_input("Título de la Propiedad (ej: Terreno en Pampatar / Apt en Altamira)")
    
    # --- SELECCIÓN DINÁMICA DE LOCALIDAD ---
    st.markdown("### 📍 Ubicación Geográfica")
    col_loc1, col_loc2, col_loc3 = st.columns(3)
    
    with col_loc1:
        estado_sel = st.selectbox("Estado / Región:", list(LOCALIDADES.keys()))
    
    with col_loc2:
        municipios_disponibles = list(LOCALIDADES[estado_sel].keys())
        municipio_sel = st.selectbox("Municipio:", municipios_disponibles)
        
    with col_loc3:
        sectores_disponibles = LOCALIDADES[estado_sel][municipio_sel]
        sector_sel = st.selectbox("Urbanización / Sector:", sectores_disponibles)
        
    # Si el usuario elige "Otro Sector", puede escribirlo manualmente
    if sector_sel == "Otro Sector":
        sector_manual = st.text_input("Especifica el nombre del Sector / Urbanización:")
        ubicacion_final = f"{estado_sel} - Mun. {municipio_sel} - {sector_manual if sector_manual else 'Otro Sector'}"
    else:
        ubicacion_final = f"{estado_sel} - Mun. {municipio_sel} - {sector_sel}"

    st.markdown("---")
    operacion = st.selectbox("Tipo de Operación:", ["Venta", "Alquiler", "Traspaso"])
    tipo_inm = st.selectbox("Tipo de Inmueble:", ["Apartamento", "Casa", "Townhouse", "Terreno", "Local Comercial", "Posada / Hotel"])
    precio = st.text_input("Precio Estimado / Oferta (ej: $45,000 USD)")

    # --- CAMPOS ESPECÍFICOS PARA VALORACIÓN DE TERRENOS ---
    detalles_terreno = ""
    if tipo_inm == "Terreno":
        st.markdown("### 📐 Variables Específicas del Terreno")
        col_t1, col_t2 = st.columns(2)
        
        with col_t1:
            area_m2 = st.number_input("Superficie del Terreno (m²):", min_value=0.0, step=10.0, value=500.0)
            tipo_cerca = st.selectbox(
                "Tipo de Cerramiento / Cerca:",
                [
                    "Sin cercar (Linderos abiertos)",
                    "Pared de bloques / Mampostería",
                    "Muro perimetral de concreto frisado",
                    "Cerca de malla alfajor / Ciclón",
                    "Cerca viva / Trinchera de madera"
                ]
            )
            topografia = st.selectbox(
                "Topografía del Terreno:",
                ["Plana (100% aprovechable)", "Semi-plana / Colina suave", "Inclinada / Pendiente severa"]
            )

        with col_t2:
            acceso_vial = st.selectbox(
                "Acceso Vial:",
                ["Calle Asfaltada", "Calle de Granzón / Consolidada", "Camino de Tierra / Rústico"]
            )
            zonificacion = st.selectbox(
                "Zonificación / Uso de Suelo:",
                ["Residencial (R1/R2/R3)", "Comercial / Mixto", "Industrial / Galpón", "Agrícola / Turístico"]
            )
            estatus_legal = st.selectbox(
                "Estatus Legal:",
                ["Título de Propiedad Registrado", "Adjudicación / Carta Agrícola", "Documento Privado / En trámite"]
            )

        st.markdown("#### 💡 Servicios Públicos y Plusvalía")
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            s_agua = st.checkbox("Agua de Calle (Red Pública)")
            s_pozo = st.checkbox("Pozo Profundo de Agua Dulce")
            s_luz = st.checkbox("Electricidad (Transformador cercano)")
        with col_s2:
            s_cloacas = st.checkbox("Red de Aguas Servidas / Cloacas")
            s_internet = st.checkbox("Internet / Fibra Óptica")
            s_vista = st.checkbox("Vista al Mar / Vista Panorámica (Plusvalía)")

        servicios_list = []
        if s_agua: servicios_list.append("Agua Pública")
        if s_pozo: servicios_list.append("Pozo Profundo")
        if s_luz: servicios_list.append("Electricidad")
        if s_cloacas: servicios_list.append("Cloacas")
        if s_internet: servicios_list.append("Fibra Óptica")
        if s_vista: servicios_list.append("Vista Panorámica")
        
        servicios_str = ", ".join(servicios_list) if servicios_list else "Sin servicios activos"

        detalles_terreno = (
            f"\n📐 Área: {area_m2} m²"
            f"\n🚧 Cerramiento: {tipo_cerca}"
            f"\n🏔 Topografía: {topografia}"
            f"\n🛣 Acceso: {acceso_vial}"
            f"\n🏙 Zonificación: {zonificacion}"
            f"\n📜 Estatus Legal: {estatus_legal}"
            f"\n⚡ Servicios / Plusvalía: {servicios_str}\n"
        )

    st.markdown("### 📸 Evidencia Fotográfica")
    fotos_tasacion = st.file_uploader(
        "Sube fotos de la propiedad/terreno desde tu celular:",
        type=["jpg", "png", "jpeg", "heic"],
        accept_multiple_files=True,
        key="tasacion_files"
    )
    
    st.markdown("---")
    nombre_t = st.text_input("Nombre del Propietario / Asesor Inmobiliario:")
    whatsapp_t = st.text_input("WhatsApp de Contacto (ej: 0412...):")
    
    btn_ejecutar_tasacion = st.button("📦 Procesar Inmueble y Subir Fotos a la Nube", use_container_width=True)

    if btn_ejecutar_tasacion:
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
            
            # Formato de mensaje para WhatsApp con Ubicación Geográfica detallada
            texto_wa = (
                f"Hola, nuevo inmueble registrado:\n"
                f"Propiedad: {titulo_prop}\n"
                f"Ubicación: {ubicacion_final}\n"
                f"Transacción: {operacion} ({tipo_inm})\n"
                f"Precio: {precio}\n"
            )
            
            if tipo_inm == "Terreno" and detalles_terreno:
                texto_wa += detalles_terreno
                
            if enlaces_fotos:
                texto_wa += f"\nFotos en la Nube ({len(enlaces_fotos)}):\n"
                for i, link in enumerate(enlaces_fotos):
                    texto_wa += f"📷 Foto {i+1}: {link}\n"
            
            # Guardar en Google Sheets
            datos_google = {
                "titulo": titulo_prop,
                "nicho": ubicacion_final,
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
                    st.info("Registro enviado correctamente a la tabla.")
            except Exception as ex:
                st.warning(f"Error al sincronizar con Google Sheets: {ex}")
            
            # Botón de envío directo a WhatsApp
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
