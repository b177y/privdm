from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, PasswordField, SubmitField, IntegerField, SelectField, validators

class LoginForm(FlaskForm):
    username = StringField('Instagram Username:', [validators.DataRequired()])
    password = PasswordField('Instagram Password:', [validators.DataRequired()])
    submit = SubmitField('Login')

class ConfigForm(FlaskForm):
    active = BooleanField('Active')
    botname = StringField('Bot username')
    submit = SubmitField('Save')
    def load(self, userdata):
        self.active.default = "checked" if userdata['active'] == True else ''
        self.botname.default = userdata['botname']
        self.process()

class NicknameForm(FlaskForm):
    nickname = StringField('nickname', [validators.DataRequired()])
    username = StringField('username', [validators.DataRequired()])
    update = SubmitField('Save')
    delete = SubmitField('Delete')
    def load(self, nn, un):
        self.nn = nn
        self.nickname.default = nn
        self.username.default = un
        self.process()

class AddNickname(FlaskForm):
    anickname = StringField('nickname', [validators.DataRequired()])
    ausername = StringField('username', [validators.DataRequired()])
    add = SubmitField('Add')
