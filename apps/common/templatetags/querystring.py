from django import template
from urllib.parse import urlencode

register = template.Library()


@register.simple_tag(takes_context=True)
def query_update(context, **kwargs):
    """
    クエリ文字列を更新し、page をリセットする
    """
    query = context["request"].GET.copy()

    # フィルター変更時にはページ番号をリセット（存在しない場合でも安全）
    query.pop("page", None)

    # 新しい値で上書き
    for key, value in kwargs.items():
        query[key] = value

    return "?" + urlencode(query)
