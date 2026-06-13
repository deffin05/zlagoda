from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, IntegerField, SelectField, BooleanField, DecimalField
from wtforms.validators import DataRequired, Length, Optional, NumberRange


class CategoryForm(FlaskForm):
    name = StringField('Назва', validators=[DataRequired(), Length(1, 50)])
    submit = SubmitField('Зберегти')


class ProductForm(FlaskForm):
    id_product = IntegerField("ID (необов'язково)", validators=[Optional()])
    category_number = SelectField('Категорія', coerce=int, validators=[DataRequired()])
    producer_name = StringField('Виробник', validators=[DataRequired(), Length(1, 50)])
    product_name = StringField('Назва', validators=[DataRequired(), Length(1, 50)])
    characteristics = TextAreaField('Характеристики', validators=[DataRequired(), Length(1, 100)])
    submit = SubmitField('Зберегти')


class StoreProductForm(FlaskForm):
    UPC = StringField('UPC', validators=[DataRequired(), Length(min=12, max=12)])
    id_product = SelectField('Продукт', coerce=int, validators=[DataRequired()])
    selling_price = DecimalField('Ціна', validators=[DataRequired(), NumberRange(min=0)])
    products_number = IntegerField('Кількість', validators=[DataRequired(), NumberRange(min=0)])
    promotional_product = BooleanField('Акційний товар?')
    UPC_prom = SelectField("UPC акційного товару (необов'язково)", coerce=str, validators=[Optional(),
                                                                                           Length(min=12, max=12)])
    submit = SubmitField('Зберегти')
