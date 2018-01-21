import time
from datetime import datetime, date, timedelta

from os.path import join, isfile

from flask import Flask, render_template, make_response, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from flask_uploads import UploadSet, IMAGES, configure_uploads
from flask_pagedown import PageDown
from flask_migrate import Migrate
from flask_httpauth import HTTPBasicAuth

from threading import Thread
import re

from sqlalchemy import and_, or_
from sqlalchemy.dialects.postgresql import insert #, update
from sqlalchemy import text

app = Flask(__name__, instance_relative_config=True)

app.config.from_pyfile('/home/flask/app/web/instance/flask.cfg')

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

import sys
sys.path.append('/home/flask/app/web/')

from project import db
from project.models import Post
from project.utilities import log,  seconds_from_youtube_duration, get_valid_video, markdown_to_plain_html

import json
import requests
from contextlib import suppress
from steem.blockchain import Blockchain
from steem import Steem

steem = Steem(nodes=app.config['STEEM_NODES'])


class PostUpdateThread(Thread):
    def __init__(self, db, app):
        Thread.__init__(self)
        self.app = app
        self.db = db

    # todo - update scores of only active posts
    def updatePostScores(self):
        try:
            q = '''
                    update posts set
                        trending_score =
                        (sqrt(pending_payout_value) * 1000000) / pow(EXTRACT(EPOCH FROM current_timestamp - created) + 300, 0.15),
                        hot_score =
                        (sqrt(pending_payout_value - least(9.99, pending_payout_value)) * 1000000) / (EXTRACT(EPOCH FROM current_timestamp - created) + 60)
                        where EXTRACT(EPOCH FROM current_timestamp - created) > 600
                        and EXTRACT(EPOCH FROM current_timestamp - created) < 604800
                    '''
                # removed 'and pending_payout_value > 9.99' to prevent flagging not updating some posts
            db.engine.execute(text(q).execution_options(autocommit=True))
        except Exception as e:
            log('Failed to update scores...')
            log(str(e))

    # query Steem API node for up to date content, and add to post
    def update_steem_info(self, post):
        try:
            # todo - trap http error and retry fetch, or return marker to retry later?
            content = steem.get_content(post.author, post.permlink)
            post.created = datetime.strptime(content['created'], '%Y-%m-%dT%H:%M:%S')
            post.category = content['category']
            js = content.get('json_metadata', '[]')
            metadata = json.loads(js)
            tags = metadata.get('tags', [])
            post.tags = ' '.join(tags)
            post.is_nsfw = True if post.tags.lower().find('nsfw') >= 0 else False
            post.title = content['title']
            post.has_declined_payout = False if float(content['max_accepted_payout'].split(' ')[0]) > 0 else True
            post.pending_payout_value = float(content['pending_payout_value'].split(' ')[0])
            post.total_payout_value = float(content['total_payout_value'].split(' ')[0])
            post.has_paidout = True if post.total_payout_value > 0 else False
            post.steem_json = content # todo - decide what of this should be stored
            post.steem_thumbnail_image_url = ''
            new_type, new_video_id, new_category = get_valid_video(content)
            # if valid on update, use new values, otherwise assume old values remain
            # this check is applied so dtube posts, edited in steemit are still retained
            if new_type and new_video_id and new_category:
                post.video_type, post.video_id, post.category = new_type, new_video_id, new_category
            post.description = markdown_to_plain_html(content['body'])
            post.pending_steem_info_update = False
            post.steem_info_update_requested = None
            db.session.commit()
            return post
        except Exception as e:
            log('Problem updating Steem info for: @' + post.author + '/' + post.permlink + '!')
            log(str(e))
            db.session.delete(post)
            db.session.commit()
            log('Deleted post!') # todo - decide whether there's a better approach to this

    # query youtube/dtube/vimeo for up to date content, and add to post
    def update_video_info(self, post):
        try:
            if post.video_type == 'youtube':
                video_id = post.video_id
                video_api_key = app.config['YOUTUBE_API_KEY']
                # url = 'https://www.googleapis.com/youtube/v3/videos?part=snippet%2CcontentDetails%2Cstatistics%2Cstatus%2Cplayer&id=' + video_id + '&key=' + video_api_key
                url = 'https://www.googleapis.com/youtube/v3/videos?part=snippet%2CcontentDetails&id=' + video_id + '&key=' + video_api_key
                js = requests.get(url).json()
                items = js['items']
                if len(items) == 1:
                    item = items[0]
                    post.video_thumbnail_image_url = item['snippet']['thumbnails']['medium']['url']
                    post.video_duration_seconds = seconds_from_youtube_duration(item['contentDetails']['duration'])
                    post.video_provider_channel_id = item['snippet']['channelId']
                    video_published = datetime.strptime(item['snippet']['publishedAt'][:-5], '%Y-%m-%dT%H:%M:%S')
                    if post.created > video_published:
                        post.video_post_publish_delay_seconds = (post.created - video_published).total_seconds()
                    else:
                        post.video_post_publish_delay_seconds = 0
                    # todo - decide which metadata to store in DB
                    # post.video_info = {'snippet': item['snippet'], 'contentDetails': item['contentDetails']}

            elif post.video_type == 'dtube':
                try:
                    url = 'https://steemit.com/dtube/@' + post.author + '/' + post.permlink + '.json'
                    js = requests.get(url).json()['post']
                    metadata = js.get('json_metadata', '[]')
                    post.video_thumbnail_image_url = 'https://ipfs.io/ipfs/' + metadata['video']['info']['snaphash']
                    post.video_duration_seconds = metadata['video']['info']['duration']
                    post.video_provider_channel_id = ''
                    post.video_post_publish_delay_seconds = 0
                    # todo - decide which metadata to store in DB
                    # post.video_info = metadata
                except Exception as e:
                    # todo - fix regex so invalid dtubes don't reach here, then remove
                    log('Problem updating updating dtube video info: ' + str(e))
                    db.session.delete(post)
                    db.session.commit()
                    log('Deleted DTube Video Post: @' + post.author + '/' + post.permlink)
                    return

            elif post.video_type == 'dlive':
                try:
                    url = 'https://steemit.com/dlive/@' + post.author + '/' + post.permlink + '.json'
                    js = requests.get(url).json()['post']
                    metadata = js.get('json_metadata', '[]')
                    post.video_thumbnail_image_url = metadata.get('thumbnail', '')
                    post.video_duration_seconds = -1
                    post.video_provider_channel_id = ''
                    post.video_post_publish_delay_seconds = 0
                    # todo - decide which metadata to store in DB
                    # post.video_info = metadata
                except Exception as e:
                    # todo - fix intake filter regex so invalid dlives don't reach here, then remove
                    log('Problem updating updating dlive video info: ' + str(e))
                    db.session.delete(post)
                    db.session.commit()
                    log('Deleted DLive Video Post: @' + post.author + '/' + post.permlink)
                    return

            # todo - implement support
            elif post.video_type == 'vimeo':
                pass

            post.pending_video_info_update = False
            post.video_info_update_requested = None
            db.session.commit()
        except Exception as e:
            log('Updating video info failed for: @' + post.author + '@' + post.permlink + '!')
            log(str(e))
            db.session.delete(post)
            db.session.commit()
            log('Deleted invalid post!!')
        return post

    # query thread to update posts with pending update, and perform them
    # also update trending/hot scores every 5 minutes
    def run(self):
        last_updated_post_scores = datetime.now()
        while True:
            time.sleep(0.5)

            # update post scores every 5 minutes
            if (datetime.now() - last_updated_post_scores).seconds > 300:
                log('Updating post scores...')
                self.updatePostScores()
                last_updated_post_scores = datetime.now()
                log('Updated post scores!')

            post = db.session.query(Post) \
                .filter(Post.pending_video_info_update).order_by(Post.video_info_update_requested).first()
            if post:
                post = self.update_steem_info(post)
                if post:
                    post = self.update_video_info(post)
            else:
                post = db.session.query(Post) \
                    .filter(Post.pending_steem_info_update).order_by(Post.steem_info_update_requested).first()
                if post:
                    post = self.update_steem_info(post)
                else:
                    time.sleep(1)


time.sleep(10)
log('Started Post Info Updater')

# start thread for updating post info
thread_1 = PostUpdateThread(db, app)
thread_1.start()