from flask import Flask, jsonify, render_template, request, redirect, url_for, flash, session
from datetime import datetime, timedelta
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
        correo TEXT,
        password_last_updated TEXT
    )
    ''')

    # Crear tabla de mensajes
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS mensajes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        asunto TEXT NOT NULL,
        mensaje TEXT NOT NULL,
        usuario_id INTEGER,
        fecha_envio TEXT NOT NULL DEFAULT (DATETIME('now')),
        fecha_entregado TEXT,
        FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
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

    # Obtener la fecha actual
    fecha_actualizacion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Insertar el usuario en la base de datos
    try:
        cursor.execute('''
            INSERT INTO usuarios (username, password, password_last_updated)
            VALUES (?, ?, ?)''', (username, hashed_password, fecha_actualizacion))
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

# Función de validación de seguridad de la contraseña para actualizacion
def es_contrasena_actualizada(fecha_actualizacion):
    if not fecha_actualizacion:
        return False, None  # Si no hay fecha registrada, se considera desactualizada

    fecha_actualizacion = datetime.strptime(fecha_actualizacion, "%Y-%m-%d %H:%M:%S")
    hoy = datetime.now()
    dias_transcurridos = (hoy - fecha_actualizacion).days

    # Considerar "actualizada" si la contraseña se cambió hace menos de 90 días
    esta_actualizada = dias_transcurridos < 90
    return esta_actualizada, dias_transcurridos

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
@app.route("/index")
def index():
    # Validar que el usuario tenga sesión iniciada
    if 'username' not in session:
        flash("Inicia sesión para continuar.", "error")
        return redirect(url_for("login"))

    # Obtener las variables 'username' y 'nivel_acceso' desde la sesión
    username = session['username']
    nivel_acceso = session.get('nivel_acceso', 1)  # Usar el nivel de acceso almacenado o por defecto 1

    return render_template("index.html", username=username, nivel_acceso=nivel_acceso)

# Ruta para la administracion de ususarios
@app.route("/gestion-usuarios")
def gestion_usuarios():
    # Verificar si el usuario está autenticado
    if 'username' not in session:
        flash("Por favor, inicia sesión primero.", "error")
        return redirect(url_for('login'))
    
    username = session['username']    
    # Verificar el nivel de acceso antes de mostrar el contenido
    nivel_acceso = session.get('nivel_acceso', 1)

    if nivel_acceso < 3:
        flash("No tienes permiso para acceder a esta página.", "error")
        return redirect(url_for('index'))
    
    # Obtener los datos de los usuarios
    conexion = sqlite3.connect('BD/usuarios.db')
    cursor = conexion.cursor()

    cursor.execute('''
        SELECT id, username, nivel_acceso, telefono, correo, password_last_updated
        FROM usuarios
        ORDER BY username ASC
    ''')
    usuarios = cursor.fetchall()

    conexion.close()

    # Calcular el estado de la contraseña
    usuarios_estado = [
        (
            id, username, nivel_acceso, telefono, correo,
            f"{'Actualizada' if actualizada else 'Desactualizada'} ({dias} días)"
            if dias is not None else "Nunca actualizada"
        )
        for id, username, nivel_acceso, telefono, correo, password_last_updated 
        in usuarios
        for actualizada, dias in [es_contrasena_actualizada(password_last_updated)]
    ]

    # Pasar los datos de la base de datos y la sesión a la plantilla
    return render_template(
        "gestion_usuarios.html",
        usuarios=usuarios_estado,
        username=username,
        nivel_acceso=nivel_acceso
    )

# -- Rutas para manejar las acciones desde la Barras de Herramientas --
# Rutas para actualizar datos de usuario
@app.route("/actualizar/datos-usuario/<int:user_id>", methods=["GET", "POST"])
def actualizar_datos_usuario(user_id):
    if 'username' not in session:
        flash("Por favor, inicia sesión primero.", "error")
        return redirect(url_for('login'))

    conexion = sqlite3.connect('BD/usuarios.db')
    cursor = conexion.cursor()

    if request.method == "POST":
        # Obtener los datos del formulario
        nuevo_nombre = request.form["username"]
        nuevo_telefono = request.form["telefono"]
        nuevo_correo = request.form["correo"]
        nueva_contrasena = request.form.get("password", "").strip()

        # Validar y procesar la nueva contraseña
        hashed_password = None
        fecha_actualizacion = None
        if nueva_contrasena:  # Si se ingresa una nueva contraseña
            if not validar_contrasena(nueva_contrasena):
                flash("La contraseña debe tener al menos 6 caracteres, una mayúscula, una minúscula y un número.", "error")
                return redirect(request.url)

            hashed_password = bcrypt.hashpw(nueva_contrasena.encode('utf-8'), bcrypt.gensalt())
            fecha_actualizacion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Actualizar los datos en la base de datos
        if hashed_password and fecha_actualizacion:
            cursor.execute('''
                UPDATE usuarios
                SET username = ?, telefono = ?, correo = ?, password = ?, password_last_updated = ?
                WHERE id = ?
            ''', (nuevo_nombre, nuevo_telefono, nuevo_correo, hashed_password, fecha_actualizacion, user_id))
        else:
            cursor.execute('''
                UPDATE usuarios
                SET username = ?, telefono = ?, correo = ?
                WHERE id = ?
            ''', (nuevo_nombre, nuevo_telefono, nuevo_correo, user_id))

        conexion.commit()
        conexion.close()

        flash("Datos del usuario actualizados correctamente.", "success")
        return redirect(url_for("gestion_usuarios"))

    # Obtener los datos actuales del usuario
    cursor.execute('SELECT username, telefono, correo FROM usuarios WHERE id = ?', (user_id,))
    usuario = cursor.fetchone()
    conexion.close()

    if not usuario:
        flash("Usuario no encontrado.", "error")
        return redirect(url_for("gestion_usuarios"))

    return render_template("editar_usuario.html", user_id=user_id, username=usuario[0], telefono=usuario[1], correo=usuario[2])

# Rutas para actualizar nivel de acceso de usuario
@app.route("/actualizar-nivel-acceso/<int:user_id>", methods=["POST"])
def actualizar_nivel_acceso(user_id):
    if 'username' not in session:
        return jsonify({"error": "No autorizado"}), 401

    data = request.get_json()
    nuevo_nivel = data.get("nivel_acceso")

    # Validar el nivel de acceso
    if nuevo_nivel not in [1, 2, 3]:
        return jsonify({"error": "Nivel de acceso inválido"}), 400

    try:
        conexion = sqlite3.connect('BD/usuarios.db')
        cursor = conexion.cursor()
        cursor.execute("UPDATE usuarios SET nivel_acceso = ? WHERE id = ?", (nuevo_nivel, user_id))
        conexion.commit()
        conexion.close()
        return jsonify({"message": "Nivel de acceso actualizado correctamente"}), 200
    except Exception as e:
        print(f"Error al actualizar el nivel de acceso: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500


# Llamar a la función para inicializar la base de datos
if __name__ == "__main__":
    inicializar_bd()  # Asegúrate de que la base de datos esté creada
    app.run(debug=True)
