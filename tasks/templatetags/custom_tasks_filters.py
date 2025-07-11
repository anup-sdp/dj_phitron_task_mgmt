# used in test.html
# templatetags directory is used to create custom template tags and filters.
"""
A custom filter is a Python function to modify or format a value in a Django template.
It works just like built-in template filters (like {{ name|lower }} or {{ date|date:"Y-m-d" }}), 
but created to handle custom logic that Django doesn't provide out of the box.
"""

from django import template

register = template.Library()

@register.filter
def is_capitalized(value):    
    if not isinstance(value, str):
        return False
    if not value:
        return False    
    
    return value.istitle() #  Checks if a string is capitalized (titlecased - each word starts uppercase)


@register.filter
def to_title(value):
    if not isinstance(value, str):
        return value
    return value.title()
