import streamlit as st
import pandas as pd
import cloudinary
import cloudinary.uploader
from PIL import Image
import io
import requests
import json
import urllib.parse
from datetime import datetime

# Soporte para formatos de imagen móvil (HEIC de iPhone/Android)
try:
    from pillow_heif import register_heif_opener
    register_heif_opener()
except ImportError:
    pass

# Configuración de la página
st.set_page_config(
    page_title="Ventas Inmuebles Venezuela | Hub Digital",
    page_icon="🏢",
    layout="centered"
)

st.title("🏢 Ventas Inmuebles Venezuela")
st.caption("Conectando compradores, propietarios y tecnología inmobiliaria en Nueva Esparta, Caracas, Miranda y La Guaira.")

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

# --- URL DEL GOOGLE APPS SCRIPT WEB APP ---
GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbz0orGQEFva4bPfWajY72CWUv-5vM1YgZd_yGYZYB-FCdeTUhJMVe9xj6WcvvBDbhM1/exec"

# --- CONEXIÓN A GOOGLE SHEETS (LECTURA) ---
SHEET_URL = "https://docs.google.com/spreadsheets/d/1AkLUKg1FgjgEPeJmSY9oE-1v2Sgld8-4wsu8og3XMEU/edit?usp=sharing"
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/1AkLUKg1FgjgEPeJmSY9oE-1v2Sgld8-4wsu8og3XMEU/export?format=csv"

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
LINK_GRUPO_MARGARITA = "https://chat.whatsapp.com/DR5lqu5ibyb7yO60BryXJf?s=cl&p=a&mlu=4&ilr=4"
LINK_GRUPO_CARACAS = "https://chat.whatsapp.com/DR5lqu5ibyb7yO60BryXJf?s=cl&p=a&mlu=4&ilr=4"

# --- BANNER SUPERIOR DE GRUPOS DE WHATSAPP ---
st.info("💬 **¿Quieres unirte a nuestras comunidades activas en WhatsApp?**")
col_top1, col_top2 = st.columns(2)
with col_top1:
    st.link_button("🌴 Grupo Margarita", LINK_GRUPO_MARGARITA, use_container_width=True)
with col_top2:
    st.link_button("🏢 Grupo Caracas / La Guaira", LINK_GRUPO_CARACAS, use_container_width=True)

st.markdown("---")

# --- ESTRUCTURA GEOGRÁFICA HIPERDETALLADA ---
ESTRUCTURA_GEOGRAFICA = {
    "Isla de Margarita (Nueva Esparta)": {
        "Municipio Antolín del Campo": [
            "Playa El Agua", "La Mira", "El Tirano / Puerto Fermín", "Manzanillo", "Aricagua",
            "Playa Parguito", "El Cardón", "Paraguachí (Casco Histórico)", "La Plaza", "Lomas de Antolín", "El Salado"
        ],
        "Municipio Maneiro": [
            "Pampatar (Casco Histórico)", "Costa Azul", "Playa El Ángel", "Jorge Coll", "Los Naranjos",
            "Moreno / Playa Moreno", "San Lorenzo", "Apostadero", "Las Salinas", "Cueva del Sapo"
        ],
        "Municipio Mariño": [
            "Porlamar Centro", "Av. 4 de Mayo", "Av. Santiago Mariño", "Bella Vista", "Genovés",
            "Los Cocos", "Pueblo Nuevo", "Av. Bolívar", "Llano Adentro", "Palguarime"
        ],
        "Municipio Arismendi": [
            "La Asunción Centro", "Atamo Sur", "Atamo Norte", "Guacuco / Playa Guacuco", "Catalán",
            "El Salado de La Asunción", "La Portada", "Salamanca"
        ],
        "Municipio Marcano": [
            "Juan Griego Centro", "La Galera", "Las Piedras", "Pedregales", "Los Millanes", "Av. Jesús Rafael Leandro"
        ],
        "Municipio García": [
            "El Valle del Espíritu Santo", "Villa Rosa", "San Antonio", "Conchesero", "La Cruz Grande", "Los Olivos"
        ],
        "Municipio Díaz": [
            "San Juan Bautista", "El Yaque", "El Espinal", "Cotoperiz", "Las Barrancas", "La Guardia"
        ],
        "Municipio Tubores": [
            "Punta de Piedras", "El Guamache", "Las Cuotas", "Las Marites"
        ],
        "Municipio Península de Macanao": [
            "Boca de Río", "San Francisco", "Boca de Pozo", "Punta Arenas", "El Horcón"
        ],
        "Municipio Villalba (Coche)": [
            "San Pedro de Coche", "Playa La Punta", "El Amor", "Güinima"
        ]
    },
    "Caracas (Distrito Capital)": {
        "Municipio Chacao": [
            "Altamira", "Los Palos Grandes", "La Castellana", "El Rosal", "Campo Alegre", "Chacao Centro", "Bello Campo"
        ],
        "Municipio Baruta": [
            "Las Mercedes", "Prados del Este", "Santa Fe", "Caurimare", "El Peñón", "Colinas de Bello Monte", "Manzanares", "Alto Hatillo"
        ],
        "Municipio El Hatillo": [
            "Pueblo de El Hatillo", "La Lagunita", "La Boyera", "El Encantado", "Oripoto", "Los Naranjos de El Hatillo"
        ],
        "Municipio Libertador": [
            "El Recreo / Sabana Grande", "La Candelaria", "San Bernardino", "Montalbán", "El Paraíso", "Centro / Capitolio"
        ]
    },
    "Estado Miranda": {
        "Municipio Plaza (Guarenas)": [
            "Nueva Casarapa", "Ciudad Casarapa", "Terrazas del Este", "Guarenas Centro", "Oropeza Castillo"
        ],
        "Municipio Zamora (Guatire)": [
            "Castillejo", "El Ingenio", "Valle Arriba", "Guatire Centro", "La Rosa"
        ],
        "Municipio Los Salias (San Antonio)": [
            "San Antonio de los Altos", "Los Castillitos", "Las Minas", "La Morita"
        ],
        "Municipio Guaicaipuro (Los Teques)": [
            "Los Teques Centro", "El Paso", "La Matica", "Venezia"
        ],
        "Municipio Cristóbal Rojas (Charallave)": [
            "Charallave Centro", "La Estrella", "Paso Real", "Ciudad Miranda"
        ]
    },
    "Estado La Guaira": {
        "Municipio Vargas": [
            "Caraballeda (Playa Grande / Caribe)", "Macuto", "Catia La Mar", "Maiquetía", "El Junko / Club de Campo",
            "Naiguatá", "Los Corales", "Tanaguarena"
        ]
    }
}

TIPOS_INMUEBLES = [
    "Terreno", "Apartamento", "Casa", "Townhouse", "Posada / Hotel", "Local Comercial", "Oficina"
]

# CREACIÓN DE PESTAÑAS
tab_comprador, tab_vendedor, tab_ia, tab_inventario, tab_contratos = st.tabs([
    "🔍 Buscar Inmueble", 
    "📝 Publicar Inmueble",
    "🤖 Tasación IA",
    "📂 Inventario Google Sheets",
    "📄 Generador Legal (Arrendamiento / Compraventa)"
])

# =========================================================
# PESTAÑA 1: COMPRADORES
# =========================================================
with tab_comprador:
    st.subheader("Búsqueda Avanzada de Inmuebles")
    
    nicho = st.selectbox("1. Estado o Región principal:", list(ESTRUCTURA_GEOGRAFICA.keys()), key="nicho_c")
    mun_c = st.selectbox("2. Municipio:", list(ESTRUCTURA_GEOGRAFICA[nicho].keys()), key="mun_c")
    sector_c = st.selectbox("3. Urbanización / Sector específico:", ESTRUCTURA_GEOGRAFICA[nicho][mun_c], key="sec_c")

    with st.form("form_comprador_detalles"):
        operacion = st.radio("Transacción:", ["Comprar", "Alquilar"])
        tipo_inmueble = st.selectbox("Tipo de propiedad:", TIPOS_INMUEBLES)
        
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            amoblado_filtro = st.selectbox("Condición:", ["Indiferente", "Amoblado y Equipado", "Sin amoblar"])
        with col_c2:
            presupuesto_max = st.number_input("Presupuesto máximo ($ USD):", min_value=0, value=50000, step=2500)
            
        st.markdown("**Servicios y Amenidades deseadas:**")
        req_piscina = st.checkbox("Debe tener Piscina")
        req_planta = st.checkbox("Debe tener Planta Eléctrica")
        req_pozo = st.checkbox("Debe tener Pozo / Tanque constante")
        
        st.markdown("---")
        st.markdown("**Datos de Contacto**")
        nombre_c = st.text_input("Nombre y Apellido:", key="nombre_c")
        telefono_c = st.text_input("WhatsApp (ej: 0412...):", key="tel_c")
        
        btn_comprador = st.form_submit_button("🔍 Buscar Opciones y Enviar Requerimiento")

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
                        st.markdown(f"💰 **Precio:** ${row['precio']} USD | 📍 **Zona:** {row['nicho']}")
                        if 'enlace_foto_o_info' in row and pd.notna(row['enlace_foto_o_info']) and str(row['enlace_foto_o_info']).strip() != "":
                            st.markdown(f"[📷 Ver Galería / Ficha Técnica]({row['enlace_foto_o_info']})")
                        st.markdown("---")
                        inmuebles_compatibles.append(str(row['titulo']))
                else:
                    st.info("No tenemos una coincidencia exacta de inmediato, pero guardamos tu requerimiento.")
            else:
                st.info("Requerimiento registrado con éxito.")

            extras_busqueda = []
            if req_piscina: extras_busqueda.append("Piscina")
            if req_planta: extras_busqueda.append("Planta")
            if req_pozo: extras_busqueda.append("Pozo/Tanque")

            msg_wa = (
                f"Hola, nuevo requerimiento de comprador:%0A"
                f"*Cliente:* {nombre_c} ({telefono_c})%0A"
                f"*Transacción:* {operacion} ({tipo_inmueble})%0A"
                f"*Ubicación:* {nicho} - {mun_c} ({sector_c})%0A"
                f"*Condición:* {amoblado_filtro}%0A"
                f"*Presupuesto Máx:* ${presupuesto_max} USD%0A"
                f"*Extras exigidos:* {', '.join(extras_busqueda) if extras_busqueda else 'Ninguno'}%0A"
                f"*Opciones vistas en web:* {', '.join(inmuebles_compatibles) if inmuebles_compatibles else 'Ninguna inmediata'}"
            )
            link_wa = f"https://wa.me/{MI_NUMERO_WA}?text={msg_wa}"
            
            st.link_button("📱 Enviar Requerimiento a WhatsApp", link_wa, use_container_width=True)

# =========================================================
# PESTAÑA 2: VENDEDORES / ALIADOS (CON GOOGLE MAPS)
# =========================================================
with tab_vendedor:
    st.subheader("Publica o Registra tu Inmueble")
    
    región_v = st.selectbox("1. Estado o Región:", list(ESTRUCTURA_GEOGRAFICA.keys()), key="reg_v")
    mun_v = st.selectbox("2. Municipio:", list(ESTRUCTURA_GEOGRAFICA[región_v].keys()), key="mun_v")
    sector_v = st.selectbox("3. Urbanización / Sector específico:", ESTRUCTURA_GEOGRAFICA[región_v][mun_v], key="sec_v")

    dir_mapa_previa = f"{sector_v}, {mun_v}, {región_v}, Venezuela"
    url_mapa_previa = f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(dir_mapa_previa)}"
    st.link_button(f"📍 Explorar {sector_v} en Google Maps", url_mapa_previa, use_container_width=True)

    with st.form("form_vendedor_detalles"):
        titulo_v = st.text_input("Título comercial corto (ej: Terreno en La Mira / Quinta en Las Mercedes):")
        tipo_v = st.selectbox("Tipo de Inmueble:", TIPOS_INMUEBLES, key="tipo_v")
        operacion_v = st.radio("Tipo de Transacción:", ["Venta", "Alquiler"], key="op_v")
        
        col_v1, col_v2 = st.columns(2)
        with col_v1:
            precio_v = st.number_input("Precio de Oferta ($ USD):", min_value=0, value=85000, step=2500)
            m2_construccion_v = st.number_input("Área de Construcción (m² techados):", min_value=0, value=0 if tipo_v=="Terreno" else 150)
            habitaciones_v = st.number_input("Habitaciones:", min_value=0, value=0 if tipo_v=="Terreno" else 3)
        with col_v2:
            m2_terreno_v = st.number_input("Área de Terreno / Parcela (m² totales):", min_value=0, value=500)
            estado_amoblado = st.selectbox("Condición / Equipamiento:", ["N/A (Terreno)", "Amoblado y Equipado de Lujo", "Semiamoblado", "Sin amoblar / Solo cocina"])
            banos_v = st.number_input("Baños:", min_value=0, value=0 if tipo_v=="Terreno" else 2)
            
        st.markdown("### ⚡ Servicios de Resistencia y Conectividad")
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            tiene_piscina = st.checkbox("Piscina / Tanque constante")
            tiene_planta = st.checkbox("Planta eléctrica / Transformador cerca")
            tiene_pozo = st.checkbox("Pozo de agua dulce")
        with col_s2:
            tiene_vista = st.checkbox("Vista privilegiada (Mar / Ávila / Montaña)")
            tiene_internet = st.checkbox("Internet de alta velocidad (Fibra/ABA)")
            
        st.markdown("### 📁 Estatus Legal")
        estatus_legal = st.selectbox(
            "Documentación:",
            ["Título de Propiedad Registrado listo para firmar", "Adjudicación / Carta Agrícola", "Ficha catastral / Solvencia en trámite", "Documento privado / En trámite"]
        )
        
        fotos_cargadas = st.file_uploader(
            "Sube fotos de la propiedad desde tu celular (puedes seleccionar varias):", 
            type=["jpg", "png", "jpeg", "heic", "webp", "JPG", "PNG", "JPEG"], 
            accept_multiple_files=True
        )

        st.markdown("---")
        nombre_v = st.text_input("Nombre del Propietario / Asesor Inmobiliario:", key="nombre_v")
        telefono_v = st.text_input("WhatsApp de Contacto (ej: 0412...):", key="tel_v")
        
        btn_vendedor = st.form_submit_button("📤 Registrar y Sincronizar Inmueble")
        
    if btn_vendedor:
        if not titulo_v or not telefono_v:
            st.error("Por favor completa el título de la propiedad y tu teléfono.")
        else:
            urls_fotos = []
            if fotos_cargadas and CLOUDINARY_ACTIVO:
                with st.spinner("☁️ Optimizando, subiendo fotos y sincronizando Google Sheets..."):
                    for foto in fotos_cargadas:
                        try:
                            img = Image.open(foto)
                            img = img.convert("RGB")
                            img.thumbnail((1200, 1200))
                            
                            buffered = io.BytesIO()
                            img.save(buffered, format="JPEG", quality=85)
                            buffered.seek(0)
                            
                            res = cloudinary.uploader.upload(buffered)
                            urls_fotos.append(res.get("secure_url"))
                        except Exception as e:
                            st.warning(f"No se pudo procesar una imagen: {e}")

            if GOOGLE_SCRIPT_URL != "TU_URL_DE_GOOGLE_SCRIPT_AQUI":
                try:
                    payload = {
                        "titulo": titulo_v,
                        "nicho": f"{región_v} - {mun_v} ({sector_v})",
                        "operacion": operacion_v,
                        "tipo": tipo_v,
                        "precio": precio_v,
                        "enlace_foto": " | ".join(urls_fotos) if urls_fotos else "Sin foto"
                    }
                    requests.post(GOOGLE_SCRIPT_URL, json=payload, timeout=5)
                except Exception:
                    pass

            st.success("✨ ¡Inmueble procesado, fotos en la nube y sincronizado en Google Sheets!")
            
            servicios_lista = []
            if tiene_piscina: servicios_lista.append("Piscina")
            if tiene_planta: servicios_lista.append("Planta/Transformador")
            if tiene_pozo: servicios_lista.append("Pozo Agua")
            if tiene_vista: servicios_lista.append("Vista Panorámica")
            if tiene_internet: servicios_lista.append("Internet")

            titulo_corto = titulo_v[:80] + ("..." if len(titulo_v) > 80 else "")

            if urls_fotos:
                enlaces_fotos_str = "%0A".join([f"📷 Foto {i}: {url}" for i, url in enumerate(urls_fotos, start=1)])
            else:
                enlaces_fotos_str = "Sin fotos subidas"

            msg_prop = (
                f"Hola, nuevo inmueble registrado:%0A"
                f"*Propiedad:* {titulo_corto}%0A"
                f"*Transacción:* {operacion_v} ({tipo_v})%0A"
                f"*Ubicación Exacta:* {región_v} - {mun_v} ({sector_v})%0A"
                f"*Precio:* ${precio_v} USD%0A"
                f"*Construcción:* {m2_construccion_v} m² | *Terreno:* {m2_terreno_v} m²%0A"
                f"*Hab:* {habitaciones_v} | *Baños:* {banos_v}%0A"
                f"*Condición:* {estado_amoblado}%0A"
                f"*Servicios/Extras:* {', '.join(servicios_lista) if servicios_lista else 'Ninguno'}%0A"
                f"*Legal:* {estatus_legal}%0A"
                f"*Fotos en la Nube ({len(urls_fotos)}):*%0A{enlaces_fotos_str}%0A"
                f"*Contacto:* {nombre_v} ({telefono_v})"
            )
            link_wa_v = f"https://wa.me/{MI_NUMERO_WA}?text={msg_prop}"
            
            st.link_button("📱 Toca aquí para Enviar Notificación con Fotos a WhatsApp", link_wa_v, use_container_width=True)
            st.link_button(f"📍 Ver {sector_v} en Google Maps", url_mapa_previa, use_container_width=True)

# =========================================================
# PESTAÑA 3: ASISTENTE DE TASACIÓN TÉCNICA E INSPECCIÓN IA (CON CAMPOS VISIBLES DE PISCINA)
# =========================================================
with tab_ia:
    st.subheader("🤖 Asistente de Tasación Técnica por IA")
    st.markdown("Cálculo algorítmico avanzado considerando porcentaje de obra, dimensiones volumétricas de piscinas, cercados perimetrales y capacidad de tanques subterráneos.")
    
    región_t = st.selectbox("1. Estado o Región:", list(ESTRUCTURA_GEOGRAFICA.keys()), key="reg_t")
    mun_t = st.selectbox("2. Municipio:", list(ESTRUCTURA_GEOGRAFICA[región_t].keys()), key="mun_t")
    sector_t = st.selectbox("3. Urbanización / Sector específico:", ESTRUCTURA_GEOGRAFICA[región_t][mun_t], key="sec_t")
    
    dir_mapa_t = f"{sector_t}, {mun_t}, {región_t}, Venezuela"
    url_mapa_t = f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(dir_mapa_t)}"
    st.link_button(f"📍 Abrir Ubicación del Sector ({sector_t}) en Google Maps", url_mapa_t, use_container_width=True)
    
    tipo_t = st.selectbox("4. Tipo de Inmueble a Tasar:", TIPOS_INMUEBLES, key="tipo_t")

    with st.form("form_tasacion_ia_avanzado_visible"):
        
        if tipo_t == "Terreno":
            st.markdown("### 📐 Criterios de Valoración para Terrenos")
            area_m2_terreno = st.number_input("Área Total de la Parcela (m²):", min_value=1.0, value=500.0, step=25.0)
            
            st.markdown("#### 🧱 Cerramiento Perimetral del Terreno")
            tipo_cerca = st.selectbox(
                "Tipo de Cerca / Muro:",
                [
                    "Muro perimetral de concreto frisado (+15%)",
                    "Pared de bloques de concreto (+10%)",
                    "Cerca de malla alfajor / Ciclón (+5%)",
                    "Cerca viva / Trinchera (+2%)",
                    "Sin cercar (Linderos abiertos) (0%)"
                ]
            )
            porcentaje_cerca = st.slider("Porcentaje de Conclusión de la Cerca/Muro (%):", min_value=0, max_value=100, value=100)

            topografia = st.selectbox("Topografía y Nivel del Suelo:", ["Plana (100% aprovechable) (+10%)", "Semi-plana / Colina suave (0%)", "Inclinada / Pendiente severa (-15%)"])
            acceso_vial = st.selectbox("Acceso Vial y Entorno:", ["Calle Asfaltada (+10%)", "Calle de Granzón / Consolidada (0%)", "Camino de Tierra / Rústico (-10%)"])
            zonificacion = st.selectbox("Zonificación / Uso de Suelo:", ["Comercial / Mixto (+15%)", "Residencial (R1/R2/R3) (+10%)", "Industrial / Galpón (+5%)", "Agrícola / Turístico (0%)"])
            estatus_legal = st.selectbox("Estatus Legal:", ["Título de Propiedad Registrado (+10%)", "Adjudicación / Carta Agrícola (0%)", "Documento Privado / En trámite (-15%)"])

            st.markdown("#### 💡 Servicios y Autonomía Hídrica")
            t_agua = st.checkbox("Red Pública de Agua de Calle (+5%)")
            t_pozo = st.checkbox("Pozo Profundo de Agua Dulce (+10%)")
            capacidad_tanque = st.number_input("Capacidad de Tanque Subterráneo (Litros):", min_value=0, value=0, step=1000)
            t_luz = st.checkbox("Electricidad / Transformador cerca (+5%)")
            t_cloacas = st.checkbox("Red de Aguas Servidas / Cloacas (+5%)")
            t_internet = st.checkbox("Fibra Óptica / Conectividad (+5%)")
            t_vista = st.checkbox("Vista al Mar / Panorámica a la Montaña (+15%)")
            
            estado_obra = "Terminado 100%"
            porcentaje_obra = 100
            piscina_estatus = "Sin piscina"
            dim_largo, dim_ancho, dim_profundidad = 0.0, 0.0, 0.0

        else:
            st.markdown("### 🏠 Criterios de Construcción y Ejecución")
            transaccion_t = st.radio("Objetivo de Tasación:", ["Valor de Venta Comercial", "Canon de Alquiler Sugerido"])
            
            estado_obra = st.selectbox(
                "Estado General de la Edificación:",
                [
                    "100% Terminado y Habitable",
                    "Obra Gris Avanzada (Tuberías, techos y paredes listas, faltan acabados)",
                    "Estructura Inconclusa / Obra Negra (Estructura de concreto sin friso)"
                ]
            )
            
            porcentaje_obra = st.slider(
                "Porcentaje Exacto de Ejecución de la Obra (%):", 
                min_value=10, max_value=100, 
                value=100 if "100%" in estado_obra else (70 if "Gris" in estado_obra else 40)
            )

            m2_construccion_t = st.number_input("Área de Construcción Techada (m²):", min_value=0, value=150)
            m2_terreno_t = st.number_input("Área de Terreno / Parcela (m² totales):", min_value=0, value=350)
            habitaciones_t = st.number_input("Habitaciones:", min_value=0, value=3, key="hab_t")
            banos_t = st.number_input("Baños:", min_value=0, value=2, key="ban_t")
            
            st.markdown("### 🏊‍♂️ Dimensiones y Estatus de Piscina (Cálculo por Volumen m³)")
            piscina_estatus = st.selectbox(
                "Estatus de la Piscina:",
                ["Sin piscina", "Piscina Operativa Completa", "Piscina en Estructura / Obra Gris (Vaso de concreto sin equipos/enchape)"]
            )
            
            # CAMPOS DE DIMENSIONES VISIBLES SIEMPRE QUE NO ESTÉ EN "Sin piscina"
            col_p1, col_p2, col_p3 = st.columns(3)
            with col_p1:
                dim_largo = st.number_input("Largo (m):", min_value=0.0, value=8.0 if piscina_estatus != "Sin piscina" else 0.0, step=0.5)
            with col_p2:
                dim_ancho = st.number_input("Ancho (m):", min_value=0.0, value=4.0 if piscina_estatus != "Sin piscina" else 0.0, step=0.5)
            with col_p3:
                dim_profundidad = st.number_input("Profundidad (m):", min_value=0.0, value=1.5 if piscina_estatus != "Sin piscina" else 0.0, step=0.1)

            st.markdown("### 🧱 Cercado Perimetral del Inmueble")
            tipo_cerca = st.selectbox(
                "Tipo de Cerca / Muro Perimetral:",
                ["Muro perimetral de concreto frisado", "Pared de bloques de concreto", "Cerca de malla alfajor / Ciclón", "Sin cerca perimetral"]
            )
            porcentaje_cerca = st.slider("Porcentaje de Conclusión de la Cerca (%):", min_value=0, max_value=100, value=100)

            st.markdown("### 💧 Autonomía Hídrica y Plusvalía")
            capacidad_tanque = st.number_input("Capacidad del Tanque Subterráneo / Aéreo (Litros):", min_value=0, value=10000, step=1000)
            t_pozo = st.checkbox("Pozo de Agua Dulce Operativo")
            t_planta = st.checkbox("Planta Eléctrica o Acometida")
            t_vista = st.checkbox("Vista Panorámica / al Mar")
            t_permisos = st.checkbox("Planos aprobados por la Alcaldía / Ingeniería")

        st.markdown("---")
        nombre_t = st.text_input("Tu Nombre / Contacto:", key="nombre_t")
        whatsapp_t = st.text_input("Tu Número de WhatsApp:", key="wa_t")
        
        btn_ejecutar_tasacion = st.form_submit_button("🚀 Calcular Tasación Profesional Avanzada", use_container_width=True)

    if btn_ejecutar_tasacion:
        if not whatsapp_t:
            st.error("Por favor ingresa tu número de WhatsApp para recibir el reporte.")
        else:
            base_m2_terr = 40.0
            base_m2_const = 500.0

            if "Margarita" in región_t:
                base_m2_terr = 55.0
                base_m2_const = 750.0
            elif "Caracas" in región_t:
                base_m2_terr = 120.0
                base_m2_const = 1100.0
            elif "Miranda" in región_t:
                base_m2_terr = 45.0
                base_m2_const = 450.0
            elif "La Guaira" in región_t:
                base_m2_terr = 50.0
                base_m2_const = 600.0

            if tipo_t == "Terreno":
                factor_cercado = (porcentaje_cerca / 100.0) * (0.15 if "concreto" in tipo_cerca else 0.05)
                factor_tanque = 0.05 if capacidad_tanque >= 5000 else 0.02
                factor_t = 1.0 + factor_cercado + factor_tanque
                
                precio_m2_final = round(base_m2_terr * factor_t, 2)
                valor_estimado = round(area_m2_terreno * precio_m2_final, 2)
                tipo_resultado = "Valor Comercial Estimado del Terreno"

                st.success(f"💰 **{tipo_resultado}:** ${valor_estimado:,.2f} USD")
                st.info(
                    f"📊 **Desglose Técnico:**\n\n"
                    f"- **Área:** {area_m2_terreno} m² | **Cercado:** {porcentaje_cerca}% ({tipo_cerca})\n"
                    f"- **Tanque de Agua:** {capacidad_tanque:,} Litros\n"
                    f"- **Precio por m²:** ${precio_m2_final} / m²"
                )
                
                msg_tasacion = (
                    f"Hola, solicito tasación de Terreno:%0A*Ubicación:* {región_t} - {mun_t} ({sector_t})%0A"
                    f"*Área:* {area_m2_terreno} m²%0A*Cercado:* {porcentaje_cerca}% (% {tipo_cerca})%0A"
                    f"*Tanque:* {capacidad_tanque:,} Lts%0A*Valor Estimado:* ${valor_estimado:,.2f} USD"
                )
            else:
                # CÁLCULO TÉCNICO AVANZADO CON PORCENTAJE DE OBRA Y TANQUE
                factor_ejecucion = porcentaje_obra / 100.0
                
                # Ajuste por cercado perimetral y su porcentaje
                factor_cercado_inm = (porcentaje_cerca / 100.0) * 0.06
                
                # Ajuste por tanque subterráneo (escala según litros)
                factor_tanque_inm = 0.08 if capacidad_tanque >= 15000 else (0.04 if capacidad_tanque >= 5000 else 0.01)

                factor_extras = 1.0 + factor_cercado_inm + factor_tanque_inm
                if t_pozo: factor_extras += 0.08
                if t_planta: factor_extras += 0.06
                if t_vista: factor_extras += 0.07

                # Valor de construcción ponderado por el % de ejecución real
                valor_construccion = m2_construccion_t * base_m2_const * factor_ejecucion * factor_extras
                valor_terreno = m2_terreno_t * base_m2_terr * factor_extras
                
                # CÁLCULO DINÁMICO DE PISCINA POR VOLUMEN (M3 / LITROS)
                valor_piscina_usd = 0.0
                dimensiones_piscina = "N/A"
                
                if piscina_estatus != "Sin piscina" and dim_largo > 0 and dim_ancho > 0 and dim_profundidad > 0:
                    volumen_m3 = dim_largo * dim_ancho * dim_profundidad
                    volumen_litros = int(volumen_m3 * 1000)
                    dimensiones_piscina = f"{dim_largo}m x {dim_ancho}m x {dim_profundidad}m (Volumen: {volumen_litros:,} Lts)"
                    
                    if piscina_estatus == "Piscina Operativa Completa":
                        valor_piscina_usd = volumen_m3 * 400.0 # Aprox $400 por m3 terminada con equipos
                    elif piscina_estatus == "Piscina en Estructura / Obra Gris":
                        valor_piscina_usd = volumen_m3 * 130.0 # Aprox $130 por m3 solo vaso de concreto

                valor_total_venta = valor_construccion + valor_terreno + valor_piscina_usd
                
                if "Alquiler" in transaccion_t:
                    valor_estimado = round(valor_total_venta * 0.007, 2)
                    tipo_resultado = "Canon de Alquiler Sugerido Mensual"
                else:
                    valor_estimado = round(valor_total_venta, 2)
                    tipo_resultado = "Valor Comercial Estimado de Venta"

                st.success(f"💰 **{tipo_resultado}:** ${valor_estimado:,.2f} USD")
                st.info(
                    f"📊 **Desglose Técnico Avanzado:**\n\n"
                    f"- **Ejecución de Obra:** {porcentaje_obra}% ({estado_obra})\n"
                    f"- **Cercado Perimetral:** {porcentaje_cerca}% concluido\n"
                    f"- **Piscina:** {piscina_estatus} [{dimensiones_piscina}] -> Valor agregado: ${valor_piscina_usd:,.2f} USD\n"
                    f"- **Tanque Subterráneo:** {capacidad_tanque:,} Litros\n"
                    f"- **Área Techada:** {m2_construccion_t} m² | **Terreno:** {m2_terreno_t} m²"
                )
                
                msg_tasacion = (
                    f"Hola, solicito informe de tasación avanzada:%0A"
                    f"*Inmueble:* {tipo_t} en {región_t} - {mun_t} ({sector_t})%0A"
                    f"*Avance de Obra:* {porcentaje_obra}%%0A"
                    f"*Cercado:* {porcentaje_cerca}% ({tipo_cerca})%0A"
                    f"*Piscina:* {piscina_estatus} ({dimensiones_piscina})%0A"
                    f"*Tanque:* {capacidad_tanque:,} Lts%0A"
                    f"*Resultado {tipo_resultado}:* ${valor_estimado:,.2f} USD"
                )

            link_wa_t = f"https://wa.me/{MI_NUMERO_WA}?text={msg_tasacion}"
            
            st.link_button("📱 Recibir Informe Detallado en WhatsApp", link_wa_t, use_container_width=True)
            st.link_button(f"📍 Ver {sector_t} en Google Maps", url_mapa_t, use_container_width=True)

# =========================================================
# PESTAÑA 4: INVENTARIO GOOGLE SHEETS (PROTEGIDO CON CONTRASEÑA)
# =========================================================
with tab_inventario:
    st.subheader("📂 Inventario General Conectado a Google Sheets")
    st.markdown("Área restringida exclusiva para la administración del portal.")
    
    CLAVE_ADMIN = "tu_clave_secreta_2026"
    
    password_ingresada = st.text_input("Introduce la clave de Administrador para acceder:", type="password", key="pass_admin_inv")
    
    if password_ingresada == CLAVE_ADMIN:
        st.success("🔓 Acceso de administrador concedido.")
        st.markdown("---")
        st.link_button("📊 Abrir/Editar Hoja de Cálculo Directa en Google Sheets", SHEET_URL, use_container_width=True)
        st.markdown("---")

        if df_inmuebles is not None and not df_inmuebles.empty:
            st.dataframe(df_inmuebles, use_container_width=True)
            st.caption(f"Total de registros activos en la base de datos: {len(df_inmuebles)}")
        else:
            st.info("No se han cargado datos o la hoja de Google Sheets está vacía por los momentos.")
            
    elif password_ingresada != "":
        st.error("❌ Clave incorrecta. Acceso denegado.")
    else:
        st.warning("🔒 Por favor introduce la contraseña de administrador para visualizar el inventario y los accesos.")

# =========================================================
# PESTAÑA 5: GENERADOR LEGAL COMPLETO (ARRENDAMIENTO Y COMPRAVENTA SAREN)
# =========================================================
with tab_contratos:
    st.subheader("📄 Generador de Borrador de Instrumento Legal")
    st.markdown("Selecciona el tipo de documento. Redacción adaptada a las normas legales venezolanas vigentes y exigencias del SAREN.")

    tipo_contrato = st.selectbox(
        "Selecciona el Tipo de Instrumento Legal:",
        ["Contrato de Arrendamiento (Alquiler)", "Documento Definitivo de Compraventa (Para Registro Inmobiliario)", "Opción a Compra-Venta"]
    )

    with st.form("form_generador_contratos_vzla_completo"):
        st.markdown("### ⚖️ DATOS DEL ABOGADO REDACTOR / VISANTE")
        col_abg1, col_abg2 = st.columns(2)
        with col_abg1:
            nombre_abogado = st.text_input("Nombre Completo del Abogado Redactor:", "Dr. Carlos Eduardo Mendoza")
        with col_abg2:
            ipsa_abogado = st.text_input("N° de Registro IPSA:", "248.910")

        st.markdown("### 👤 PARTE A (Propietario / Arrendador / Vendedor)")
        col_pa1, col_pa2 = st.columns(2)
        with col_pa1:
            nombre_p1 = st.text_input("Nombre Completo / Razón Social:", "Juan Carlos Pérez")
            ci_p1 = st.text_input("Cédula de Identidad / RIF:", "V-12.345.678")
            email_p1 = st.text_input("Correo Electrónico de Notificaciones:", "juancarlos.perez@gmail.com")
        with col_pa2:
            estado_civil_p1 = st.selectbox("Estado Civil:", ["Soltero(a)", "Casado(a)", "Divorciado(a)", "Viudo(a)"])
            domicilio_p1 = st.text_input("Domicilio Legal Completo:", "Porlamar, Municipio Mariño, Estado Nueva Esparta")
            tel_p1 = st.text_input("Teléfono Móvil de Notificaciones:", "0412-1234567")

        st.markdown("### 👤 PARTE B (Inquilino / Arrendatario / Comprador)")
        col_pb1, col_pb2 = st.columns(2)
        with col_pb1:
            nombre_p2 = st.text_input("Nombre Completo B:", "María Alejandra Gómez")
            ci_p2 = st.text_input("Cédula / RIF B:", "V-18.765.432")
            email_p2 = st.text_input("Correo Electrónico B:", "mariao.gomez@gmail.com")
        with col_pb2:
            estado_civil_p2 = st.selectbox("Estado Civil B:", ["Soltero(a)", "Casado(a)", "Divorciado(a)", "Viudo(a)"])
            domicilio_p2 = st.text_input("Domicilio Legal B:", "Caracas, Distrito Capital")
            tel_p2 = st.text_input("Teléfono Móvil B:", "0414-9876543")

        st.markdown("### 🏠 IDENTIFICACIÓN Y REGISTRO DEL INMUEBLE")
        región_cnt = st.selectbox("Estado o Región:", list(ESTRUCTURA_GEOGRAFICA.keys()), key="reg_cnt")
        mun_cnt = st.selectbox("Municipio:", list(ESTRUCTURA_GEOGRAFICA[región_cnt].keys()), key="mun_cnt")
        sector_cnt = st.selectbox("Urbanización / Sector:", ESTRUCTURA_GEOGRAFICA[región_cnt][mun_cnt], key="sec_cnt")
        
        tipo_inm_cnt = st.selectbox("Tipo de Inmueble:", TIPOS_INMUEBLES, key="tipo_cnt")
        detalles_inm_cnt = st.text_area("Linderos completos, Metros2, Ficha Catastral:", "Un inmueble tipo apartamento constante de 120m² de construcción. Linderos: Norte: Apto 4-C; Sur: Área común; Este: Fachada Este; Oeste: Pasillo. Ficha Catastral N° 4010128.")

        st.markdown("#### 📜 Datos del Título de Propiedad Anterior (Para Compraventa SAREN)")
        col_reg1, col_reg2 = st.columns(2)
        with col_reg1:
            registro_origen = st.text_input("Oficina de Registro Inmobiliario:", "Registro Inmobiliario del Municipio Mariño")
            doc_numero = st.text_input("N° de Documento / Asunto:", "45")
            doc_tomo = st.text_input("Tomo:", "12")
        with col_reg2:
            doc_protocolo = st.text_input("Protocolo / Matrícula:", "Primero (1°)")
            doc_fecha = st.text_input("Fecha del Título Anterior:", "15/03/2018")
            alicuota_condominio = st.text_input("Alícuota % (si es Apartamento/Oficina):", "2.15%")

        if tipo_contrato == "Contrato de Arrendamiento (Alquiler)":
            st.markdown("### 🔑 CONDICIONES ESPECÍFICAS DE ALQUILER")
            col_oper1, col_oper2 = st.columns(2)
            with col_oper1:
                juegos_llaves = st.number_input("Juegos de Llaves Entregados:", min_value=1, value=2)
                max_ocupantes = st.number_input("Ocupación Máxima (Personas):", min_value=1, value=4)
            with col_oper2:
                permite_mascotas = st.radio("Mascotas en el Inmueble:", ["Prohibidas expresamente", "Permitidas previo acuerdo por escrito"])
                obras_inquilino = st.radio("Mejoras / Obras por el Inquilino:", ["Prohibidas sin consentimiento por escrito", "Permitidas en beneficio del inmueble"])

        st.markdown("### 💰 CONDICIONES FINANCIERAS Y PAGO")
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            monto_negocio = st.number_input("Monto en USD ($):", min_value=1, value=45000 if "Compraventa" in tipo_contrato else 500, step=500)
            monto_garantia = st.number_input("Garantía / Depósito / Arras ($ USD):", min_value=0, value=1500, step=100)
            dia_pago = st.number_input("Día límite de pago cada mes (Si es alquiler):", min_value=1, max_value=28, value=5)
        with col_m2:
            duracion_meses = st.number_input("Plazo del Contrato (Meses para Alquiler / Días para Venta):", min_value=1, value=12 if "Arrendamiento" in tipo_contrato else 60)
            pagador_servicios = st.selectbox("Servicios y Condominio:", ["A cargo exclusivo del Arrendatario", "Servicios Arrendatario / Condominio Arrendador", "Incluidos en el canon"])
            lugar_firma = st.text_input("Ciudad de Firma / Registro:", "Porlamar")

        st.markdown("#### 🏦 Datos de Pago (Tasa BCV y Transferencia/Pago Móvil)")
        col_banc1, col_banc2 = st.columns(2)
        with col_banc1:
            banco_titular = st.text_input("Titular de la Cuenta:", "Juan Carlos Pérez")
            banco_nombre = st.text_input("Banco y N° Cuenta / Pago Móvil / Ref:", "Banesco N° 0134-XXXX-XXXX-XXXX / Ref: 987654")
        with col_banc2:
            banco_rif = st.text_input("Cédula / RIF del Titular:", "V-12345678")

        btn_generar_doc = st.form_submit_button("📄 Generar Documento Legal Adaptado", use_container_width=True)

    if btn_generar_doc:
        fecha_hoy = datetime.now().strftime("%d de %B de %Y")
        
        if "Compraventa" in tipo_contrato:
            borrador_texto = f"""CIUDADANO:
REGISTRADOR(A) INMOBILIARIO(A) DEL CIRCUITO DEL {mun_cnt.upper()}, {región_cnt.upper()}.
SU DESPACHO.-

Nosotros, {nombre_p1}, venezolano(a), mayor de edad, estado civil {estado_civil_p1}, titular de la Cédula de Identidad N° {ci_p1}, domiciliado(a) en {domicilio_p1}, por una parte, y quien en lo sucesivo se denominará EL VENDEDOR; y por la otra parte, {nombre_p2}, venezolano(a), mayor de edad, estado civil {estado_civil_p2}, titular de la Cédula de Identidad N° {ci_p2}, domiciliado(a) en {domicilio_p2}, quien en lo sucesivo se denominará EL COMPRADOR, hemos convenido en celebrar el presente Contrato de Compraventa, contenido en las cláusulas siguientes:

PRIMERA (DEL INMUEBLE): Declara EL VENDEDOR que es único e exclusivo propietario de un inmueble tipo {tipo_inm_cnt}, ubicado en: {sector_cnt}, {mun_cnt}, {región_cnt}. 
Características, Linderos y Ficha Catastral: {detalles_inm_cnt}. (Alícuota de Condominio: {alicuota_condominio}).

SEGUNDA (TÍTULO DE ADQUISICIÓN): El inmueble antes descrito lo adquirió EL VENDEDOR según documento inscrito por ante la Oficina de {registro_origen}, bajo el N° {doc_numero}, Tomo {doc_tomo}, Protocolo {doc_protocolo}, en fecha {doc_fecha}.

TERCERA (DE LA VENTA Y PRECIO): Declara EL VENDEDOR que por medio del presente instrumento da en Venta Pura y Simple, Perfecta e Irrevocable a EL COMPRADOR el inmueble antes identificado. El precio convenido por las partes para esta negociación es la cantidad de {monto_negocio:,.2f} DÓLARES DE LOS ESTADOS UNIDOS DE AMÉRICA ($ USD), cancelados en divisa pactada o en Bolívares (VES) ajustados a la tasa oficial de cambio del Banco Central de Venezuela (BCV) al día del pago efectivo (Convenio Cambiario N° 1). EL VENDEDOR declara tener recibida dicha suma a su entera satisfacción mediante la siguiente transacción bancaria: {banco_nombre}, a nombre de {banco_titular} (C.I./RIF: {banco_rif}).

CUARTA (LIBRE DE GRAVAMEN Y SANEAMIENTO): Declara EL VENDEDOR que el inmueble se encuentra libre de toda hipoteca, embargo, prohibición de enajenar y gravar, pleito pendiente o gravamen, obligándose en todo caso al saneamiento de Ley conforme al Código Civil.

QUINTA (SOLVENCIAS Y TAXAS): EL VENDEDOR entrega el inmueble totalmente solvente en el pago de impuestos municipales (Derecho de Frente y Aseo Urbano), servicios públicos domiciliarios y cuotas de condominio acumuladas a la fecha.

SEXTA (DECLARACIÓN FISCAL / VIVIENDA PRINCIPAL): Las partes declaran a los fines fiscales y tributarios ante el SENIAT que la presente operación cumple con la normativa de Vivienda Principal o la consignación de la Planilla Forma 33 según corresponda.

SÉPTIMA (GASTOS DE REGISTRO): Los gastos de registro, aranceles y tributos que cause la protocolización del presente documento serán asumidos por EL COMPRADOR.

Se hacen dos (2) ejemplares de un mismo tenor en la ciudad de {lugar_firma}, a los {fecha_hoy}.


EL VENDEDOR ________________________        EL COMPRADOR ________________________
{nombre_p1}                                 {nombre_p2}
C.I.: {ci_p1}                               C.I.: {ci_p2}

Documento redactado y visado por el Abogado {nombre_abogado}, inscrito en el IPSA bajo el N° {ipsa_abogado}.
"""

        elif "Arrendamiento" in tipo_contrato:
            if tipo_inm_cnt in ["Local Comercial", "Oficina", "Posada / Hotel"]:
                marco_ley = "Decreto con Rango, Valor y Fuerza de Ley de Regulación del Arrendamiento Inmobiliario para Uso Comercial (Decreto N° 929, G.O. N° 40.418)."
                destino_uso = f"Uso comercial exclusivo de la firma arrendataria."
                prorroga_clausula = f"QUINTA (PRÓRROGA LEGAL OBLIGATORIA): Cumplido el plazo de {duracion_meses} meses, aplicará la Prórroga Legal Obligatoria (Art. 38 del Decreto N° 929)."
            else:
                marco_ley = "Ley para la Regularización y Control de los Arrendamientos de Vivienda y las disposiciones del Código Civil."
                destino_uso = f"Uso estrictamente residencial y habitación del ARRENDATARIO y su núcleo familiar (ocupación máxima: {max_ocupantes} personas)."
                prorroga_clausula = f"QUINTA (DURACIÓN Y RENOVACIÓN): El contrato tendrá una vigencia de {duracion_meses} meses (a falta de pacto la ley prescribe un mínimo de 1 año)."

            borrador_texto = f"""================================================================================
          CONTRATO DE ARRENDAMIENTO INMOBILIARIO ({tipo_inm_cnt.upper()})
================================================================================

En la ciudad de {lugar_firma}, a los {fecha_hoy}, entre los ciudadanos:

POR UNA PARTE (EL ARRENDADOR): {nombre_p1} (C.I./RIF: {ci_p1}, Estado Civil: {estado_civil_p1}, Domicilio: {domicilio_p1}, Email: {email_p1}, Tel: {tel_p1})
POR LA OTRA PARTE (EL ARRENDATARIO): {nombre_p2} (C.I./RIF: {ci_p2}, Estado Civil: {estado_civil_p2}, Domicilio: {domicilio_p2}, Email: {email_p2}, Tel: {tel_p2})

Acuerdan celebrar el presente Contrato de Arrendamiento regido por: {marco_ley}

CLÁUSULAS:
PRIMERA (OBJETO Y USO): EL ARRENDADOR cede en alquiler el inmueble tipo {tipo_inm_cnt}, ubicado en {sector_cnt}, {mun_cnt}, {región_cnt}. Dirección y catastro: {detalles_inm_cnt}. Destino: {destino_uso}
SEGUNDA (DURACIÓN): El contrato tendrá una duración de {duracion_meses} meses continuos.
TERCERA (CANON Y PAGO BCV): El canon mensual es de {monto_negocio:,.2f} DÓLARES ($ USD), pagaderos los primeros {dia_pago} días de cada mes en divisa o Bolívares (VES) a la tasa oficial del BCV. Pago a: {banco_nombre} - Titular: {banco_titular} (C.I./RIF: {banco_rif}).
CUARTA (GARANTÍA): EL ARRENDATARIO entrega {monto_garantia:,.2f} USD (máximo 3 cánones) como depósito de garantía.
{prorroga_clausula}
SEXTA (SERVICIOS Y CONDOMINIO): Gastos de servicios y condominio: {pagador_servicios}.
SÉPTIMA (LLAVES, MASCOTAS Y OBRAS): Llaves entregadas: {juegos_llaves} juegos. Mascotas: {permite_mascotas}. Obras: {obras_inquilino}.
OCTAVA (TERMINACIÓN Y RESOLUCIÓN): El incumplimiento de tres (3) cánones consecutivos o servicios por 3 meses dará derecho a la resolución del contrato.
NOVENA (NOTIFICACIONES Y JURISDICCIÓN): Notificaciones válidas por email/WhatsApp. Sometimiento a conciliación o Tribunales de Municipio de la jurisdicción.

__________________________________            __________________________________
            EL ARRENDADOR                                 EL ARRENDATARIO
     {nombre_p1} (C.I.: {ci_p1})                   {nombre_p2} (C.I.: {ci_p2})
"""

        else:
            borrador_texto = f"""================================================================================
             CONTRATO DE OPCIÓN A COMPRA-VENTA DE INMUEBLE
================================================================================

En la ciudad de {lugar_firma}, a los {fecha_hoy}, entre EL VENDEDOR: {nombre_p1} (C.I.: {ci_p1}), y EL COMPRADOR: {nombre_p2} (C.I.: {ci_p2}), se conviene celebrar el presente Contrato de Opción a Compra-Venta bajo los preceptos del Código Civil Venezolano:

PRIMERA (EL INMUEBLE): EL VENDEDOR es propietario del inmueble tipo {tipo_inm_cnt}, ubicado en {sector_cnt}, {mun_cnt}, {región_cnt}. Detalles registrales: {detalles_inm_cnt}. Título inscrito en {registro_origen}, bajo el N° {doc_numero}, Tomo {doc_tomo}.
SEGUNDA (PRECIO Y MONEDA): El precio pactado es de {monto_negocio:,.2f} USD, pagaderos en divisa o Bolívares (VES) a tasa BCV (Convenio Cambiario N° 1).
TERCERA (ARRAS PENITENCIALES): EL COMPRADOR entrega {monto_garantia:,.2f} USD en calidad de arras penitenciales (Art. 1.263 C.C.). Si la venta falla por culpa de EL COMPRADOR, perderá la señal. Si es por EL VENDEDOR, restituirá el doble.
CUARTA (PLAZO): Se fijan {duracion_meses} días continuos para protocolizar el documento definitivo ante el Registro Inmobiliario.

__________________________________            __________________________________
     EL VENDEDOR / PROPIETARIO                     EL COMPRADOR / OPTANTE
     {nombre_p1} (C.I.: {ci_p1})                   {nombre_p2} (C.I.: {ci_p2})
"""

        st.success("✨ ¡Documento redactado con éxito ajustado a las normas legales venezolanas!")
        st.text_area("📄 Texto Completo para Copiar / Editar:", borrador_texto, height=400)

        st.markdown("### 📥 Descarga del Documento y Notificación")
        col_down1, col_down2 = st.columns(2)
        
        with col_down1:
            nombre_archivo = f"Documento_{tipo_inm_cnt}_{lugar_firma}.txt"
            st.download_button(
                label="💾 Descargar Documento Editable (.txt / Word)",
                data=borrador_texto,
                file_name=nombre_archivo,
                mime="text/plain",
                use_container_width=True
            )

        with col_down2:
            msg_contrato_wa = (
                f"Hola, adjunto el resumen del borrador legal generado:%0A"
                f"*Tipo:* {tipo_contrato}%0A"
                f"*Inmueble:* {tipo_inm_cnt} en {sector_cnt}, {mun_cnt}%0A"
                f"*Parte A:* {nombre_p1} ({ci_p1})%0A"
                f"*Parte B:* {nombre_p2} ({ci_p2})%0A"
                f"*Monto:* ${monto_negocio:,.2f} USD%0A"
                f"*Abogado Visante:* {nombre_abogado} (IPSA: {ipsa_abogado})%0A%0A"
                f"_Documento listo para revisión del Registro o Abogado de la firma._"
            )
            link_wa_contrato = f"https://wa.me/{MI_NUMERO_WA}?text={msg_contrato_wa}"
            st.link_button("📱 Notificar y Enviar por WhatsApp", link_wa_contrato, use_container_width=True)
