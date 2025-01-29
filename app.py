import streamlit as st
import bcrypt
import requests
import pandas as pd

# Configurar contraseña encriptada
hashed_password = bcrypt.hashpw("perupaysergiorequena".encode('utf-8'), bcrypt.gensalt())

# Función para verificar credenciales
def check_credentials(username, password):
    return username == "administrador" and bcrypt.checkpw(password.encode('utf-8'), hashed_password)

# Función para obtener datos de la API
def fetch_data():
    url = "https://apisheetsdb.vercel.app/api/sheets?range=A1:Z100"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()["data"]
            headers = data[0]  # La primera fila es el encabezado
            records = data[1:]  # Datos sin encabezados

            # Asegurar que cada fila tenga el mismo número de columnas
            fixed_data = [row + [None] * (len(headers) - len(row)) for row in records]

            # Convertir a DataFrame
            df = pd.DataFrame(fixed_data, columns=headers)

            return df
        else:
            st.error(f"Error al obtener datos: {response.status_code}")
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Error en la solicitud: {e}")
        return pd.DataFrame()

# Función para actualizar el estado en Google Sheets (usando el formato adecuado)
def update_user_state(dni, new_state):
    url = "https://apisheetsdb.vercel.app/api/sheets"  # URL correcta de la API
    
    # Obtener los datos de la API
    data = fetch_data()
    if not data.empty:
        user_row = data[data['dni'] == str(dni)]
        if user_row.empty:
            st.error("No se encontró el usuario con ese DNI.")
            return
        
        # Obtener el índice de la fila a actualizar
        row_index = user_row.index[0] + 2  # Las filas en Google Sheets empiezan desde 1, pero la API usa un índice base 1
        
        # Crear el cuerpo de la solicitud con los nuevos datos
        updated_data = {
            "action": "update",
            "sheetId": "1GNHtJRX8LpvxYLjpYK780y6DwKmPcahbbmfJJUgX_MI",  # Reemplaza con tu ID de hoja
            "range": f"A{row_index}:Z{row_index}",
            "values": [user_row.iloc[0].tolist()]
        }
        
        # Actualizar el estado en la columna correspondiente
        updated_data["values"][0][data.columns.get_loc("estado")] = new_state
        
        # Enviar la solicitud POST para actualizar la fila
        try:
            response = requests.post(url, json=updated_data)
            response.raise_for_status()  # Esto lanzará una excepción si el código de estado es 4xx o 5xx
            st.success(f"✅ Estado actualizado correctamente a **{new_state}** para {dni}")
        except requests.exceptions.RequestException as e:
            # Mostrar detalles completos del error
            st.error(f"❌ Error al actualizar el estado: {e}")
            st.write("Detalles de la respuesta de la API:")
            st.write(response.text)  # Imprime la respuesta completa de la API

# Mostrar detalles del usuario con opción para editar estado
def show_user_details(user):
    with st.expander(f"📌 {user['nombreCompleto']} - {user['dni']}"):
        st.write(f"📞 **Teléfono:** {user['numeroCelular']}")
        st.write(f"🗓️ **Fecha de Nacimiento:** {user['fechaNacimiento']}")
        st.write(f"💼 **Tipo de Empleo:** {user['tipoEmpleo']}")
        st.write(f"🏢 **RUC de la Empresa:** {user['rucEmpresa']}")
        st.write(f"💳 **En Planilla:** {user['enPlanilla']}")
        st.write(f"📋 **En Infocorp:** {user['enInfocorp']}")
        st.write(f"💰 **Monto del Préstamo:** {user['montoPrestamo']}")
        st.write(f"💸 **Monto de la Cuota:** {user['montoCuota']}")
        st.write(f"⏳ **Frecuencia de Pago:** {user['frecuenciaPago']}")
        st.write(f"🗓️ **Plazo del Préstamo:** {user['plazoPrestamo']}")
        st.write(f"📜 **Estado Actual:** {user['estado']}")
        st.write(f"📝 **Razón de Rechazo:** {user['razonRechazo']}")
        st.write(f"🔒 **Contraseña:** {user['contrasena']}")
        st.write(f"✔️ **Créditos Pagados:** {user['creditos pagados']}")
        st.write(f"📑 **Datos Adicionales:** {user['datos']}")

        # Asignar un key único usando el DNI
        new_state = st.selectbox(
            "Cambiar Estado",
            ["Denegado", "Aprobado", "Confianza", "Pendiente", "Preaprobado", "Validación"],
            index=["Denegado", "Aprobado", "Confianza", "Pendiente", "Preaprobado", "Validación"].index(user["estado"]) if user["estado"] in ["Denegado", "Aprobado", "Confianza", "Pendiente", "Preaprobado", "Validación"] else 0,
            key=f"estado_{user['dni']}"  # Usar el DNI del usuario como clave única
        )

        if st.button(f"Actualizar Estado de {user['nombreCompleto']}"):
            update_user_state(user["dni"], new_state)

# Dashboard de administración con filtros
def admin_dashboard():
    st.title("📊 Panel de Administración")

    data = fetch_data()

    if not data.empty:
        st.subheader("🔍 Filtros de búsqueda")
        col1, col2, col3 = st.columns(3)

        dni_filter = col1.text_input("Buscar por DNI")
        name_filter = col2.text_input("Buscar por Nombre")
        state_filter = col3.selectbox("Filtrar por Estado", ["Todos", "Denegado", "Aprobado", "Confianza", "Pendiente", "Preaprobado", "Validación"])

        # Aplicar filtros
        filtered_data = data
        if dni_filter:
            filtered_data = filtered_data[filtered_data["dni"].astype(str).str.contains(dni_filter, case=False, na=False)]
        if name_filter:
            filtered_data = filtered_data[filtered_data["nombreCompleto"].str.contains(name_filter, case=False, na=False)]
        if state_filter != "Todos":
            filtered_data = filtered_data[filtered_data["estado"] == state_filter]

        # Mostrar resultados filtrados
        st.subheader(f"Resultados ({len(filtered_data)})")
        for _, user in filtered_data.iterrows():
            show_user_details(user)
    else:
        st.warning("No se encontraron datos.")

# Sidebar para el inicio de sesión
def login_sidebar():
    st.sidebar.title("Iniciar sesión")
    username = st.sidebar.text_input("Usuario")
    password = st.sidebar.text_input("Contraseña", type="password")

    if st.sidebar.button("Ingresar"):
        if check_credentials(username, password):
            st.session_state.authenticated = True
            st.sidebar.success("Inicio de sesión exitoso")
        else:
            st.sidebar.error("Usuario o contraseña incorrectos")

# Lógica principal
def main():
    st.set_page_config(page_title="Admin Dashboard", layout="wide")

    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    login_sidebar()

    if st.session_state.authenticated:
        admin_dashboard()
    else:
        st.warning("Por favor, inicia sesión en la barra lateral.")

if __name__ == "__main__":
    main()

