from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing

# --- Database Configuration ---
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hotel_menu.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- MenuItem Model ---
class MenuItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(300), nullable=True)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(80), nullable=False)
    image_url = db.Column(db.String(300), nullable=True)

    def to_dict(self):
        return {
            "id": self.id, "name": self.name, "description": self.description,
            "price": self.price, "category": self.category, "image_url": self.image_url
        }

# Create database tables
with app.app_context():
    db.create_all()

# --- API Routes ---

@app.route('/')
def home():
    return "Hotel Menu API is running."

@app.route('/menu-items', methods=['GET'])
def get_menu_items():
    items = MenuItem.query.all()
    return jsonify([item.to_dict() for item in items])

@app.route('/menu-items/<int:item_id>', methods=['GET'])
def get_menu_item(item_id):
    item = db.session.get(MenuItem, item_id)
    return jsonify(item.to_dict()) if item else (jsonify({"error": "Item not found"}), 404)

@app.route('/menu-items', methods=['POST'])
def add_menu_item():
    data = request.get_json()
    if not data or not all(k in data for k in ['name', 'price', 'category']):
        return jsonify({"error": "Missing required fields"}), 400
    
    new_item = MenuItem(
        name=data['name'], price=data['price'], category=data['category'],
        description=data.get('description', ''), image_url=data.get('image_url', '')
    )
    db.session.add(new_item)
    db.session.commit()
    return jsonify(new_item.to_dict()), 201

@app.route('/menu-items/<int:item_id>', methods=['PUT'])
def update_menu_item(item_id):
    item = db.session.get(MenuItem, item_id)
    if not item:
        return jsonify({"error": "Item not found"}), 404
    data = request.get_json()
    item.name = data.get('name', item.name)
    item.description = data.get('description', item.description)
    item.price = data.get('price', item.price)
    item.category = data.get('category', item.category)
    item.image_url = data.get('image_url', item.image_url)
    db.session.commit()
    return jsonify(item.to_dict())

@app.route('/menu-items/<int:item_id>', methods=['DELETE'])
def delete_menu_item(item_id):
    item = db.session.get(MenuItem, item_id)
    if not item:
        return jsonify({"error": "Item not found"}), 404
    db.session.delete(item)
    db.session.commit()
    return jsonify({"message": "Menu item deleted"})

if __name__ == '__main__':
    # This server runs on port 5000
    app.run(debug=True, port=5000)
