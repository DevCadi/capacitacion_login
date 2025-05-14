from flask import Flask, render_template, request, url_for, redirect, flash
#llamar a las funciones para poner un login
from flask_login import login_user, login_required, logout_user,UserMixin, current_user,LoginManager 
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecretkey'

#funciones y rutas de la aplicacion
#funcion para conectar a la base de datos
def get_db_connection():
    conn = sqlite3.connect('bd_instituto.db')
    #para gestionar los resultados como diccionarios
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def index():
    conn = get_db_connection()
    cursos = conn.execute("SELECT * FROM cursos").fetchall()
    conn.close()
    return render_template("index.html", cursos=cursos)



@app.route('/cursos')
def cursos():
    conn = get_db_connection()
    cursos = conn.execute('SELECT * FROM cursos').fetchall() #fetchall obtener todos los registros
    conn.close()
    return render_template('cursos.html',cursos=cursos)

@app.route("/curso/nuevo", methods=["GET", "POST"])
def nuevo_curso():
    if request.method == "POST":
        #leet contenido del formulario
        descripcion = request.form['descripcion']
        horas = request.form['horas']
        conn = get_db_connection()
        conn.execute('INSERT INTO cursos(descripcion,horas) VALUES (?,?)', (descripcion,horas))
        conn.commit()
        conn.close()
        flash('Curso creado con exito','success')
        return redirect(url_for('cursos'))
    return render_template('form_curso.html')
        
@app.route("/curso/editar/<int:id>", methods=["GET", "POST"])
def editar_curso(id):
    conn = get_db_connection()
    curso = conn.execute('SELECT * FROM cursos WHERE id = ?', (id,)).fetchone()
    if request.method == "POST":
        #leet contenido del formulario
        descripcion = request.form['descripcion']
        horas = request.form['horas']
        conn.execute('UPDATE cursos SET descripcion = ?, horas = ? WHERE id = ?', (descripcion,horas,id))
        conn.commit()
        conn.close()
        flash('Curso actualizado con exito','success')
        return redirect(url_for('cursos'))
    return render_template('form_curso.html', curso=curso)

@app.route('/curso/eliminar/<int:id>')
def eliminar_curso(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM cursos WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('Curso eliminado con exito','success')
    return redirect(url_for('cursos'))

@app.route('/estudiantes')
def estudiantes():
    conn = get_db_connection()
    estudiantes = conn.execute('SELECT * FROM estudiantes').fetchall()
    conn.close()
    return render_template('estudiantes.html',estudiantes=estudiantes)

@app.route("/estudiante/nuevo", methods=["GET", "POST"])
def nuevo_estudiante():
    if request.method == "POST":
        #leet contenido del formulario
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        fecha_nacimiento = request.form['fecha_nacimiento']
        conn = get_db_connection()
        conn.execute('INSERT INTO estudiantes(nombre,apellidos,fecha_nacimiento) VALUES (?,?,?)', (nombre,apellido,fecha_nacimiento))
        conn.commit()
        conn.close()
        flash('Estudiante creado con exito','success')
        return redirect(url_for('estudiantes'))
    return render_template('form_estudiante.html')

@app.route("/estudiante/editar/<int:id>", methods=["GET", "POST"])
def editar_estudiante(id):
    conn= get_db_connection()
    estudiante = conn.execute('SELECT * FROM estudiantes WHERE id = ?', (id,)).fetchone()
    if request.method == "POST":
        #leet contenido del formulario
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        conn.execute('UPDATE estudiantes SET nombre = ?, apellidos = ? WHERE id = ?', (nombre,apellido,id))
        conn.commit()
        conn.close()
        flash('Estudiante actualizado con exito','success')
        return redirect(url_for('estudiantes'))
    return render_template('form_estudiante.html', estudiante=estudiante)

@app.route('/estudiante/eliminar/<int:id>')
def eliminar_estudiante(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM estudiantes WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('Estudiante eliminado con exito','success')
    return redirect(url_for('estudiantes'))

@app.route("/inscripciones")
def inscripciones():
    conn = get_db_connection()
    inscripciones = conn.execute(
        """
        SELECT i.id,
        i.fecha,
        e.nombre || ' ' || e.apellidos as estudiante,
        c.descripcion as curso
        FROM inscripciones i
        JOIN estudiantes e ON i.estudiante_id = e.id
        JOIN cursos c ON i.curso_id = c.id
        """).fetchall()
    conn.close()
    return render_template('inscripciones.html',inscripciones=inscripciones)


@app.route("/inscripcion/nuevo", methods=["GET", "POST"])
def nueva_inscripcion():
    conn = get_db_connection()
    if request.method == "POST":
        #leer contenido del formulario
        fecha = request.form['fecha']
        estudiante_id = request.form['estudiante_id']
        curso_id = request.form['curso_id']
        conn = get_db_connection()
        conn.execute(
            """
            INSERT INTO inscripciones(fecha,estudiante_id,curso_id) VALUES (?,?,?)
            """, (fecha,estudiante_id,curso_id)
        )
        conn.commit()
        conn.close()
        flash('Inscripcion creada con exito','success')
        return redirect(url_for('inscripciones'))
    # en caso de GET enaviar datos para mostrar en formualrio de inscripcion
    estudiantes = conn.execute(
        """
        SELECT id, concat(nombre || ' ' || apellidos) as nombre
        FROM estudiantes
        """
    ).fetchall()
    cursos = conn.execute(
        """
        SELECT id, descripcion
        FROM cursos"""
    ).fetchall()

    return render_template('form_inscripciones.html',estudiantes=estudiantes,cursos=cursos)
        


@app.route("/inscripcion/eliminar/<int:id>")
def eliminar_inscripcion(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM inscripciones WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('Inscripcion eliminada con exito','success')
    return redirect(url_for('inscripciones'))


@app.route("/inscripcion/editar/<int:id>", methods=["GET", "POST"])
def editar_inscripcion(id):
    conn = get_db_connection()
    inscripcion = conn.execute(
        """
        SELECT i.id,
        i.fecha,
        e.nombre || ' ' || e.apellidos as estudiante,
        c.descripcion as curso
        FROM inscripciones i
        JOIN estudiantes e ON i.estudiante_id = e.id
        JOIN cursos c ON i.curso_id = c.id
        WHERE i.id = ?
        """, (id,)
    ).fetchone()
    if request.method == "POST":
        #leer contenido del formulario
        fecha = request.form['fecha']
        estudiante_id = request.form['estudiante_id']
        curso_id = request.form['curso_id']
        conn = get_db_connection()
        conn.execute(
            """
            UPDATE inscripciones SET fecha = ?, estudiante_id = ?, curso_id = ? WHERE id = ?
            """, (fecha,estudiante_id,curso_id,id)
        )
        conn.commit()
        conn.close()
        flash('Inscripcion actualizada con exito','success')
        return redirect(url_for('inscripciones'))
    # en caso de GET enaviar datos para mostrar en formualrio de inscripcion esto me muestra apellido y nombre
    estudiantes = conn.execute(
        """
        SELECT id, concat(nombre || ' ' || apellidos) as nombre
        FROM estudiantes
        """
    ).fetchall()
    cursos = conn.execute(
        """
        SELECT id, descripcion
        FROM cursos"""
    ).fetchall()

    return render_template('form_inscripciones.html',inscripcion=inscripcion,estudiantes=estudiantes,cursos=cursos)

#creando el login para la pagina login y registrar
#configurar login manager
login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)
#inicializar la base de datos
def init_db():
    conn = get_db_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()

#clase ususario para Flask-login

class User(UserMixin):
    def __init__(self, id, username, password, name=None, email=None):
        self.id = id
        self.username = username
        self.password = password
        self.name = name
        self.email = email
    
    @staticmethod
    def get_by_id(user_id):
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
        conn.close()
        if user:
            return User(user['id'], user['username'], user['password'], user['name'], user['email'])
        return None
        
    @staticmethod
    def get_by_username(username):
        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        conn.close()
        if user:
            return User(user['id'], user['username'], user['password'], user['name'], user['email'])
        return None
@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        username = request.form["username"]
        password = request.form["password"]
        hass_pass = generate_password_hash(password)
        conn = get_db_connection()
        try:
            conn.execute(
                "INSERT INTO users (name, email, username, password) VALUES (?, ?, ?, ?)",
                (name, email, username, hass_pass),
            )
            conn.commit()
            flash('Usuario registrado exitosamente. Inicia Sesion','success')
            return redirect(url_for("login"))

        except sqlite3.IntegrityError:
            conn.rollback()
            flash('El usuario ya existe', 'danger')
        finally:
            conn.close()    
    return render_template("register.html")
            
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.get_by_username(username)
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Inicio de sesion exitoso', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Credenciales invalidas', 'danger')
    return render_template("login.html")

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html",username=current_user.username,name=current_user.name)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesion', 'info')
    return redirect(url_for("index"))


if __name__ == '__main__':
    init_db()
    app.run(debug=True)