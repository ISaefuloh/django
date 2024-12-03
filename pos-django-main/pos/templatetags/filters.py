from django import template

register = template.Library()

@register.filter
def is_kasir(user):
    return user.groups.filter(name='Level_Kasir').exists()
