import streamlit as st
import bcrypt

# Contraseña encriptada (esto es solo un ejemplo; en un entorno real deberías almacenarla de manera más segura)
hashed_password = bcrypt.hashpw("perupaysergiorequena".encode('utf-8'), bcrypt.gensalt())

# Función para verificar las credenciales
def check_credentials(username, password):
    # Solo se permite el acceso si el usuario es 'administrador' y la contraseña coincide con el hash
    if username == "administrador" and bcrypt.checkpw(password.encode('utf-8'), hashed_password):
        return True
    return False

# Interfaz de inicio de sesión
def login():
    st.title("Panel de Administración")
    
    # Campos de entrada
    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")
    
    if st.button("Iniciar sesión"):
        if check_credentials(username, password):
            st.success("¡Has iniciado sesión correctamente!")
            return True
        else:
            st.error("Usuario o contraseña incorrectos. Intenta nuevamente.")
            return False
    return False

# Función para el panel de administración
def admin_dashboard():
    st.title("Bienvenido al Panel de Administración")
    st.write("Aquí puedes gestionar los datos, usuarios y otras configuraciones.")
    # Agrega más funcionalidades aquí, como gráficos, tablas o formularios.

# Lógica principal
def main():
    if login():
        admin_dashboard()

if __name__ == "__main__":
    main()
