from django import template

register = template.Library()


@register.filter
def display_name(user):
    """日本語風に名字→名前で表示。なければ username を返す"""
    if user.last_name or user.first_name:
        return f"{user.last_name} {user.first_name}"
    return user.username
