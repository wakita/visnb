import glob
import json

from IPython.display import display, Markdown, Latex

from urllib.parse import urlencode, urlparse, parse_qs, unquote

def mybinder_url(user='wakita', repo='visnb', path='index.ipynb'):
    content_spec = [
        ('repo', f'https://github.com/{user}/{repo}'),
        ('urlpath', [ f'lab/tree/{repo}/{path}' ]),
        ('branch', [ 'main' ]) ]
    binder_spec = [ ('urlpath', f'git-pull?{urlencode(content_spec, doseq=True)}') ]
    return f'https://mybinder.org/v2/gh/wakita/binder-vis/main?{urlencode(binder_spec)}'

def generate(user='wakita', repo='visnb'):
    doc = ['# 公開ノートブックへのリンク']
    
    env = { 'user': user, 'repo': repo }
    
    for path in glob.glob('**/*.ipynb', recursive=True):
        with open(path) as f:
            title = json.load(f)['cells'][0]['source'][0].strip('# \n')
        url = mybinder_url(path=path, **env)
        doc.append(f'- [{title}]({url})')
    
    return Markdown('\n'.join(doc))