import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)
DATABASE = 'database.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/')
def index():
    return "Welcome to the API"

if __name__ == '__main__':
    app.run(debug=True)



@app.route('/api/products', methods=['POST'])
def create_product():
            data = request.get_json()
            name = data.get('name')
            description = data.get('description')
            price = data.get('price')
            category_id = data.get('category_id')

            if not name or price is None:
                return jsonify({'error': 'Product name and price are required'}), 400

            conn = get_db()
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "INSERT INTO products (name, description, price, category_id) VALUES (?, ?, ?, ?)",
                    (name, description, price, category_id)
                )
                conn.commit()
                product_id = cursor.lastrowid
                return jsonify({'id': product_id, 'name': name, 'price': price}), 201
            finally:
                conn.close()



@app.route('/api/products', methods=['GET'])
def get_products_v2():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    conn.close()

    products_list = [{'id': row['id'], 'name': row['name'], 'description': row['description'], 'price': row['price'], 'category_id': row['category_id']} for row in products]
    return jsonify(products_list), 200



@app.route('/api/products/<int:id>', methods=['GET','DELETE'])
def handle_Product(id):
    if request.method == 'GET':
        product = get_product_by_id(id)

    elif request.method == 'DELETE':
        affected_rows = delete_product_by_id(id)
        if affected_rows > 0:
            return jsonify({'message': 'Product deleted successfully'}), 200
        else:
            return jsonify({'error': 'Product not found'}), 404
        
def get_product_by_id(product_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    product = cursor.fetchone()
    conn.close()
    return product
def delete_product_by_id(product_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
    conn.commit()
    affected_rows = cursor.rowcount
    conn.close()
    return affected_rows



@app.route('/api/products', methods=['PATCH'])
def update_product(id):
    new_data = request.get_json()
    fields_to_update = ['name', 'price', 'description', 'category_id']
    
    updates = []
    values = []

    for field in fields_to_update:
        if field in new_data:
            updates.append(f"{field} = ?")
            values.append(new_data[field])

    if not updates:
        return jsonify({"error": "No data provided to update"}), 400

    values.append(id)
    query = f"UPDATE products SET {', '.join(updates)} WHERE id = ?"

    conn = get_db()
    cursor = conn.execute(query, tuple(values))
    conn.commit()
    conn.close()

    if cursor.rowcount == 0:
        return jsonify({"error": "Product not found"}), 404

    return jsonify({"message": f"Product {id} updated successfully"})


@app.route('/api/categories', methods=['POST'])
def create_category():
    data = request.get_json()
    name = data.get('name')

    if not name:
        return jsonify({'error': 'Category name is required'}), 400

    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO categories (name) VALUES (?)", (name,))
        conn.commit()
        category_id = cursor.lastrowid
        return jsonify({'id': category_id, 'name': name}), 201
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Category already exists'}), 409
    finally:
        conn.close()

@app.route('/api/products', methods=['GET'])
def get_products():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    conn.close()

    products_list = [{'id': row['id'], 'name': row['name'], 'description': row['description'], 'price': row['price'], 'category_id': row['category_id']} for row in products]
    return jsonify(products_list), 200

@app.route('/api/categories', methods=['GET'])
def get_categories():
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM categories")
        categories = cursor.fetchall()
        conn.close()

        categories_list = [{'id': row['id'], 'name': row['name']} for row in categories]
        return jsonify(categories_list), 200


@app.route('/api/categories/<int:id>', methods=['GET'])
def handle_category(id):
        if request.method == 'GET':
            category = get_category_by_id(id)
            if category:
                return jsonify({'id': category['id'], 'name': category['name']}), 200
            else:
                return jsonify({'error': 'Category not found'}), 404



def get_category_by_id(category_id):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM categories WHERE id = ?", (category_id,))
        category = cursor.fetchone()
        conn.close()
        return category



@app.route('/api/categories/<int:id>', methods=['PATCH'])
def update_category(id):
        new_data = request.get_json()
        
        if 'name' not in new_data:
            return jsonify({"error": "No data provided to update"}), 400

        conn = get_db()
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE categories SET name = ? WHERE id = ?", (new_data['name'], id))
            conn.commit()
            if cursor.rowcount == 0:
                return jsonify({"error": "Category not found"}), 404
            return jsonify({"message": f"Category {id} updated successfully"}), 200
        except sqlite3.IntegrityError:
            return jsonify({'error': 'Category name already exists'}), 409
        finally:
            conn.close()

@app.route('/api/carts', methods=['POST'])
def create_cart():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO carts DEFAULT VALUES")
    conn.commit()
    cart_id = cursor.lastrowid
    conn.close()
    return jsonify({'id': cart_id}), 201

@app.route('/api/carts',methods=['GET'])
def handle_cart():
    if request.method == 'GET':
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM carts")
        carts = cursor.fetchall()
        conn.close()

        carts_list = [{'id': row['id'], 'created_at': row['created_at']} for row in carts]
        return jsonify(carts_list), 200

@app.route('/api/carts/<int:id>',methods=['GET','DELETE'])
def handle_cart_by_id(id):
    if request.method == 'GET':
        cart = get_cart_by_id(id)
        if cart:
            return jsonify({'id': cart['id'], 'created_at': cart['created_at']}), 200
        else:
            return jsonify({'error': 'Cart not found'}), 404

    elif request.method == 'DELETE':
        affected_rows = delete_cart_by_id(id)
        if affected_rows > 0:
            return jsonify({'message': 'Cart deleted successfully'}), 200
        else:
            return jsonify({'error': 'Cart not found'}), 404
        
def get_cart_by_id(cart_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM carts WHERE id = ?", (cart_id,))
    cart = cursor.fetchone()
    conn.close()
    return cart
def delete_cart_by_id(cart_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM carts WHERE id = ?", (cart_id,))
    conn.commit()
    affected_rows = cursor.rowcount
    conn.close()
    return affected_rows

@app.route('/api/cartlist', methods=['POST'])
def add_to_cart():
    data = request.get_json()
    cart_id = data.get('cart_id')
    product_id = data.get('product_id')
    quantity = data.get('quantity', 1)

    if not cart_id or not product_id:
        return jsonify({'error': 'Cart ID and Product ID are required'}), 400

    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO cartlist (cart_id, product_id, quantity) VALUES (?, ?, ?)", (cart_id, product_id, quantity))
        conn.commit()
        return jsonify({'message': 'Product added to cart successfully'}), 201
    finally:
        conn.close()


