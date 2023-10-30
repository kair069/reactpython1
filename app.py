from flask import Flask, request, jsonify, send_file

from flask_cors import CORS
import mysql.connector
#nuevas librerias
import pandas as pd
import xlsxwriter
import io
import openpyxl


app = Flask(__name__)
# CORS(app, origins="http://localhost:3000")
CORS(app, origins="*")
#CORS(app, origins="*")
# Configura la conexión a MySQL
db = mysql.connector.connect(
    #host="localhost",
    #user="root",
    #password="1234",
    #database="mi_base_de_datos"
    
    host="mysqlalex.mysql.database.azure.com",
    user="administrador",
    password="boltimax.P",
    database="mi_base_de_datos",
    
    # user="administrador",
    # password="boltimax.P",
    # host="mysqlalex.mysql.database.azure.com",
    # port=3306,
    # database="mi_base_de_datos",
    # ssl_ca="C:/Users/Acer/Downloads/DigiCertGlobalRootG2.crt.pem",
    # ssl_disabled=False
)

@app.route('/productos', methods=['GET'])
def listar_productos():
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM productos")
        productos = cursor.fetchall()
        return jsonify(productos)
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/productos', methods=['POST'])
def agregar_producto():
    try:
        data = request.get_json()
        nombre = data['nombre']
        descripcion = data['descripcion']
        precio = data['precio']

        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO productos (nombre, descripcion, precio) VALUES (%s, %s, %s)",
            (nombre, descripcion, precio)
        )
        db.commit()
        return jsonify({"mensaje": "Producto agregado correctamente"})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/productos/<int:producto_id>', methods=['GET', 'PUT', 'DELETE'])
def gestionar_producto(producto_id):
    try:
        cursor = db.cursor(dictionary=True)
        if request.method == 'GET':
            cursor.execute("SELECT * FROM productos WHERE id = %s", (producto_id,))
            producto = cursor.fetchone()
            if producto:
                return jsonify(producto)
            else:
                return jsonify({"mensaje": "Producto no encontrado"}), 404
        elif request.method == 'PUT':
            data = request.get_json()
            nombre = data['nombre']
            descripcion = data['descripcion']
            precio = data['precio']

            cursor.execute(
                "UPDATE productos SET nombre = %s, descripcion = %s, precio = %s WHERE id = %s",
                (nombre, descripcion, precio, producto_id)
            )
            db.commit()
            return jsonify({"mensaje": "Producto actualizado correctamente"})
        elif request.method == 'DELETE':
            cursor.execute("DELETE FROM productos WHERE id = %s", (producto_id,))
            db.commit()
            return jsonify({"mensaje": "Producto eliminado correctamente"})
    except Exception as e:
        return jsonify({"error": str(e)})
    
 # Simulación de una función de predicción de precio   
def predecir_precio(datos):
    # En este ejemplo, simplemente sumamos el precio ingresado por el usuario y le agregamos 10
    precio_predicho = datos['precio'] + 10
    return precio_predicho

@app.route('/prediccion-precio', methods=['GET', 'POST'])
def manejar_prediccion():
    if request.method == 'GET':
        # En el método GET, puedes devolver información o instrucciones de uso
        respuesta = {
            'mensaje': 'Utiliza el método POST para realizar una predicción de precio.',
            'ejemplo_solicitud': {
                'nombre': 'Producto de ejemplo',
                'descripcion': 'Descripción de ejemplo',
                'precio': 100
            }
        }
        return jsonify(respuesta), 200

    elif request.method == 'POST':
        try:
            # Obtén los datos del cuerpo de la solicitud POST
            datos = request.json

            # Realiza la predicción de precio utilizando la función de predicción
            precio_predicho = predecir_precio(datos)

            # Devuelve la predicción de precio como JSON
            respuesta = {'prediccion': precio_predicho}
            return jsonify(respuesta), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
        
#nuvo codigo
@app.route('/productos/export-csv', methods=['GET'])
def export_to_csv():
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM productos")
        productos = cursor.fetchall()

        # Convert the product data to a DataFrame
        df = pd.DataFrame(productos)

        # Create an in-memory CSV writer object
        output = io.StringIO()

        # Write the DataFrame to the StringIO object in binary mode
        df.to_csv(output, index=False, encoding='utf-8', mode='w', header=True, sep=',', quotechar='"')

        # Save the CSV data to the output stream
        output.seek(0)

        # Return the CSV file as a downloadable attachment
        return send_file(
            io.BytesIO(output.getvalue().encode()),
            as_attachment=True,
            download_name='productos.csv',
            mimetype='text/csv'
        )

    except Exception as e:
        return jsonify({"error": str(e)})
@app.route('/productos/export-excel', methods=['GET'])
def export_to_excel():
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM productos")
        productos = cursor.fetchall()

        # Convert the product data to a DataFrame
        df = pd.DataFrame(productos)

        # Create an in-memory Excel writer object
        output = io.BytesIO()

        # Create a Pandas Excel writer using openpyxl as the engine
        writer = pd.ExcelWriter(output, engine='openpyxl')

        # Write the DataFrame to the Excel writer
        df.to_excel(writer, sheet_name='productos', index=False)

        # Save the Excel workbook to the output stream
        writer.save()
        output.seek(0)

        # Return the Excel file as a downloadable attachment
        return send_file(
            io.BytesIO(output.read()),
            as_attachment=True,
            download_name='productos.xlsx',
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

    except Exception as e:
        return jsonify({"error": str(e)})
if __name__ == '__main__':
    app.run(debug=True)
