function formatMoneyBr(value) {
  const digits = value.replace(/\D/g, '');

  if (!digits) {
    return 'R$ 0,00';
  }

  const number = (parseInt(digits, 10) / 100).toFixed(2);
  const formatted = number
    .replace('.', ',')
    .replace(/\B(?=(\d{3})+(?!\d))/g, '.');

  return `R$ ${formatted}`;
}

function initValorUnitarioMask() {
  const fields = document.querySelectorAll('.js-money-br');

  fields.forEach((field) => {
    if (!field.value || field.value.trim() === '') {
      field.value = 'R$ 0,00';
    } else {
      field.value = formatMoneyBr(field.value);
    }

    field.addEventListener('focus', (event) => {
      if (!event.target.value || event.target.value.trim() === '') {
        event.target.value = 'R$ 0,00';
      }
    });

    field.addEventListener('input', (event) => {
      const cursorAtEnd = event.target.selectionStart === event.target.value.length;
      event.target.value = formatMoneyBr(event.target.value);

      if (cursorAtEnd) {
        requestAnimationFrame(() => {
          event.target.setSelectionRange(event.target.value.length, event.target.value.length);
        });
      }
    });

    field.addEventListener('blur', (event) => {
      event.target.value = formatMoneyBr(event.target.value);
    });
  });
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initValorUnitarioMask);
} else {
  initValorUnitarioMask();
}