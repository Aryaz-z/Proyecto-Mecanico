import sqlite3
import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime
import os



# Base de datos
os.makedirs("database", exist_ok=True)
conexion = sqlite3.connect("database/taller.db")
cursor = conexion.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS facturas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente TEXT,
    patente TEXT,
    total REAL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS detalle_factura (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    factura_id INTEGER,
    servicio TEXT,
    precio REAL,
    FOREIGN KEY (factura_id) REFERENCES facturas(id)
)
""")

conexion.commit()

def generar_pdf(cliente, patente, servicios, total, factura_id):

    pdf = FPDF()

    pdf.add_page()

    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "FACTURA TALLER MECANICO", ln=True)

    pdf.ln(5)

    pdf.set_font("Arial", size=12)

    fecha = datetime.now().strftime("%d/%m/%Y")

    pdf.cell(0, 10, f"Factura N° {factura_id}", ln=True)
    pdf.cell(0, 10, f"Fecha: {fecha}", ln=True)
    pdf.cell(0, 10, f"Cliente: {cliente}", ln=True)
    pdf.cell(0, 10, f"Patente: {patente}", ln=True)

    pdf.ln(5)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(10)

    pdf.ln(3)

    pdf.cell(0, 10, "Servicios:", ln=True)



    for item in servicios:

        pdf.cell(
            0,
            10,
            f"{item['servicio']} - ${item['precio']:,.0f}",
            ln=True
        )

    pdf.ln(5)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(10)


    pdf.cell(
        0,
        10,
        f"TOTAL: ${total:,.0f}",
        ln=True
    )

    nombre_archivo = f"facturas/Factura_{factura_id}.pdf"

    pdf.output(nombre_archivo)

    return nombre_archivo

# Interfaz
st.title("🚗 Taller Mecánico")

if "cliente" not in st.session_state:
    st.session_state.cliente = ""

if "patente" not in st.session_state:
    st.session_state.patente = ""

if "servicio" not in st.session_state:
    st.session_state.servicio = ""

if "precio" not in st.session_state:
    st.session_state.precio = 0

cliente = st.text_input(
    "Nombre del cliente",
    key="cliente"
)

patente = st.text_input(
    "Patente",
    key="patente"
)

servicio = st.text_input(
    "Servicio realizado",
    key="servicio"
)

precio = st.number_input(
    "Precio",
    min_value=0,
    key="precio"
)

if "servicios" not in st.session_state:
    st.session_state.servicios = []

if st.button("Agregar servicio"):
    if servicio:
        st.session_state.servicios.append({
            "servicio": servicio,
            "precio": precio
        })

st.divider()

st.subheader("Detalle")

total = 0

for item in st.session_state.servicios:
    st.write(
        f"🔧 {item['servicio']} - ${item['precio']:,}"
    )
    total += item["precio"]

st.success(f"TOTAL: ${total:,}")

# Guardar factura
if st.button("Guardar Factura"):

    # Guardar factura
    cursor.execute("""
    INSERT INTO facturas (
        cliente,
        patente,
        total
    )
    VALUES (?, ?, ?)
    """, (
        cliente,
        patente,
        total
    ))

    # Obtener ID de la factura recién creada
    factura_id = cursor.lastrowid

    # Guardar cada servicio
    for item in st.session_state.servicios:

        cursor.execute("""
        INSERT INTO detalle_factura (
            factura_id,
            servicio,
            precio
        )
        VALUES (?, ?, ?)
        """, (
            factura_id,
            item["servicio"],
            item["precio"]
        ))


    
    conexion.commit()

    # GENERAR PDF
    archivo_pdf = generar_pdf(
        cliente,
        patente,
        st.session_state.servicios,
        total,
        factura_id
    )

    st.session_state.servicios = []

    #st.session_state.cliente = ""
    #st.session_state.patente = ""
    #st.session_state.servicio = ""
    #st.session_state.precio = 0

    st.success("✅ Factura y servicios guardados correctamente")

    st.info(f"PDF generado: {archivo_pdf}")

    st.rerun()



st.divider()

st.subheader("📋 Últimas facturas")

cursor.execute("""
SELECT id, cliente, patente, total
FROM facturas
ORDER BY id DESC
LIMIT 10
""")

facturas = cursor.fetchall()

df = pd.DataFrame(
    facturas,
    columns=[
        "ID",
        "Cliente",
        "Patente",
        "Total"
    ]
)

st.dataframe(
    df,
    use_container_width=True
)