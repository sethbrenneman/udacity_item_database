from flask import Flask, g, render_template, request, redirect
from flask import url_for, jsonify, flash
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from models import User, Movie, Category, pragma_fk_conn
import string
import random

from flask import session as login_session

from oauth2client.client import flow_from_clientsecrets, FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())[
    'web']['client_id']

app = Flask(__name__)
app.secret_key = 'item_database_project'
engine = create_engine("sqlite:///items.db")
event.listen(engine, "connect", pragma_fk_conn)
session = sessionmaker(bind=engine)()


@app.route('/')
@app.route('/catalog')
@app.route('/catalog/')
def render_catalog():
    categories = session.query(Category).order_by(Category.name).all()
    movies = session.query(Movie).join(Category).order_by(Category.name).all()
    return render_template('catalog.html',
                           categories=categories, movies=movies)


@app.route('/catalog/<string:category>')
@app.route('/catalog/<string:category>/')
def render_category(category):
    category = session.query(Category).filter(Category.name == category).one()
    movies = session.query(Movie).filter(
        Movie.category_id == category.id).all()
    return render_template('category.html', category=category, movies=movies)


@app.route('/catalog/<string:category>/<int:movie_id>')
@app.route('/catalog/<string:category>/<int:movie_id>/')
def render_movie(category, movie_id):
    movie = session.query(Movie).filter(Movie.id == movie_id).one()
    if login_session.get('user_id') == movie.user_id:
        return render_template('movie.html', movie=movie, owner=True)
    else:
        return render_template('movie.html', movie=movie)


@app.route('/catalog.json')
def catalog_json():
    movies = session.query(Movie).all()
    return jsonify(Movies=[m.serialize for m in movies])


@app.route('/catalog/<string:category>/<int:movie_id>.json')
def movie_json(category, movie_id):
    try:
        movie = session.query(Movie).filter(Movie.id == movie_id).one()
    except:
        flash("Invalid movie id number")
        return redirect(url_for('render_catalog'))
    return jsonify(movie.serialize)


@app.route('/newmovie', methods=['GET', 'POST'])
@app.route('/newmovie/', methods=['GET', 'POST'])
def new_movie():
    if request.method == 'GET':
        if 'username' in login_session:
            return render_template('newmovie.html')
        else:
            flash('You must be logged in to add a movie')
            return redirect(url_for('render_catalog'))
    else:
        if 'username' in login_session:
            name = request.form['name']
            description = request.form['description']
            if not name or not description:
                flash('You must include both a name and description')
                return redirect(url_for('new_movie'))
            category_id = session.query(Category).filter(
                Category.name == request.form['category']).one().id
            new_movie = Movie(name=name, description=description,
                              category_id=category_id,
                              user_id=login_session['user_id'])
            session.add(new_movie)
            session.commit()
            flash('New movie ' + new_movie.name + ' created!')
            return redirect(url_for('render_catalog'))
        else:
            flash('You must be logged in to add a movie')
            return redirect(url_for('render_catalog'))


@app.route('/catalog/<string:category>/<int:movie_id>/edit',
           methods=['GET', 'POST'])
@app.route('/catalog/<string:category>/<int:movie_id>/edit/',
           methods=['GET', 'POST'])
def edit_movie(category, movie_id):
    if request.method == 'GET':
        try:
            movie = session.query(Movie).filter(Movie.id == movie_id).one()
        except:
            flash("Invalid movie ID")
            return redirect(url_for('render_catalog'))
        if login_session.get('user_id') == movie.user_id:
            return render_template('editmovie.html', movie=movie)
        else:
            flash("You must be logged in as owner of " + movie.name +
                  " to edit")
            return redirect(url_for('render_catalog'))
    else:
        try:
            movie = session.query(Movie).filter(Movie.id == movie_id).one()
        except:
            flash("Invalid movie ID")
            return redirect(url_for('render_catalog'))
        if request.form['submit'] == 'cancel':
            flash('Edit of ' + movie.name + ' cancelled')
            return redirect(url_for('render_catalog'))
        if login_session.get('user_id') == movie.user_id:
            if not request.form['name'] or not request.form['description']:
                flash('You must include both a name and description')
                return redirect(url_for('edit_movie', category=category,
                                movie_id=movie_id))
            movie.name = request.form['name']
            movie.description = request.form['description']
            movie.category_id = session.query(Category).filter(
                Category.name == request.form['category']).one().id
            session.commit()
            flash('Movie ' + movie.name + ' has been successfully edited!')
            return redirect(url_for('render_catalog'))
        else:
            flash("You must be logged in as owner of " + movie.name +
                  " to edit")
            return redirect(url_for('render_catalog'))


@app.route('/catalog/<string:category>/<int:movie_id>/delete',
           methods=['GET', 'POST'])
@app.route('/catalog/<string:category>/<int:movie_id>/delete/',
           methods=['GET', 'POST'])
def delete_movie(category, movie_id):
    try:
        movie = session.query(Movie).filter(Movie.id == movie_id).one()
    except:
        flash("Invalid movie ID")
        return redirect(url_for('render_catalog'))
    if request.method == 'GET':
        if login_session.get('user_id') == movie.user_id:
            return render_template('deletemovie.html', movie=movie)
        else:
            flash('You must be logged in as owner of ' + movie.name +
                  'to delete')
            return redirect(url_for('render_catalog'))
    else:
        if request.form['submit'] == 'cancel':
            flash('Deletion of ' + movie.name + ' cancelled')
            return redirect(url_for('render_catalog'))
        if login_session.get('user_id') == movie.user_id:
            session.delete(movie)
            session.commit()
            flash(movie.name + ' deleted')
            return redirect(url_for('render_catalog'))
        else:
            flash('You must be logged in as owner of ' + movie.name +
                  'to delete')
            return redirect(url_for('render_catalog'))


@app.route('/login')
def login():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', state=state)


@app.route('/logout')
def logout():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
        flash('You have been successfully logged out.')
        return redirect(url_for('render_catalog'))

    else:
        flash('You were not logged in to begin with!')
        return redirect(url_for('render_catalog'))


@app.route('/gdisconnect')
def gdisconnect():
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(json.dumps(
            'Current user is not connected'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    access_token = credentials.access_token
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        del login_session['credentials']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['user_id']

        flash('Successfully disconnected!')
        return redirect(url_for('render_catalog'))

    else:
        response = make_response(json.dumps(
            'Failed to revoke token for given user'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/gconnect', methods=['POST'])
def gconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    code = request.data
    try:
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(json.dumps(
            'Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' %
           access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(json.dumps(
            'Token\'s user ID doesn\'nt match the given user id'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    if result['issued_to'] != CLIENT_ID:
        response = make_response(json.dumps(
            "Token's client ID does not match app's"), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps(
            'Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'

    login_session['provider'] = 'google'
    login_session['credentials'] = credentials
    login_session['gplus_id'] = gplus_id

    userinfo_url = 'https://www.googleapis.com/oauth2/v1/userinfo'
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['email'] = data['email']


    user_id = getUserId(login_session['email'])

    if user_id:
        login_session['user_id'] = user_id
    else:
        login_session['user_id'] = createUser(login_session)

    output = ''
    output += '<h1>Welcome, ' + login_session['username'] + '!</h1'
    flash("You are now logged in as %s" % login_session['username'])
    return output


def createUser(login_session):
    newUser = User(name=login_session['username'],
                   email=login_session['email'])
    session.add(newUser)
    session.commit()
    return session.query(User).filter(User.email ==
                                      login_session['email']).one().id


def getUserInfo(user_id):
    if user_id:
        user = session.query(User).filter(User.id == user_id).one()
        return user
    return None


def getUserId(user_email):
    try:
        uid = session.query(User).filter(User.email == user_email).one().id
        return uid
    except:
        return None


def response(msg, code):
    response = make_response(json.dumps(msg), code)
    response.headers['Content-Type'] = 'application/json'
    return response


if __name__ == '__main__':
    app.debug = True
    print getattr(app, "debug", "NONE")
    app.run(host='0.0.0.0', port=8000)
