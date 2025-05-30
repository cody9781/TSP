from django import template
register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter(name='access')
def access(value, arg):
    return value.get(arg, '')

# custom_filters.py에 필터 추가
@register.filter
def humanize_field_name(value):
    field_map = {
        'ts_id': 'TS ID',
        'moq': 'MOQ',
        'unit_price': '단가',
        'product': '제품',
        'item': '자재',
        # ... 추가 매핑
    }
    return field_map.get(value, value)