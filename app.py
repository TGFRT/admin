import streamlit as st
import requests

# URL de la API
API_URL = "https://apisheetsdb.vercel.app/api/sheets"  # Usando tu API correcta

# Información de inicio de sesión del administrador
ADMIN_USERNAME = "administrador"
ADMIN_PASSWORD = "perupaysergiorequena"

# Función para obtener los datos de la API
def fetch_data():
    response = requests.get(f"{API_URL}?range=A1:Z100")
    return response.json().get("data", [])

# Función para actualizar el estado de un usuario
def update_user_state(dni, new_state):
    response = requests.put(API_URL, json={
        "range": "A2:Z100",  # Asegúrate de que el rango de la hoja sea correcto
        "values": [[new_state]]  # Actualiza solo el estado (en la columna correspondiente)
    })
    return response.json()

# Función de inicio de sesión
def login():
    st.sidebar.title("Iniciar sesión")
    username = st.sidebar.text_input("Usuario")
    password = st.sidebar.text_input("Contraseña", type="password")

    if st.sidebar.button("Iniciar sesión"):
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            st.session_state.logged_in = True
            st.sidebar.success("¡Inicio de sesión exitoso!")
        else:
            st.sidebar.error("Usuario o contraseña incorrectos.")

# Verificar si el usuario está autenticado
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# Si el usuario no está autenticado, mostrar el formulario de inicio de sesión
if not st.session_state.logged_in:
    login()

# Si el usuario está autenticado, mostrar el dashboard
else:
    st.title("Panel de Administración")

    # Filtro para seleccionar un usuario
    dni = st.text_input("Ingrese el DNI del usuario")

    if dni:
        # Obtener los datos del usuario
        data = fetch_data()
        user_data = [row for row in data if row[2] == dni]  # Filtra por DNI

        if user_data:
            user = user_data[0]
            st.write("Datos del Usuario:")
            st.write(f"Nombre: {user[0]}")
            st.write(f"Celular: {user[1]}")
            st.write(f"DNI: {user[2]}")
            st.write(f"Estado: {user[12]}")  # Asegúrate de que esta columna corresponda al estado
            
            # Opción para actualizar el estado
            new_state = st.selectbox("Seleccionar nuevo estado", ["Denegado", "Aprobado", "Confianza", "Pendiente", "Preaprobado", "Validación"])
            
            if st.button("Actualizar Estado"):
                result = update_user_state(dni, new_state)
                st.write("Estado actualizado:", result)
        else:
            st.write("Usuario no encontrado")
