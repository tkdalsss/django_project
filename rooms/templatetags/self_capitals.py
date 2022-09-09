from django import template

register = template.Library()

@register.filter
def self_capitals(value):
    print(value)
    return 'lalalalala'