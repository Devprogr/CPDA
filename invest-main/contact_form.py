from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email, Length

class ContactForm(FlaskForm):
    name = StringField(
        'Full Name',
        validators=[DataRequired(), Length(min=2, max=100)],
        render_kw={"placeholder": "Your Name"}
    )

    email = StringField(
        'Email',
        validators=[DataRequired(), Email()],
        render_kw={"placeholder": "Your Email"}
    )

    message = TextAreaField(
        'How can we help you?',
        validators=[DataRequired(), Length(min=10)],
        render_kw={"placeholder": "Your Message", "rows": 5}
    )

    submit = SubmitField('Send Message')