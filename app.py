from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

#Database Config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///stockflow.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

#Models 

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    sku = db.Column(db.String(50), unique=True, nullable=False)
    price = db.Column(db.Float, nullable=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'))

class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouse.id'), nullable=False)
    quantity = db.Column(db.Integer, default=0)
    low_stock_threshold = db.Column(db.Integer, default=10)

class Warehouse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    company_id = db.Column(db.Integer, nullable=False)

class Supplier(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    contact_email = db.Column(db.String(100))

# API Endpoints

@app.route('/api/products', methods=['POST'])
def create_product():
    incoming_data = request.json
    
    # Manual validation for required fields
    required_fields = ['name', 'sku', 'price', 'warehouse_id', 'initial_quantity']
    for field in required_fields:
        if field not in incoming_data:
            return jsonify({"error": f"Opps! '{field}' is missing."}), 400

    try:
        #Check if SKU is unique
        check_sku = Product.query.filter_by(sku=incoming_data['sku']).first()
        if check_sku:
            return jsonify({"error": "This SKU is already taken, try a different one."}), 400

        #Create new product record
        new_prod = Product(
            name=incoming_data['name'],
            sku=incoming_data['sku'],
            price=incoming_data['price']
        )
        db.session.add(new_prod)
        db.session.flush() 

        #Create initial inventory record
        new_inv = Inventory(
            product_id=new_prod.id,
            warehouse_id=incoming_data['warehouse_id'],
            quantity=incoming_data['initial_quantity']
        )
        db.session.add(new_inv)
        
        db.session.commit()
        return jsonify({"message": "Great! Product and stock added.", "id": new_prod.id}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Database error", "msg": str(e)}), 500

@app.route('/api/companies/<int:company_id>/alerts/low-stock', methods=['GET'])
def get_low_stock_alerts(company_id):
    low_stock_list = []
    
    #Joining tables to fetch detailed alert data
    items = db.session.query(Inventory, Product, Warehouse, Supplier)\
        .join(Product, Inventory.product_id == Product.id)\
        .join(Warehouse, Inventory.warehouse_id == Warehouse.id)\
        .join(Supplier, Product.supplier_id == Supplier.id)\
        .filter(Warehouse.company_id == company_id)\
        .filter(Inventory.quantity <= Inventory.low_stock_threshold).all()

    for inv, prod, wh, sup in items:
        avg_sales = get_daily_sales_rate(prod.id) 
        
        if avg_sales > 0:
            days_remaining = int(inv.quantity / avg_sales)
            
            low_stock_list.append({
                "product_name": prod.name,
                "sku": prod.sku,
                "warehouse": wh.name,
                "current_stock": inv.quantity,
                "threshold": inv.low_stock_threshold,
                "days_until_stockout": days_remaining,
                "supplier": {
                    "name": sup.name,
                    "email": sup.contact_email
                }
            })

    return jsonify({
        "alerts": low_stock_list,
        "total": len(low_stock_list)
    }), 200

def get_daily_sales_rate(product_id):
    #Currently returning a static rate
    return 1.5 

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)