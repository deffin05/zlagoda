from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, IntegerField, SelectField
from wtforms.validators import DataRequired, Length, Optional


class CategoryForm(FlaskForm):
    name = StringField('Category Name', validators=[DataRequired(), Length(1, 50)])
    submit = SubmitField('Submit')


class ProductForm(FlaskForm):
    id_product = IntegerField("ID (необов'язково)", validators=[Optional()])
    category_number = SelectField('Категорія', coerce=int, validators=[DataRequired()])
    producer_name = StringField('Виробник', validators=[DataRequired(), Length(1, 50)])
    product_name = StringField('Назва', validators=[DataRequired(), Length(1, 50)])
    characteristics = TextAreaField('Характеристики', validators=[DataRequired(), Length(1, 100)])
    submit = SubmitField('Надіслати')
