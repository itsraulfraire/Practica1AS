# python.exe -m venv .venv
# cd .venv/Scripts
# activate.bat
# py -m ensurepip --upgrade
# pip install -r requirements.txt

from flask import Flask

from flask import render_template
from flask import request
from flask import jsonify, make_response

import mysql.connector

import datetime
import pytz

from flask_cors import CORS, cross_origin

con = mysql.connector.connect(
    host="185.232.14.52",
    database="u760464709_23005116_bd",
    user="u760464709_23005116_usr",
    password="z8[T&05u"
)

app = Flask(__name__)
CORS(app)

def pusherMascotas():
    import pusher
    
    pusher_client = pusher.Pusher(
      app_id='2046026',
      key='c018d337fb7e8338dc3a',
      secret='ee47376ce42adae4531e',
      cluster='us2',
      ssl=True
    )
    
    pusher_client.trigger("rapid-bird-168", "eventoMascotas", {"message": "Hola Mundo!"})
    return make_response(jsonify({}))

@app.route("/")
def index():
    if not con.is_connected():
        con.reconnect()

    con.close()

    return render_template("index.html")

@app.route("/app")
def app2():
    if not con.is_connected():
        con.reconnect()

    con.close()

    return render_template("login.html")
    # return "<h5>Hola, soy la view app</h5>"

@app.route("/iniciarSesion", methods=["POST"])
# Usar cuando solo se quiera usar CORS en rutas específicas
# @cross_origin()
def iniciarSesion():
    if not con.is_connected():
        con.reconnect()

    usuario    = request.form["txtUsuario"]
    contrasena = request.form["txtContrasena"]

    cursor = con.cursor(dictionary=True)
    sql    = """
    SELECT id_usuario
    FROM usuarios

    WHERE nombre_usuario = %s
    AND contrasena = %s
    """
    val    = (usuario, contrasena)

    cursor.execute(sql, val)
    registros = cursor.fetchall()
    con.close()

    return make_response(jsonify(registros))

@app.route("/mascotas")
def mascotas():
    return render_template("mascotas.html")

@app.route("/tbodyMascotas")
def tbodyMascotas():
    if not con.is_connected():
        con.reconnect()

    cursor = con.cursor(dictionary=True)
    sql    = """
    SELECT idMascota,
           nombre,
           sexo,
           raza,
           peso,
           condiciones

    FROM mascotas

    ORDER BY idMascota DESC

    LIMIT 10 OFFSET 0
    """

    cursor.execute(sql)
    registros = cursor.fetchall()

    # Si manejas fechas y horas
    """
    for registro in registros:
        fecha_hora = registro["Fecha_Hora"]

        registro["Fecha_Hora"] = fecha_hora.strftime("%Y-%m-%d %H:%M:%S")
        registro["Fecha"]      = fecha_hora.strftime("%d/%m/%Y")
        registro["Hora"]       = fecha_hora.strftime("%H:%M:%S")
    """

    return render_template("tbodyMascotas.html", mascotas=registros)

@app.route("/productos/ingredientes/<int:idMascota>")
def productosIngredientes(idMascota):
    if not con.is_connected():
        con.reconnect()

    cursor = con.cursor(dictionary=True)
    sql    = """
    SELECT productos.Nombre_Producto, ingredientes.*, productos_ingredientes.Cantidad FROM productos_ingredientes
    INNER JOIN productos ON productos.Id_Producto = productos_ingredientes.Id_Producto
    INNER JOIN ingredientes ON ingredientes.Id_Ingrediente = productos_ingredientes.Id_Ingrediente
    WHERE productos_ingredientes.Id_Producto = %s
    ORDER BY productos.Nombre_Producto
    """

    cursor.execute(sql, (idMascota, ))
    registros = cursor.fetchall()

    return render_template("modal.html", productosIngredientes=registros)

@app.route("/mascotas/buscar", methods=["GET"])
def buscarMascotas():
    if not con.is_connected():
        con.reconnect()

    args     = request.args
    busqueda = args["busqueda"]
    busqueda = f"%{busqueda}%"
    
    cursor = con.cursor(dictionary=True)
    sql    = """
    SELECT idMascota,
           nombre,
           sexo,
           raza,
           peso,
           condiciones

    FROM mascotas

    WHERE nombre LIKE %s
    OR    sexo          LIKE %s
    OR    raza     LIKE %s
    OR    peso     LIKE %s
    OR    condiciones     LIKE %s

    ORDER BY idMascota DESC
    
    LIMIT 10 OFFSET 0
    """
    val    = (busqueda, busqueda, busqueda, busqueda, busqueda)

    try:
        cursor.execute(sql, val)
        registros = cursor.fetchall()

        # Si manejas fechas y horas
        """
        for registro in registros:
            fecha_hora = registro["Fecha_Hora"]

            registro["Fecha_Hora"] = fecha_hora.strftime("%Y-%m-%d %H:%M:%S")
            registro["Fecha"]      = fecha_hora.strftime("%d/%m/%Y")
            registro["Hora"]       = fecha_hora.strftime("%H:%M:%S")
        """

    except mysql.connector.errors.ProgrammingError as error:
        print(f"Ocurrió un error de programación en MySQL: {error}")
        registros = []

    finally:
        con.close()

    return make_response(jsonify(registros))

@app.route("/mascota", methods=["POST"])
# Usar cuando solo se quiera usar CORS en rutas específicas
# @cross_origin()
def guardarMascotas():
    if not con.is_connected():
        con.reconnect()

    idMascota   = request.form.get("idMascota")
    nombre      = request.form.get("nombre")
    sexo        = request.form.get("sexo")
    raza        = request.form.get("raza")
    peso        = request.form.get("peso")
    condiciones = request.form.get("condiciones")
    # fechahora   = datetime.datetime.now(pytz.timezone("America/Matamoros"))
    
    cursor = con.cursor()

    if idMascota:
        sql = """
        UPDATE mascotas

        SET nombre            = %s,
            sexo              = %s,
            raza              = %s,
            peso              = %s,
            condiciones       = %s

        WHERE idMascota = %s
        """
        val = (nombre, sexo, raza, peso, condiciones, idMascota)
    else:
        sql = """
        INSERT INTO mascotas (nombre, sexo, raza, peso, condiciones)
                    VALUES (%s, %s, %s, %s, %s)
        """
        val =                 (nombre, sexo, raza, peso, condiciones)
    
    cursor.execute(sql, val)
    con.commit()
    con.close()

    pusherMascotas()
    
    return make_response(jsonify({}))

@app.route("/mascota/<int:idMascota>")
def editarMascota(idMascota):
    if not con.is_connected():
        con.reconnect()

    cursor = con.cursor(dictionary=True)
    sql    = """
    SELECT idMascota, nombre, sexo, raza, peso, condiciones

    FROM mascotas

    WHERE idMascota = %s
    """
    val    = (idMascota,)

    cursor.execute(sql, val)
    registros = cursor.fetchall()
    con.close()

    return make_response(jsonify(registros))

def get_connection():
    return mysql.connector.connect(
        host="185.232.14.52",
        database="u760464709_23005116_bd",
        user="u760464709_23005116_usr",
        password="z8[T&05u"
    )

@app.route("/mascota/eliminar", methods=["POST"])
def eliminarMascota():
    idMascota = request.form.get("idMascota")
    if not idMascota:
        return make_response(jsonify({"error": "idMascota no proporcionado"}), 400)

    con = None
    cursor = None
    try:
        con = get_connection()
        cursor = con.cursor()
        sql = "DELETE FROM mascotas WHERE idMascota = %s"
        val = (idMascota,)
        cursor.execute(sql, val)
        con.commit()
        filas = cursor.rowcount
        return make_response(jsonify({"deleted_rows": filas}), 200)
    except mysql.connector.Error as e:
        app.logger.exception("Error eliminando mascota:")
        return make_response(jsonify({"error": str(e)}), 500)
    finally:
        try:
            if cursor:
                cursor.close()
            if con:
                con.close()
        except Exception:
            pass
