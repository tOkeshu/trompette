import re
from django import template
from django.urls import reverse
from django.utils.html import escape

register = template.Library()

@register.filter
def as_html(content):
    content = re.sub('@(\S+)', _handle, content)
    content = re.sub('\S+\.[a-z]{2,}', _url, content)
    content = re.sub('#(\w+)', _hashtag, content)
    return content

def _handle(match):
    handle = escape(match.group(1))
    url    = reverse('user_tl', args=(handle,))
    tpl    = '<a class="to-account" href="{url}" data-info="{handle}">@{handle}</a>'
    return tpl.format(url=url, handle=handle)

def _url(match):
    url = escape(match.group(0))
    tpl = '<a href="{url}">{url}</a>'
    return tpl.format(url=url)

def _hashtag(match):
    hashtag = escape(match.group(1))
    url     = reverse('tag_tl', args=(hashtag,))
    tpl     = '<a class="to-hashtag" href="{url}" data-info="{hashtag}">#{hashtag}</a>'
    return tpl.format(hashtag=hashtag, url=url)

