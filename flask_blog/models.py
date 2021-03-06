from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask_blog import db, login_manager, app
from flask_login import UserMixin
from sqlalchemy import update
from sqlalchemy.sql import func

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Shipping(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    method = db.Column(db.String(40), nullable=False)
    weight = db.Column(db.String(40), nullable=False)
    price_per_pound = db.Column(db.Float, nullable=False)
    flat_charges = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"Shipping('id: {self.id}, method: {self.method}, weight: {self.weight}, price_per_pound: {self.price_per_pound}, flat_charges: {self.flat_charges}')"

class Shipper(db.Model):
    shipper_id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(40), nullable=False)
    phone = db.Column(db.String(40), nullable=False)

    orders = db.relationship('Orders', backref='shipped', lazy=True)
    
    def __repr__(self):
        return f"Shipper('shipper_id (PK): {self.shipper_id}, company_name: {self.company_name}, phone: {self.phone}')"

class User(db.Model, UserMixin):
    user_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(40), nullable=False)
    last_name = db.Column(db.String(40), nullable=False)
    email = db.Column(db.String(40), nullable=False)
    password = db.Column(db.String(60), nullable=False)
    address = db.Column(db.String(50), nullable=False)
    city = db.Column(db.String(40), nullable=False)
    state = db.Column(db.String(40), nullable=False)
    postcode = db.Column(db.String(40), nullable=False)
    country = db.Column(db.String(40), nullable=False)
    phone = db.Column(db.String(40), nullable=False)
    role = db.Column(db.Integer, nullable=False, default=0)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')

    orders = db.relationship('Orders', backref='buy', lazy=True)

    def get_id(self):
           return (self.user_id)

    def get_role(self):
        return self.role

    def set_admin(self):
        user = User.query.filter_by(user_id=self.user_id).first()
        user.role = 1
        db.session.commit()

    def set_user(self):
        user = User.query.filter_by(user_id=self.user_id).first()
        user.role = 0
        db.session.commit()

    def is_admin(self):
        return True if self.role == 1 else False

    def is_user(self):
        return True if self.role == 0 else False

    def get_reset_token(self, expires_seconds=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_seconds)
        return s.dumps({'user_id': self.user_id}).decode('utf-8')

    @staticmethod
    def verify_reset(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('user_id(PK): {self.user_id}, first_name: {self.first_name}, last_name: {self.last_name}, phone: {self.phone}, email: {self.email}, image: {self.image_file}')"

class Orders(db.Model):
    order_id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.Integer, nullable=False)
    date_order = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    shipper_id = db.Column(db.Integer, db.ForeignKey('shipper.shipper_id'), nullable=False)

    order_details = db.relationship('OrderDetails', backref='has', lazy=True)
    user = db.relationship('User', backref='ordered', lazy=True)
    shipper = db.relationship('Shipper', backref='managed', lazy=True)
    
    def __repr__(self):
        return f"Orders('order_id(PK): {self.order_id}, user_id(FK): {self.user_id}, shipper_id(FK):{self.shipper_id},  order_number: {self.order_number})"

class OrderDetails(db.Model):
    order_details_id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    price = db.Column(db.Float, nullable=False)  
    total = db.Column(db.Float, nullable=False)
    user_id = db.Column(db.Integer, nullable=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.order_id'), nullable=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.product_id'), nullable=False)

    order = db.relationship('Orders', backref='fromorder', lazy=True)
    product = db.relationship('Products', backref='includes', lazy=True)
    
    def __repr__(self):
        return f"OrderDetails('order_details_id(PK): {self.order_details_id}, product_id(FK): {self.product_id}, order_id(FK): {self.order_id}, quantity: {self.quantity}, price: {self.price}, total: {self.total}')"

class Category(db.Model):
    category_id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(40), nullable=False)
    category_description = db.Column(db.String(100), nullable=False)

    products = db.relationship('Products', backref='contains', lazy=True)
    
    def __repr__(self):
        return f"Category('category_id(PK): {self.category_id}, category_name: {self.category_name}, category_description: {self.category_description}')"

class Products(db.Model):
    product_id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(40), nullable=False)
    product_description = db.Column(db.String(100), nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    image_product = db.Column(db.String(20), nullable=False, default='default.jpg')
    category_id = db.Column(db.Integer, db.ForeignKey('category.category_id'), nullable=False)

    category = db.relationship('Category', backref='is', lazy=True)
    
    def __repr__(self):
        return f"Products('product_id(PK): {self.product_id}, category_id(FK): {self.category_id}, product_name: {self.product_name}, product_description: {self.product_description}, unit_price: {self.unit_price}')"