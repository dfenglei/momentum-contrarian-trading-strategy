#coding: utf-8
from flask_wtf import Form
from wtforms import TextField
from wtforms import StringField, PasswordField, BooleanField, SelectField,SubmitField
from wtforms.validators import DataRequired, Length,Required, Regexp
import sys

#reload(sys)
#sys.setdefaultencoding('utf8')


class IndexAnalyzer(Form):
    #index_analyze = TextField(
    #    'Analyze', validators=[DataRequired(), Length(min=2)])
    indextype = SelectField('指数类型',validators=[Required()] ,  choices=[('0', '沪深300'),('1', '中证500'),('2', '中证800')] )
    frequencytime = StringField('观察动量/反转效应时间长度', validators=[
        Required(), Length(1, 64), Regexp('^[0-9]*$', 0,
                                          'frequencytime must be '
                                          'numbers')])
    submit = SubmitField('分析')
