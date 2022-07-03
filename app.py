from flask import Flask, flash, render_template, redirect, url_for,request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey

app = Flask(__name__)

app.config['SECRET_KEY'] = 'clave_secretaa'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://usuario:contrasenia@host/nombreDB'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://BD2021:BD2021itec@143.198.156.171/sqlRosales'

db = SQLAlchemy(app)

class Provincia(db.Model):
    __tablename__ = 'provincia'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False, unique=True)

    def __init__(self, nombre):
        self.nombre = nombre

    def __str__(self):
        return self.nombre


class Localidad(db.Model):
    __tablename__ = 'localidad'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    idProvincia = db.Column(db.Integer, ForeignKey("provincia.id"))
    provincia = db.relationship("Provincia")
    def __init__(self, nombre, idProvincia):
        self.nombre = nombre
        self.idProvincia = idProvincia

    def __str__(self):
        return self.nombre


@app.route('/',methods=['GET'])
def index():
    return render_template('index.html')


# -----------  INICIO DE LOS METODOS DE LAS PROVINCIAS ------------
@app.route('/provincias/')
def provincias():
    provincias = db.session.query(Provincia).order_by('nombre').all()
    # localidades = db.session.query(Localidad).order_by('nombre').all()
    print("Pasa por el metodo provincias de la ruta /provincias/") 
    return render_template(
        'provincias.html',      
        
         provs=provincias
    )


@app.route('/agregar_provincia/', methods=['POST'])
def agregar_provincia():
    if request.method == 'POST':
        #Recibo el parametro por el formulario
        nombre = request.form['nombreProvincia']
        #Comienzo la creacion del objecto Provincia
        nueva_provincia = Provincia(nombre)
        db.session.add(nueva_provincia)
        db.session.commit()
        flash ('Provincia agregada correctamente', 'success')
        print("Pasa por el primer metodo")
        return redirect(url_for('provincias'))
        

@app.route('/provincias/<id>')
def localidades_provincias(id):
    localidades = db.session.query(Localidad).filter_by(idProvincia=id).all()
    nombre_provincia = localidades[0].provincia if localidades else None
    return render_template(
        'localidades_de_provincias.html',
        localidades=localidades,
        provincia = nombre_provincia
    )


@app.route('/provincias/editar/<id>/')
def editar_provincia(id):
    provincia = db.session.query(Provincia).filter_by(id=id).first()
    return render_template(
        "edit_provincia.html",
        provincia = provincia
    )


@app.route('/guardar_edicion_provincia', methods=['POST'])
def guardar_edicion_provincia():
    if request.method == 'POST':
        # Recibo el parametro por el formulario
        id = request.form['id']
        nombre = request.form['nombreProvincia']
        # Busco si existe una provincia con el mismo nombre
        validar_nombre = db.session.query(Provincia).filter_by(nombre=nombre).first()
        if validar_nombre:
            flash(f'Ya existe un provincia con el nombre {nombre}','warning')
            return redirect(url_for('provincias'))
        # Busco la provincia por el id
        provincia = db.session.query(Provincia).filter_by(id=id).first()
        # Modifico el campo deseado
        provincia.nombre = nombre
        # Guardo
        db.session.commit()
        flash('Provincia editada correctamente','success')
        return redirect(url_for('provincias'))


@app.route('/provincias/borrar/<id>/')
def borrar_provincia(id):
    # Busco el objeto a eliminar
    provincia = db.session.query(Provincia).filter_by(id=id).first()
    # Elimino
    db.session.delete(provincia)
    db.session.commit()
    flash('Provincia eliminada correctamente','danger')
    return redirect(url_for('provincias'))

# ------------ FIN METODOS DE PROVINCIAS -----------------

# ------------ INICIO METODOS DE LOCALIDADES -----------------

# Ruta de las localidades
@app.route('/localidades/')
def localidades():
    localidades = db.session.query(Localidad).all()
    provincias = db.session.query(Provincia).all()
    print("pasa por el metodo localidades de la ruta /localidades/")
    return render_template(
        'localidades.html',
         localidades=localidades,
         provs=provincias
    )

# Crear localidad
@app.route('/agregar_localidad/', methods=['POST'])
def agregar_localidad():
    if request.method == 'POST':
        # Recibo el parametro por el formulario
        nombre = request.form['nombreLocalidad']
        # obtener ID de la etiqueta SELECT de provincias.html
        idProvincia = request.form.get('selectProvincias')
        # verificar que la nueva localidad no exista
        if db.session.query(Localidad).filter_by(nombre=nombre).first():
            flash(f'Ya existe una localidad con el nombre {nombre}','warning')
            return redirect(url_for('localidades'))
        
        
        # Comienzo la creacion del objecto Localidad
        nueva_localidad = Localidad(nombre, idProvincia)
        db.session.add(nueva_localidad)
        db.session.commit()
        flash ('Localidad agregada correctamente', 'success')
        return redirect(url_for('localidades'))

# Eliminar localidad
@app.route('/localidades/borrar/<id>/')
def borrar_localidad(id):
    # Busco el objeto a eliminar
    localidad = db.session.query(Localidad).filter_by(id=id).first()
    # Elimino
    db.session.delete(localidad)
    db.session.commit()
    print("Pasa por el metodo borrar_localidad de la ruta /localidades/borrar/<id>/")
    flash('Localidad eliminada correctamente','danger')
    return redirect(url_for('localidades'))
# -------------------------
# editar localidad
@app.route('/localidades/editar/<id>/')
def editar_localidad(id):
    localidad = db.session.query(Localidad).filter_by(id=id).first()
    provincias = db.session.query(Provincia).all()
    print('Entro en la edicion de la localidad')
    return render_template(
        "edit_localidad.html",
        localidad = localidad,
        provs=provincias
    )
@app.route('/guardar_edicion_localidad', methods=['POST'])
def guardar_edicion_localidad():
    if request.method == 'POST':
        # Recibo el parametro por el formulario
        id = request.form['id']
        nombre = request.form['nombreLocalidad']
        #Busco el ID de la provincia a la que pertenece la localidad
        idProvincia =db.session.query(Localidad).filter_by(id=id).first().idProvincia
        # Busco si existe una localidad con el mismo nombre
        validar_nombre = db.session.query(Localidad).filter_by(nombre=nombre).first()
        if validar_nombre:
            flash(f'Ya existe una localidad con el nombre {nombre}','warning')
            return redirect(url_for('localidades'))
        # Busco la localidad por el id
        localidad = db.session.query(Localidad).filter_by(id=id).first()
        # Modifico el campo deseado
        localidad.nombre = nombre
        localidad.idProvincia = idProvincia
        # Guardo
        db.session.commit()
        flash('Localidad editada correctamente','success')
        print('Termina la edicion de la localidad')
        return redirect(url_for('localidades'))
    


if __name__ == '__main':
    app.run(debug=True)