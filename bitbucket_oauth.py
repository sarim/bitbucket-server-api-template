import oauth2 as oauth
import urlparse
import os
from flask import Flask, request, flash, redirect, url_for, session
from flask_session import Session
from signature import SignatureMethod_RSA_SHA1
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
SESSION_TYPE = 'filesystem'
app.config.from_object(__name__)
Session(app)

consumer_key = os.getenv('CONSUMER_KEY')
consumer_secret = os.getenv('CONSUMER_SECRET')

base_url =  os.getenv("BASE_URL")
request_token_url = base_url + '/plugins/servlet/oauth/request-token'
access_token_url = base_url + '/plugins/servlet/oauth/access-token'
authorize_url = base_url + '/plugins/servlet/oauth/authorize'

user_data_url = base_url + '/rest/api/1.0/users/%s'
get_user_url = base_url + '/plugins/servlet/applinks/whoami'

consumer = oauth.Consumer(consumer_key, consumer_secret)

@app.route('/')
def index():
    session.clear()
    return '<a href="/link">link</a>'

@app.route('/dostuff')
def dostuff():
    access_token = session['access_token']
    accessToken = oauth.Token(access_token['oauth_token'], access_token['oauth_token_secret'])

    client = oauth.Client(consumer, accessToken)
    client.set_signature_method(SignatureMethod_RSA_SHA1())

    resp, content = client.request(get_user_url, "GET")
    if resp['status'] != '200':
        raise Exception("Should have access!")
    
    username = content.strip()

    resp, content = client.request(user_data_url % (username), "GET")
    if resp['status'] != '200':
        raise Exception("Should have access!")
    
    response = app.response_class(
        response=content,
        status=200,
        mimetype='application/json'
    )
    return response


@app.route('/callback')
def callback():

    request_token = session['request_token']

    token = oauth.Token(request_token['oauth_token'],
            request_token['oauth_token_secret'])

    client = oauth.Client(consumer, token)
    client.set_signature_method(SignatureMethod_RSA_SHA1())

    resp, content = client.request(access_token_url, "POST")
    if resp['status'] != '200':
        raise Exception("User denied access")

    access_token = dict(urlparse.parse_qsl(content))

    session['access_token'] = access_token

    return redirect(url_for("dostuff"))

@app.route('/link')
def link():

    client = oauth.Client(consumer)
    client.set_signature_method(SignatureMethod_RSA_SHA1())

    resp, content = client.request(request_token_url, "POST")
    if resp['status'] != '200':
        raise Exception("Invalid response %s: %s" % (resp['status'],  content))

    request_token = dict(urlparse.parse_qsl(content))

    session['request_token'] = request_token

    return redirect("%s?oauth_token=%s&oauth_callback=%s" % (authorize_url, request_token['oauth_token'], url_for("callback", _external=True)))

app.run(debug=True, host='0.0.0.0', port=8000)