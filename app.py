import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, Email, ValidationError
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key-12345'

# Завдання 3: URI підключення SQLite
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'flask_shop.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Завдання 3: Проміжна таблиця для зв'язку багато-до-багатьох
product_tags = db.Table('product_tags',
    db.Column('product_id', db.Integer, db.ForeignKey('product.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True)
)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    products = db.relationship('Product', backref='category', lazy=True)

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)
    in_stock = db.Column(db.Boolean, default=True)
    rating = db.Column(db.Float, default=5.0)  # Поле для ревізії міграції
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    tags = db.relationship('Tag', secondary=product_tags, backref=db.backref('products', lazy='dynamic'))

class ProductDetail(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), unique=True, nullable=False)
    warranty_months = db.Column(db.Integer, default=12)
    manufacturer_country = db.Column(db.String(100))

# Форма зворотного зв'язку
class FeedbackForm(FlaskForm):
    name = StringField('ПІБ користувача', validators=[DataRequired(), Length(min=2, max=50)])
    email = StringField('Електронна пошта', validators=[DataRequired(), Email()])
    category = SelectField('Категорія звернення', choices=[('general', 'Загальне'), ('order', 'Замовлення'), ('tech', 'Підтримка')])
    message = TextAreaField('Повідомлення', validators=[DataRequired(), Length(min=10)])
    submit = SubmitField('Надіслати')

    def validate_message(self, field):
        if len(field.data.strip().split()) < 3:
            raise ValidationError("Повідомлення повинно містити щонайменше 3 слова.")

@app.route('/')
def index():
    return render_template('index.html', title="Головна", site_name="TechStore Flask", year=datetime.now().year)

@app.route('/catalog')
def catalog():
    items = Product.query.all()
    return render_template('catalog.html', title="Каталог товарів", items=items, year=datetime.now().year)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    form = FeedbackForm()
    if form.validate_on_submit():
        flash("Ваше повідомлення успішно надіслано!", "success")
        return redirect(url_for('contact'))
    return render_template('contact.html', title="Зворотний зв'язок", form=form, year=datetime.now().year)

# Завдання 4: Сценарій транзакційної атомарності (commit / rollback)
@app.route('/test-transaction')
def test_transaction():
    try:
        cat = Category(name="Електроніка", slug="electronics")
        db.session.add(cat)
        db.session.flush()

        prod1 = Product(name="Планшет 10", price=8500.0, category_id=cat.id)
        prod2 = Product(name="Смартфон X", price=-100.0, category_id=cat.id) # Помилка логіки
        
        if prod2.price < 0:
            raise ValueError("Ціна не може бути від'ємною!")

        db.session.add_all([prod1, prod2])
        db.session.commit()
        return "Транзакція виконана"
    except Exception as e:
        db.session.rollback()
        return f"Транзакцію скасовано (Rollback): {e}"

if __name__ == '__main__':
    app.run(debug=True)