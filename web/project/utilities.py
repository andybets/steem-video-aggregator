import re
from datetime import datetime, timedelta, date
from steem import Steem
from sqlalchemy.dialects.postgresql import insert
from project.models import *
from collections import Counter
import json
import math
import markdown
import bleach

# compile regex for checking for youtube videos
youtube_video_regex = '(\n)|(src\s?=\s?.{1})((http(s)?://youtu.be/)|(http(s)?://www.youtube.com/embed/)|(http(s)?://www.youtube.com/)|(http(s)?://m.youtube.com/))(watch\?v=)?(?P<videoid>(\w|\_|\-)*)'
youtube_video_regex = re.compile(youtube_video_regex)

def log(s):
    with open('monitor-log.txt', 'a') as f:
        f.write(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ', ')
        f.write(str(s) + '\n')

def get_payout_string(payout):
    return "${:.2f}".format(payout)

# todo - add weeks, months and years
def get_age_string(dt):
    timediff = datetime.now() - dt
    if timediff < timedelta(minutes=2):
        return '{0:.0f} minute ago'.format(math.floor(timediff.seconds/60))
    elif timediff < timedelta(hours=1):
        return '{0:.0f} minutes ago'.format(math.floor(timediff.seconds/60))
    elif timediff < timedelta(hours=2):
        return '1 hour ago'
    if timediff < timedelta(days=1):
        return '{0:.0f} hours ago'.format(math.floor(timediff.seconds/3600))
    elif timediff < timedelta(days=2):
        return '1 day ago'
    else:
        return '{0:.0f} days ago'.format(math.floor(timediff.days))

def get_duration_string(seconds):
    try:
        if seconds > 0:
            m, s = divmod(seconds, 60)
            h, m = divmod(m, 60)
            if h > 0:
                return "%d:%02d:%02d" % (h, m, s)
            else:
                return "%d:%02d" % (m, s)
        else:
            return ''
    except Exception as e:
        return '' # duration not available

def markdown_to_plain_html(s):
    html = s
    try:
        html = html.replace('\n', '<br>')
        html = markdown.markdown(html)
    except Exception as e:
        log('Problem converting markdown to html: ' + str(e))
    try:
        html = bleach.clean(html, tags=['br', 'b', 'i', 'pre', 'code', 'table', 'a'], strip=True) # remove scripts/images
    except Exception as e:
        log('Problem removing unwanted html elements: ' + str(e))
    try:
        html = bleach.linkify(html)
    except Exception as e:
        log('Problem adding links: ' + str(e))

    # remove unwanted blank lines, todo - use regex instead
    for a in range(3):
        html = html.replace('<br><br><br>', '<br><br>')
    return html


def get_valid_video(comment): # returns
    try:
        body = comment['body']
        if body[:2] == '@@':
            return (None, None, None)
    except Exception as e:
        log('Error: No valid body html/markdown in comment: ' + comment['author'] + '/' + comment['permlink'])
        return (None, None, None)

    js = comment.get('json_metadata', '[]')
    try:
        metadata = json.loads(js)
    except Exception as e:
        log('Error: No valid json_metadata for comment: ' + comment['author'] + '/' + comment['permlink'])
        return (None, None, None)

    category = comment.get('category', '')
    if not category:
        try:
            category = metadata['tags'][0]
        except:
            category = 'Unknown'

    # see if it's a dlive video
    try:
        if metadata['app'].find('dlive') >= 0:
            log('DLive post detected...')
            video_id = metadata.get('ipfsHash', 'live') # will initially be marked as live, then get hash once finished
            if video_id:
                log('DLive post returned - ' + str(video_id))
                return ('dlive', video_id, category)
    except Exception as e:
        pass

    # see if it's a dtube video, and use 480 version if available - todo - store both hashs?
    try:
        if metadata['app'].find('dtube') >= 0 \
            or comment['parent_permlink'] == 'dtube': # sometimes dtube video are shown with app: steemit
            content = metadata['video']['content']
            video_id = content.get('videohash', '')
            video_id = content.get('video480hash', video_id)
            if video_id:
                return ('dtube', video_id, category)
    except Exception as e:
        pass

    # get youtube video (if only 1 is embedded in post body)
    # todo - check regex will collect all videos, possibly use bs instead of regex for parsing
    # todo - better handle posts with more than 1 video
    try:
        matches = [m.groupdict() for m in youtube_video_regex.finditer(body)]
        if len(matches) == 1:
            media_id = matches[0]['videoid']
        if (media_id != 'channel') and (media_id != 'edit') and (media_id != 'watch') \
            and (media_id != 'c') and (media_id != 'user') and (media_id != 'playlist'): # exclude invalid video ids
            return ('youtube', media_id, category)
    except Exception as e:
        pass

    return (None, None, None)


def seconds_from_youtube_duration(durationstring):
    match = re.search('PT((?P<hours>\d{1,2})H)?((?P<minutes>\d{1,2})M)?((?P<seconds>\d{1,2})S)?', durationstring)
    try: hours = int(match.group('hours'))
    except: hours = 0
    try: minutes = int(match.group('minutes'))
    except: minutes = 0
    try: seconds = int(match.group('seconds'))
    except: seconds = 0
    return hours * 3600 + minutes * 60 + seconds
