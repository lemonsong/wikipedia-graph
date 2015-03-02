__author__ = 'Julian'

from flask.ext.wtf import Form
from wtforms import StringField
from wtforms.validators import DataRequired


class SearchForm(Form):
    """Form for entering Wikipedia search terms."""
    search_term = StringField('Wikipedia Entry', [DataRequired()])