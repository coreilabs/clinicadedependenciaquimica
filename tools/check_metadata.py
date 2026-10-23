import sys, urllib.request, re
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'lib'))
from bs4 import BeautifulSoup
for url in ['https://grupoaraujotratamentos.com.br/', 'https://grupoaraujotratamentos.com.br/publicacoes/']:
    s = BeautifulSoup(urllib.request.urlopen(url).read().decode('utf-8'), 'html.parser')
    print('URL:', url)
    for tag in s.select('meta[name], meta[property]'):
        key = tag.get('name') or tag.get('property')
        if key in ('description', 'og:description', 'twitter:description', 'og:title'):
            print(key + ':', tag.get('content'))
    print('Cassino no texto do corpo:', bool(re.search(r'casino|cassino|x7', s.body.get_text(), re.I)))
local = Path(__file__).parent.parent / 'index.html'
print('Cassino no HTML novo:', bool(re.search(r'casino|cassino|x7', local.read_text(encoding='utf-8'), re.I)))
