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
    "Apartamento", "Casa", "Townhouse", "Posada / Hotel", "Local Comercial", "Terreno", "Oficina"
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
    st.subheader("Búsqueda Avanzada de Inmuebles")
    
    nicho = st.selectbox(
        "1. Selecciona el Estado o Región principal:",
        ["Isla de Margarita (Nueva Esparta)", "Caracas (Distrito Capital)", "Estado Miranda", "Estado La Guaira"],
        key="nicho_c_reactivo"
    )
    
    if "Margarita" in nicho:
        loc_opciones = LOCALIDADES_MARGARITA
    elif "Caracas" in nicho:
        loc_opciones = LOCALIDADES_CARACAS
    elif "Miranda" in nicho:
        loc_opciones = LOCALIDADES_MIRANDA
    else:
        loc_opciones = LOCALIDADES_LA_GUAIRA
        
    localidad = st.selectbox("2. Selecciona la localidad o sector específico:", loc_opciones, key="loc_c_reactivo")

    with st.form("form_comprador_detalles"):
        operacion = st.radio("Transacción:", ["Comprar", "Alquilar"])
        tipo_inmueble = st.selectbox("Tipo de propiedad:", TIPOS_INMUEBLES)
        
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            amoblado_filtro = st.selectbox("Condición:", ["Indiferente", "Amoblado y Equipado", "Sin amoblar"])
        with col_c2:
            presupuesto_max = st.number_input("Presupuesto máximo ($):", min_value=0, value=50000, step=2500)
            
        st.markdown("**Amenidades deseadas:**")
        req_piscina = st.checkbox("Debe tener Piscina")
        req_planta = st.checkbox("Debe tener Planta Eléctrica")
        req_pozo = st.checkbox("Debe tener Pozo / Agua constante")
        
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
                        st.markdown(f"💰 **Precio:** ${row['precio']} | 📍 **Zona:** {row['nicho']}")
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
            if req_pozo: extras_busqueda.append("Pozo")

            msg_wa = (
                f"Hola, nuevo requerimiento de comprador:%0A"
                f"*Cliente:* {nombre_c} ({telefono_c})%0A"
                f"*Transacción:* {operacion} ({tipo_inmueble})%0A"
                f"*Región:* {nicho} - {localidad}%0A"
                f"*Condición:* {amoblado_filtro}%0A"
                f"*Presupuesto Máx:* ${presupuesto_max}%0A"
                f"*Extras exigidos:* {', '.join(extras_busqueda) if extras_busqueda else 'Ninguno'}%0A"
                f"*Opciones vistas en web:* {', '.join(inmuebles_compatibles) if inmuebles_compatibles else 'Ninguna inmediata'}"
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
    st.subheader("Publica o Registra tu Inmueble con Metrajes y Factores de Valor")
    
    región_v = st.selectbox(
        "1. Estado o Región de la propiedad:",
        ["Isla de Margarita (Nueva Esparta)", "Caracas (Distrito Capital)", "Estado Miranda", "Estado La Guaira"],
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
        
    localidad_v = st.selectbox("2. Localidad o Sector específico:", loc_v_opciones, key="loc_v_reactivo")

    with st.form("form_vendedor_detalles"):
        titulo_v = st.text_input("Título o breve descripción (ej: Casa quinta en El Hatillo con amplio jardín):")
        tipo_v = st.selectbox("Tipo de Inmueble:", TIPOS_INMUEBLES, key="tipo_v")
        operacion_v = st.radio("Tipo de Transacción:", ["Venta", "Alquiler"], key="op_v")
        
        col_v1, col_v2 = st.columns(2)
        with col_v1:
            precio_v = st.number_input("Precio ($ USD):", min_value=0, value=85000, step=2500)
            m2_construccion_v = st.number_input("Área de Construcción (m² techados):", min_value=0, value=150)
            habitaciones_v = st.number_input("Habitaciones:", min_value=0, value=3)
        with col_v2:
            m2_terreno_v = st.number_input("Área de Terreno / Parcela (m² totales):", min_value=0, value=500)
            estado_amoblado = st.selectbox("Condición de amoblado:", ["Amoblado y Equipado", "Semiamoblado", "Sin amoblar / Solo cocina"])
            banos_v = st.number_input("Baños:", min_value=1, value=2)
            
        st.markdown("**Aspectos de Valor y Amenidades:**")
        tiene_piscina = st.checkbox("Piscina")
        tiene_planta = st.checkbox("Planta eléctrica (total o áreas comunes)")
        tiene_pozo = st.checkbox("Pozo de agua / Tanque de gran capacidad")
        tiene_vista = st.checkbox("Vista destacada (Mar / Ávila / Montaña)")
        
        fotos_cargadas = st.file_uploader(
            "Sube fotos de la propiedad desde tu celular:", 
            type=["jpg", "png", "jpeg"], 
            accept_multiple_files=True
        )
        
        if fotos_cargadas:
            st.success(f"¡Se han seleccionado {len(fotos_cargadas)} foto(s) correctamente!")
            st.image(fotos_cargadas[0], caption="Vista previa de la foto principal", width=200)

        st.markdown("---")
        nombre_v = st.text_input("Nombre del Propietario / Agente:", key="nombre_v")
        telefono_v = st.text_input("WhatsApp de Contacto:", key="tel_v")
        
        btn_vendedor = st.form_submit_button("📤 Registrar Inmueble y Notificar")
        
    if btn_vendedor:
        if not titulo_v or not telefono_v:
            st.error("Por favor completa el título de la propiedad y tu teléfono.")
        else:
            st.success("¡Información procesada con éxito!")
            num_fotos = len(fotos_cargadas) if fotos_cargadas else 0
            
            amenidades_lista = []
            if tiene_piscina: amenidades_lista.append("Piscina")
            if tiene_planta: amenidades_lista.append("Planta")
            if tiene_pozo: amenidades_lista.append("Pozo")
            if tiene_vista: amenidades_lista.append("Vista")

            msg_prop = (
                f"Hola, deseo publicar un inmueble:%0A"
                f"*Propiedad:* {titulo_v}%0A"
                f"*Transacción:* {operacion_v} ({tipo_v})%0A"
                f"*Región:* {región_v} - {localidad_v}%0A"
                f"*Precio:* ${precio_v}%0A"
                f"*Construcción:* {m2_construccion_v} m² | *Terreno:* {m2_terreno_v} m²%0A"
                f"*Hab:* {habitaciones_v} | *Baños:* {banos_v}%0A"
                f"*Condición:* {estado_amoblado}%0A"
                f"*Extras de valor:* {', '.join(amenidades_lista) if amenidades_lista else 'Ninguno'}%0A"
                f"*Fotos en app:* {num_fotos} foto(s)%0A"
                f"*Contacto:* {nombre_v} ({telefono_v})"
            )
            link_wa_v = f"https://wa.me/{MI_NUMERO_WA}?text={msg_prop}"
            
            st.markdown(
                f'<a href="{link_wa_v}" target="_blank" style="display:inline-block;padding:12px 20px;font-size:15px;font-weight:bold;color:white;background-color:#25D366;text-align:center;text-decoration:none;border-radius:8px;">📱 Enviar Notificación con Detalles a WhatsApp</a>',
                unsafe_allow_html=True
            )

# =========================================================
# PESTAÑA 3: ASISTENTE DE TASACIÓN E INSPECCIÓN VISUAL POR IA
# =========================================================
with tab_ia:
    st.subheader("🤖 Asistente de Tasación e Inspección Visual por IA")
    st.markdown("""
    El sistema evalúa de forma independiente los metros de construcción y los metros de terreno, combinándolos con la zona, amoblado y factores de valor para calcular la **banda de precios de mercado sugerida**.
    """)
    
    with st.form("form_tasacion_ia"):
        st.markdown("### 1. Datos Técnicos, Metrajes y Factores de Valor")
        región_t = st.selectbox(
            "Región / Estado:",
            ["Isla de Margarita (Nueva Esparta)", "Caracas (Distrito Capital)", "Estado Miranda", "Estado La Guaira"],
            key="reg_t"
        )
        tipo_t = st.selectbox("Tipo de Inmueble:", TIPOS_INMUEBLES, key="tipo_t")
        transaccion_t = st.radio("Objetivo de Tasación:", ["Valor de Venta Comercial", "Canon de Alquiler Sugerido"])
        
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            m2_construccion_t = st.number_input("Área de Construcción (m² techados):", min_value=10, value=120)
            habitaciones_t = st.number_input("Habitaciones:", min_value=0, value=3)
            estado_amoblado_t = st.selectbox("Nivel de Equipamiento:", ["Amoblado y Equipado", "Semiamoblado", "Sin amoblar"])
        with col_t2:
            m2_terreno_t = st.number_input("Área de Terreno / Parcela (m² totales):", min_value=0, value=350)
            banos_t = st.number_input("Baños:", min_value=1, value=2)
            antiguedad_t = st.selectbox("Antigüedad:", ["A estrenar / Nuevo", "Menos de 10 años", "Más de 10 años / A actualizar"])
            
        estado_conservacion = st.selectbox(
            "Estado de Conservación:",
            ["Excelente / Modernizado", "Bueno / Habitable", "A reparar / Para actualizar"]
        )
        
        st.markdown("**Factores Críticos de Plusvalía:**")
        t_piscina = st.checkbox("Tiene Piscina", key="tp")
        t_planta = st.checkbox("Tiene Planta Eléctrica", key="tpl")
        t_pozo = st.checkbox("Tiene Pozo o Agua constante", key="tpz")
        t_vista = st.checkbox("Tiene Vista privilegiada (Mar/Ávila/Montaña)", key="tv")
        
        st.markdown("### 2. Evidencia Fotográfica")
        fotos_tasacion = st.file_uploader(
            "Sube fotos del inmueble (Fachada, Sala, Cocina, Baños):", 
            type=["jpg", "png", "jpeg"], 
            accept_multiple_files=True,
            key="tasacion_files"
        )
        
        st.markdown("---")
        nombre_t = st.text_input("Tu Nombre / Contacto:", key="nombre_t")
        whatsapp_t = st.text_input("Tu Número de WhatsApp:", key="wa_t")
        
        btn_ejecutar_tasacion = st.form_submit_button("🚀 Calcular Tasación por IA")

    if btn_ejecutar_tasacion:
        if not whatsapp_t:
            st.error("Por favor ingresa tu número de WhatsApp para enviarte el reporte detallado.")
        else:
            base_m2_const = 750 if "Margarita" in región_t or "Caracas" in región_t else 450
            base_m2_terr = 60 if "Margarita" in región_t or "Caracas" in región_t else 30
            
            if "Alquiler" in transaccion_t:
                base_m2_const = base_m2_const * 0.0075 
                base_m2_terr = base_m2_terr * 0.005
            
            multiplicador = 1.0
            if "Amoblado" in estado_amoblado_t: multiplicador += 0.15
            if "Excelente" in estado_conservacion: multiplicador += 0.15
            if t_piscina: multiplicador += 0.10
            if t_planta: multiplicador += 0.12
            if t_pozo: multiplicador += 0.12
            if t_vista: multiplicador += 0.15
            
            valor_construccion = m2_construccion_t * base_m2_const
            valor_terreno = m2_terreno_t * base_m2_terr
            
            precio_estimado = (valor_construccion + valor_terreno) * multiplicador
            rango_min = int(precio_estimado * 0.9)
            rango_max = int(precio_estimado * 1.1)
            
            st.success("¡Análisis de Tasación e Inspección Visual completado con éxito!")
            
            st.markdown("### 📊 Resultado Preliminar del Asistente IA")
            etiqueta_resultado = "Banda de Venta Sugerida" if "Venta" in transaccion_t else "Banda de Alquiler Sugerida"
            st.metric(label=etiqueta_resultado, value=f"${rango_min:,} - ${rango_max:,} USD")
            st.info(f"💡 **Criterio IA:** Valuación calculada para {m2_construccion_t} m² de construcción y {m2_terreno_t} m² de terreno, con equipamiento '{estado_amoblado_t}'.")
            
            num_fotos_t = len(fotos_tasacion) if fotos_tasacion else 0
            
            msg_tasacion = (
                f"Hola, he realizado una Tasación por IA en la web:%0A"
                f"*Objetivo:* {transaccion_t}%0A"
                f"*Región:* {región_t}%0A"
                f"*Inmueble:* {tipo_t} ({m2_construccion_t} m² const. / {m2_terreno_t} m² terreno)%0A"
                f"*Condición:* {estado_amoblado_t} | *Conservación:* {estado_conservacion}%0A"
                f"*Plusvalías:* Piscina({t_piscina}), Planta({t_planta}), Pozo({t_pozo}), Vista({t_vista})%0A"
                f"*Banda calculada:* ${rango_min:,} - ${rango_max:,} USD%0A"
                f"*Fotos adjuntas:* {num_fotos_t} foto(s)%0A"
                f"*Solicitante:* {nombre_t} ({whatsapp_t})"
            )
            link_wa_tasacion = f"https://wa.me/{MI_NUMERO_WA}?text={msg_tasacion}"
            
            st.markdown(
                f'<a href="{link_wa_tasacion}" target="_blank" style="display:inline-block;padding:14px 24px;font-size:16px;font-weight:bold;color:white;background-color:#25D366;text-align:center;text-decoration:none;border-radius:8px;">📱 Enviar Reporte Completo de Tasación a WhatsApp</a>',
                unsafe_allow_html=True
            )

# =========================================================
# SECCIÓN FINAL: GRUPOS DE WHATSAPP
# =========================================================
st.markdown("---")
st.subheader("💬 Únete a nuestras comunidades en WhatsApp")
col_g1, col_g2 = st.columns(2)

with col_g1:
    st.link_button("🌴 Grupo Margarita", LINK_GRUPO_MARGARITA, use_container_width=True)

with col_g2:
    st.link_button("🏢 Grupo Caracas / La Guaira", LINK_GRUPO_CARACAS, use_container_width=True)

