from flask_wtf import FlaskForm
from wtforms import TextField, IntegerField, SubmitField, BooleanField, validators
from wtforms.fields import Label
from wtforms.validators import Required

class RegisterForm(FlaskForm):
	username = TextField('Username', validators=[Required()])
	password = TextField('Password', validators=[Required()])
	email = TextField('Email', validators=[Required()])
	customer_id = IntegerField('customer idx', validators=[Required()])
	# radio_field = RadioField('This is a radio field', choices=[
	# 	('like_button', 'like'),
	# 	('dislike_button', 'dislike')
	# ])
	# checkbox_field = BooleanField('This is a checkbox', default=False, description='Checkboxes can be tricky.')
	submit_button = SubmitField('Submit Form')

class LoginForm(FlaskForm):
	username = TextField('Username', validators=[Required()])
	password = TextField('Password', validators=[Required()])
	submit_button = SubmitField('Submit Form')

class ProductForm(FlaskForm):
	label = Label('testing', 'hellolllll')
	like_button = BooleanField('like', default=False)