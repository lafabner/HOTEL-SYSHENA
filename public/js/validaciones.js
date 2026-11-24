/* ==========================================================
   SysHSENA - Validaciones del lado del cliente
   Campos marcados con data-solo-numeros: solo aceptan dígitos.
   El servidor también valida; esto evita errores de digitación.
   ========================================================== */
(function () {
  'use strict';

  function soloDigitos(valor) {
    return valor.replace(/[^\d]/g, '');
  }

  // Sanitiza mientras se escribe y cuando se pega contenido
  document.addEventListener('input', function (e) {
    var campo = e.target;
    if (campo && campo.dataset && campo.dataset.soloNumeros !== undefined) {
      var limpio = soloDigitos(campo.value);
      if (limpio !== campo.value) {
        campo.value = limpio;
        campo.dispatchEvent(new Event('input', { bubbles: true }));
      }
    }
  });

  // Bloquea teclas que no son dígitos ni teclas de edición
  document.addEventListener('keydown', function (e) {
    var campo = e.target;
    if (!campo || !campo.dataset || campo.dataset.soloNumeros === undefined) return;
    var teclasPermitidas = ['Backspace', 'Delete', 'Tab', 'Escape', 'Enter',
                            'Home', 'End', 'ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown'];
    var esControl = e.ctrlKey || e.metaKey;
    if (teclasPermitidas.indexOf(e.key) !== -1 || esControl) return;
    if (e.key && e.key.length === 1 && !/\d/.test(e.key)) {
      e.preventDefault();
    }
  });

  // Al pegar, deja únicamente los dígitos del contenido pegado
  document.addEventListener('paste', function (e) {
    var campo = e.target;
    if (!campo || !campo.dataset || campo.dataset.soloNumeros === undefined) return;
    var texto = (e.clipboardData || window.clipboardData).getData('text') || '';
    e.preventDefault();
    campo.value = soloDigitos(texto);
    campo.dispatchEvent(new Event('input', { bubbles: true }));
  });
})();
