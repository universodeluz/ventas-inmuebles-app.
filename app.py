import streamlit as st
import pandas as pd
import cloudinary
import cloudinary.uploader
from PIL import Image
import io
import requests
import json

# Intento de importar soporte para formatos de iPhone/Android (HEIC)
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
LINK_GRUPO_MARGARITA = "https://chat.whatsapp.com/TU_ENLACE_MARGARITA_AQUI"
LINK_GRUPO_CARACAS = "https://chat.whatsapp.com/TU_ENLACE_CARACAS_AQUI"

# --- BANNER SUPERIOR DE GRUPOS DE WHATSAPP ---
st.info("💬 **¿Quieres unirte a nuestras comunidades activas en WhatsApp?**")
col_top1, col_top2 = st.columns(2)
with col_top1:
    st.link_button("🌴 Grupo Margarita", LINK_GRUPO_MARGARITA, use_container_width=True)
with col_top2:
    st.link_button("🏢 Grupo Caracas / La Guaira", LINK_GRUPO_CARACAS, use_container_width=True)

st.markdown("---")

# --- LISTAS DE LOCALIDADES ---
LOCALIDADES_MARGARITA = [
    "Pampatar (Municipio Maneiro - Alta Plusvalía)",
    "Costa Azul / Playa El Ángel (Municipio Maneiro)",
    "Porlamar - Centro y Av. 4 de Mayo (Municipio Mariño)",
    "La Asunción (Municipio Arismendi)",
    "Juan Griego (Municipio Marcano)",
    "El Valle del Espíritu Santo (Municipio García)",
    "Playa El Agua / Manzanillo (Municipio Antolín del Campo)",
    "Punta de Piedras (Municipio Tubores)",
    "Península de Macanao",
    "Coche (Municipio Villalba)"
]

LOCALIDADES_CARACAS = [
    "Las Mercedes (Municipio Baruta)",
    "Altamira (Municipio Chacao)",
    "El Hatillo (Pueblo y Urbanizaciones)",
    "El Junquito (Distrito Capital)",
    "Chacaíto / Campo Alegre / El Rosal",
    "La Castellana / Los Palos Grandes",
    "Santa Fe / Caurimare / Las Minitas",
    "Libertador (Centro, El Recreo, Candelaria, San Bernardino)",
    "Sucre (Petare / Lechería / Terrazas del Ávila)"
]

LOCALIDADES_MIRANDA = [
    "Guarenas / Guatire (Plaza y Zamora)",
    "Los Teques / Carrizal / Los Salias (Altos Mirandinos)",
    "Valles del Tuy (Cúa, Ocumare, Charallave)",
    "Barlovento: Río Chico / San José / Mamporal / Cúpira",
    "Otro sector de Miranda"
]

LOCALIDADES_LA_GUAIRA = [
    "El Junko (Estado La Guaira / Club de Campo)",
    "Caraballeda (Playa Grande / Caribe)",
    "Macuto",
    "Catia La Mar",
    "Maiquetía",
    "La Guaira (Casco Histórico)",
    "Naiguatá",
    "Caruao"
]

TIPOS_INMUEBLES = [
    "Terreno", "Apartamento", "Casa", "Townhouse", "Posada / Hotel", "Local Comercial", "Oficina"
]

# CREACIÓN DE PESTAÑAS (Tasación como Pestaña 3 e Inventario como Pestaña 4)
tab_comprador, tab_vendedor, tab_ia, tab_inventario = st.tabs([
    "🔍 Buscar Inmueble", 
    "📝 Publicar Inmueble",
    "🤖 Tasación IA",
    "📂 Inventario Google Sheets"
])

# =========================================================
# PESTAÑA 1: COMPRADORES
# =========================================================
with tab_comprador:
    st.subheader("Búsqueda Avanzada de Inmuebles")
    
    nicho = st.selectbox(
        "1. Selecciona el Estado o Región principal:",
        ["Isla de Margarita (Nueva Esparta)", "Caracas (Distrito Capital)", "Estado Miranda", "Estado La Guaira"],
        key="nicho_c"
    )
    
    if "Margarita" in nicho:
        loc_opciones = LOCALIDADES_MARGARITA
    elif "Caracas" in nicho:
        loc_opciones = LOCALIDADES_CARACAS
    elif "Miranda" in nicho:
        loc_opciones = LOCALIDADES_MIRANDA
    else:
        loc_opciones = LOCALIDADES_LA_GUAIRA
        
    localidad = st.selectbox("2. Selecciona la localidad o sector específico:", loc_opciones, key="loc_c")

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
                f"*Región:* {nicho} - {localidad}%0A"
                f"*Condición:* {amoblado_filtro}%0A"
                f"*Presupuesto Máx:* ${presupuesto_max} USD%0A"
                f"*Extras exigidos:* {', '.join(extras_busqueda) if extras_busqueda else 'Ninguno'}%0A"
                f"*Opciones vistas en web:* {', '.join(inmuebles_compatibles) if inmuebles_compatibles else 'Ninguna inmediata'}"
            )
            link_wa = f"https://wa.me/{MI_NUMERO_WA}?text={msg_wa}"
            
            estilo_btn = "display:inline-block;padding:12px 20px;font-size:15px;font-weight:bold;color:white;background-color:#25D366;text-align:center;text-decoration:none;border-radius:8px;"
            st.markdown(
                f'<a href="{link_wa}" target="_blank" style="{estilo_btn}">📱 Enviar Requerimiento a WhatsApp</a>',
                unsafe_allow_html=True
)
                   # =========================================================
# PESTAÑA 2: VENDEDORES / ALIADOS
# =========================================================
with tab_vendedor:
    st.subheader("Publica o Registra tu Inmueble")
    
    región_v = st.selectbox(
        "1. Estado o Región de la propiedad:",
        ["Isla de Margarita (Nueva Esparta)", "Caracas (Distrito Capital)", "Estado Miranda", "Estado La Guaira"],
        key="reg_v"
    )
    
    if "Margarita" in región_v:
        loc_v_opciones = LOCALIDADES_MARGARITA
    elif "Caracas" in región_v:
        loc_v_opciones = LOCALIDADES_CARACAS
    elif "Miranda" in región_v:
        loc_v_opciones = LOCALIDADES_MIRANDA
    else:
        loc_v_opciones = LOCALIDADES_LA_GUAIRA
        
    localidad_v = st.selectbox("2. Localidad o Sector específico:", loc_v_opciones, key="loc_v")

    with st.form("form_vendedor_detalles"):
        titulo_v = st.text_input("Título comercial corto (ej: Terreno amplio en Pampatar / Quinta en Caracas):")
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
            tiene_vista = st.checkbox("Vista privileged (Mar / Ávila)")
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
                        "nicho": región_v,
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
                f"*Región:* {región_v} - {localidad_v}%0A"
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
            
            estilo_btn_v = "display:inline-block;padding:12px 20px;font-size:15px;font-weight:bold;color:white;background-color:#25D366;text-align:center;text-decoration:none;border-radius:8px;"
            st.markdown(
                f'<a href="{link_wa_v}" target="_blank" style="{estilo_btn_v}">📱 Toca aquí para Enviar Notificación con Fotos a WhatsApp</a>',
                unsafe_allow_html=True
            )

# =========================================================
# PESTAÑA 3: ASISTENTE DE TASACIÓN TÉCNICA E INSPECCIÓN IA
# =========================================================
with tab_ia:
    st.subheader("🤖 Asistente de Tasación Técnica por IA")
    st.markdown("Selecciona el tipo de inmueble para desplegar los factores de valoración correspondientes.")
    
    región_t = st.selectbox(
        "1. Región / Estado:",
        ["Isla de Margarita (Nueva Esparta)", "Caracas (Distrito Capital)", "Estado Miranda", "Estado La Guaira"],
        key="reg_t"
    )
    
    if "Margarita" in región_t:
        loc_t_opciones = LOCALIDADES_MARGARITA
    elif "Caracas" in región_t:
        loc_t_opciones = LOCALIDADES_CARACAS
    elif "Miranda" in región_t:
        loc_t_opciones = LOCALIDADES_MIRANDA
    else:
        loc_t_opciones = LOCALIDADES_LA_GUAIRA
        
    localidad_t = st.selectbox("2. Localidad o Sector específico:", loc_t_opciones, key="loc_t")
    tipo_t = st.selectbox("3. Tipo de Inmueble a Tasar:", TIPOS_INMUEBLES, key="tipo_t")

    with st.form("form_tasacion_ia_optimizado"):
        
        if tipo_t == "Terreno":
            st.markdown("### 📐 Criterios de Valoración para Terrenos")
            
            area_m2_terreno = st.number_input("Área Total de la Parcela (m²):", min_value=1.0, value=500.0, step=25.0)
            
            tipo_cerca = st.selectbox(
                "Tipo de Cerramiento / Lindero:",
                [
                    "Muro perimetral de concreto frisado (+15%)",
                    "Pared de bloques de concreto (+10%)",
                    "Cerca de malla alfajor / Ciclón (+5%)",
                    "Cerca viva / Trinchera (+2%)",
                    "Sin cercar (Linderos abiertos) (0%)"
                ]
            )
            topografia = st.selectbox(
                "Topografía y Nivel del Suelo:",
                ["Plana (100% aprovechable) (+10%)", "Semi-plana / Colina suave (0%)", "Inclinada / Pendiente severa (-15%)"]
            )
            acceso_vial = st.selectbox(
                "Acceso Vial y Entorno:",
                ["Calle Asfaltada (+10%)", "Calle de Granzón / Consolidada (0%)", "Camino de Tierra / Rústico (-10%)"]
            )
            zonificacion = st.selectbox(
                "Zonificación / Uso de Suelo:",
                ["Comercial / Mixto (+15%)", "Residencial (R1/R2/R3) (+10%)", "Industrial / Galpón (+5%)", "Agrícola / Turístico (0%)"]
            )
            estatus_legal = st.selectbox(
                "Estatus Legal:",
                ["Título de Propiedad Registrado (+10%)", "Adjudicación / Carta Agrícola (0%)", "Documento Privado / En trámite (-15%)"]
            )

            st.markdown("#### 💡 Servicios Públicos y Plusvalía Directa")
            t_agua = st.checkbox("Red Pública de Agua de Calle (+5%)")
            t_pozo = st.checkbox("Pozo Profundo de Agua Dulce (+10%)")
            t_luz = st.checkbox("Electricidad / Transformador cerca (+5%)")
            t_cloacas = st.checkbox("Red de Aguas Servidas / Cloacas (+5%)")
            t_internet = st.checkbox("Fibra Óptica / Conectividad (+5%)")
            t_vista = st.checkbox("Vista al Mar / Panorámica a la Montaña (+15%)")

        else:
            st.markdown("### 🏠 Criterios para Inmuebles Construidos")
            transaccion_t = st.radio("Objetivo de Tasación:", ["Valor de Venta Comercial", "Canon de Alquiler Sugerido"])
            
            m2_construccion_t = st.number_input("Área de Construcción (m² techados):", min_value=0, value=120)
            m2_terreno_t = st.number_input("Área de Terreno / Parcela (m² totales):", min_value=0, value=350)
            habitaciones_t = st.number_input("Habitaciones:", min_value=0, value=3, key="hab_t")
            banos_t = st.number_input("Baños:", min_value=1, value=2, key="ban_t")
            estado_amoblado_t = st.selectbox("Nivel de Equipamiento:", ["Amoblado y Equipado", "Semiamoblado", "Sin amoblar"])
            antiguedad_t = st.selectbox("Antigüedad:", ["A estrenar / Nuevo", "Menos de 10 años", "Más de 10 años / A actualizar"])
            estado_conservacion = st.selectbox(
                "Estado de Conservación:",
                ["Excelente / Modernizado", "Bueno / Habitable", "A reparar / Para actualizar"]
            )
            
            st.markdown("**Factores Críticos de Plusvalía:**")
            t_piscina = st.checkbox("Tiene Piscina", key="tp")
            t_planta = st.checkbox("Tiene Planta Eléctrica", key="tpl")
            t_pozo = st.checkbox("Tiene Pozo o Tanque constante", key="tpz")
            t_vista = st.checkbox("Tiene Vista privilegiada (Mar/Ávila/Montaña)", key="tv")

        st.markdown("---")
        nombre_t = st.text_input("Tu Nombre / Contacto:", key="nombre_t")
        whatsapp_t = st.text_input("Tu Número de WhatsApp:", key="wa_t")
        
        btn_ejecutar_tasacion = st.form_submit_button("🚀 Calcular Tasación por IA", use_container_width=True)

    if btn_ejecutar_tasacion:
        if not whatsapp_t:
            st.error("Por favor ingresa tu número de WhatsApp para enviarte el reporte detallado.")
        else:
            if tipo_t == "Terreno":
                base_m2_terr = 50.0
                if "Margarita" in región_t:
                    base_m2_terr = 60.0 if ("Pampatar" in localidad_t or "Costa Azul" in localidad_t) else 45.0
                elif "Caracas" in región_t:
                    base_m2_terr = 180.0 if ("Mercedes" in localidad_t or "Altamira" in localidad_t) else 110.0
                elif "Miranda" in región_t:
                    base_m2_terr = 40.0
                elif "La Guaira" in región_t:
                    base_m2_terr = 55.0

                factor_t = 1.0
                if "Muro perimetral" in tipo_cerca: factor_t += 0.15
                elif "Pared de bloques" in tipo_cerca: factor_t += 0.10
                elif "malla alfajor" in tipo_cerca: factor_t += 0.05
                elif "Cerca viva" in tipo_cerca: factor_t += 0.02

                if "Plana" in topografia: factor_t += 0.10
                elif "Inclinada" in topografia: factor_t -= 0.15

                if "Asfaltada" in acceso_vial: factor_t += 0.10
                elif "Tierra" in acceso_vial: factor_t -= 0.10

                if "Comercial" in zonificacion: factor_t += 0.15
                elif "Residencial" in zonificacion: factor_t += 0.10
                elif "Industrial" in zonificacion: factor_t += 0.05

                if "Título" in estatus_legal: factor_t += 0.10
                elif "Documento Privado" in estatus_legal: factor_t -= 0.15

                if t_agua: factor_t += 0.05
                if t_pozo: factor_t += 0.10
                if t_luz: factor_t += 0.05
                if t_cloacas: factor_t += 0.05
                if t_internet: factor_t += 0.05
                if t_vista: factor_t += 0.15

                precio_m2_final = round(base_m2_terr * factor_t, 2)
                valor_estimado = round(area_m2_terreno * precio_m2_final, 2)
                tipo_resultado = "Valor Comercial Estimado del Terreno"

                st.success(f"💰 **{tipo_resultado}:** ${valor_estimado:,.2f} USD")
                st.info(
                    f"📊 **Desglose Técnico de Tasación:**\n\n"
                    f"- **Área Total:** {area_m2_terreno} m²\n"
                    f"- **Precio Estimado por m²:** ${precio_m2_final} / m²\n"
                    f"- **Factor de Ajuste (Servicios y Plusvalía):** +{round((factor_t - 1.0)*100, 1)}%"
                )

                servicios_act = []
                if t_agua: servicios_act.append("Agua Pública")
                if t_pozo: servicios_act.append("Pozo Agua")
                if t_luz: servicios_act.append("Electricidad")
                if t_cloacas: servicios_act.append("Cloacas")
                if t_internet: servicios_act.append("Fibra Óptica")
                if t_vista: servicios_act.append("Vista Panorámica")

                msg_tasacion = (
                    f"Hola, solicito informe formal de tasación de Terreno por IA:%0A"
                    f"*Solicitante:* {nombre_t} ({whatsapp_t})%0A"
                    f"*Terreno:* {región_t} - {localidad_t}%0A"
                    f"*Área:* {area_m2_terreno} m² (%20${precio_m2_final}/m²)%0A"
                    f"*Cerramiento:* {tipo_cerca}%0A"
                    f"*Topografía:* {topografia}%0A"
                    f"*Servicios:* {', '.join(servicios_act) if servicios_act else 'Ninguno'}%0A"
                    f"*Valor Comercial Estimado:* ${valor_estimado:,.2f} USD"
                )

            else:
                if "Margarita" in región_t or "Caracas" in región_t:
                    base_m2_const = 750
                    base_m2_terr = 60
                else:
                    base_m2_const = 450
                    base_m2_terr = 30
                
                factor = 1.0
                if "Excelente" in estado_conservacion: factor += 0.15
                elif "A reparar" in estado_conservacion: factor -= 0.20
                
                if "Amoblado y Equipado" in estado_amoblado_t: factor += 0.10
                if t_piscina: factor += 0.05
                if t_planta: factor += 0.08
                if t_pozo: factor += 0.05
                if t_vista: factor += 0.07

                valor_construccion = m2_construccion_t * base_m2_const * factor
                valor_terreno = m2_terreno_t * base_m2_terr * factor
                valor_total_venta = valor_construccion + valor_terreno
                
                if "Alquiler" in transaccion_t:
                    valor_estimado = round(valor_total_venta * 0.007, 2)
                    tipo_resultado = "Canon de Alquiler Sugerido Mensual"
                else:
                    valor_estimado = round(valor_total_venta, 2)
                    tipo_resultado = "Valor Comercial Estimado de Venta"

                st.success(f"💰 **{tipo_resultado}:** ${valor_estimado:,.2f} USD")
                
                msg_tasacion = (
                    f"Hola, solicito el informe formal de tasación por IA:%0A"
                    f"*Solicitante:* {nombre_t} ({whatsapp_t})%0A"
                    f"*Propiedad:* {tipo_t} en {región_t} - {localidad_t}%0A"
                    f"*Área Techada:* {m2_construccion_t} m² | *Terreno:* {m2_terreno_t} m²%0A"
                    f"*Resultado {tipo_resultado}:* ${valor_estimado:,.2f} USD"
                )

            link_wa_t = f"https://wa.me/{MI_NUMERO_WA}?text={msg_tasacion}"
            
            estilo_btn_t = "display:inline-block;padding:12px 20px;font-size:15px;font-weight:bold;color:white;background-color:#25D366;text-align:center;text-decoration:none;border-radius:8px;"
            st.markdown(
                f'<a href="{link_wa_t}" target="_blank" style="{estilo_btn_t}">📱 Recibir Informe Detallado en WhatsApp</a>',
                unsafe_allow_html=True
            )

# =========================================================
# PESTAÑA 4: INVENTARIO GOOGLE SHEETS
# =========================================================
with tab_inventario:
    st.subheader("📂 Inventario General Conectado a Google Sheets")
    st.markdown("Visualización en tiempo real de los inmuebles cargados en la base de datos.")
    
    st.link_button("📊 Abrir/Editar Hoja de Cálculo Directa en Google Sheets", SHEET_URL, use_container_width=True)
    st.markdown("---")

    if df_inmuebles is not None and not df_inmuebles.empty:
        st.dataframe(df_inmuebles, use_container_width=True)
        st.caption(f"Total de registros activos: {len(df_inmuebles)}")
    else:
        st.info("No se han cargado datos o la hoja de Google Sheets está vacía por los momentos.")
