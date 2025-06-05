from django import template
from urllib.parse import urlencode

register = template.Library()


@register.simple_tag(takes_context=True)
def query_update(context, **kwargs):
    """
    現在のリクエストのクエリパラメータを保持しつつ、
    指定した値（kwargs）で上書きしたクエリ文字列を返す
    """
    query = context["request"].GET.copy()
    for key, value in kwargs.items():
        query[key] = value
    return "?" + urlencode(query)
