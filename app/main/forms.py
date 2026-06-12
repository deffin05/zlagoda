from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length


class CategoryForm(FlaskForm):
    name = StringField('Category Name', validators=[DataRequired(), Length(1, 50)])
    submit = SubmitField('Submit')
