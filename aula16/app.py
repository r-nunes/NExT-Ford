from itertools import product
import os

from datetime import datetime
from unicodedata import category, name
from flask import Flask, jsonify, abort, request
from flask_restful import Api, Resource, reqparse
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy import Table, Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
api = Api(app)

db = SQLAlchemy(app)

class Product(db.Model, SerializerMixin):
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float(2), nullable=False)
    favorite = db.Column(db.Boolean, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id', ondelete="CASCADE"), nullable=True)
    #category = db.relationship('Category', back_populates='products', lazy=True)
    #orders = db.relationship("ProductOrder", backref="products")

    def __repr__(self):
        return '<Product %r>' % self.name

class Category(db.Model, SerializerMixin):
    __tablename__ = 'category'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    #products = db.relationship('Product', back_populates='category', cascade='all, delete, delete-orphan', single_parent=True, lazy=True, passive_deletes=True, order_by='desc(Product.name)')
    
    def __repr__(self):
        return '<Category %r>' % self.name

class Order(db.Model, SerializerMixin):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.Integer, nullable=False, unique=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    #products = db.relationship("ProductOrder", backref="orders")

    def __repr__(self):
        return '<Order %r>' % self.name

class ProductOrder(db.Model, SerializerMixin):
    __tablename__ = 'product_order'
    product_id = db.Column(db.ForeignKey('product.id'), primary_key=True)
    order_id = db.Column(db.ForeignKey('order.id'), primary_key=True)
    amount = db.Column(db.Integer, nullable=False)

@app.before_first_request
def create_db():
    # Delete database file if it exists currently
    if os.path.exists("database.db"):
        os.remove("database.db")
    db.create_all()

@app.route('/product', methods=['GET'])
def list_prod():
    data_product = Product.query.all()
    return jsonify(
        {"product": [data_product_.to_dict() for data_product_ in data_product]}
    )

@app.route('/product', methods=['POST'])
def create_prod():
    data_prod = request.json

    prod_name = data_prod['name']
    prod_price = data_prod['price']
    prod_favorite = data_prod['favorite']
    prod_category_id = data_prod['category_id']

    product = Product(name=prod_name, price=prod_price, favorite=prod_favorite, category_id=prod_category_id)
    db.session.add(product)
    db.session.commit()

    return jsonify({"success": True, "response": "Product added"})

@app.route('/category', methods=['GET'])
def list_category():
    category = Category.query.all()
    return jsonify(
        {"category": [category_.to_dict() for category_ in category]}
    )

@app.route('/category', methods=['POST'])
def create_cat():
    data_categ = request.json
    db.session.add(Category(name=data_categ['name']))
    db.session.commit()

    return jsonify({"success": True, "response": "Product added"})


if __name__ == '__main__':
    app.run(debug=True)