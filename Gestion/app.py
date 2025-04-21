from flask import Flask, request, jsonify, render_template, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventario.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Modelo de Producto
class Producto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    cantidad = db.Column(db.Integer, default=0)
    precio = db.Column(db.Float, nullable=False)

# Crear la base de datos
with app.app_context():
    db.create_all()

# Ruta para obtener todos los productos y estadísticas
@app.route('/productos', methods=['GET'])
def obtener_productos():
    productos = Producto.query.all()
    total_productos = len(productos)
    total_valor_inventario = sum(p.cantidad * p.precio for p in productos)
    return jsonify({
        'productos': [{
            'id': p.id,
            'nombre': p.nombre,
            'cantidad': p.cantidad,
            'precio': p.precio,
            'total_valor': p.cantidad * p.precio
        } for p in productos],
        'total_productos': total_productos,
        'total_valor_inventario': total_valor_inventario
    })

# Ruta para agregar un producto
@app.route('/productos', methods=['POST'])
def agregar_producto():
    data = request.form
    nuevo_producto = Producto(nombre=data['nombre'], cantidad=int(data['cantidad']), precio=float(data['precio']))
    db.session.add(nuevo_producto)
    db.session.commit()
    return jsonify({'mensaje': 'Producto agregado'}), 201

# Ruta para actualizar stock
@app.route('/productos/<int:id>', methods=['PUT'])
def actualizar_producto(id):
    producto = Producto.query.get(id)
    if not producto:
        return jsonify({'mensaje': 'Producto no encontrado'}), 404
    data = request.json
    producto.cantidad = data.get('cantidad', producto.cantidad)
    producto.precio = data.get('precio', producto.precio)
    db.session.commit()
    return jsonify({'mensaje': 'Producto actualizado'})

# Ruta para eliminar o reducir cantidad de un producto
@app.route('/productos/<int:id>', methods=['DELETE'])
def eliminar_producto(id):
    producto = Producto.query.get(id)
    if not producto:
        return jsonify({'mensaje': 'Producto no encontrado'}), 404
    
    data = request.json
    cantidad_eliminar = data.get('cantidad', producto.cantidad)
    precio_reduccion = cantidad_eliminar * producto.precio
    
    if cantidad_eliminar >= producto.cantidad:
        db.session.delete(producto)
        mensaje = f'Producto eliminado completamente. Se redujo un total de ${precio_reduccion:.2f}'
    else:
        producto.cantidad -= cantidad_eliminar
        mensaje = f'Se eliminaron {cantidad_eliminar} unidades del producto, reduciendo ${precio_reduccion:.2f}'
    
    db.session.commit()
    return jsonify({'mensaje': mensaje, 'precio_reduccion': precio_reduccion})

# Ruta para la interfaz web
@app.route('/')
def index():
    productos = Producto.query.all()
    total_productos = len(productos)
    total_valor_inventario = sum(p.cantidad * p.precio for p in productos)
    return render_template('index.html', productos=productos, total_productos=total_productos, total_valor_inventario=total_valor_inventario)

if __name__ == '__main__':
    app.run(debug=True)
