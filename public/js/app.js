/* SysHSENA - comportamiento común de la interfaz */
(() => {
  const root = document.documentElement;

  // ----- Tema claro / oscuro (se recuerda en el navegador) -----
  const themeBtn = document.getElementById('themeBtn');
  const iconoTema = () => (root.dataset.theme === 'dark' ? '☀' : '☾');
  if (themeBtn) {
    themeBtn.textContent = iconoTema();
    themeBtn.addEventListener('click', () => {
      const nuevo = root.dataset.theme === 'dark' ? 'light' : 'dark';
      root.dataset.theme = nuevo;
      localStorage.setItem('syshsena-tema', nuevo);
      themeBtn.textContent = iconoTema();
    });
  }

  // ----- Menú lateral en móviles -----
  const sidebar = document.getElementById('sidebar');
  const overlay = document.getElementById('mobileOverlay');
  const menuBtn = document.getElementById('menuBtn');
  if (sidebar && overlay && menuBtn) {
    const cerrar = () => { sidebar.classList.remove('open'); overlay.classList.remove('show'); };
    menuBtn.addEventListener('click', () => { sidebar.classList.add('open'); overlay.classList.add('show'); });
    overlay.addEventListener('click', cerrar);
    document.addEventListener('keydown', e => { if (e.key === 'Escape') cerrar(); });
  }

  // ----- Aviso emergente (toast) -----
  window.mostrarAviso = (mensaje) => {
    const t = document.getElementById('toast');
    if (!t) return;
    t.textContent = mensaje;
    t.classList.add('show');
    setTimeout(() => t.classList.remove('show'), 2600);
  };
  document.querySelectorAll('.action-toast').forEach(b =>
    b.addEventListener('click', () => window.mostrarAviso(b.dataset.msg)));

  // ----- Buscador rápido de tablas: <input class="table-search" data-table="idTabla"> -----
  document.querySelectorAll('.table-search').forEach(input => input.addEventListener('input', () => {
    const q = input.value.toLowerCase();
    const tabla = document.getElementById(input.dataset.table);
    if (!tabla) return;
    tabla.querySelectorAll('tbody tr').forEach(r => {
      r.style.display = r.textContent.toLowerCase().includes(q) ? '' : 'none';
    });
  }));
})();

  /* ----- Cancelar reserva: pide el motivo en la propia lista ----- */
  document.querySelectorAll('a[data-motivo-pendiente]').forEach(enlace => {
    enlace.addEventListener('click', e => {
      e.preventDefault();
      const motivo = window.prompt('Escribe el motivo de la cancelación (obligatorio):');
      if (motivo && motivo.trim()) {
        const url = new URL(enlace.href, window.location.origin);
        url.searchParams.set('motivo', motivo.trim());
        window.location.href = url.pathname + url.search;
      } else if (motivo !== null) {
        window.mostrarAviso('El motivo es obligatorio para cancelar.');
      }
    });
  });
