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
        telefono TEXT NOT NULL, 
        correo TEXT NOT NULL,
        password_last_updated TEXT
    )
    ''')

    # Crear tabla de mensajes
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS mensajes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        asunto TEXT NOT NULL,
        mensaje TEXT NOT NULL,
        usuario_id INTEGER NOT NULL,
        fecha_envio TEXT NOT NULL DEFAULT (DATETIME('now')),
        fecha_entregado TEXT,
        FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
    )
    ''')
    
    # Guardar cambios y cerrar conexión
    conexion.commit()
    conexion.close()

    print("Base de datos inicializada correctamente.")

#Registrar Usuario
def registrar_usuario(username, password, telefono, correo):
        
    #Validar datos
    if not username or not password or not telefono or not correo:
        return "El teléfono y el correo son obligatorios."
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
            INSERT INTO usuarios (username, password, telefono, correo, password_last_updated)
            VALUES (?, ?, ?, ?, ?)
        ''', (username, hashed_password, telefono, correo, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conexion.commit()
        print("Usuario registrado exitosamente: ", username)
        return None  # No hay error, todo está bien
    except sqlite3.IntegrityError:
        print("Error: El usuario ya existe:", username)
        return "El usuario ya existe."
    finally:
        conexion.close()

#Validar usuario
def validar_usuario(username, password):
    print(f"Validando usuario: {username}")  # Depuración

    conexion = sqlite3.connect('BD/usuarios.db')
    cursor = conexion.cursor()

    cursor.execute('SELECT password, nivel_acceso FROM usuarios WHERE username = ?', (username,))
    resultado = cursor.fetchone()
    conexion.close()

    print(f"Resultado de consulta SQL para {username}: {resultado}")  # Depuración

    if resultado:
        hashed_password, nivel_acceso = resultado
        print(f"Contraseña almacenada: {hashed_password}")  # Depuración

        if bcrypt.checkpw(password.encode('utf-8'), hashed_password):
            print(f"Usuario validado correctamente. Nivel de acceso: {nivel_acceso}")  # Depuración
            return nivel_acceso
        else:
            print("Contraseña incorrecta.")  # Depuración
    else:
        print("Usuario no encontrado.")  # Depuración

    return None

#Validar contraseña
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

# Función para crear mensajes
def crear_mensaje(asunto, mensaje, usuario_id=None):
    """
    Crea un mensaje en la base de datos.
    - Si `usuario_id` es None, se crea un mensaje para todos los usuarios activos.
    """
    conexion = sqlite3.connect('BD/usuarios.db')
    cursor = conexion.cursor()

    if usuario_id is None:
        # Crear mensajes individuales para cada usuario activo
        cursor.execute('SELECT id FROM usuarios')
        usuarios = cursor.fetchall()

        for user in usuarios:
            cursor.execute('''
            INSERT INTO mensajes (asunto, mensaje, usuario_id, fecha_envio)
            VALUES (?, ?, ?, DATETIME('now'))
            ''', (asunto, mensaje, user[0]))
    else:
        # Crear mensaje individual para un usuario específico
        cursor.execute('''
        INSERT INTO mensajes (asunto, mensaje, usuario_id, fecha_envio)
        VALUES (?, ?, ?, DATETIME('now'))
        ''', (asunto, mensaje, usuario_id))

    conexion.commit()
    conexion.close()
    print(f"Mensaje '{asunto}' creado correctamente.")

# Función para verificar usuarios sin datos (teléfono o correo) y notificarles
def notificar_usuarios_sin_datos():
    conexion = sqlite3.connect('BD/usuarios.db')
    cursor = conexion.cursor()

    # Consultar los usuarios que tienen teléfono o correo vacío
    cursor.execute('''
        SELECT id, username, telefono, correo FROM usuarios
        WHERE telefono IS NULL OR correo IS NULL
    ''')
    usuarios_sin_datos = cursor.fetchall()

    # Enviar un mensaje a los usuarios sin datos
    for usuario in usuarios_sin_datos:
        id_usuario, username, telefono, correo = usuario
        asunto = "Actualiza tus datos"
        mensaje = "Hola, tu información de contacto está incompleta. Por favor, actualiza tu teléfono o correo."

        # Crear un mensaje de notificación para el usuario
        crear_mensaje(asunto, mensaje, id_usuario)
        print(f"Mensaje enviado a {username} (ID: {id_usuario})")

    conexion.commit()
    conexion.close()
    print("Notificación enviada a los usuarios sin datos.")

#---FLASK---
# App Flask
app = Flask(__name__)

# Configuración de la clave secreta para usar flash
app.secret_key = 'supersecretkey'

# Ruta para la página de inicio de sesión
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        print(f"Intentando validar usuario: {username}")  # Depuración

        # Obtener el nivel de acceso y el id del usuario al validar las credenciales
        nivel_acceso = validar_usuario(username, password)
        
        if nivel_acceso is not None:
            # Obtener el ID del usuario de la base de datos
            conexion = sqlite3.connect('BD/usuarios.db')
            cursor = conexion.cursor()
            cursor.execute('SELECT id FROM usuarios WHERE username = ?', (username,))
            user_id = cursor.fetchone()[0]  # Obtener el ID del usuario
            conexion.close()

            # Almacenar el user_id y el nivel de acceso en la sesión
            session['user_id'] = user_id
            session['username'] = username
            session['nivel_acceso'] = nivel_acceso

            print(f"Inicio de sesión exitoso para {username} con nivel de acceso {nivel_acceso}")  # Depuración
            return redirect(url_for("index"))
        else:
            flash("Credenciales incorrectas, intenta nuevamente.", "error")

    return render_template("login.html")

#Cerrar Ruta Cerrar sesion
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
        telefono = request.form["telefono"]
        correo = request.form["correo"]
        
        error = registrar_usuario(username, password, telefono, correo)        
        if error:
            flash(error, 'error')  # Usamos flash para mostrar el mensaje en la página
        else:
            flash("Usuario registrado exitosamente. Por favor, inicia sesión.", 'success')
            return redirect(url_for("login"))
    
    return render_template("register.html")

# Ruta para manejar la página principal después de iniciar sesión
@app.route("/index")
def index():
    if 'username' not in session:
        flash("Inicia sesión para continuar.", "error")
        return redirect(url_for("login"))

    username = session['username']
    nivel_acceso = session.get('nivel_acceso', 1)
    user_id = session['user_id']

    # Verificar si el usuario tiene datos incompletos
    conexion = sqlite3.connect('BD/usuarios.db')
    cursor = conexion.cursor()
    cursor.execute("SELECT telefono, correo FROM usuarios WHERE id = ?", (user_id,))
    datos_usuario = cursor.fetchone()
    conexion.close()

    # Determinar si los datos están incompletos
    datos_incompletos = not datos_usuario or not all(datos_usuario)

    return render_template(
        "index.html",
        username=username,
        nivel_acceso=nivel_acceso,
        user_id=user_id,
        datos_incompletos=datos_incompletos  # Enviar este indicador a la plantilla
    )

# Ruta para la administracion de ususarios
@app.route("/gestion-usuarios")
def gestion_usuarios():
    if 'username' not in session:
        flash("Por favor, inicia sesión primero.", "error")
        return redirect(url_for('login'))
    
    username = session['username']
    nivel_acceso = session.get('nivel_acceso', 1)

    if nivel_acceso < 3:
        flash("No tienes permiso para acceder a esta página.", "error")
        return redirect(url_for('index'))

    return render_template(
        "gestion_usuarios.html",
        username=username,
        nivel_acceso=nivel_acceso
    )

#Ruta para crear un nuevo endpoint para devolver los datos en formato JSON:
@app.route("/api/usuarios", methods=["GET"])
def api_usuarios():
    if 'username' not in session:
        return jsonify({"error": "No autorizado"}), 401

    nivel_acceso = session.get("nivel_acceso", 1)
    if nivel_acceso < 3:
        return jsonify({"error": "No tienes permiso para acceder a esta página."}), 403

    conexion = sqlite3.connect("BD/usuarios.db")
    cursor = conexion.cursor()
    cursor.execute('''
        SELECT id, username, nivel_acceso, telefono, correo, password_last_updated
        FROM usuarios
        ORDER BY username ASC
    ''')
    usuarios = cursor.fetchall()
    conexion.close()

    usuarios_estado = [
        {
            "id": id,
            "username": username,
            "nivel_acceso": nivel_acceso,
            "telefono": telefono,
            "correo": correo,
            "estado_contrasena": (
                f"{'Actualizada' if actualizada else 'Desactualizada'} ({dias} días)"
                if dias is not None else "Nunca actualizada"
            )
        }
        for id, username, nivel_acceso, telefono, correo, password_last_updated 
        in usuarios
        for actualizada, dias in [es_contrasena_actualizada(password_last_updated)]
    ]

    return jsonify(usuarios_estado), 200

# -- Rutas para manejar las acciones desde la Barras de Herramientas --
# Ruta para actualizar los datos de cualquier usuario (sin importar nivel de acceso)
@app.route("/actualizar/datos-usuario/<int:user_id>", methods=["GET", "POST"])
def actualizar_datos_usuario(user_id):    

    # Validar existencia del usuario en la base de datos
    conexion = sqlite3.connect('BD/usuarios.db')
    cursor = conexion.cursor()
    cursor.execute('SELECT username, telefono, correo FROM usuarios WHERE id = ?', (user_id,))
    usuario = cursor.fetchone()
    conexion.close()

    if not usuario:
        flash("Usuario no encontrado.", "error")
        return redirect(url_for('index'))  # Redirige a la página de origen

    # Manejo de solicitud POST
    if request.method == "POST":
        nuevo_nombre = request.form["username"]
        nuevo_telefono = request.form["telefono"]
        nuevo_correo = request.form["correo"]
        nueva_contrasena = request.form.get("password", "").strip()

        # Validar y procesar la nueva contraseña
        hashed_password = None
        fecha_actualizacion = None
        if nueva_contrasena:  # Si se ingresa una nueva contraseña
            if not validar_contrasena(nueva_contrasena):
                flash("La contraseña debe cumplir los requisitos mínimos.", "error")
                return redirect(request.url)

            hashed_password = bcrypt.hashpw(nueva_contrasena.encode('utf-8'), bcrypt.gensalt())
            fecha_actualizacion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Actualizar los datos en la base de datos
        conexion = sqlite3.connect('BD/usuarios.db')
        cursor = conexion.cursor()
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
        return redirect(url_for('index'))  # Redirige a la página de origen después de guardar

    # Manejo de solicitud GET: Renderizar el formulario con los datos actuales
    return render_template(
        "editar_usuario.html",
        user_id=user_id,
        username=usuario[0],
        telefono=usuario[1],
        correo=usuario[2]
    )

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

# Rutas para mensajes leidos por usuario
# Ruta para obtener mensajes
@app.route("/mensajes/<int:usuario_id>")
def obtener_mensajes(usuario_id):
    try:
        conexion = sqlite3.connect('BD/usuarios.db')
        cursor = conexion.cursor()

        # Obtener mensajes no entregados para este usuario
        cursor.execute('''
        SELECT id, asunto, mensaje, fecha_envio
        FROM mensajes
        WHERE usuario_id = ? AND fecha_entregado IS NULL
        ''', (usuario_id,))
        mensajes = cursor.fetchall()

        print("Mensajes obtenidos:", mensajes)  # Depuración

        # Registrar fecha de entrega
        fecha_entregado = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if mensajes:
            cursor.executemany(
                'UPDATE mensajes SET fecha_entregado = ? WHERE id = ?',
                [(fecha_entregado, mensaje[0]) for mensaje in mensajes]
            )

        conexion.commit()
        conexion.close()

        # Devolver los mensajes en formato JSON
        return jsonify([
            {"id": mensaje[0], "asunto": mensaje[1], "mensaje": mensaje[2], "fecha_envio": mensaje[3]}
            for mensaje in mensajes
        ])
    except Exception as e:
        print("Error al obtener mensajes:", e)
        return jsonify({"error": "Error interno del servidor"}), 500

# Rutas para envios de mensajes
@app.route("/enviar-mensaje/<string:tipo>", methods=["GET", "POST"])
@app.route("/enviar-mensaje/<string:tipo>/<int:usuario_id>", methods=["GET", "POST"])
def enviar_mensaje(tipo, usuario_id=None):
    """
    Renderiza el formulario para enviar un mensaje.
    - tipo: "individual" o "difusion".
    - usuario_id: Solo aplica para mensajes individuales.
    """
    if 'username' not in session:
        flash("Inicia sesión para continuar.", "error")
        return redirect(url_for("login"))

    if request.method == "POST":
        asunto = request.form["asunto"]
        mensaje = request.form["mensaje"]

        if tipo == "individual" and usuario_id:
            # Crear un mensaje individual
            crear_mensaje(asunto, mensaje, usuario_id)
        elif tipo == "difusion":
            # Crear mensajes para todos los usuarios
            crear_mensaje(asunto, mensaje)
        else:
            flash("Error: Tipo de mensaje inválido.", "error")
            return redirect(request.url)

        flash("Mensaje enviado correctamente.", "success")
        return redirect(url_for("gestion_usuarios"))

    # Preparar datos para el formulario
    destinatario = None
    if tipo == "individual" and usuario_id:
        conexion = sqlite3.connect('BD/usuarios.db')
        cursor = conexion.cursor()
        cursor.execute("SELECT username FROM usuarios WHERE id = ?", (usuario_id,))
        usuario = cursor.fetchone()
        conexion.close()

        if usuario:
            destinatario = usuario[0]
        else:
            flash("Usuario no encontrado.", "error")
            return redirect(url_for("gestion_usuarios"))

    return render_template(
        "enviar_mensaje.html",
        tipo=tipo,
        destinatario=destinatario
    )

# Rutas para notificar usuarios
@app.route("/notificar-usuarios-sin-datos", methods=["POST"])
def notificar_usuarios_sin_datos():
    try:
        # Conectar a la base de datos
        conexion = sqlite3.connect('BD/usuarios.db')
        cursor = conexion.cursor()

        # Buscar usuarios con datos faltantes
        cursor.execute('''
            SELECT id, username 
            FROM usuarios 
            WHERE telefono IS NULL OR telefono = '' OR correo IS NULL OR correo = ''
        ''')
        usuarios_faltantes = cursor.fetchall()

        # Crear un mensaje si no hay faltantes
        if not usuarios_faltantes:
            return jsonify({"message": "No hay usuarios con datos faltantes."}), 200

        # Crear un mensaje para cada usuario con datos faltantes
        for usuario_id, username in usuarios_faltantes:
            crear_mensaje(
                asunto="Actualización de Datos Requerida",
                mensaje=f"Hola {username}, por favor actualiza tu información de contacto.",
                usuario_id=usuario_id
            )

        conexion.close()

        # Retornar éxito
        return jsonify({"message": "Notificaciones enviadas correctamente", "usuarios_notificados": len(usuarios_faltantes)}), 200

    except Exception as e:
        print("Error al notificar usuarios sin datos:", e)
        return jsonify({"error": "Error interno del servidor"}), 500

# Llamar a la función para inicializar la base de datos
if __name__ == "__main__":
    inicializar_bd()  # Asegúrate de que la base de datos esté creada
    app.run(debug=True)
