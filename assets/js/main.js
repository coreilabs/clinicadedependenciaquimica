const WHATSAPP_ATENDENTE = "556299063384";
const NOME_ATENDENTE = window.GAT_CONFIG?.atendente || "equipe";

const MENSAGEM_PADRAO =
  `Olá, ${NOME_ATENDENTE}. Vim pelo site e preciso de orientação sobre dependência química ou alcoolismo.`;

const MENSAGEM_UNIDADE_INDEFINIDA =
  `Olá, ${NOME_ATENDENTE}. Vim pelo site e preciso de orientação, mas ainda não sei qual unidade seria mais adequada.`;

const MENSAGEM_OUTRAS_UNIDADES =
  `Olá, ${NOME_ATENDENTE}. Vim pelo site e gostaria de verificar disponibilidade de outras unidades.`;

const unidadesAtivas = Array.isArray(window.GAT_CONFIG?.unidades)
  ? window.GAT_CONFIG.unidades
  : [];

const imagemFallbackUnidade =
  window.GAT_CONFIG?.unidadeFallbackImage || "assets/img/backgrounds/chacara-piscina-01.webp";

let galeriaUnidades = null;

function gerarLinkWhatsappPadrao(texto = MENSAGEM_PADRAO) {
  const numeroConfigurado = window.GAT_CONFIG?.whatsapp || WHATSAPP_ATENDENTE;
  const numero = String(numeroConfigurado).replace(/\D/g, "").replace(/^55629(?=\d{8}$)/, "5562");
  return `https://wa.me/${numero}?text=${encodeURIComponent(texto)}`;
}

function gerarLinkWhatsappUnidade(unidade) {
  const identificacao = unidade.nome
    ? `${unidade.nome}, em ${unidade.cidade}/${unidade.estado}`
    : `uma unidade em ${unidade.cidade}/${unidade.estado}`;
  const texto = `Olá, ${NOME_ATENDENTE}. Vim pelo site e gostaria de mais informações sobre ${identificacao}, modalidade ${unidade.modalidade}. Pode me orientar?`;
  return gerarLinkWhatsappPadrao(texto);
}

function escaparHtml(valor) {
  return String(valor)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function definirLinksWhatsapp() {
  document.querySelectorAll("[data-whatsapp-default]").forEach((link) => {
    link.href = gerarLinkWhatsappPadrao();
  });

  document.querySelectorAll("[data-whatsapp-unknown]").forEach((link) => {
    link.href = gerarLinkWhatsappPadrao(MENSAGEM_UNIDADE_INDEFINIDA);
  });

  document.querySelectorAll("[data-whatsapp-other-units]").forEach((link) => {
    link.href = gerarLinkWhatsappPadrao(MENSAGEM_OUTRAS_UNIDADES);
  });
}

function midiaEhVideo(caminho) {
  return /\.(mp4|webm|ogg)$/i.test(caminho);
}

function criarSlide(unidade, foto, indice) {
  const rotulo = escaparHtml(`Unidade em ${unidade.cidade}/${unidade.estado} - ${unidade.modalidade}`);
  const caminho = escaparHtml(foto);
  const posicao = indice + 1;

  if (midiaEhVideo(foto)) {
    return `
      <div class="swiper-slide">
        <div class="unit-slide-link unit-slide-video" aria-label="Vídeo ${posicao} de unidade em ${escaparHtml(unidade.cidade)}/${escaparHtml(unidade.estado)}, modalidade ${escaparHtml(unidade.modalidade)}">
          <video class="unit-slide-media" src="${caminho}" controls preload="metadata" playsinline></video>
        </div>
      </div>
    `;
  }

  return `
    <div class="swiper-slide">
      <a class="unit-slide-link glightbox" href="${caminho}" data-gallery="galeria-${unidade.id}" data-title="${rotulo}">
        <img class="unit-slide-media" src="${caminho}" alt="Foto ${posicao} de unidade em ${escaparHtml(unidade.cidade)}/${escaparHtml(unidade.estado)}, modalidade ${escaparHtml(unidade.modalidade)}" loading="lazy" width="640" height="480">
      </a>
    </div>
  `;
}

function criarCardUnidade(unidade) {
  const recursos = Array.isArray(unidade.recursos)
    ? unidade.recursos
    .map((recurso) => `<li>${escaparHtml(recurso)}</li>`)
    .join("")
    : "";
  const fotos = Array.isArray(unidade.fotos) && unidade.fotos.length
    ? unidade.fotos
    : [imagemFallbackUnidade];
  const slides = fotos
    .map((foto, indice) => criarSlide(unidade, foto, indice))
    .join("");
  const detalhes = unidade.url
    ? `
        <a class="btn btn-secondary full" href="${escaparHtml(unidade.url)}" target="_blank" rel="noopener">
          <i data-lucide="external-link"></i>
          <span>Ver detalhes da unidade</span>
        </a>
      `
    : "";

  return `
    <article class="unit-card" data-aos="fade-up" data-modalidade="${escaparHtml(unidade.modalidade)}" data-cidade="${escaparHtml(unidade.cidade)}" data-unidade="${escaparHtml(unidade.id)}">
      <div class="unit-carousel swiper swiper-${unidade.id}" aria-label="Fotos de unidade em ${escaparHtml(unidade.cidade)}/${escaparHtml(unidade.estado)}, modalidade ${escaparHtml(unidade.modalidade)}">
        <div class="swiper-wrapper">
          ${slides}
        </div>
        <button class="swiper-nav swiper-prev prev-${unidade.id}" type="button" aria-label="Foto anterior da unidade em ${escaparHtml(unidade.cidade)}">
          <i data-lucide="chevron-left"></i>
        </button>
        <button class="swiper-nav swiper-next next-${unidade.id}" type="button" aria-label="Próxima foto da unidade em ${escaparHtml(unidade.cidade)}">
          <i data-lucide="chevron-right"></i>
        </button>
        <div class="swiper-pagination pagination-${unidade.id}"></div>
      </div>
      <div class="unit-body">
        <h3>${escaparHtml(unidade.nome || "Unidade parceira")}</h3>
        <div class="unit-meta">
          <span class="tag"><i data-lucide="map-pin"></i>${escaparHtml(unidade.cidade)}/${escaparHtml(unidade.estado)}</span>
          <span class="tag accent"><i data-lucide="users"></i>${escaparHtml(unidade.modalidade)}</span>
        </div>
        <p>${escaparHtml(unidade.descricao)}</p>
        <ul class="resource-list">
          ${recursos}
        </ul>
        <div class="unit-card-actions">
          ${detalhes}
          <a class="btn btn-primary full" href="${gerarLinkWhatsappUnidade(unidade)}" target="_blank" rel="noopener">
            <i data-lucide="message-circle"></i>
            <span>Quero informações desta unidade</span>
          </a>
        </div>
      </div>
    </article>
  `;
}

function renderizarUnidades() {
  const grid = document.querySelector("#unidadesGrid");
  if (!grid) return;

  grid.querySelectorAll('.swiper').forEach(el => el.swiper?.destroy(true, true));
  grid.innerHTML = obterUnidadesFiltradas().map(criarCardUnidade).join("");
  inicializarSwipers();
  inicializarGaleria();
  atualizarContadorUnidades();

  if (window.lucide) {
    window.lucide.createIcons();
  }

  if (window.AOS) {
    window.AOS.refresh();
  }
}

function inicializarSwipers() {
  if (!window.Swiper) return;

  obterUnidadesFiltradas().forEach((unidade) => {
    const quantidadeFotos = Array.isArray(unidade.fotos) && unidade.fotos.length
      ? unidade.fotos.length
      : 1;

    new Swiper(`.swiper-${unidade.id}`, {
      loop: quantidadeFotos > 1,
      slidesPerView: 1,
      spaceBetween: 12,
      on: {
        slideChangeTransitionStart(swiper) {
          swiper.el.querySelectorAll("video").forEach((video) => video.pause());
        }
      },
      pagination: {
        el: `.pagination-${unidade.id}`,
        clickable: quantidadeFotos <= 10,
        type: quantidadeFotos > 10 ? "fraction" : "bullets"
      },
      navigation: {
        nextEl: `.next-${unidade.id}`,
        prevEl: `.prev-${unidade.id}`
      }
    });
  });
}

function inicializarGaleria() {
  if (!window.GLightbox) return;

  if (galeriaUnidades) {
    galeriaUnidades.destroy();
  }

  galeriaUnidades = GLightbox({
    selector: ".glightbox",
    touchNavigation: true,
    loop: true
  });
}

function inicializarCarrosselPlanos() {
  const carrossel = document.querySelector("[data-health-plans-carousel]");
  if (!carrossel || !window.Swiper) return;

  const wrapper = carrossel.querySelector(".swiper-wrapper");
  const slidesOriginais = [...carrossel.querySelectorAll(".swiper-slide")];
  if (!wrapper || !slidesOriginais.length) return;

  // Garante slides suficientes para o loop contínuo em qualquer resolução,
  // mesmo quando apenas uma ou duas imagens foram cadastradas.
  let indice = 0;
  while (wrapper.children.length < 12) {
    const clone = slidesOriginais[indice % slidesOriginais.length].cloneNode(true);
    clone.setAttribute("aria-hidden", "true");
    wrapper.appendChild(clone);
    indice += 1;
  }

  new Swiper(carrossel, {
    loop: true,
    loopAdditionalSlides: 6,
    watchOverflow: false,
    allowTouchMove: true,
    grabCursor: true,
    spaceBetween: 18,
    slidesPerView: 2,
    speed: 4200,
    autoplay: {
      delay: 0,
      disableOnInteraction: false,
      pauseOnMouseEnter: true
    },
    breakpoints: {
      640: { slidesPerView: 3 },
      900: { slidesPerView: 4 },
      1120: { slidesPerView: 5 }
    }
  });
}

function atualizarContadorUnidades() {
  const contador = document.querySelector("#unitCount");
  const vazio = document.querySelector("#emptyState");
  const cardsVisiveis = document.querySelectorAll(".unit-card").length;
  const total = cardsVisiveis;
  if (!contador) return;

  contador.textContent =
    total === 1
      ? "1 unidade encontrada"
      : `${total.toLocaleString("pt-BR")} unidades encontradas`;

  if (vazio) {
    vazio.hidden = cardsVisiveis !== 0;
  }
}

function enviarFormularioWhatsapp(event) {
  event.preventDefault();

  const nome = document.querySelector("#nome").value.trim();
  const telefone = document.querySelector("#telefone").value.trim();
  const email = document.querySelector("#email").value.trim();
  const mensagem = document.querySelector("#mensagem").value.trim();

  if (!nome) {
    alert("Preencha o nome antes de enviar.");
    return;
  }

  const texto = `
Olá, ${NOME_ATENDENTE}. Vim pelo site e gostaria de atendimento.

Nome: ${nome}
Telefone: ${telefone || "Não informado"}
E-mail: ${email || "Não informado"}

Mensagem:
${mensagem || "Sem mensagem adicional."}

Gostaria de receber orientação sobre dependência química ou alcoolismo.
`;

  window.open(gerarLinkWhatsappPadrao(texto), "_blank", "noopener");
}

function inicializarFormulario() {
  document
    .querySelector("[data-contact-form]")
    ?.addEventListener("submit", enviarFormularioWhatsapp);
}

function inicializarAOS() {
  if (!window.AOS) return;

  AOS.init({
    duration: 650,
    easing: "ease-out",
    once: true,
    offset: 80
  });
}

function inicializarParallax() {
  const secoes = document.querySelectorAll("[data-parallax]");
  const movimentoReduzido = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  if (!secoes.length || movimentoReduzido) return;

  let agendado = false;

  const atualizar = () => {
    const mobile = window.matchMedia("(max-width: 767px)").matches;
    const intensidade = mobile ? -0.035 : -0.06;
    const limite = mobile ? 28 : 64;

    secoes.forEach((secao) => {
      const rect = secao.getBoundingClientRect();
      const distanciaCentro = rect.top + rect.height / 2 - window.innerHeight / 2;
      const deslocamento = Math.max(Math.min(distanciaCentro * intensidade, limite), -limite);
      secao.style.setProperty("--parallax-y", `${deslocamento}px`);
    });
    agendado = false;
  };

  const aoRolar = () => {
    if (!agendado) {
      window.requestAnimationFrame(atualizar);
      agendado = true;
    }
  };

  window.addEventListener("scroll", aoRolar, { passive: true });
  window.addEventListener("resize", aoRolar);
  atualizar();
}

function inicializarMenuMobile() {
  const botao = document.querySelector("[data-nav-toggle]");
  const menu = document.querySelector("[data-nav-menu]");
  const header = document.querySelector("[data-header]");

  if (!botao || !menu) return;

  botao.addEventListener("click", () => {
    const aberto = botao.getAttribute("aria-expanded") === "true";
    botao.setAttribute("aria-expanded", String(!aberto));
    menu.classList.toggle("is-open", !aberto);
    document.body.classList.toggle("nav-open", !aberto);
  });

  menu.querySelectorAll("a").forEach((link) => {
    link.addEventListener("click", () => {
      botao.setAttribute("aria-expanded", "false");
      menu.classList.remove("is-open");
      document.body.classList.remove("nav-open");
    });
  });

  const atualizarHeader = () => {
    header?.classList.toggle("is-scrolled", window.scrollY > 12);
  };

  window.addEventListener("scroll", atualizarHeader, { passive: true });
  atualizarHeader();
}

function inicializarFAQ() {
  document.querySelectorAll(".faq-item button").forEach((botao) => {
    botao.addEventListener("click", () => {
      const resposta = document.querySelector(`#${botao.getAttribute("aria-controls")}`);
      const aberto = botao.getAttribute("aria-expanded") === "true";

      botao.setAttribute("aria-expanded", String(!aberto));
      if (resposta) {
        resposta.hidden = aberto;
      }
    });
  });
}


function normalizar(valor) { return String(valor || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase(); }
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

document.addEventListener("DOMContentLoaded", () => {
  definirLinksWhatsapp();
  inicializarAOS();
  renderizarUnidades();
  inicializarCarrosselPlanos();
  inicializarFormulario();
  inicializarParallax();
  inicializarMenuMobile();
  inicializarFAQ();
  inicializarFiltros();

  if (window.lucide) {
    window.lucide.createIcons();
  }
});
