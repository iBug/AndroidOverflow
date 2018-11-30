import requests
import html

import core
from classes import Post
import parsing


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

    request_url = "https://api.stackexchange.com/2.2/{}s/{}".format(post_type, post_id)
    params = {
        'filter': api_filter,
        'key': core.config.read_key,
        'site': site,
    }
    response = requests.get(request_url, params=params).json()
    try:
        item = response['items'][0]
    except (KeyError, IndexError):
        return None

    post = Post()
    post.id = post_id
    post.url = parsing.url_to_shortlink(item['link'])
    post.type = post_type
    post.title = html.unescape(item['title'])
    if 'owner' in item and 'link' in item['owner']:
        post_data.owner_name = html.unescape(item['owner']['display_name'])
        post_data.owner_url = item['owner']['link']
        post_data.owner_rep = item['owner']['reputation']
    else:
        post_data.owner_name = ""
        post_data.owner_url = ""
        post_data.owner_rep = 1
    post.site = site
    post.body = item['body']
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
