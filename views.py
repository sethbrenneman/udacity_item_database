from flask import Flask, g, render_template, request, redirect, url_for, jsonify, flash
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from models import User, Movie, Category, pragma_fk_conn
import string, random

from oauth2client.client import flow_from_clientsecrets, FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web']['client_id']

app = Flask(__name__)
engine = create_engine("sqlite:///items.db")
event.listen(engine, "connect", pragma_fk_conn)
session = sessionmaker(bind=engine)()

@app.route('/')
@app.route('/catalog')
@app.route('/catalog/')
def render_catalog():
  categories = session.query(Category).order_by(Category.name).all()
  movies = session.query(Movie).join(Category).order_by(Category.name).all()
  return render_template('catalog.html', categories=categories, movies=movies)

@app.route('/catalog/<string:category>')
@app.route('/catalog/<string:category>/')
def render_category(category):
  category = session.query(Category).filter(Category.name == category).one()
  movies = session.query(Movie).filter(Movie.category_id == category.id).all()
  return render_template('category.html', category=category, movies=movies)


@app.route('/catalog/<string:category>/<int:movie_id>')
@app.route('/catalog/<string:category>/<int:movie_id>/')
def render_movie(category, movie_id):
  movie = session.query(Movie).filter(Movie.id == movie_id).one()
  return render_template('movie.html', movie=movie)

@app.route('/catalog.json')
def catalog_json():
  movies = session.query(Movie).all()
  return jsonify(Movies = [m.serialize for m in movies])

@app.route('/login')
def login():
  state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
  g['state'] = state
  return render_template('login.html', state=state)

@app.route('/logout')
def logout():
  return "LOGOUT"

@app.route('/gconnect', methods=['POST'])
def gconnect():
  if request.args.get('state') != g['state']:
    return response('Invalid state parameter', 401)

  code = request.data
  try:
    oauth_flow = flow_from_clientsecrets('client_secrets.json', scope = '')
    oauth_flow.redirect_uri = 'postmessage'
    credentials = oauth_flow.step2_exchange(code)
  except FlowExchangeError:
    return response('Failed to upgrade the authorization code.', 401)

  access_token = credentials.access_token
  url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' % access_token)
  h = httplib2.Http()
  result = json.loads(h.request(url, 'GET')[1])
  if result.get('error') is not None:
    return response(result.get('error'), 500)
  gplus_id = credentials.id_token['sub']
  if result['user_id'] != gplus_id:
    return response('Token\'s user ID doesn\'nt match the given user id', 401)
  if result['issued_to'] != CLIENT_ID:
    return response("Token's client ID does not match app's", 401)
  stored_credentials = g.get('credentials', None)
  stored_gplus_id = g.get('gplus_id', None)
  if stored_credentials is not None and gplus_id == stored_gplus_id:
    return response('Current user is already connected', 200)

  g['provider'] == 'google'
  g['credentials'] = credentials
  g['gplus_id'] = gplus_id

  userinfo_url = 'https://www.googleapis.com/oauth2/v1/userinfo'
  params = {'access_token': credentials.access_token, 'alt': 'json'}
  answer = requests.get(userinfo_url, params=params)

  data = answer.json()

  g['username'] = data['name']
  g['email'] = data['email']

  user_id = getUserId(g['email'])
  if user_id:
    g['user_id'] = user_id
  else:
    g['user_id'] = createUser(g)

  output = ''
  output += '<h1>Welcome, ' + g['username'] + '!</h1'
  flash("You are now logged in as %s" % login_session['username'])
  return output

@app.route('/gdisconnect')
def gdisconnect():
  # access_token = login_session.get('access_token')
  # if access_token is None:
  #   response = make_response(json.dumps('Current user is not connected'), 401)
  #   response.headers['Content-Type'] = 'application/json'
  #   return response
  # url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
  # h = httplib2.Http()
  # result = h.request(url, 'GET')[0]

  credentials = g.get('credentials', None)
  if credentials is None:
    return response('Current user is not connected', 401)
  access_token = credentials.access_token
  url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
  h = httplib2.Http()
  result = h.request(url, 'GET')[0]
  print('XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX')
  print(result)

  if result['status'] == '200':
    del g['credentials']
    del g['gplus_id']
    del g['username']
    del g['email']
    del g['user_id']

    flash('Successfully disconnected!')
    return redirect('/')

def createUser(g):
  newUser = User(name=g['username'], email=g['email'])
  session.add(newUser)
  session.commit()
  return session.query(User).filter(User.email == login_session['email']).one().id

def getUserInfo(user_id):
  user = session.query(User).filter(User.id == user_id).one()
  return user

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