from django import template

register = template.Library()


@register.filter
def display_name(user):
    """フルネームがあればそれを返し、なければ username を返す"""
    full_name = user.get_full_name()
    return full_name if full_name else user.username
