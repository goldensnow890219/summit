import phonenumbers

from django.template import Library

register = Library()


@register.filter(name='phonenumber')
def phonenumber(value, country=None):
    try:
        number = phonenumbers.parse(value, country)
    except phonenumbers.NumberParseException:
        return value
    else:
        return phonenumbers.format_number(number, phonenumbers.PhoneNumberFormat.NATIONAL)
