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
            if not os.path.exists("client_secret.json"):
                st.error("Error: No se encontró el archivo 'client_secret.json'. Verifica que esté en el mismo directorio que el script.")
                return None

            flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", SCOPES)
            creds = flow.run_local_server(port=0)

        # Guardar credenciales para futuras sesiones
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)

    return creds

# Conectar con Google Sheets
def connect_to_gsheets():
    creds = authenticate()
    if creds is None:
        st.error("Error de autenticación. No se pudo conectar con Google Sheets.")
        return None

    try:
        client = gspread.authorize(creds)
        sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1IIgiyDPQ-hplE3vT5f0o9J75lKbV3yxg3HOPlX2EScs/edit?gid=0#gid=0").sheet1
        return sheet
    except Exception as e:
        st.error(f"Error conectando con Google Sheets: {e}")
        return None

# Interfaz en Streamlit
st.title("Vending Machine Restocking App")

user = st.text_input("Enter your name", placeholder="E.g., John Doe").strip()
machines = ["Machine A", "Machine B", "Machine C", "Machine D"]
selected_machine = st.selectbox("Choose the vending machine:", machines)

products = ["Coca-Cola", "Pepsi", "Lays", "Snickers", "Water"]
selected_products = st.multiselect("Select the products being restocked:", products)

product_quantities = {}
for product in selected_products:
    quantity = st.number_input(f"Quantity of {product}:", min_value=1, value=1)
    product_quantities[product] = quantity

identifier_options = ["Ingresado", "Inventario Inicial"]
selected_identifier = st.radio("Choose the type of entry:", identifier_options, index=0)

if st.button("Submit Data"):
    if not user:
        st.error("Please enter your name.")
    elif not selected_products:
        st.error("Please select at least one product.")
    else:
        sheet = connect_to_gsheets()
        if sheet:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            try:
                for product, qty in product_quantities.items():
                    data = [timestamp, user, selected_machine, product, qty, selected_identifier]
                    sheet.append_row(data)
                
                st.success("Data successfully recorded in Google Sheets!")
            except Exception as e:
                st.error(f"Error writing to Google Sheets: {e}")
