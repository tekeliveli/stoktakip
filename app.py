from flask import Flask, jsonify, request, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import func

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///stok.db'
db = SQLAlchemy(app)

# Malzeme Modeli
class Material(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(200), nullable=True)
    initial_stock = db.Column(db.Integer, nullable=False)
    unit = db.Column(db.String(20), nullable=False)  # Birim alanı

# Stok Kayıt Modeli
class StockRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    material_id = db.Column(db.Integer, db.ForeignKey('material.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    produced = db.Column(db.Integer, nullable=False)
    sold = db.Column(db.Integer, nullable=False)

    material = db.relationship('Material', backref=db.backref('records', lazy=True))

# Veritabanını oluştur
with app.app_context():
    db.create_all()

# Ana sayfayı sunma (Frontend)
@app.route('/')
def index():
    return render_template('index.html')

# Malzeme Ekleme
@app.route('/materials', methods=['POST'])
def add_material():
    data = request.json
    new_material = Material(
        name=data['name'],
        description=data.get('description', ''),
        initial_stock=data['initial_stock'],
        unit=data['unit']  # Birimi ekliyoruz
    )
    db.session.add(new_material)
    db.session.commit()
    return jsonify({'message': 'Yeni malzeme eklendi!'}), 201

# Malzemeleri Listeleme
@app.route('/materials', methods=['GET'])
def get_materials():
    materials = Material.query.all()
    result = []
    for material in materials:
        material_data = {
            'id': material.id,
            'name': material.name,
            'description': material.description,
            'initial_stock': material.initial_stock,
            'unit': material.unit  # Birimi de dahil ediyoruz
        }
        result.append(material_data)
    return jsonify(result), 200

# Stok Kayıt Ekleme
@app.route('/stock', methods=['POST'])
def add_stock():
    data = request.json
    material = Material.query.get(data['material_id'])
    if not material:
        return jsonify({'message': 'Malzeme bulunamadı!'}), 404

    new_record = StockRecord(
        material_id=material.id,
        date=datetime.strptime(data['date'], '%Y-%m-%d'),
        produced=data['produced'],
        sold=data['sold']
    )
    db.session.add(new_record)
    db.session.commit()
    return jsonify({'message': 'Stok kaydı eklendi!'}), 201

# Güncel Stok Durumunu Görüntüleme
@app.route('/stock/<int:material_id>', methods=['GET'])
def get_stock(material_id):
    material = Material.query.get(material_id)
    if not material:
        return jsonify({'message': 'Malzeme bulunamadı!'}), 404

    total_produced = db.session.query(func.sum(StockRecord.produced)).filter_by(material_id=material_id).scalar() or 0
    total_sold = db.session.query(func.sum(StockRecord.sold)).filter_by(material_id=material_id).scalar() or 0
    current_stock = material.initial_stock + total_produced - total_sold

    return jsonify({'material': material.name, 'current_stock': current_stock}), 200

# Stoktan Malzeme Çıkışı
@app.route('/stock/withdraw', methods=['POST'])
def withdraw_stock():
    data = request.json
    material_id = data['material_id']
    quantity = data['quantity']

    material = Material.query.get(material_id)
    if not material:
        return jsonify({'message': 'Malzeme bulunamadı!'}), 404

    total_produced = db.session.query(func.sum(StockRecord.produced)).filter_by(material_id=material_id).scalar() or 0
    total_sold = db.session.query(func.sum(StockRecord.sold)).filter_by(material_id=material_id).scalar() or 0
    current_stock = material.initial_stock + total_produced - total_sold

    if quantity > current_stock:
        return jsonify({'message': 'Yeterli stok yok!'}), 400

    new_record = StockRecord(
        material_id=material_id,
        date=datetime.today(),
        produced=0,
        sold=quantity
    )
    db.session.add(new_record)
    db.session.commit()

    return jsonify({'message': 'Stoktan malzeme çıkışı yapıldı!'}), 200

# Tarih Aralığında Üretim ve Satış Raporu
@app.route('/report', methods=['GET'])
def get_report():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    if not start_date or not end_date:
        return jsonify({'message': 'Başlangıç ve bitiş tarihleri gerekli!'}), 400

    start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

    records = db.session.query(
        Material.name, 
        Material.unit, 
        func.sum(StockRecord.produced).label('total_produced'), 
        func.sum(StockRecord.sold).label('total_sold')
    ).join(StockRecord, Material.id == StockRecord.material_id)\
    .filter(StockRecord.date.between(start_date, end_date))\
    .group_by(Material.name, Material.unit)\
    .all()

    result = []
    for record in records:
        result.append({
            'name': record[0],
            'unit': record[1],
            'total_produced': record[2] or 0,
            'total_sold': record[3] or 0
        })

    return jsonify(result), 200

# Stoktaki Tüm Malzemeleri Listeleme
@app.route('/stock/all', methods=['GET'])
def get_all_stock():
    materials = Material.query.all()
    result = []

    for material in materials:
        total_produced = db.session.query(func.sum(StockRecord.produced)).filter_by(material_id=material.id).scalar() or 0
        total_sold = db.session.query(func.sum(StockRecord.sold)).filter_by(material_id=material.id).scalar() or 0
        current_stock = material.initial_stock + total_produced - total_sold

        result.append({
            'name': material.name,
            'unit': material.unit,
            'current_stock': current_stock
        })

    return jsonify(result), 200

if __name__ == '__main__':
    app.run(debug=True)
