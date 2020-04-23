from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from bookhub.models import User, Book, Review
from flask_login import current_user


class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')
    # Vaidation of duplicate registeration
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')
    # validate email address 
    def validate_email(self, email):
        email = User.query.filter_by(email=email.data).first()
        if email:
            raise ValidationError('That email is taken. Please choose a different one.')


class LoginForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class UpdateAccountForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Update')


    # Vaidation of duplicate registeration

    def validate_username(self, username):
        currentuser = current_user.username
        user = User.query.filter_by(username=username.data).first()
        if user and currentuser:
            raise ValidationError('That username is taken. Please choose a different one.')
    # validate email address 
    def validate_email(self, email):
        currentemail = current_user.email
        email = User.query.filter_by(email=email.data).first()
        if email and currentemail:
            raise ValidationError('That email is taken. Please choose a different one.')

class SearchForm(FlaskForm):
    searchby = SelectField(u'Search by:', choices=[('title', 'Book Title'), ('author', 'Book Author'), 
                                                    ('isbn', 'Book ISBN'), ('year', 'Publication Year')],)
    searchword = StringField(validators=[DataRequired()], render_kw={"placeholder": "Enter search word here"})
    submit = SubmitField('Search')

class ReviewForm(FlaskForm):
    # review_title =  StringField(u'Search by:', validators=[DataRequired()], render_kw={"placeholder": "Title of review"})
    book_rate =  SelectField(u'Select a rate:',default='', choices=[('XX', 'Pick a rate'), ('0', 0), ('1', 1), 
                                                    ('2', 2), ('3', 3),
                                                    ('4', 4), ('5', 5)],
                                                    )
    book_review = TextAreaField(('Write a review'),[DataRequired()], render_kw={"placeholder": "Write your review"})
    submit = SubmitField('Submit')


    