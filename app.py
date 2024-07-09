from flask import Flask #Importamos el framework Flask
from flask import render_template,request,redirect,url_for,flash  #Importamos el render para mostrar todos los templates
from flaskext.mysql import MySQL #Importamos para conectarnos a la BD
from datetime import datetime #Nos permitirá darle el nombre a la foto
import os #Nos pemite acceder a los archivos
from flask import send_from_directory #Acceso a las carpetas

app = Flask(__name__) #Creando la app

mysql = MySQL()
# app.config['MYSQL_DATABASE_HOST']='http://127.0.0.1/' #Creamos la refencia al localhost
app.config['MYSQL_DATABASE_HOST']='localhost' #Creamos la refencia al localhost
app.config['MYSQL_DATABASE_USER']='root' #El user que viene por defecto
app.config['MYSQL_DATABASE_PASSWORD']='' #Se puede omitir si no hay contraseña definida
app.config['MYSQL_DATABASE_DB']='sistemaempleados' #nombre de la DB
mysql.init_app(app) #Creamos la conexion con la DB

CARPETA= os.path.join('uploads') #Referencia a la carpeta
app.config['CARPETA']=CARPETA #Indicamos que vamos a guardar esta ruta de la carpeta

@app.route('/uploads/<nombreFoto>')
def uploads(nombreFoto):
   return send_from_directory(app.config['CARPETA'], nombreFoto)


@app.route('/')  #Hacemos el ruteo para que el user entre en la raiz
def index():
    sql = "SELECT * FROM `sistemaempleados`. `empleados`;"
    conn = mysql.connect() #Se conecta a la conexión mysql.init_app(app)
    cursor = conn.cursor() #Almacenaremos lo que ejecutamos
    cursor.execute(sql) #Ejecutamos la sentencia SQL

    empleados=cursor.fetchall() #Traemos toda la información
    print(empleados) #Imprimimos los datos en la terminal

    conn.commit() #Cerramos la conexión

    return render_template('empleados/index.html', empleados=empleados) #Identifica la carpeta y el archivo html

@app.route('/destroy/<int:id>') #Recibe como parámetro el id del registro
def destroy(id):
    conn = mysql.connect() #Se conecta a la conexión mysql.init_app(app)
    cursor = conn.cursor() #Almacenaremos lo que ejecutamos

    cursor.execute("SELECT foto FROM  `sistemaempleados`. `empleados` WHERE id=%s", id) #Buscamos la foto
    fila= cursor.fetchall() #Traemos toda la información
    os.remove(os.path.join(app.config['CARPETA'], fila[0][0])) #Ese valor seleccionado se encuentra en la posición 0 y la fila 0

    cursor.execute("DELETE FROM  `sistemaempleados`. `empleados` WHERE id=%s", (id)) #En vez de pasarle el string la escribimos
    conn.commit() #Cerramos la conexión
    return redirect('/') #Regresamos de donde vinimos

@app.route('/edit/<int:id>')
def edit(id):
    # sql = "SELECT * FROM `sistemaempleados`. `empleados` WHERE id=%s;"
    conn = mysql.connect()#Se conecta a la conexion de mysql.init_app(app)
    cursor = conn.cursor() #almacenamos lo que ejecutamos
    cursor.execute("SELECT * FROM `sistemaempleados`. `empleados` WHERE id=%s;", (id)) #Ejecutamos la sentencia SQL
    empleados = cursor.fetchall()
    conn.commit() #Cerramos la conexion
    print(empleados)
    return render_template('empleados/edit.html', empleados=empleados)

@app.route('/update', methods=['POST'])
def update():
    _nombre=request.form['txtNombre']
    _correo=request.form['txtCorreo']
    _foto=request.files['txtFoto']
    id=request.form['txtID']
    print(_nombre)
    sql = "UPDATE `sistemaempleados`. `empleados` SET `nombre`=%s, `correo`=%s WHERE id=%s;"
    datos=(_nombre,_correo,id)

    conn = mysql.connect() #Se conecta a la conexión mysql.init_app(app)
    cursor = conn.cursor() #Almacenaremos lo que ejecutamos
    
    now= datetime.now()
    tiempo= now.strftime("%Y%H%M%S") #Años horas minutos y segundos

    if _foto.filename!='':
        nuevoNombreFoto=tiempo+_foto.filename #Concatena el nombre
        _foto.save("uploads/"+nuevoNombreFoto) #Lo guarda en la carpeta

        cursor.execute("SELECT foto FROM `sistemaempleados`. `empleados` WHERE id=%s", id) #Buscamos la foto
        fila= cursor.fetchall() #Traemos toda la información

        os.remove(os.path.join(app.config['CARPETA'], fila[0][0])) #Ese valor seleccionado se encuentra en la posición 0 y la fila 0
        cursor.execute("UPDATE `sistemaempleados`. `empleados` SET foto=%s WHERE id=%s", (nuevoNombreFoto, id)) #Buscamos la foto
    cursor.execute(sql,datos)
    conn.commit() #Cerramos la conexión

    return redirect('/')

@app.route('/create')
def create():
    return render_template('empleados/create.html')

@app.route('/store', methods=['POST'])
def storage():
    _nombre=request.form['txtNombre']
    _correo=request.form['txtCorreo']
    _foto=request.files['txtFoto']

    if _nombre == '' or _correo == '' or _foto =='':
        # flash('Recuerda llenar los datos de los campos') #Envía el mensaje
        return redirect(url_for('create')) #Vuelve a la página de carga de datos

    now= datetime.now()
    tiempo= now.strftime("%Y%H%M%S") #Años horas minutos y segundos

    if _foto.filename!='':
        nuevoNombreFoto=tiempo+_foto.filename #Concatena el nombre
        _foto.save("uploads/"+nuevoNombreFoto) #Lo guarda en la carpeta

    sql = "INSERT INTO `sistemaempleados`. `empleados` (`id`, `nombre`, `correo`, `foto`) VALUES (NULL, %s, %s, %s);"
    datos=(_nombre,_correo,nuevoNombreFoto)

    conn = mysql.connect() #Se conecta a la conexión mysql.init_app(app)
    cursor = conn.cursor() #Almacenaremos lo que ejecutamos
    cursor.execute(sql,datos) #Ejecutamos la sentencia SQL
    conn.commit() #Cerramos la conexión
    return redirect('/') #Regresamos de donde vinimos



#Linea requerida para que se pueda empezar a ejecutar la app
if __name__ == '__main__':
    app.run(debug=True) #Corremos la app en modo debuger