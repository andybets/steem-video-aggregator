from project import db, bcrypt, app, images
from sqlalchemy.ext.hybrid import hybrid_method, hybrid_property
from datetime import datetime, timedelta
from markdown import markdown
from flask import url_for
import bleach
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
import math

from sqlalchemy import cast, func
from sqlalchemy.dialects import postgresql

def create_tsvector(*args):
    exp = args[0]
    for e in args[1:]:
        exp += ' ' + e
    return func.to_tsvector('english', exp)

class SteemAccount(db.Model):
    __tablename__ = "steem_accounts"
    author = db.Column(db.String, primary_key=True)
    info = db.Column(db.JSON, nullable=True)

class Post(db.Model):
    __tablename__ = "posts"
#    author_account = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=True)
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String, nullable=False)
    permlink = db.Column(db.String, nullable=False)

    block_number = db.Column(db.Integer, nullable=False)
    created = db.Column(db.DateTime, nullable=True)
    category = db.Column(db.String, nullable=True, default='') # todo - force not null, when bug found
    tags = db.Column(db.String, nullable=False, default='')
    is_nsfw = db.Column(db.Boolean, nullable=False, default=False)
    has_declined_payout = db.Column(db.Boolean, nullable=False, default=False)
    title = db.Column(db.String, nullable=False, default='')
    has_paidout = db.Column(db.Boolean, nullable=False, default=False)
    pending_payout_value = db.Column(db.Numeric, nullable=True) # move to steem_json?
    total_payout_value = db.Column(db.Numeric, nullable=True) # move to steem_json?
    steem_json = db.Column(db.JSON, nullable=True)
    video_type = db.Column(db.String, nullable=True)
    video_id = db.Column(db.String, nullable=True)
    video_info = db.Column(db.JSON, nullable=True) # whether unlisted etc, different scores?
    trending_score = db.Column(db.Integer, nullable=True, default=0) # to define/index later
    hot_score = db.Column(db.Integer, nullable=True, default=0) # to define/index later
    other_score = db.Column(db.Integer, nullable=True, default=0) # to define/index later
    steem_thumbnail_image_url = db.Column(db.String, nullable=True)
    video_thumbnail_image_url = db.Column(db.String, nullable=True)
    video_provider_channel_id = db.Column(db.String, nullable=True)
    video_duration_seconds = db.Column(db.Integer, nullable=True)
    video_post_publish_delay_seconds = db.Column(db.Integer, nullable=True)
    description = db.Column(db.String, nullable=True)

    pending_steem_info_update = db.Column(db.Boolean, nullable=False, default=True)
    pending_video_info_update = db.Column(db.Boolean, nullable=False, default=True)
    steem_info_update_requested = db.Column(db.DateTime, nullable=True, default=datetime.now())
    video_info_update_requested = db.Column(db.DateTime, nullable=True, default=datetime.now())

    # for full text title search
    title_ts_vector = create_tsvector(
        cast(func.coalesce(func.lower(title), ''), postgresql.TEXT)
    )
    fts_index_1 = db.Index('idx_post_title_fts', title_ts_vector, postgresql_using='gin')

    # for full text description search
    description_ts_vector = create_tsvector(
        cast(func.coalesce(func.lower(description), ''), postgresql.TEXT)
    )
    fts_index_2 = db.Index('idx_post_description_fts', description_ts_vector, postgresql_using='gin')

    # for full text tags search
    tags_ts_vector = create_tsvector(
        cast(func.coalesce(func.lower(tags), ''), postgresql.TEXT)
    )
    fts_index_3 = db.Index('idx_tags_fts', tags_ts_vector, postgresql_using='gin')

    u_key = db.UniqueConstraint(author, permlink, name='posts_unique')
    index_0 = db.Index('posts_idx_0', author, permlink)
    index_1 = db.Index('posts_idx_1', trending_score)
    index_2 = db.Index('posts_idx_2', hot_score)
    index_4 = db.Index('posts_idx_4', pending_payout_value)
    index_5 = db.Index('posts_idx_5', category, trending_score)
    index_6 = db.Index('posts_idx_6', category, hot_score)
    index_7 = db.Index('posts_idx_7', category, other_score)
    index_8 = db.Index('posts_idx_8', category, pending_payout_value)
    index_9 = db.Index('posts_idx_9', created.desc())
    index_10 = db.Index('posts_idx_10', category, created.desc())
    index_11 = db.Index('posts_idx_11', pending_video_info_update, video_info_update_requested,
                        postgresql_where=(pending_video_info_update))
    index_12 = db.Index('posts_idx_12', pending_steem_info_update, steem_info_update_requested,
                        postgresql_where=(pending_steem_info_update))


    channel_posts = db.relationship("ChannelPost", backref="channelpost_post")

class Account(db.Model):
    __tablename__ = "accounts"
    owner = db.Column(db.String, primary_key=True)
    password = db.Column(db.String, nullable=False)
    channels = db.relationship("Channel", backref="channel_account")

class Channel(db.Model):
    __tablename__ = "channels"
    id = db.Column(db.Integer, primary_key=True)
    account = db.Column(db.String, db.ForeignKey('accounts.owner'))
    title = db.Column(db.String, nullable=False)
    category = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=True)
    auto_add_criteria = db.Column(db.JSON, nullable=True) # videos matching this are added to channel
    benefactor_info = db.Column(db.JSON, nullable=True)
    default_post_sort_order = db.Column(db.JSON, nullable=True)
    last_auto_added = db.Column(db.DateTime, nullable=False)
    pending_auto_add = db.Column(db.Boolean, nullable=False, default=False)
    posts = db.relationship("ChannelPost", backref="channelpost_channel")

# for assigning posts to channels
class ChannelPost(db.Model):
    __tablename__ = "channel_posts"
    id = db.Column(db.Integer, primary_key=True)
    channel_id = db.Column(db.Integer, db.ForeignKey('channels.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    default_position = db.Column(db.Integer, nullable=True)

