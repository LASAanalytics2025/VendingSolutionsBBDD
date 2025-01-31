import streamlit as st
import gspread
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
import pickle
import pandas as pd
from datetime import datetime

# Configuración de los alcances de acceso
SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

# Autenticación con OAuth 2.0
def authenticate():
    creds = None
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)

    # Si no hay credenciales válidas, iniciar sesión
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", SCOPES)
            creds = flow.run_local_server(port=0)

        # Guardar credenciales para futuras sesiones
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)

    return creds

# Conectar con Google Sheets
def connect_to_gsheets():
    creds = authenticate()
    client = gspread.authorize(creds)
    sheet = client.open_by_url("TU_GOOGLE_SHEET_URL_AQUÍ").sheet1
    return sheet

# Interfaz en Streamlit
st.title("Vending Machine Restocking Appp")

user = st.text_input("Enter your name", placeholder="E.g., John Doe")
machines = ["Machine A", "Machine B", "Machine C", "Machine D"]
selected_machine = st.selectbox("Choose the vending machine:", machines)

products = ["Coca-Cola", "Pepsi", "Lays", "Snickers", "Water"]
selected_products = st.multiselect("Select the products being restocked:", products)

product_quantities = {product: st.number_input(f"Quantity of {product}:", min_value=1, value=1) for product in selected_products}

identifier_options = ["Ingresado", "Inventario Inicial"]
selected_identifier = st.radio("Choose the type of entry:", identifier_options, index=0)

if st.button("Submit Data"):
    if user and selected_machine and selected_products:
        sheet = connect_to_gsheets()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        for product, qty in product_quantities.items():
            data = [timestamp, user, selected_machine, product, qty, selected_identifier]
            sheet.append_row(data)

        st.success("Data successfully recorded in Google Sheets!")

    else:
        st.error("Please fill out all fields before submitting.")
