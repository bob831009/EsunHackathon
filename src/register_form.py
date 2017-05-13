from flask_wtf import FlaskForm
from wtforms import TextField, IntegerField, SubmitField, validators
from wtforms.validators import Required

class RegisterForm(FlaskForm):
	username = TextField('Username', validators=[Required()])
	password = TextField('Password', validators=[Required()])
	email = TextField('Email', validators=[Required()])
	customer_id = IntegerField('customer idx', validators=[Required()])
	submit_button = SubmitField('Submit Form')