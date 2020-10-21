from django import template
register = template.Library()
@register.filter(name='remove_marks')
def remove_marks(word):
    chars = "'\",.!$?"
    for c in chars:
        if c in word:
            word = word.replace(c,'')
    return word
