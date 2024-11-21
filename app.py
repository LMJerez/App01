from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import bcrypt
import re

def inicializar_bd():
    # Crear conexión a la base de datos
    conexion = sqlite3.connect('BD/usuarios.db')
    cursor = conexion.cursor()

    # Crear tabla de usuarios si no existe
    cursor.execute(''' 
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        nivel_acceso INTEGER DEFAULT 1,
        telefono TEXT,
        correo TEXT
    )
    ''')

    # Guardar cambios y cerrar conexión
    conexion.commit()
    conexion.close()
    print("Base de datos inicializada correctamente.")

def registrar_usuario(username, password):
    # Validar la contraseña
    if not validar_contrasena(password):
        return "La contraseña debe tener al menos 6 caracteres, una mayúscula, una minúscula y un número."

    # Conexión a la base de datos
    conexion = sqlite3.connect('BD/usuarios.db')
    cursor = conexion.cursor()

    # Hashear la contraseña
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    # Insertar el usuario en la base de datos
    try:
        cursor.execute('INSERT INTO usuarios (username, password) VALUES (?, ?)', (username, hashed_password))
        conexion.commit()
        print("Usuario registrado exitosamente.")
        return None  # No hay error, todo está bien
    except sqlite3.IntegrityError:
        print("Error: El usuario ya existe.")
        return "El usuario ya existe."
    finally:
        conexion.close()

def validar_usuario(username, password):
    # Conexión a la base de datos
    conexion = sqlite3.connect('BD/usuarios.db')
    cursor = conexion.cursor()

    # Buscar la contraseña y el nivel de acceso del usuario
    cursor.execute('SELECT password, nivel_acceso FROM usuarios WHERE username = ?', (username,))
    resultado = cursor.fetchone()
    conexion.close()

    # Validar las credenciales
    if resultado:
        hashed_password, nivel_acceso = resultado        
        # Validar contraseña encriptada
        if bcrypt.checkpw(password.encode('utf-8'), hashed_password):
            return nivel_acceso  # Devuelve el nivel de acceso si es válido
    return None  # Retorna None si no son válidas las credenciales

# Función de validación de la contraseña
def validar_contrasena(password):
    # Expresión regular para validar la contraseña
    patron = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[A-Za-z\d]{6,}$'
    if re.match(patron, password):
        return True
    return False

app = Flask(__name__)

# Configuración de la clave secreta para usar flash
app.secret_key = 'supersecretkey'

# Ruta para la página de inicio de sesión
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        nivel_acceso = validar_usuario(username, password)
        if nivel_acceso is not None:
            # Guardar usuario en la sesión
            session['username'] = username
            session['nivel_acceso'] = nivel_acceso
            return redirect(url_for("index", username=username, nivel_acceso=nivel_acceso))
        else:
            flash("Credenciales incorrectas, intenta nuevamente.", "error")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop('username', None)
    session.pop('nivel_acceso', None)
    flash("Has cerrado sesión.", "success")
    return redirect(url_for("login"))

# Ruta para el registro de usuarios
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        error = registrar_usuario(username, password)
        
        if error:
            flash(error, 'error')  # Usamos flash para mostrar el mensaje en la página
        else:
            flash("Usuario registrado exitosamente.", 'success')
            return redirect(url_for("login"))
    
    return render_template("register.html")

# Ruta para manejar la página principal después de iniciar sesión
@app.route("/index/<username>/<int:nivel_acceso>")
def index(username, nivel_acceso):
    # Validar que el usuario tenga sesión iniciada
    if 'username' not in session or session['username'] != username:
        flash("Inicia sesión para continuar.", "error")
        return redirect(url_for("login"))
    return render_template("index.html", username=username, nivel_acceso=nivel_acceso)

# Ruta para la administracion de ususarios
@app.route("/gestion-usuarios")
def gestion_usuarios():
    # Verificar si el usuario está autenticado
    if 'username' not in session:
        flash("Por favor, inicia sesión primero.", "error")
        return redirect(url_for('login'))
    
    # Obtener los datos de los usuarios
    conexion = sqlite3.connect('BD/usuarios.db')
    cursor = conexion.cursor()

    cursor.execute('SELECT id, username, password, nivel_acceso, telefono, correo FROM usuarios ORDER BY username ASC')
    usuarios = cursor.fetchall()

    conexion.close()

    # Pasar los datos de la base de datos y la sesión a la plantilla
    return render_template("gestion_usuarios.html", usuarios=usuarios, username=session['username'], nivel_acceso=session['nivel_acceso'])

# Llamar a la función para inicializar la base de datos
if __name__ == "__main__":
    inicializar_bd()  # Asegúrate de que la base de datos esté creada
    app.run(debug=True)
