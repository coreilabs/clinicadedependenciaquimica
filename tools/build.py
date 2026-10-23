"""Gera o site estático. Escreve somente na pasta deste novo projeto."""
from pathlib import Path
import sys, json, re, shutil, hashlib, random, urllib.request, urllib.parse
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, str(Path(__file__).parent / 'lib'))
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
SOURCE = Path(r'C:\laragon\www\grupoaraujotratamentos')
THEME = SOURCE / 'wordpress-theme/grupo-araujo'
ORIGIN = 'https://grupoaraujotratamentos.com.br'
DOMAIN = 'https://clinicadependenciaquimica.net.br'
ASSETS = ROOT / 'assets'
ASSETS.mkdir(exist_ok=True)

def get(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'StaticSiteExporter/1.0'})
    with urllib.request.urlopen(req, timeout=60) as response:
        return response.read()

def fragment(html):
    return BeautifulSoup(html, 'html.parser')

# Usamos o HTML público apenas como captura de apresentação. Scripts, head,
# metadados e conteúdo dinâmico são descartados e gerados de fontes explícitas.
home = fragment(get(ORIGIN).decode('utf-8'))
for tag in home.select('script, head, noscript, iframe, #publicacoes, .unit-pagination, .difference-card-link'):
    tag.decompose()
for tag in home.find_all(True):
    for attr in list(tag.attrs):
        if attr.startswith('on'):
            del tag[attr]
body = home.body
assert body is not None
body['class'] = ['home', 'static-site']
assert not re.search(r'casino|cassino|x7|slot machine', body.get_text(), re.I), 'Conteúdo público inesperado; revisar antes de importar.'
for a in body.select('a[href]'):
    href = a['href']
    if any(term in href.lower() for term in ('triagem', 'contrato', 'publicacoes', 'wp-admin', 'wp-login')):
        a.decompose()
    elif href.startswith(ORIGIN):
        path = urllib.parse.urlsplit(href)
        if 'privacidade' in path.path:
            a['href'] = 'politica-de-privacidade.html'
        elif path.fragment:
            a['href'] = '#' + path.fragment
        elif path.path in ('', '/'):
            a['href'] = 'index.html'
        else:
            a['href'] = '#contato'
for node in body.find_all(string=True):
    if 'grupoaraujotratamentos.com.br' in node:
        node.replace_with(str(node).replace('www.grupoaraujotratamentos.com.br', 'clinicadependenciaquimica.net.br').replace('grupoaraujotratamentos.com.br', 'clinicadependenciaquimica.net.br'))

# Copiamos somente recursos públicos utilizados pelo site, sem PHP/administração.
for name in ('vendor', 'img'):
    shutil.copytree(THEME / 'assets' / name, ASSETS / name, dirs_exist_ok=True)
shutil.copy2(THEME / 'assets/css-original.css', ASSETS / 'style.css')
for name in ('favicon.png', 'og.png', 'logotipo-horizontal.png', 'logotipo-vertical.png'):
    shutil.copy2(THEME / name, ASSETS / name)
(ASSETS / 'js').mkdir(exist_ok=True)

# Seleção persistente: reexecutar não troca as clínicas. --reselect faz novo sorteio.
selection = ROOT / 'tools/selected-units.json'
if selection.exists() and '--reselect' not in sys.argv:
    units = json.loads(selection.read_text(encoding='utf-8'))
else:
    catalog = json.loads(get(ORIGIN + '/clinicas/api/public/unidades?state=GO&per_page=100'))
    candidates = [u for u in catalog['data'] if u['estado'] == 'GO' and u.get('fotos')]
    units = random.SystemRandom().sample(candidates, 9)
    selection.write_text(json.dumps(units, ensure_ascii=False, indent=2), encoding='utf-8')
assert len(units) == 9 and all(u['estado'] == 'GO' for u in units)

downloads = {}
def local_url(url):
    if url.startswith('data:') or not url:
        return url
    absolute = urllib.parse.urljoin(ORIGIN, url)
    parsed = urllib.parse.urlsplit(absolute)
    theme_path = '/wp-content/themes/grupo-araujo/'
    if parsed.path.startswith(theme_path):
        relative = parsed.path[len(theme_path):]
        candidate = THEME / relative
        if candidate.is_file():
            destination = ('assets/' + relative[len('assets/'):] if relative.startswith('assets/') else 'assets/' + relative)
            return destination
    suffix = Path(parsed.path).suffix.lower()
    assert suffix in ('.webp', '.jpg', '.jpeg', '.png', '.gif', '.svg', '.avif', '.mp4', '.webm', '.woff', '.woff2'), f'Recurso inesperado: {url}'
    relative = 'assets/media/' + hashlib.sha256(absolute.encode()).hexdigest()[:20] + suffix
    downloads[absolute] = ROOT / relative
    return relative

for image in body.select('img[src], video[src], source[src]'):
    image['src'] = local_url(image['src'])
    image.attrs.pop('srcset', None)
    image.attrs.pop('sizes', None)
for tag in body.select('[style]'):
    # A variável CSS é resolvida pelo arquivo assets/style.css que a consome.
    tag['style'] = re.sub(r'url\([\'"]?([^\)\'\"]+)[\'"]?\)', lambda m: "url('" + local_url(m[1]).removeprefix('assets/') + "')", tag['style'])

local_units = []
for original in units:
    unit = dict(original)
    unit['cidade'] = re.sub(r'\s*-\s*GO$', '', unit['cidade'], flags=re.I)
    unit['url'] = ''  # Galeria e contato no próprio cartão; sem páginas extras.
    unit['fotos'] = [local_url(url) for url in unit['fotos'] if re.search(r'\.(webp|png|jpe?g|avif)(\?|$)', url, re.I)]
    assert unit['fotos'], f"Sem imagens: {unit['id']}"
    local_units.append(unit)

def download(item):
    url, path = item
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(get(url))
    return path
with ThreadPoolExecutor(max_workers=8) as executor:
    results = list(executor.map(download, downloads.items()))
print(f'{len(results)} mídias locais; 9 clínicas selecionadas.', flush=True)

toolbar = body.select_one('.unit-toolbar')
toolbar.replace_with(fragment('''<form class="unit-toolbar unit-toolbar-api" aria-label="Filtros das unidades">
<label class="select-filter" for="unitSearch"><span>Buscar unidade</span><input id="unitSearch" type="search" maxlength="100" placeholder="Nome ou tratamento" aria-controls="unidadesGrid"></label>
<label class="select-filter" for="stateFilter"><span>Estado</span><select id="stateFilter" aria-controls="unidadesGrid"><option value="">Todos os estados</option><option value="GO">Goiás</option></select></label>
<label class="select-filter" for="cityFilter"><span>Cidade</span><select id="cityFilter" aria-controls="unidadesGrid"><option value="">Todas as cidades</option></select></label>
<label class="select-filter" for="typeFilter"><span>Tipo de unidade</span><select id="typeFilter" aria-controls="unidadesGrid"><option value="">Todos os perfis</option></select></label>
<div class="unit-filter-actions"><button class="btn btn-primary" type="submit"><i data-lucide="search"></i><span>Filtrar</span></button><button class="filter-reset" type="reset"><i data-lucide="rotate-ccw"></i><span>Limpar</span></button></div></form>'''))
count = body.select_one('#unitCount')
count.string = '9 unidades encontradas'
count['aria-live'] = 'polite'
body.select_one('#emptyState')['hidden'] = ''
body.select_one('#unidadesGrid')['aria-live'] = 'polite'
body.select_one('#unidadesGrid').insert_after(fragment('<noscript><p>Ative o JavaScript para consultar as nove clínicas e suas fotos, ou fale com nossa equipe pelo telefone <a href="tel:08005757714">0800 575 7714</a>.</p></noscript>'))
contact_form = body.select_one('[data-contact-form]')
if contact_form:
    contact_form['action'] = 'https://api.whatsapp.com/send/'
    contact_form['method'] = 'get'
    for field in contact_form.select('input, textarea'):
        field.attrs.pop('name', None)
    phone = fragment('<input type="hidden" name="phone" value="558005757714">')
    contact_form.insert(0, phone)
for a in body.select('[data-whatsapp-default], [data-whatsapp-unknown], [data-whatsapp-other-units]'):
    a['href'] = 'https://api.whatsapp.com/send/?phone=558005757714'

# Política institucional existente, adaptada ao funcionamento real deste site.
policy_source = fragment((SOURCE / 'politica-de-privacidade.html').read_text(encoding='utf-8'))
policy_article = policy_source.select_one('.policy-card')
cookie_section = policy_article.select('.policy-section')[6]
cookie_section.clear()
cookie_section.append(fragment('<h2>7. Cookies e serviços externos</h2><p>Este site estático não utiliza cookies próprios, ferramentas de análise ou rastreamento. Imagens, estilos e scripts são servidos localmente.</p><p>O formulário de contato prepara uma mensagem e abre o WhatsApp. Os dados preenchidos não são enviados a um banco de dados deste site. Ao acessar o WhatsApp, aplicam-se as políticas de privacidade desse serviço. A hospedagem pode registrar dados técnicos de acesso em seus logs.</p>'))
policy_html = str(policy_article).replace('https://www.grupoaraujotratamentos.com.br', DOMAIN).replace('www.grupoaraujotratamentos.com.br', 'clinicadependenciaquimica.net.br')
policy_body = fragment(str(body))
policy_body.select_one('main').replace_with(fragment('<main class="section section-white"><div class="container"><p class="eyebrow">Proteção de dados</p><h1>Política de Privacidade, Termos de Uso e Cookies</h1>' + policy_html + '</div></main>'))
for a in policy_body.select('a[href^="#"]'):
    a['href'] = 'index.html' + a['href']

vendors = ['swiper/11.2.10/swiper-bundle.min', 'glightbox/3.3.1/glightbox.min', 'aos/2.3.4/aos']
def document(content, privacy=False):
    title = 'Política de Privacidade | Grupo Araújo Tratamentos' if privacy else 'Clínica de Dependência Química em Goiás | Grupo Araújo Tratamentos'
    description = 'Conheça nossa política de privacidade, termos de uso e funcionamento do contato pelo WhatsApp.' if privacy else 'Acolhimento e orientação para dependência química em Goiás. Conheça nove unidades parceiras e fale com o Grupo Araújo Tratamentos. Atendimento 24 horas.'
    canonical = DOMAIN + ('/politica-de-privacidade.html' if privacy else '/')
    styles = ''.join(f'<link rel="stylesheet" href="assets/vendor/{v}.css">' for v in vendors)
    scripts = ''.join(f'<script src="assets/vendor/{v}.js" defer></script>' for v in vendors)
    schema = json.dumps({'@context':'https://schema.org','@type':'Organization','name':'Grupo Araújo Tratamentos','url':DOMAIN,'logo':DOMAIN+'/assets/logotipo-horizontal.png','telephone':'+558005757714','identifier':'67.252.579/0001-50','areaServed':{'@type':'State','name':'Goiás'}}, ensure_ascii=False)
    head = f'''<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{title}</title><meta name="description" content="{description}"><meta name="theme-color" content="#0e2848"><link rel="canonical" href="{canonical}"><link rel="icon" href="assets/favicon.png"><meta property="og:locale" content="pt_BR"><meta property="og:type" content="website"><meta property="og:title" content="{title}"><meta property="og:description" content="{description}"><meta property="og:url" content="{canonical}"><meta property="og:image" content="{DOMAIN}/assets/og.png"><meta name="twitter:card" content="summary_large_image">{styles}<link rel="stylesheet" href="assets/style.css"><link rel="stylesheet" href="assets/static.css"><script type="application/ld+json">{schema}</script></head>'''
    content = str(content)
    content = content.replace('</body>', scripts + '<script src="assets/vendor/lucide/1.58.0/lucide.min.js" defer></script><script src="assets/js/units.js" defer></script><script src="assets/js/main.js" defer></script></body>')
    return '<!doctype html>\n<html lang="pt-BR">' + head + content + '</html>\n'

(ROOT / 'index.html').write_text(document(body), encoding='utf-8')
(ROOT / 'politica-de-privacidade.html').write_text(document(policy_body.body or policy_body, True), encoding='utf-8')
(ASSETS / 'js/units.js').write_text('window.GAT_CONFIG = ' + json.dumps({'whatsapp':'558005757714','atendente':'equipe','unidades':local_units,'unidadeFallbackImage':'assets/img/backgrounds/chacara-piscina-01.webp'}, ensure_ascii=False) + ';\n', encoding='utf-8')

js = (THEME / 'assets/js/main.js').read_text(encoding='utf-8')
js = js.replace('"/wp-content/themes/grupo-araujo/assets/img/backgrounds/chacara-piscina-01.webp"', '"assets/img/backgrounds/chacara-piscina-01.webp"')
js = js.replace('  grid.innerHTML = unidadesAtivas.map(criarCardUnidade).join("");', '''  grid.querySelectorAll('.swiper').forEach(el => el.swiper?.destroy(true, true));
  grid.innerHTML = obterUnidadesFiltradas().map(criarCardUnidade).join("");''')
js = js.replace('  unidadesAtivas.forEach((unidade) => {', '  obterUnidadesFiltradas().forEach((unidade) => {')
js = re.sub(r'  const total = Number.isFinite\(Number\(unidadesMeta.total\)\).*?    : cardsVisiveis;', '  const total = cardsVisiveis;', js, flags=re.S)
js = js.replace('const unidadesMeta = window.GAT_CONFIG?.unidadesMeta || {};', '')
js = js[:js.index('async function copiarTexto(')] + js[js.index('document.addEventListener("DOMContentLoaded"'):]
js = js.replace('  inicializarCompartilhamentoArtigo();', '  inicializarFiltros();')
js = js.replace('const texto = `\nOlá,', 'const texto = `\nOlá,')
filters = '''
function normalizar(valor) { return String(valor || '').normalize('NFD').replace(/[\\u0300-\\u036f]/g, '').toLowerCase(); }
function obterUnidadesFiltradas() {
  const busca = normalizar(document.querySelector('#unitSearch')?.value).trim();
  const cidade = document.querySelector('#cityFilter')?.value || '';
  const estado = document.querySelector('#stateFilter')?.value || '';
  const tipo = document.querySelector('#typeFilter')?.value || '';
  return unidadesAtivas.filter(u => (!busca || normalizar([u.nome,u.cidade,u.descricao,u.modalidade,...u.recursos].join(' ')).includes(busca)) && (!cidade || u.cidade === cidade) && (!estado || u.estado === estado) && (!tipo || u.modalidade === tipo));
}
function inicializarFiltros() {
  const form = document.querySelector('.unit-toolbar');
  if (!form) return;
  [['#cityFilter', 'cidade'], ['#typeFilter', 'modalidade']].forEach(([selector,key]) => {
    const select = document.querySelector(selector);
    [...new Set(unidadesAtivas.map(u => u[key]))].sort((a,b) => a.localeCompare(b,'pt-BR')).forEach(value => select.add(new Option(value,value)));
  });
  form.addEventListener('submit', event => { event.preventDefault(); renderizarUnidades(); });
  form.addEventListener('change', renderizarUnidades);
  form.addEventListener('input', event => { if (event.target.id === 'unitSearch') renderizarUnidades(); });
  form.addEventListener('reset', () => setTimeout(renderizarUnidades, 0));
}
'''
js = js.replace('document.addEventListener("DOMContentLoaded"', filters + '\ndocument.addEventListener("DOMContentLoaded"')
(ASSETS / 'js/main.js').write_text(js, encoding='utf-8')
(ASSETS / 'static.css').write_text('''/* Ajustes exclusivos do site estático. */
[hidden] { display: none !important; }
.filter-reset { cursor: pointer; font: inherit; }
.policy-card { max-width: 900px; margin: 2rem auto; padding: clamp(20px,4vw,48px); background: #fff; border: 1px solid var(--border); border-radius: var(--radius); }
.policy-section + .policy-section { margin-top: 2rem; }
.policy-card li { margin: .5rem 0; }
.policy-card a { overflow-wrap: anywhere; }
@media (prefers-reduced-motion: reduce) { html { scroll-behavior: auto; } [data-aos] { opacity: 1 !important; transform: none !important; } }
''', encoding='utf-8')
(ROOT / 'robots.txt').write_text('User-agent: *\nAllow: /\nDisallow: /tools/\nSitemap: ' + DOMAIN + '/sitemap.xml\n', encoding='utf-8')
(ROOT / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>' + DOMAIN + '/</loc></url><url><loc>' + DOMAIN + '/politica-de-privacidade.html</loc></url></urlset>\n', encoding='utf-8')
(ROOT / '.htaccess').write_text('Options -Indexes\n<IfModule mod_authz_core.c>\n<FilesMatch "^(build\\.py|selected-units\\.json|README\\.md|package.*\\.json)$">\nRequire all denied\n</FilesMatch>\n</IfModule>\n', encoding='utf-8')
(ROOT / 'tools/.htaccess').write_text('Require all denied\n', encoding='utf-8')
print('\n'.join(f"- {u['nome']} ({u['cidade']}/GO): {len(u['fotos'])} fotos" for u in local_units))
