document.addEventListener('DOMContentLoaded', function () {
  const cinema = document.querySelector('.hotel-cinema');
  if (cinema) {
    const slides = Array.from(cinema.querySelectorAll('.cinema-slide'));
    const dots = Array.from(cinema.querySelectorAll('[data-slide-index]'));
    const pause = cinema.querySelector('[data-cinema-action="pause"]');
    const status = cinema.querySelector('#cinema-status');
    const reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
    let current = 0, paused = reduced.matches, timer = null, touchStart = null, inView = true;
    function media() {
      cinema.querySelectorAll('video').forEach(function (video) {
        const active = video.closest('.cinema-slide') === slides[current];
        if (active && !paused && !document.hidden && inView) {
          if (!video.src) video.src = video.dataset.videoSrc;
          video.play().catch(function () { /* El poster es la alternativa sin reproducción. */ });
        } else video.pause();
      });
    }
    function schedule() {
      clearTimeout(timer);
      if (!paused && !document.hidden && inView) timer = setTimeout(function () { show(current + 1, false); }, 9000);
      pause.textContent = paused ? 'Reproducir' : 'Pausar';
      pause.setAttribute('aria-label', paused ? 'Reproducir presentación' : 'Pausar presentación');
      pause.setAttribute('aria-pressed', String(paused));
      media();
    }
    function show(index, manual) {
      current = (index + slides.length) % slides.length;
      slides.forEach(function (slide, i) {
        const active = i === current;
        // Cada escena parte debajo de la anterior: movimiento vertical, sin secuestrar el scroll.
        slide.style.transform = 'translateY(' + ((i - current) * 100) + '%)';
        slide.classList.toggle('is-active', active);
        slide.setAttribute('aria-hidden', String(!active));
        slide.inert = !active;
        if (active) dots[i].setAttribute('aria-current', 'true');
        else dots[i].removeAttribute('aria-current');
      });
      if (manual) status.textContent = 'Escena ' + (current + 1) + ' de ' + slides.length + ': ' + slides[current].dataset.slideLabel;
      schedule();
    }
    dots.forEach(function (dot) { dot.addEventListener('click', function () { paused = true; show(Number(dot.dataset.slideIndex), true); }); });
    cinema.querySelector('[data-cinema-action="prev"]').addEventListener('click', function () { paused = true; show(current - 1, true); });
    cinema.querySelector('[data-cinema-action="next"]').addEventListener('click', function () { paused = true; show(current + 1, true); });
    pause.addEventListener('click', function () { paused = !paused; schedule(); });
    cinema.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
        e.preventDefault(); paused = true; show(current + (e.key === 'ArrowDown' ? 1 : -1), true);
      }
    });
    cinema.addEventListener('focusin', function (e) {
      if (e.target !== pause) { paused = true; schedule(); }
    });
    // Un gesto sobre la imagen cambia de escena; fuera del carrusel la página se desplaza normalmente.
    cinema.addEventListener('touchstart', function (e) {
      if (e.target.closest('button,a')) return;
      touchStart = {x: e.touches[0].clientX, y: e.touches[0].clientY};
    }, {passive: true});
    cinema.addEventListener('touchend', function (e) {
      if (!touchStart) return;
      const dy = e.changedTouches[0].clientY - touchStart.y;
      const dx = e.changedTouches[0].clientX - touchStart.x;
      if (Math.abs(dy) > 65 && Math.abs(dy) > Math.abs(dx) * 1.3) {
        paused = true; show(current + (dy < 0 ? 1 : -1), true);
      }
      touchStart = null;
    }, {passive: true});
    document.addEventListener('visibilitychange', schedule);
    reduced.addEventListener('change', function () { if (reduced.matches) { paused = true; schedule(); } });
    if ('IntersectionObserver' in window) {
      new IntersectionObserver(function (entries) {
        inView = entries[0].isIntersecting;
        schedule();
      }, {threshold: 0.1}).observe(cinema);
    }
    show(0, false);
  }
  const boton = document.querySelector('.hotel-menu-toggle');
  const nav = document.querySelector('#hotel-nav');
  if (boton && nav) {
    boton.addEventListener('click', function () {
      const abierto = boton.getAttribute('aria-expanded') !== 'true';
      boton.setAttribute('aria-expanded', String(abierto));
      nav.classList.toggle('is-open', abierto);
    });
    nav.addEventListener('click', function (e) {
      if (e.target.closest('a')) {
        nav.classList.remove('is-open');
        boton.setAttribute('aria-expanded', 'false');
      }
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') { nav.classList.remove('is-open'); boton.setAttribute('aria-expanded', 'false'); }
    });
  }
  const entrada = document.querySelector('#public-entrada');
  const salida = document.querySelector('#public-salida');
  if (entrada && salida) {
    entrada.addEventListener('change', function () {
      if (!entrada.value) return;
      const fecha = new Date(entrada.value + 'T12:00:00');
      fecha.setDate(fecha.getDate() + 1);
      const siguiente = fecha.getFullYear() + '-' + String(fecha.getMonth()+1).padStart(2,'0') + '-' + String(fecha.getDate()).padStart(2,'0');
      salida.min = siguiente;
      if (salida.value && salida.value < siguiente) salida.value = '';
    });
  }
});
