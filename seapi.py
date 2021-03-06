import time
import html

import requests

import core
from utils import log


class Post:
    __getitem__ = getattr
    __setitem__ = setattr

    def __init__(self):
        self.id = None
        self.url = None
        self.type = None
        self.site = None
        self.owner_url = None
        self.owner_name = None
        self.owner_rep = None
        self.title = None
        self.body = None
        self.raw_body = None
        self.score = None
        self.upvote = None
        self.downvote = None
        self.question_id = None
        self.creation_date = None
        self.last_edit_date = None

    def to_list(self):
        return [
            self.id, self.url, self.type, self.site,
            self.owner_url or "", self.owner_name or "", self.owner_rep or 0, self.title,
            self.body, self.raw_body, self.score, self.upvote,
            self.downvote, self.question_id or 0, self.creation_date, self.last_edit_date
        ]


def get_post(site, post_id, post_type):
    """
    Fetch a post from the Stack Exchange API
    """
    if post_type == "answer":
        api_filter = r"!FdmhxNRjn0vYtGOu3FfS5xSwvL"
    elif post_type == "question":
        api_filter = r"!DEPw4-PqDduRmCwMBNAxrCdSZl81364qitC3TebCzqyF4-y*r2L"
    else:
        raise ValueError("post_type must be either 'question' or 'answer'")

    api_filter = r"!*1SdVEqS-F*E3oCZH7zp*8EkDYoKq98j9rjbmSU4y"
    request_url = "https://api.stackexchange.com/2.2/{}s/{}".format(post_type, post_id)
    params = {
        'filter': api_filter,
        'key': core.config.read_key,
        'site': site,
    }
    for attempt in range(1, 4):
        response = requests.get(request_url, params=params).json()
        try:
            item = response['items'][0]
            break
        except (KeyError, IndexError):
            time.sleep(2.000)
    else:
        log('warning', "Failed to fetch {} after 3 attempts".format(post_id))
        return None

    post = Post()
    post.id = post_id
    post.url = item['share_link']
    post.type = post_type
    post.title = html.unescape(item['title'])
    if 'owner' in item and 'link' in item['owner']:
        post.owner_name = html.unescape(item['owner']['display_name'])
        post.owner_url = item['owner']['link']
        post.owner_rep = item['owner']['reputation']
    else:
        post.owner_name = ""
        post.owner_url = ""
        post.owner_rep = 1
    post.site = site
    post.body = item['body']
    post.raw_body = item['body_markdown']
    post.score = item['score']
    post.upvotes = item['up_vote_count']
    post.downvotes = item['down_vote_count']
    post.creation_date = item['creation_date']
    post.last_edit_date = item.get('last_edit_date', post.creation_date)
    if post_type == "answer":
        post.question_id = item['question_id']
    else:
        post.question_id = post_id
    return post


def check_write_permission():
    return bool(core.config.write_key and core.config.write_token)


def close_as_off_topic(site, post_id, keyword="developers"):
    if not check_write_permission():
        return

    # Query API for close vote ID
    url = "https://api.stackexchange.com/2.2/questions/{}/close/options".format(post_id)
    params = {
        'site': site,
        'access_token': core.config.write_token,
        'key': core.config.write_key,
    }
    response = requests.get(url, params=params).json()
    for item in response['items']:
        if 'off-topic' in item['title']:
            break
    else:
        return None  # No "off-topic" ???
    off_topic_list = item['sub_options']

    for item in off_topic_list:
        if keyword in item['description']:
            option_id = item['option_id']
            break
    else:
        return None  # bad keyword

    # Add close vote
    url = "https://api.stackexchange.com/2.2/questions/{}/flags/add".format(post_id)
    payload = {
        'id': int(post_id),
        'question_id': int(post_id),
        'option_id': option_id,
        'site': site,
        'target_site': site,
        'key': core.config.write_key,
        'access_token': core.config.write_token,
    }
    response = requests.post(url, data=payload).json()
    return response


def add_mod_flag(site, post_id, post_type, text):
    if not check_write_permission():
        return

    url = "https://api.stackexchange.com/2.2/{}s/{}/flags/options".format(
        post_type, post_id)
    params = {
        'key': core.config.write_key,
        'access_token': core.config.write_token,
        'site': site,
    }
    response = requests.get(url, params=params).json()
    # look for "in need of moderator intervention
    option_id = None
    if 'items' not in response:
        log('debug', "'items' not found in response")
        return
    for item in response['items']:
        if item['title'] == "in need of moderator intervention":
            option_id = item['option_id']
            log('debug', "Found mod flag option ID {}".format(option_id))
            break
    else:
        log('debug', "Mod flag option not found")
        return

    # cast the flag
    url = "https://api.stackexchange.com/2.2/{}s/{}/flags/add".format(
        post_type, post_id)
    params = {
        'key': core.config.write_key,
        'access_token': core.config.write_token,
        'site': site,
        'option_id': str(option_id),
        'comment': str(text),
    }
    response = requests.post(url, data=params).json()
    return response


def get_site_id(hostname):
    if not core.obj.site_list:
        core.obj.site_list = requests.get(
            "https://meta.stackexchange.com/topbar/site-switcher/all-pinnable-sites").json()

    for item in core.obj.site_list:
        if item['hostname'] == hostname:
            return item['siteid']
    return None
