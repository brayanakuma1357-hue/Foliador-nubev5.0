import streamlit as st
import fitz  # PyMuPDF
import io

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Foliador Pro Web", layout="centered")

# --- ESTILOS CSS ---
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
st.title("🗂️ Foliador de Expedientes PRO")
st.write("Herramienta de foliado inverso con soporte para grandes volúmenes.")

# --- BARRA LATERAL (CONFIGURACIÓN) ---
with st.sidebar:
    st.header("⚙️ Configuración")
    
    prefijo = st.text_input("Prefijo del sello", value="N°")
    
    col1, col2 = st.columns(2)
    with col1:
        inicio = st.number_input("Iniciar en:", min_value=1, value=1)
    with col2:
        # MEJORA 1: MÁS OPCIONES DE DÍGITOS
        opciones_ceros = [
            "1 dígito (1)",
            "2 dígitos (01)", 
            "3 dígitos (001)", 
            "4 dígitos (0001)", 
            "5 dígitos (00001)",
            "6 dígitos (000001)"
        ]
        ceros_texto = st.selectbox("Ceros:", opciones_ceros, index=2) # Por defecto 3 dígitos
        # Extraemos el número del texto (el primer caracter)
        cant_ceros = int(ceros_texto.split()[0])
    
    st.divider() 
    
    # MEJORA 2: TODAS LAS TIPOGRAFÍAS BASE 14
    fuente_map = {
        "Courier - Negrita (Sello)": "Courier-Bold",
        "Courier - Normal": "Courier",
        "Courier - Cursiva": "Courier-Oblique",
        "Helvetica - Negrita (Moderno)": "Helvetica-Bold",
        "Helvetica - Normal": "Helvetica",
        "Helvetica - Cursiva": "Helvetica-Oblique",
        "Times - Negrita (Formal)": "Times-Bold",
        "Times - Normal": "Times-Roman",
        "Times - Cursiva": "Times-Italic"
    }
    fuente_elegida = st.selectbox("Tipografía:", list(fuente_map.keys()))
    font_code = fuente_map[fuente_elegida]
    
    tamano = st.slider("Tamaño de letra:", 8, 48, 14)
    
    color_hex = st.color_picker("Color de tinta:", "#000000")
    
    posicion = st.selectbox("Ubicación:", 
                            ["Arriba Derecha", "Abajo Derecha", "Arriba Izquierda", "Abajo Izquierda", "Abajo Centro", "Arriba Centro"])
    
    espaciado = st.checkbox("Espaciado ancho (0 0 1)")

# --- FUNCIÓN HELPER COLOR ---
def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16)/255 for i in (0, 2, 4))

# --- ÁREA PRINCIPAL ---
uploaded_file = st.file_uploader("Sube tu archivo PDF aquí", type="pdf")

if uploaded_file is not None:
    st.success(f"Archivo cargado: {uploaded_file.name}")
    
    if st.button("🚀 FOLIAR DOCUMENTO AHORA"):
        try:
            # Leer archivo
            pdf_bytes = uploaded_file.read()
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            total_pages = len(doc)
            
            progress_bar = st.progress(0)
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
                elif posicion == "Abajo Izquierda": x, y = 30, h - my
                elif posicion == "Abajo Centro": x, y = (w/2)-30, h - my
                elif posicion == "Arriba Centro": x, y = (w/2)-30, my
                else: x, y = w - mx, my
                
                page.insert_text((x, y), texto_final, fontsize=tamano, 
                                 fontname=font_code, color=color_rgb)
                
                progress_bar.progress((i + 1) / total_pages)

            # Guardar
            output_buffer = io.BytesIO()
            doc.save(output_buffer)
            doc.close()
            output_data = output_buffer.getvalue()
            
            st.balloons()
            st.success("¡Listo! Descarga tu archivo abajo:")
            
            st.download_button(
                label="📥 Descargar PDF Foliado",
                data=output_data,
                file_name=f"FOLIADO_{uploaded_file.name}",
                mime="application/pdf"
            )
            
        except Exception as e:
            st.error(f"Ocurrió un error técnico: {e}")

else:
    st.info("👆 Esperando archivo PDF...")
