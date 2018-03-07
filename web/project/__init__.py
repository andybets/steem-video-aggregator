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

from sqlalchemy import and_, or_, not_
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
from project.utilities import get_age_string, get_duration_string, get_payout_string, markdown_to_safe_html
from project.utilities import resized_image_url_from_url, get_sparkline_data_from_content, get_voters_list_from_content
from project.utilities import tlog

import json
from contextlib import suppress
from steem.blockchain import Blockchain
from steem import Steem

steem = Steem(nodes=app.config['STEEM_NODES'])

def create_video_summary_fields(df, filter_data={}):
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
    df['title'] = df['title'].apply(lambda x: markdown_to_safe_html(x))
    df['title_truncated'] = df['title'].apply(lambda x: x[:80])

    # experimental resizing through free image proxy/cache
    df['video_thumbnail_image_url'] = df['video_thumbnail_image_url'].apply(lambda x: resized_image_url_from_url(x))

    return df[['author', 'permlink', 'category', 'title', 'title_truncated', 'created', 'age_string', 'payout_string',
             'duration_string', 'video_type', 'video_id', 'video_thumbnail_image_url', 'video_post_delay_days',
             'trending_score', 'hot_score', 'votes_sparkline_data']]

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

    # video type inclusions filter (requires posts to be of type in filter)
    inclusions_list = filter_data.get('filter_included_types', [])
    type_filter_list = []
    for video_type in inclusions_list:
        type_filter_list.append(Post.video_type == video_type)
    if type_filter_list:
        new_query = new_query.filter(or_(*type_filter_list))


    if filter_data.get('filter_duration_selection', 'all') == 'short':
        new_query = new_query.filter(Post.video_duration_seconds <= 240)
    elif filter_data.get('filter_duration_selection', 'all') == 'long':
        new_query = new_query.filter(Post.video_duration_seconds > 1200)
    if filter_data.get('filter_exclude_old_video', 'false') == 'true':
        new_query = new_query.filter(Post.video_post_publish_delay_seconds < (7*24*3600))
    if filter_data.get('filter_exclude_nsfw', 'false') == 'true':
        new_query = new_query.filter(not_(Post.is_nsfw))

    # author exclusions filter
    inclusions_list = filter_data.get('filter_excluded_authors', [])
    author_filter_list = []
    for account in inclusions_list:
        author_filter_list.append(Post.author == account)
    if author_filter_list:
        new_query = new_query.filter(not_(or_(*author_filter_list)))

    # author inclusions filter
    inclusions_list = filter_data.get('filter_included_authors', [])
    author_filter_list = []
    for account in inclusions_list:
        author_filter_list.append(Post.author == account)
    if author_filter_list:
        new_query = new_query.filter(or_(*author_filter_list))

    # voter exclusions filter (removes posts voted by any of first five accounts in filter)
    exclusions_list = filter_data.get('filter_excluded_voters', [])[:5]
    voter_filter_list = []
    for account in exclusions_list:
        voter_filter_list.append(Post.voters_list_ts_vector.match(account, postgresql_regconfig='english'))
    if voter_filter_list:
        new_query = new_query.filter(not_(or_(*voter_filter_list)))

    # voter inclusions filter (requires posts voted by any of first five accounts in filter)
    inclusions_list = filter_data.get('filter_included_voters', [])[:5]
    voter_filter_list = []
    for account in inclusions_list:
        voter_filter_list.append(Post.voters_list_ts_vector.match(account, postgresql_regconfig='english'))
    if voter_filter_list:
        new_query = new_query.filter(or_(*voter_filter_list))

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
    query = query.order_by(Post.trending_score.desc()).limit(int(limit*1.2))
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
    query = query.order_by(Post.hot_score.desc()).limit(int(limit*1.2))
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
        query = query.order_by(Post.created.desc()).limit(int(limit*1.2))
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
        modified_search_terms = "'" + search_terms + "'"
        title_filter = Post.title_ts_vector.match(modified_search_terms, postgresql_regconfig='english')
        tags_filter = Post.tags_ts_vector.match(modified_search_terms, postgresql_regconfig='english')
        query = db.session.query(Post).filter(author_filter | title_filter | tags_filter)
        query = apply_filter_to_query(query, filter_data)
        query = apply_sort_to_query(query, filter_data)
        query = query.limit(int(limit*1.2)) # get more records than needed as post query filters may remove some
        df = pd.read_sql(query.statement, db.session.bind)
        df = create_video_summary_fields(df, filter_data)
        df = df.head(limit)
        return df.to_json(orient='records')
    except Exception as e:
        return jsonify([])

@app.route('/f/api/video/@<author>/<permlink>')
def video(author=None, permlink=None):
    tlog('Incoming Request: ' + author + '/' + permlink)
    post = db.session.query(Post) \
                .filter(and_(Post.author==author, Post.permlink==permlink)).order_by(Post.video_info_update_requested).first()
    tlog('Done DB Query: ' + author + '/' + permlink)
    if post:
        post_dict = {
            'title': post.title,
            'author': post.author,
            'category': post.category,
            'permlink': post.permlink,
            'age_string': get_age_string(post.created),
            'created': post.created,
            'tags': post.tags.split(' '),
            'description': markdown_to_safe_html(post.description),
            'payout_string': get_payout_string(post.pending_payout_value + post.total_payout_value),
            'upvotes': 0,
            'downvotes': 0,
            'video_type': post.video_type,
            'video_id': post.video_id,
            'video_source': ''
        }
        json = jsonify(post_dict)
        tlog('Ready to return JSON: ' + author + '/' + permlink)
        return json
    else:
        return 'Video Not Found for: ' + str(author) + '/' + str(permlink)

@app.route('/f/api/state/<category>/@<author>/<permlink>')
def state(category, author, permlink):
    path = category + '/@' + author + '/' + permlink
    state = steem.get_state(path)

    # handles cases where errors return random Steem content!
    if len(state['error']) > 0:
        js = {'error': 'could not get state for ' + path, 'replies': [], 'payout_string': '' }
        return jsonify(js)

    content = state['content']
    post_content = content[author + '/' + permlink]
    reply_urls = post_content['replies']
    replies = [content[x] for x in reply_urls]
    data = {'error': '',
            'replies': [],
            'payout_string': get_payout_string(float(post_content['pending_payout_value'].split(' ')[0]) + float(post_content['total_payout_value'].split(' ')[0]))
    }
    for reply in replies:
        comment = {
            'author': reply['author'],
            'permlink': reply['permlink'],
            'age_string': get_age_string(datetime.strptime(reply['created'], '%Y-%m-%dT%H:%M:%S')),
            'created': reply['created'],
            'payout_string': get_payout_string(float(reply['pending_payout_value'].split(' ')[0]) + float(reply['total_payout_value'].split(' ')[0])),
            'body': markdown_to_safe_html(reply['body']),
            'reply_count': int(reply['children']),
            'active_votes': reply['active_votes'],
            'upvotes': 0,
            'downvotes': 0
        }
        data['replies'].append(comment)
    return jsonify(data)

# todo - implement for when users click on payout, to show breakdown from db
@app.route('/f/api/votes/@<author>/<permlink>')
def votes(author=None, permlink=None):
    return jsonify([])

########################################################################

# DEBUGGING AND EXPERIMENTAL PAGES (NOT USED IN VUE APP) ###############

# testing steem request for getting content and nested replies
@app.route('/f/api/' + app.config['DEBUGGING_KEY'] + '/state/<category>/@<author>/<permlink>')
def debug_state(category, author, permlink):
    path = category + '/@' + author + '/' + permlink
    content = steem.get_state(path)
    return jsonify(content)

@app.route('/f/api/' + app.config['DEBUGGING_KEY'] + '/vtp/@<author>/<permlink>')
def vote_time_profile(author, permlink):
    content = steem.get_content(author, permlink)
    return str(get_sparkline_data_from_content(content))

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
    html += 'Approximate Database Head Delay Seconds: ' + str((steem.head_block_number - bn) * 3) + '<br>'
    html += 'Posts in Database: ' + str(db.session.query(Post.id).count()) + '<br>'
    html += 'Posts Pending Steem Info Update: ' \
            + str(db.session.query(Post.id).filter(Post.pending_steem_info_update==True).count()) + '<br>'
    html += 'Posts Pending Video Info Update: ' \
            + str(db.session.query(Post.id).filter(Post.pending_video_info_update==True).count()) + '<br>'
    return html

# to explore how better full text search might be done
# todo - establish whether existing indexes are used in the query below (suspect not)
@app.route('/f/api/' + app.config['DEBUGGING_KEY'] + '/test-search/<search_terms>', methods=['GET', 'POST'])
def test_search(search_terms):
    try:
        sql = text('''
                    SELECT pid, p_title
                    FROM (SELECT posts.id as pid,
                                 posts.title as p_title,
                                 setweight(to_tsvector('english', posts.title), 'A') ||
                                 setweight(to_tsvector('english', posts.tags), 'A') ||
                                 setweight(to_tsvector('simple', posts.author), 'A') as document
                          FROM posts) as p_search
                    WHERE p_search.document @@ to_tsquery('english', 'acoustic <-> guitar')
                    ORDER BY ts_rank(p_search.document, to_tsquery('english', 'acoustic <-> guitar')) DESC;
                   ''')
        df = pd.read_sql(sql, db.session.connection())
        return df.to_html()

    except Exception as e:
        return str(e)

#######################################################################
