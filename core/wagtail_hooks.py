from django.urls import reverse
from wagtail.admin.menu import MenuItem
from wagtail.core import hooks


@hooks.register('register_settings_menu_item')
def register_frank_menu_item():
    return MenuItem(
        'Tenant File', reverse('google-api-files'), classnames='icon icon-folder-inverse', order=10000
    )

@hooks.register('construct_page_action_menu')
def make_publish_default_action(menu_items, request, context):
    for (index, item) in enumerate(menu_items):
        if item.name == 'action-publish':
            menu_items.pop(index)
            menu_items.insert(0, item)
            break