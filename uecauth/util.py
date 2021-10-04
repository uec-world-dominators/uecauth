from pprint import pprint
import requests
import bs4


def create_form_data(html: str, form_name: str = None):
    doc = bs4.BeautifulSoup(html, 'html.parser')
    form = doc.select_one(f'form[name={form_name}]' if form_name else 'form')
    # method
    method = form.get('method')
    # url
    url = form.get('action')
    # keyvalue
    keyvalue = {}
    for _input in form.select('input'):
        keyvalue[_input.get('name')] = _input.get('value', '')

    return method, url, keyvalue


def debug_response(res: requests.Response):
    print(res.url)
    print(res.status_code)
    print(res.cookies)
    pprint(dict(res.headers))
    with open('response.html', 'wt', encoding='utf-8') as f:
        f.write(res.text)
