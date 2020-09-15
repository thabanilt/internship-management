from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField,DateField
from wtforms.widgets import PasswordInput
from wtforms.validators import InputRequired, Length, DataRequired
from flask_ckeditor import CKEditorField


class StudentForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Length(max=30)])
    name = StringField('First Name', validators=[InputRequired()])
    regnumber=StringField('Reg Number', validators=[InputRequired()])
    surname = StringField('Last Name', validators=[InputRequired()])
    password = StringField('Password', widget=PasswordInput(hide_value=False))
    # here we need a DropDown field for school
    school = SelectField('School', coerce=str, validators=[DataRequired()], id='school')
    school_name = StringField('School Name')
    submit = SubmitField('Register')


class EditForm(FlaskForm):
    name = StringField('First Name', validators=[InputRequired()])
    surname = StringField('Last Name', validators=[InputRequired()])
    submit = SubmitField('Update')

class internForm(FlaskForm):
    title = StringField('Title', validators=[InputRequired()])
    description = CKEditorField('Body', validators=[DataRequired()])
    # submission_date = DateField('Submission Date', format='%m/%d/%Y', validators=[InputRequired()])
    submit = SubmitField('Submit')