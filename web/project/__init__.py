from os.path import join, isfile

from flask import Flask, render_template, make_response, jsonify, request, redirect, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from flask_uploads import UploadSet, IMAGES, configure_uploads
from flask_pagedown import PageDown
from flask_migrate import Migrate
from flask_httpauth import HTTPBasicAuth
from flask import jsonify
import markdown
import bleach
import pandas as pd

from sqlalchemy import and_, or_
from sqlalchemy import text


import time
from datetime import datetime, date, timedelta

app = Flask(__name__, instance_relative_config=True)
if isfile(join('instance', 'flask_full.cfg')):
    app.config.from_pyfile('flask_full.cfg')
else:
    app.config.from_pyfile('flask.cfg')

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
mail = Mail(app)
pagedown = PageDown(app)
migrate = Migrate(app, db)
auth = HTTPBasicAuth()
auth_token = HTTPBasicAuth()

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "users.login"

# Configure the image uploading via Flask-Uploads
images = UploadSet('images', IMAGES)
configure_uploads(app, images)


from project import db
from project.models import *
from project.utilities import get_age_string, get_duration_string, get_payout_string

import json
from contextlib import suppress
from steem.blockchain import Blockchain
from steem import Steem

steem = Steem(nodes=app.config['STEEM_NODES'])

def create_video_summary_fields(df, filter_data={}):

    if filter_data.get('filter_exclude_nsfw', 'false') == 'true':
        df = df[~(df['tags'].apply(lambda x: x.lower().find('nsfw') >= 0))]

    # temporary fix dlive thumbnails to https to prevent SSL warning
#    df = df[~(df['video_thumbnail_image_url']==None)]
    df['video_thumbnail_image_url'] = df['video_thumbnail_image_url'].apply(lambda x: x.replace('http://', 'https://') if x != None else '')

    df = df[~pd.isnull(df['created'])]
    df = df[~(df['video_id']=='c')] # remove erroneous records todo - remove once db refreshed
    df = df[~(df['video_id']=='user')] # remove erroneous records todo - remove once db refreshed
    df['duration_string'] = df['video_duration_seconds'].apply(get_duration_string)
    df['age_string'] = df['created'].apply(get_age_string)
    df['video_post_delay_days'] = df['video_post_publish_delay_seconds'] // (3600 * 24)

    df['payout_string'] = (df['pending_payout_value'] + df['total_payout_value']).apply(lambda x: get_payout_string(x))
    df['title_truncated'] = df['title'].apply(lambda x: x[:80])
    return df[['author', 'permlink', 'category', 'title', 'title_truncated', 'created', 'age_string', 'payout_string',
             'duration_string', 'video_type', 'video_id', 'video_thumbnail_image_url', 'video_post_delay_days',
             'trending_score', 'hot_score']]

# appends the query dict (from json filter data) to existing query
def apply_filter_to_query(original_query, filter_data):
    new_query = original_query
    if filter_data.get('filter_age_selection', 'all') == 'hour':
        new_query = new_query.filter(Post.created > (datetime.now() - timedelta(hours=1)))
    elif filter_data.get('filter_age_selection', 'all') == 'today':
        new_query = new_query.filter(Post.created > (datetime.now() - timedelta(hours=24)))
    elif filter_data.get('filter_age_selection', 'all') == 'week':
        new_query = new_query.filter(Post.created > (datetime.now() - timedelta(days=7)))
    elif filter_data.get('filter_age_selection', 'all') == 'month':
        new_query = new_query.filter(Post.created > (datetime.now() - timedelta(days=30)))
    if filter_data.get('filter_type_selection', 'all') == 'youtube':
        new_query = new_query.filter(Post.video_type == 'youtube')
    elif filter_data.get('filter_type_selection', 'all') == 'dtube':
        new_query = new_query.filter(Post.video_type == 'dtube')
    elif filter_data.get('filter_type_selection', 'all') == 'dlive':
        new_query = new_query.filter(Post.video_type == 'dlive')
    if filter_data.get('filter_duration_selection', 'all') == 'short':
        new_query = new_query.filter(Post.video_duration_seconds <= 240)
    elif filter_data.get('filter_duration_selection', 'all') == 'long':
        new_query = new_query.filter(Post.video_duration_seconds > 1200)
    if filter_data.get('filter_exclude_old_video', 'false') == 'true':
        new_query = new_query.filter(Post.video_post_publish_delay_seconds < (7*24*3600))
    return new_query

def apply_sort_to_query(original_query, filter_data):
    new_query = original_query
    sort_order = Post.pending_payout_value.desc()
    if filter_data.get('filter_sort_selection', 'all') == 'date':
        sort_order = Post.created.desc()
    elif filter_data.get('filter_sort_selection', 'all') == 'payout':
        sort_order = Post.pending_payout_value.desc()
    elif filter_data.get('filter_sort_selection', 'all') == 'trending':
        sort_order = Post.trending_score.desc()
    elif filter_data.get('filter_sort_selection', 'all') == 'hot':
        sort_order = Post.hot_score.desc()
    return new_query.order_by(sort_order)


# DEBUGGING PAGES #####################################################

@app.route('/f/api/' + app.config['DEBUGGING_KEY'] + '/raw/@<author>/<permlink>')
def raw(author, permlink):
    content = steem.get_content(author, permlink)
    return str(content)

# shows current replies
@app.route('/f/api/' + app.config['DEBUGGING_KEY'] + '/raw-replies/@<author>/<permlink>')
def raw_replies(author, permlink):
    replies = steem.get_content_replies(author, permlink)
    return str(replies)

@app.route('/f/api/' + app.config['DEBUGGING_KEY'] + '/status')
def status():
    html = 'Steem Blockchain Head Block: ' + str(steem.head_block_number) + '<br>'
    try:
        bn = db.session.query(Post).order_by(Post.id.desc()).first().block_number
    except:
        bn = 0
    html += 'Database Head Block: ' + str(bn) + '<br>'
    html += 'Approximate Database Head Delay: ' + str(steem.head_block_number - bn) + '<br>'
    html += 'Posts: ' + str(db.session.query(Post.id).count()) + '<br>'
    html += 'Posts Pending Steem Info Update: ' \
            + str(db.session.query(Post.id).filter(Post.pending_steem_info_update==True).count()) + '<br>'
    html += 'Posts Pending Video Info Update: ' \
            + str(db.session.query(Post.id).filter(Post.pending_video_info_update==True).count()) + '<br>'
    return html

#######################################################################


# PUBLIC PAGES ########################################################

@app.route('/f/api/trending-videos/<limit>', methods=['GET', 'POST'])
@app.route('/f/api/trending-videos', methods=['GET', 'POST'])
def trending_videos(limit="30"):
    limit = int(limit)
    filter_data = {}
    query = db.session.query(Post)
    if request.method == 'POST':
        data = request.data
        filter_data = json.loads(data)
        query = apply_filter_to_query(query, filter_data)
    # get more records than needed as post query filters may remove some
    query = query.order_by(Post.trending_score.desc()).limit(limit*2)
    df = pd.read_sql(query.statement, db.session.bind)
    df = create_video_summary_fields(df, filter_data)
    df = df.head(limit)
    return df.to_json(orient='records')

@app.route('/f/api/hot-videos/<limit>', methods=['GET', 'POST'])
@app.route('/f/api/hot-videos', methods=['GET', 'POST'])
def hot_videos(limit="30"):
    limit = int(limit)
    filter_data = {}
    query = db.session.query(Post)
    if request.method == 'POST':
        data = request.data
        filter_data = json.loads(data)
        query = apply_filter_to_query(query, filter_data)
    # get more records than needed as post query filters may remove some
    query = query.order_by(Post.hot_score.desc()).limit(limit*2)
    df = pd.read_sql(query.statement, db.session.bind)
    df = create_video_summary_fields(df, filter_data)
    df = df.head(limit)
    return df.to_json(orient='records')

@app.route('/f/api/new-videos/<limit>', methods=['GET', 'POST'])
@app.route('/f/api/new-videos', methods=['GET', 'POST'])
def new_videos(limit="30"):
    limit = int(limit)
    filter_data = {}
    try:
        query = db.session.query(Post)
        if request.method == 'POST':
            data = request.data
            filter_data = json.loads(data)
            query = apply_filter_to_query(query, filter_data)
        # get more records than needed as post query filters may remove some
        query = query.order_by(Post.created.desc()).limit(limit*2)
        df = pd.read_sql(query.statement, db.session.bind)
        df = create_video_summary_fields(df, filter_data)
        df = df.head(limit)
        return df.to_json(orient='records')
    except Exception as e:
        return str(e)

@app.route('/f/api/search/<search_terms>/<limit>', methods=['GET', 'POST'])
@app.route('/f/api/search/<search_terms>', methods=['GET', 'POST'])
def search(search_terms, limit='50'):
    limit = int(limit)
    if request.method == 'GET':
        filter_data = json.loads(request.args.get("json"))
    elif request.method == 'POST':
        data = request.data
        filter_data = json.loads(data)
    try:
        author_filter = (Post.author == search_terms)
        search_terms = "'" + search_terms + "'"
        title_filter = Post.title_ts_vector.match(search_terms, postgresql_regconfig='english')
        tags_filter = Post.tags_ts_vector.match(search_terms, postgresql_regconfig='english')
        query = db.session.query(Post).filter(author_filter | title_filter | tags_filter)
        query = apply_filter_to_query(query, filter_data)
        query = apply_sort_to_query(query, filter_data)
        query = query.limit(limit*2) # get more records than needed as post query filters may remove some
        df = pd.read_sql(query.statement, db.session.bind)
        df = create_video_summary_fields(df, filter_data)
        df = df.head(limit)
        return df.to_json(orient='records')
    except Exception as e:
        return jsonify([])

@app.route('/f/api/video/@<author>/<permlink>')
def video(author=None, permlink=None):
    post = db.session.query(Post) \
                .filter(and_(Post.author==author, Post.permlink==permlink)).order_by(Post.video_info_update_requested).first()
    if post:
        post_dict = {
            'title': post.title,
            'author': post.author,
            'permlink': post.permlink,
            'age_string': get_age_string(post.created),
            'created': post.created,
            'tags': post.tags.split(' '),
            'description': post.description, # sanitise?
            'payout_string': get_payout_string(post.pending_payout_value + post.total_payout_value),
            'upvotes': 0,
            'downvotes': 0,
            'video_type': post.video_type,
            'video_id': post.video_id,
            'video_source': ''
        }

        comments = []
        if True:
            replies = steem.get_content_replies(author, permlink)
            for reply in replies:
                comment = {
                    'author': reply['author'],
                    'permlink': reply['permlink'],
                    'age_string': get_age_string(datetime.strptime(reply['created'], '%Y-%m-%dT%H:%M:%S')),
                    'created': datetime.strptime(reply['created'], '%Y-%m-%dT%H:%M:%S'),
                    'payout_string': get_payout_string(float(reply['pending_payout_value'].split(' ')[0]) + float(reply['total_payout_value'].split(' ')[0])),
                    'body': reply['body'], # todo - sanitise?
                    'reply_count': int(reply['children']),
                    'upvotes': 0,
                    'downvotes': 0
                }
                comments.append(comment)
            post_dict['comments'] = comments

        return jsonify(post_dict)
    else:
        return 'Video Not Found for: ' + str(author) + '/' + str(permlink)

@app.route('/f/api/replies/@<author>/<permlink>')
def replies(author=None, permlink=None):
    replies = steem.get_content_replies(author, permlink)
    comments = []
    for reply in replies:
        comment = {
            'author': reply['author'],
            'permlink': reply['permlink'],
            'age_string': get_age_string(datetime.strptime(reply['created'], '%Y-%m-%dT%H:%M:%S')),
            'created': datetime.strptime(reply['created'], '%Y-%m-%dT%H:%M:%S'),
            'payout_string': get_payout_string(float(reply['pending_payout_value'].split(' ')[0]) + float(reply['total_payout_value'].split(' ')[0])),
            'body': reply['body'], # todo - sanitise?
            'reply_count': int(reply['children']),
            'upvotes': 0,
            'downvotes': 0
        }
        comments.append(comment)
    return jsonify(comments)


# todo - implement for when users click on payout, to show breakdown from db
@app.route('/f/api/votes/@<author>/<permlink>')
def votes(author=None, permlink=None):
    return jsonify([])

########################################################################


# ERROR PAGES ##########################################################

@app.errorhandler(400)
def page_not_found(e):
    html = str(e)
    return render_template('simple.html', content_html=html)

@app.errorhandler(404)
def page_not_found(e):
    html = str(e)
    return render_template('simple.html', content_html=html)

@app.errorhandler(403)
def page_not_found(e):
    html = str(e)
    return render_template('simple.html', content_html=html)

@app.errorhandler(410)
def page_not_found(e):
    html = str(e)
    return render_template('simple.html', content_html=html)

########################################################################