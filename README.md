# Site estático — Grupo Araújo Tratamentos

Domínio: https://clinicadependenciaquimica.net.br

O projeto contém somente duas páginas públicas: `index.html` e `politica-de-privacidade.html`. São nove unidades de Goiás com fotos: seis masculinas e três femininas. Todas as imagens e bibliotecas são locais. Não há WordPress, PHP, banco de dados, blog, posts, triagem ou painel administrativo.

## Visualização

No Laragon, acesse o endereço local configurado para esta pasta. Alternativamente, execute nesta pasta:

```powershell
python -m http.server 8765 --bind 127.0.0.1
```

Abra http://127.0.0.1:8765/. O servidor é apenas para visualização; não é necessário Python na hospedagem.

## Publicação

Envie para a raiz da hospedagem apenas:

- `index.html`
- `politica-de-privacidade.html`
- `assets/`
- `robots.txt`
- `sitemap.xml`
- `.htaccess` se a hospedagem utilizar Apache

Não publique `tools/`, que contém os utilitários de geração e validação e suas dependências. Os metadados e o sitemap já usam o domínio final. Configure DNS e HTTPS na hospedagem. O projeto foi preparado localmente; não foi publicado.

## Contato e conteúdo

Identidade visual atualizada com os logotipos da Clínica de Dependência Química, favicon e Open Graph fornecidos. O rodapé mantém a marca do Grupo Araujo Tratamentos. Telefone: 62 99906-3384; WhatsApp: https://wa.me/556299063384. CNPJ preservado. O formulário prepara uma mensagem e abre o WhatsApp; não armazena informações nem realiza envios automáticos. Disponibilidade e condições das clínicas precisam ser confirmadas com a equipe.

Dados e fotos são uma cópia local, não uma consulta em tempo real. Alterações no WordPress e na API não se refletem automaticamente aqui. Para edições manuais, altere o HTML, `assets/style.css`, `assets/static.css` e `assets/js/units.js`.

## Regeneração opcional

```powershell
python tools/build.py
```

Esse comando lê o tema original e captura novamente a apresentação pública da página inicial, removendo scripts e metadados remotos e gerando as descrições institucionais. Não modifica o projeto original. As nove clínicas permanecem registradas em `tools/selected-units.json`. Use `--reselect` apenas se quiser sortear outras nove clínicas. A regeneração sobrescreve os arquivos públicos gerados; preserve alterações manuais antes de executá-la.

O gerador depende de Beautiful Soup em `tools/lib` (já incluído no ambiente local). As bibliotecas utilizadas no site estão em `assets/vendor` com suas licenças originais.

## Validação

`tools/validate.cjs` utiliza Playwright e o Chrome instalado, com servidor local na porta 8765. Verifica filtros, nove cartões, galerias, FAQ, formulário sem envio, menu mobile, imagens, metadados, ausência de dependências externas e erros de JavaScript. Evidências e capturas ficam em `tools/validation/`.

O HTML gerado recebeu metadados novos. O conteúdo estranho encontrado nos metadados da página inicial do domínio original não foi importado. Esta conversão não altera nem corrige o WordPress publicado.
