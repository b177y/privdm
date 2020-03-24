from flask import render_template, request, redirect, session, url_for, flash
from app import app
from app.forms import ConfigForm, LoginForm, NicknameForm, AddNickname
from instagram_private_api import Client, ClientCompatPatch
from .dmapi.utils import encrypt
from .dmapi.manage import create_user, get_userdata, delete_nickname, update_nickname

@app.route('/', methods=['POST', 'GET'])
def login():
    form = LoginForm()
    error=False
    if form.validate_on_submit():
        uname = form.username.data
        pw = form.password.data
        try:
            api = Client(uname, pw)
            session['username'] = uname
            session['ig_settings'] = api.settings
            session['user_id'] = api.authenticated_user_id
            create_user(uname, session['user_id'], settings=session['ig_settings'])
            print("successfully logged in for user", uname)
            return redirect(url_for('settings'))
        except:
            session.pop('username', None)
            session.pop('password', None)
            print("Couldn't log in")
            error = True
    return render_template('login.html', form=form, error=error)

@app.route('/settings', methods=['POST', 'GET'])
def settings():
    if request.method == 'POST':
        if 'delete' in request.form:
            print("Deleting nickname", request.form['nickname'])
            delete_nickname(session['user_id'], request.form['nickname'])
            return redirect(url_for('settings'))
        elif 'update' in request.form:
            print("Updating nickname", request.form['nickname'])
            update_nickname(session['user_id'], request.form['nickname'], request.form['username'])
            return redirect(url_for('settings'))
    userdata = get_userdata(session['user_id'])
    cform = ConfigForm()
    anform = AddNickname()
    nn_forms = []
    for n in userdata['nicknames']:
        nform = NicknameForm()
        nform.load(n, userdata['nicknames'][n])
        nn_forms.append(nform)
    if cform.validate_on_submit() and 'submit' in request.form:
        create_user(session['username'], session['user_id'], cform.botname.data, active=cform.active.data, settings=session['ig_settings']) 
        print("Updated user settings - botname {0}, active {1}".format(cform.botname.data, cform.active.data))
        return redirect(url_for('settings'))
    if anform.validate_on_submit() and 'add' in request.form:
        update_nickname(session['user_id'], anform.anickname.data, anform.ausername.data)
        return redirect(url_for('settings'))
    cform.load(userdata)
    return render_template('settings.html', cform=cform, nn_forms=nn_forms, anform=anform, username=session['username'])
