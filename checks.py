import math
import regex

import core
from utils import log
from scanning import PostScanner


development = core.check.development = PostScanner("development question", 1.99)


@development.new("bracket count", 1.4)
def bracket_count(post):
    score = 0.0
    body = post.title + "\n\n" + post.raw_body

    n_brackets = body.count("{") + body.count("}") + len(regex.compile(r"(?<=\w)\(\)(?=[\s);])").findall(body))
    if n_brackets >= 3:
        score += math.sqrt(n_brackets - 3)

    return score, "Post has {} brackets".format(n_brackets)


@development.new("java keyword", 1.0)
def java_keyword(post):
    score = 0.0
    body = post.title + "\n\n" + post.raw_body

    n = body.count("public")
    if n >= 5:
        score += (n - 5) / 10
    n = regex.compile(r"\b(?:class|void|int|boolean)\b").findall(body)
    if len(n) >= 2:
        score += (len(n) - 2) / 2
    n = body.count("@Override")
    score += n
    m = regex.compile(r"(public|private)\s+(class|void|int)").findall(body)
    score += len(m) * 1.5
    return score, "Post has Java keyword"


@development.new("android code", 1.5)
def android_code(post):
    score = 0.0
    body = post.title + "\n\n" + post.raw_body

    match = regex.compile(
        r"(?s)(?<!\.)[A-Za-z]{2,}(?:Activity|Fragment|(?<!(?i:web))View|Text|Exception|Manager|Method|Interface)\b"
    ).findall(body)
    score += len(match)

    match = regex.compile(r"\b[A-Z]+(?:_[A-Z]+)+\b").findall(body)
    score += len(match) * 0.5

    match = regex.compile(
        r"\b(?:MainActivity|onCreate|layout|private class|public class|Bundle)\b"
    ).findall(body)
    score += len(match)

    match = regex.compile("(?i)android\W*studio").findall(body)
    score += len(match)

    return score, "Post has Android code"


@development.new("coding intention", 1.0)
def coding_intention(post):
    score = 0.0
    body = post.title + "\n\n" + post.raw_body

    match = regex.compile(r"(?i)\b(build|write?)(?:ing)?\b.{,20}\bandroid\b.{,20}\bapp\b").findall(body)
    score += len(match)

    return score, "placeholder"
