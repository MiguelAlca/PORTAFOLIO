from flask import Flask, render_template, request, redirect, url_for, flash, session 
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
from functools import wraps
import mysql.connector  # Asegúrate de tenerlo instalado

# Configuración inicial
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "super_secret_key")  # Usa una clave secreta para sesiones
app.secret_key = 'MIGUEL'

# Rutas para la base de datos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "usuarios.db")

# Configuración para subida de archivos
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # Máximo 2 MB

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Extensiones permitidas
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Inicialización de la base de datos
def init_sqlite_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS contacto 
                 (id INTEGER PRIMARY KEY, name TEXT, email TEXT, message TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS camiones 
                 (id INTEGER PRIMARY KEY, modelo TEXT, anio INTEGER, descripcion TEXT, imagen TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS personal 
                 (id INTEGER PRIMARY KEY, nombre TEXT, email TEXT, telefono TEXT, imagen TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS usuarios
                 (id INTEGER PRIMARY KEY, username TEXT, password TEXT, rol TEXT)''')
    conn.commit()
    conn.close()

init_sqlite_db()

@app.route('/test-db')
def test_db_query():
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='4LC4NT4R4',
            database='mi_basededatos'
        )
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        if result:
            return "Conexión y consulta exitosa a la base de datos."
        conn.close()
    except mysql.connector.Error as err:
        return f"Error de conexión: {err}"

@app.route('/ver_usuarios')
def ver_usuarios():
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='4LC4NT4R4',
            database='mi_basededatos'
        )
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, username, rol FROM usuarios")
        usuarios = cursor.fetchall()
        conn.close()
        return render_template('ver_usuarios.html', usuarios=usuarios)
    except mysql.connector.Error as err:
        return f"Error de conexión: {err}"

def get_db_connection_sqlite():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def requiere_rol(rol):
    def decorador(func):
        @wraps(func)
        def verificacion(*args, **kwargs):
            if session.get('rol') != rol:
                flash("Acceso denegado: No tienes los permisos necesarios", "danger")
                return redirect(url_for('home'))
            return func(*args, **kwargs)
        return verificacion
    return decorador

# Usuario y contraseña predefinidos para el administrador
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD_HASH = generate_password_hash("admin123")  # Contraseña encriptada

# Función de verificación de la contraseña del administrador
def check_admin(username, password):
    return username == ADMIN_USERNAME and check_password_hash(ADMIN_PASSWORD_HASH, password)

@app.route('/')
def home():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('home.html')

@app.route('/login/', methods=['GET', 'POST'])
def login():
    # Verificar si ya hay una sesión activa
    if 'username' in session:
        flash("Ya estás logueado", "info")
        return redirect(url_for('home'))  # Redirige al home si ya está logueado
    
    if request.method == 'POST':
        # Obtener los datos del formulario
        username = request.form['username']
        password = request.form['password']
        
        # Verificar si el usuario es el administrador (usuario predeterminado)
        if username == "admin" and password == "admin123":
            session['username'] = username
            session['rol'] = 'admin'  # Rol de administrador
            flash("Inicio de sesión exitoso como administrador", "success")
            return redirect(url_for('home'))
        
        # Verificar si el usuario existe en la base de datos
        conn = get_db_connection_sqlite()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            # Si el usuario existe y la contraseña es correcta
            session['username'] = user['username']
            session['rol'] = user['rol']  # Guardar el rol del usuario
            flash("Inicio de sesión exitoso", "success")
            return redirect(url_for('home'))
        else:
            # Si el usuario o la contraseña son incorrectos
            flash("Usuario o contraseña incorrectos", "danger")
            return redirect(url_for('login'))  # Volver al login

    return render_template('login.html')


@app.route('/register/', methods=['GET', 'POST'])
def register():
    if 'username' in session:
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        rol = request.form['rol']  # El rol se puede asignar manualmente (por ejemplo, 'user' o 'admin')
        
        if not username or not password:
            flash("Todos los campos son obligatorios", "danger")
            return redirect(url_for('register'))
        
        conn = get_db_connection_sqlite()
        c = conn.cursor()
        c.execute("SELECT * FROM usuarios WHERE username = ?", (username,))
        user = c.fetchone()
        
        if user:
            flash("El nombre de usuario ya existe", "danger")
            return redirect(url_for('register'))
        
        hashed_password = generate_password_hash(password)
        c.execute("INSERT INTO usuarios (username, password, rol) VALUES (?, ?, ?)", (username, hashed_password, rol))
        conn.commit()
        conn.close()
        
        flash("Cuenta creada con éxito. Ahora puedes iniciar sesión.", "success")
        return redirect(url_for('login'))
    
    return render_template('register.html')


@app.route('/servicios')
def servicios():
    return render_template('servicios.html')
# Revisión de la tabla 'usuarios' en SQLite
def init_sqlite_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            rol TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/logout/')
def logout():
    # Limpiar la sesión
    session.clear()
    flash("Sesión cerrada correctamente", "success")
    return redirect(url_for('login'))  # Redirige al login después de cerrar sesión


@app.route('/camiones/', methods=['GET', 'POST'])
@requiere_rol('admin')
def camiones():
    conn = get_db_connection_sqlite()
    c = conn.cursor()
    if request.method == 'POST':
        modelo = request.form['modelo']
        anio = request.form['anio']
        descripcion = request.form['descripcion']
        imagen = request.files['imagen']
        if not modelo or not anio or not descripcion:
            flash("Todos los campos son obligatorios", "danger")
            return redirect(url_for('camiones'))
        if imagen and allowed_file(imagen.filename):
            imagen_filename = secure_filename(imagen.filename)
            imagen_path = os.path.join(app.config['UPLOAD_FOLDER'], imagen_filename)
            imagen.save(imagen_path)
            c.execute("INSERT INTO camiones (modelo, anio, descripcion, imagen) VALUES (?, ?, ?, ?)",
                      (modelo, anio, descripcion, imagen_filename))
            conn.commit()
            flash("Ficha técnica añadida correctamente", "success")
        else:
            flash("Tipo de archivo no permitido o error al cargar la imagen", "danger")
            return redirect(url_for('camiones'))
    c.execute("SELECT * FROM camiones")
    camiones = c.fetchall()
    conn.close()
    return render_template('camiones.html', camiones=camiones)

@app.route('/eliminar_camion/<int:camion_id>', methods=['POST'])
@requiere_rol('admin')
def eliminar_camion(camion_id):
    conn = get_db_connection_sqlite()
    c = conn.cursor()
    c.execute("SELECT imagen FROM camiones WHERE id = ?", (camion_id,))
    imagen_filename = c.fetchone()[0]
    if imagen_filename:
        imagen_path = os.path.join(app.config['UPLOAD_FOLDER'], imagen_filename)
        if os.path.exists(imagen_path):
            os.remove(imagen_path)
    c.execute("DELETE FROM camiones WHERE id = ?", (camion_id,))
    conn.commit()
    conn.close()
    flash("Ficha técnica eliminada correctamente", "success")
    return redirect(url_for('camiones'))

@app.route('/contacto/', methods=['GET', 'POST'])
def contacto():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']
        if not name or not email or not message:
            flash("Todos los campos son obligatorios", "danger")
            return redirect(url_for('contacto'))
        conn = get_db_connection_sqlite()
        c = conn.cursor()
        c.execute("INSERT INTO contacto (name, email, message) VALUES (?, ?, ?)", (name, email, message))
        conn.commit()
        conn.close()
        flash('Tu mensaje ha sido enviado con éxito', "success")
        return redirect(url_for('contacto'))
    return render_template('contacto.html')

@app.route('/ruta/')
def ruta():
    return render_template('ruta.html')

@app.route('/ver_datos/')
@requiere_rol('admin')
def ver_datos():
    conn = get_db_connection_sqlite()
    c = conn.cursor()
    c.execute("SELECT * FROM contacto")
    contactos = c.fetchall()
    conn.close()
    return render_template('ver_datos.html', contactos=contactos)

@app.route('/personal/', methods=['GET', 'POST'])
@requiere_rol('admin')
def personal():
    conn = get_db_connection_sqlite()
    c = conn.cursor()
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        telefono = request.form['telefono']
        imagen = request.files['imagen']
        if not nombre or not email or not telefono:
            flash("Todos los campos son obligatorios", "danger")
            return redirect(url_for('personal'))
        if imagen and allowed_file(imagen.filename):
            imagen_filename = secure_filename(imagen.filename)
            imagen_path = os.path.join(app.config['UPLOAD_FOLDER'], imagen_filename)
            imagen.save(imagen_path)
            c.execute("INSERT INTO personal (nombre, email, telefono, imagen) VALUES (?, ?, ?, ?)", 
                      (nombre, email, telefono, imagen_filename))
            conn.commit()
            flash("Información del personal agregada correctamente", "success")
        else:
            flash("Tipo de archivo no permitido o error al cargar la imagen", "danger")
            return redirect(url_for('personal'))
    c.execute("SELECT * FROM personal")
    personal = c.fetchall()
    conn.close()
    return render_template('personal.html', personal=personal)

@app.route('/eliminar_personal/<int:id>', methods=['POST'])
@requiere_rol('admin')
def eliminar_personal(id):
    conn = get_db_connection_sqlite()
    c = conn.cursor()
    c.execute("SELECT imagen FROM personal WHERE id = ?", (id,))
    imagen_filename = c.fetchone()[0]
    if imagen_filename:
        imagen_path = os.path.join(app.config['UPLOAD_FOLDER'], imagen_filename)
        if os.path.exists(imagen_path):
            os.remove(imagen_path)
    c.execute("DELETE FROM personal WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    flash("Personal eliminado correctamente", "success")
    return redirect(url_for('personal'))

# Método auxiliar para verificar las extensiones de archivo permitidas
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
