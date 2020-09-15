from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.widgets import PasswordInput
from wtforms.validators import InputRequired, Email, Length, DataRequired
from flask_ckeditor import CKEditorField


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Length(max=30)])
    password = StringField('Password', validators=[InputRequired()], widget=PasswordInput(hide_value=False))
    submit = SubmitField('Login')

class AdminForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=30)])
    title = SelectField('Title',
                        validators=[DataRequired()],
                        choices=[('', 'Select title'), ('Mrs', 'Mrs'),
                                 ('Miss', 'Miss'),
                                 ('Ms', 'Ms'),
                                 ('Mr', 'Mr'),
                                 ('Dr.', 'Dr.'),
                                 ('Prof.', 'Prof.')])
    name = StringField('First Name', validators=[InputRequired()])
    surname = StringField('Last Name', validators=[InputRequired()])
    password = StringField('Password', widget=PasswordInput(hide_value=False))
    # here we need a DropDown field for school
    # coerce this property is saying that the select value will be string type
    school = SelectField('School', coerce=str, validators=[DataRequired()], id='school')
    school_name = StringField('School Name')
    submit = SubmitField('Register')