import streamlit as st
import fitz  # PyMuPDF
import io

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Foliador Pro Web", layout="centered")

# --- ESTILOS CSS PARA QUE SE VEA BIEN EN MÓVIL ---
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        background-color: #FF4B4B;
        color: white;
        height: 3em;
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# --- TÍTULO ---
st.title("📱 Foliador de Expedientes")
st.write("Sube tu PDF, configúralo y descárgalo foliado.")

# --- BARRA LATERAL (CONFIGURACIÓN) ---
with st.sidebar:
    st.header("⚙️ Configuración")
    
    prefijo = st.text_input("Prefijo", value="N°")
    inicio = st.number_input("Iniciar conteo en:", min_value=1, value=1)
    
    # Selector de ceros
    ceros_opcion = st.selectbox("Ceros a la izquierda:", 
                                ["2 dígitos (01)", "3 dígitos (001)", "4 dígitos (0001)"])
    cant_ceros = int(ceros_opcion.split()[0])
    
    st.divider() # Línea separadora
    
    # Fuente
    fuente_map = {
        "Sello (Courier)": "Courier-Bold",
        "Moderno (Helvetica)": "Helvetica-Bold",
        "Formal (Times)": "Times-Bold"
    }
    fuente_elegida = st.selectbox("Tipografía:", list(fuente_map.keys()))
    font_code = fuente_map[fuente_elegida]
    
    tamano = st.slider("Tamaño de letra:", 8, 36, 14)
    
    # Color (Streamlit devuelve Hex, PyMuPDF quiere RGB 0-1)
    color_hex = st.color_picker("Color de tinta:", "#000000")
    
    # Posición
    posicion = st.selectbox("Ubicación:", 
                            ["Arriba Derecha", "Abajo Derecha", "Arriba Izquierda", "Abajo Centro"])
    
    espaciado = st.checkbox("Espaciado ancho (0 0 1)")

# --- FUNCIÓN HELPER PARA COLOR ---
def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16)/255 for i in (0, 2, 4))

# --- ÁREA PRINCIPAL ---
uploaded_file = st.file_uploader("Sube tu archivo PDF aquí", type="pdf")

if uploaded_file is not None:
    st.success("Archivo cargado con éxito.")
    
    # Botón grande de acción
    if st.button("🚀 FOLIAR DOCUMENTO AHORA"):
        try:
            # 1. Leer archivo en memoria (sin guardar en disco)
            pdf_bytes = uploaded_file.read()
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            total_pages = len(doc)
            
            # Barra de progreso visual
            progress_bar = st.progress(0)
            
            # 2. Procesar
            color_rgb = hex_to_rgb(color_hex)
            
            for i, page in enumerate(doc):
                # Lógica inversa
                numero_calculado = (inicio + total_pages - 1) - i
                
                num_str = f"{numero_calculado:0{cant_ceros}d}"
                if espaciado: num_str = " ".join(num_str)
                texto_final = f"{prefijo} {num_str}"
                
                # Posición
                w = page.rect.width
                h = page.rect.height
                mx, my = 70, 40
                
                if posicion == "Arriba Derecha": x, y = w - mx, my
                elif posicion == "Abajo Derecha": x, y = w - mx, h - my
                elif posicion == "Arriba Izquierda": x, y = 30, my
                elif posicion == "Abajo Centro": x, y = (w/2)-30, h - my
                else: x, y = w - mx, my
                
                page.insert_text((x, y), texto_final, fontsize=tamano, 
                                 fontname=font_code, color=color_rgb)
                
                # Actualizar barra
                progress_bar.progress((i + 1) / total_pages)

            # 3. Guardar en memoria para descarga
            output_buffer = io.BytesIO()
            doc.save(output_buffer)
            doc.close()
            output_data = output_buffer.getvalue()
            
            st.balloons() # Efecto de celebración 🎉
            st.success("¡Listo! Descarga tu archivo abajo:")
            
            # Botón de Descarga
            st.download_button(
                label="📥 Descargar PDF Foliado",
                data=output_data,
                file_name=f"FOLIADO_{uploaded_file.name}",
                mime="application/pdf"
            )
            
        except Exception as e:
            st.error(f"Ocurrió un error: {e}")

else:
    st.info("👆 Sube un PDF para comenzar. Puedes usar el menú lateral para configurar el sello.")