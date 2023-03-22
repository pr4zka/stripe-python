from flask import Flask, request, redirect, jsonify, render_template, url_for
import mysql.connector
import stripe


app = Flask(__name__)

stripe.api_key = 'private_key'
YOUR_DOMAIN = 'http://localhost:4000'

mydb = mysql.connector.connect(
    host="",
    user="",
    password="",
    database="python"
)


@app.route('/products')
def getProducts():
    mycursor = mydb.cursor()
    mycursor.execute('SELECT * FROM products')
    result = mycursor.fetchall()
    return render_template('index.html', products=result)


@app.route('/')
def render():
    return render_template('index.html')


@app.route('/products', methods=['POST'])
def createProducts():
    if request.method == 'POST':
        data = request.get_json()
        name = data['name']
        descripcion = data['descripcion']
        price = data['price']
        cur = mydb.cursor()
        cur.execute('INSERT INTO products (name, descripcion, price) VALUES (%s, %s, %s)',
                    (name, descripcion, price))
        mydb.commit()
        cur.close()
        return jsonify({"message": "Products created succes"})


@app.route('/products/<int:id>')
def getById(id):
    cur = mydb.cursor()
    cur.execute('SELECT * FROM products WHERE id = (%s)', (id,))
    product = cur.fetchall()
    cur.close()
    if product is not None:
        return jsonify(product)
    else:
        return jsonify({"message": "Not Found"}), 404


@app.route('/products/<int:id>', methods=['PATCH'])
def updateProducts(id):
    data = request.get_json()
    cur = mydb.cursor()
    productsFound = cur.execute(
        'SELECT * FROM products WHERE id = (%s)', (id,))
    product = cur.fetchone()

    if not product:
        cur.close()
        return jsonify({'error': "Product not found"}), 404
    else:
        name = data.get('name', product[1])
        descripcion = data.get('descripcion', product[2])
        price = data.get('price', product[3])
        cur.execute('UPDATE products SET name = %s, descripcion = %s, price = %s WHERE id = %s',
                    (name, descripcion, price, id))
        mydb.commit()
        cur.close()
        return jsonify({"message": "Actualizado"})


@app.route('/products/<int:id>', methods=['DELETE'])
def deleteProducts(id):
    cur = mydb.cursor()
    cur.execute('SELECT * FROM products WHERE id= %s', (id,))
    product = cur.fetchone()

    if not product:
        cur.close()
        return jsonify({"message": "Product you want to deleted not found"})
    else:
        cur.execute("DELETE FROM products WHERE id= %s", (id,))
        mydb.commit()
        cur.close()
        return jsonify({"message": "Product Deleted"})


@app.route('/checkout')
def renderCheckout():
    return render_template('checkout.html')

@app.route('/success')
def renderSuccess():
    return render_template('success.html')
    # return jsonify({"message": "Hola mi loco"})


@app.route('/checkout', methods=['POST'])
def checkout():
    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    'price': 'price_1Mo9kKLZITrZk5TFglBaILPe',
                    'quantity': 1,
                }
            ],
            mode='payment',
            success_url=YOUR_DOMAIN + '/success',
            cancel_url=YOUR_DOMAIN + '/cancel',
        )
    except Exception as e:
        return str(e)

    return redirect(checkout_session.url, code=303)


if __name__ == '__main__':
    app.run(debug=True, port=4000)
