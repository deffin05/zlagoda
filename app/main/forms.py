from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, IntegerField, SelectField, BooleanField, DecimalField, \
    DateField
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


class EmployeeForm(FlaskForm):
    id_employee = StringField("ID", validators=[DataRequired(), Length(1, 10)])

    empl_surname = StringField("Прізвище", validators=[DataRequired(), Length(1, 50)])
    empl_name = StringField("Ім'я", validators=[DataRequired(), Length(1, 50)])
    empl_patronymic = StringField("По батькові", validators=[Optional(), Length(1, 50)])

    empl_role = SelectField("Посада", validators=[DataRequired()], choices=[
        ("Менеджер", "Менеджер"),
        ("Касир", "Касир")
    ])
    salary = DecimalField('Зарплата', validators=[DataRequired(), NumberRange(min=0)])

    date_of_birth = DateField("Дата народження", validators=[DataRequired()])
    date_of_start = DateField("Дата початку роботи", validators=[DataRequired()])

    phone_number = StringField("Номер телефону", validators=[DataRequired(), Length(1, 13)])

    city = StringField("Місто", validators=[DataRequired(), Length(1, 50)])
    street = StringField("Вулиця", validators=[DataRequired(), Length(1, 50)])
    zip_code = StringField("Індекс", validators=[DataRequired(), Length(1, 9)])

    submit = SubmitField('Зберегти')


class CustomerForm(FlaskForm):
    card_number = StringField("Номер карти", validators=[DataRequired(), Length(1, 13)])

    cust_surname = StringField("Прізвище", validators=[DataRequired(), Length(1, 50)])
    cust_name = StringField("Ім'я", validators=[DataRequired(), Length(1, 50)])
    cust_patronymic = StringField("По батькові", validators=[Optional(), Length(1, 50)])

    phone_number = StringField("Номер телефону", validators=[DataRequired(), Length(1, 13)])

    city = StringField("Місто (необов'язково)", validators=[Optional(), Length(1, 50)])
    street = StringField("Вулиця (необов'язково)", validators=[Optional(), Length(1, 50)])
    zip_code = StringField("Індекс (необов'язково)", validators=[Optional(), Length(1, 9)])

    percent = IntegerField("Знижка", validators=[Optional(), NumberRange(min=0, max=100)])

    submit = SubmitField('Зберегти')
