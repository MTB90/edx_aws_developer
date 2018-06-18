"""
Copyright 2017 Amazon.com, Inc. or its affiliates. All Rights Reserved.
Licensed under the Apache License, Version 2.0 (the "License").
You may not use this file except in compliance with the License.
A copy of the License is located at

https://aws.amazon.com/apache-2-0/
or in the "license" file accompanying this file.
This file is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing
permissions and limitations under the License.
"""

import sys
from datetime import datetime

import requests
import boto3
import flask_login

from requests.auth import HTTPBasicAuth
from wtforms import TextAreaField
from flask import Flask, session
from flask import redirect, request, url_for, render_template
from flask_wtf import FlaskForm

from flask_wtf.file import FileField, FileRequired
from aws_xray_sdk.core import xray_recorder, patch_all
from aws_xray_sdk.ext.flask.middleware import XRayMiddleware
from jose import jwt

import config
import util
import database

application = Flask(__name__)
application.secret_key = config.FLASK_SECRET
login_manager = flask_login.LoginManager()
login_manager.init_app(application)


# load and cache cognito JSON Web Key (JWK)
# https://docs.aws.amazon.com/cognito/latest/developerguide/amazon-cognito-user-pools-using-tokens-with-identity-providers.html
JWKS_URL = ("https://cognito-idp.%s.amazonaws.com/%s/.well-known/jwks.json"
            % (config.AWS_REGION, config.COGNITO_POOL_ID))
JWKS = requests.get(JWKS_URL).json()["keys"]

# x-ray set up
plugins = ('EC2Plugin',)
xray_recorder.configure(service='MyApplication', plugins=plugins)
XRayMiddleware(application, xray_recorder)
patch_all()


# FlaskForm set up
class PhotoForm(FlaskForm):
    """flask_wtf form class the file upload"""
    photo = FileField('image', validators=[
        FileRequired()
    ])
    description = TextAreaField(u'Image Description')


class User(flask_login.UserMixin):
    """Standard flask_login UserMixin"""
    pass


@login_manager.user_loader
def user_loader(session_token):
    """Populate user object, check expiry"""
    if "expires" not in session:
        return None

    expires = datetime.utcfromtimestamp(session['expires'])
    expires_seconds = (expires - datetime.utcnow()).total_seconds()
    if expires_seconds < 0:
        return None

    user = User()
    user.id = session_token
    user.nickname = session['nickname']
    return user


@application.route("/")
def index():
    """Homepage route"""
    return render_template("index.html")


@application.route("/myphotos", methods=('GET', 'POST'))
@flask_login.login_required
def myphotos():
    "login required my photos route"
    all_labels = ["No labels yet"]

    #####
    # rds exercise get list of images from database
    # now we have a user id from cognito
    #####
    s3_client = boto3.client('s3')
    photos = database.list_photos(flask_login.current_user.id)
    for photo in photos:
        photo["signed_url"] = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': config.PHOTOS_BUCKET, 'Key': photo["object_key"]}
        )

    form = PhotoForm()
    url = None
    if form.validate_on_submit():
        image_bytes = util.resize_image(form.photo.data, (300, 300))
        if image_bytes:
            #######
            # s3 excercise - save the file to a bucket
            #######
            prefix = "photos/"
            key = prefix + util.random_hex_bytes(8) + '.png'
            s3_client.put_object(
                Bucket=config.PHOTOS_BUCKET,
                Key=key,
                Body=image_bytes,
                ContentType='image/png'
            )
            # http://boto3.readthedocs.io/en/latest/guide/s3.html#generating-presigned-urls
            url = s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': config.PHOTOS_BUCKET, 'Key': key})

            #######
            # rekcognition exercise - this code has moved to lambda
            #######
            all_labels = ["Processing labels asyncronously"]

            #######
            # rds excercise
            # added user id and description to the database
            #######
            labels_comma_separated = ", ".join(all_labels)
            database.add_photo(key,
                               labels_comma_separated,
                               form.description.data,
                               flask_login.current_user.id)

            form.description.data = ''

    return render_template("myphotos.html",
                           form=form,
                           url=url,
                           photos=photos,
                           all_labels=all_labels)


@application.route("/myphotos/delete/<path:object_key>")
@flask_login.login_required
def myphotos_delete(object_key):
    "delete photo route"
    database.delete_photo(object_key, flask_login.current_user.id)
    return redirect(url_for("myphotos"))


@application.route("/info")
def info():
    """Webserver info route"""

    metadata = "http://169.254.169.254"
    instance_id = requests.get(
        metadata + "/latest/meta-data/instance-id").text

    availability_zone = requests.get(
        metadata + "/latest/meta-data/placement/availability-zone").text

    return render_template("info.html",
                           instance_id=instance_id,
                           availability_zone=availability_zone,
                           sys_version=sys.version)


@application.route("/login")
def login():
    """Login route"""
    # http://docs.aws.amazon.com/cognito/latest/developerguide/login-endpoint.html
    session['csrf_state'] = util.random_hex_bytes(8)
    cognito_login = ("https://%s/"
                     "login?response_type=code&client_id=%s"
                     "&state=%s"
                     "&redirect_uri=%s/callback" %
                     (config.COGNITO_DOMAIN,
                      config.COGNITO_CLIENT_ID,
                      session['csrf_state'],
                      config.BASE_URL))
    return redirect(cognito_login)


@application.route("/logout")
def logout():
    """Logout route"""
    # http://docs.aws.amazon.com/cognito/latest/developerguide/logout-endpoint.html
    flask_login.logout_user()
    cognito_logout = ("https://%s/"
                      "logout?response_type=code&client_id=%s"
                      "&logout_uri=%s/" % (config.COGNITO_DOMAIN,
                                           config.COGNITO_CLIENT_ID,
                                           config.BASE_URL))

    return redirect(cognito_logout)


@application.route("/callback")
def callback():
    """Exchange the 'code' for Cognito tokens"""
    # http://docs.aws.amazon.com/cognito/latest/developerguide/token-endpoint.html
    csrf_state = request.args.get('state')
    code = request.args.get('code')
    request_parameters = {'grant_type': 'authorization_code',
                          'client_id': config.COGNITO_CLIENT_ID,
                          'code': code,
                          "redirect_uri": config.BASE_URL + "/callback"}
    response = requests.post("https://%s/oauth2/token" % config.COGNITO_DOMAIN,
                             data=request_parameters,
                             auth=HTTPBasicAuth(config.COGNITO_CLIENT_ID,
                                                config.COGNITO_CLIENT_SECRET))

    # the response:
    # http://docs.aws.amazon.com/cognito/latest/developerguide/amazon-cognito-user-pools-using-tokens-with-identity-providers.html
    is_csrf_state_ok = csrf_state == session['csrf_state']
    if response.status_code == requests.codes.ok and is_csrf_state_ok:
        verify(response.json()["access_token"])
        id_token = verify(response.json()["id_token"],
                          response.json()["access_token"])

        user = User()
        user.id = id_token["cognito:username"]
        session['nickname'] = id_token["nickname"]
        session['expires'] = id_token["exp"]
        session['refresh_token'] = response.json()["refresh_token"]
        flask_login.login_user(user, remember=True)
        return redirect(url_for("index"))

    return render_template("error.html")


@application.errorhandler(401)
def unauthorized(exception):
    """Unauthorized access route"""
    return render_template("unauthorized.html"), 401


def verify(token, access_token=None):
    """Verify a cognito JWT"""
    # get the key id from the header, locate it in the cognito keys
    # and verify the key
    header = jwt.get_unverified_header(token)
    key = [k for k in JWKS if k["kid"] == header['kid']][0]
    id_token = jwt.decode(token, key,
                          audience=config.COGNITO_CLIENT_ID,
                          access_token=access_token)
    return id_token


if __name__ == "__main__":
    # http://flask.pocoo.org/docs/0.12/errorhandling/#working-with-debuggers
    # https://docs.aws.amazon.com/cloud9/latest/user-guide/app-preview.html#app-preview-share
    use_c9_debugger = False
    application.run(use_debugger=not use_c9_debugger, debug=True,
                    use_reloader=not use_c9_debugger, host='0.0.0.0')
