function initUsuarioStatusSelect() {
  if (typeof TomSelect === 'undefined') {
    return;
  }

  const statusSelect = document.querySelector('.js-usuario-status-select');

  if (!statusSelect) {
    return;
  }

  if (statusSelect.tomselect) {
    statusSelect.tomselect.destroy();
  }

  new TomSelect(statusSelect, {
    create: false,
    allowEmptyOption: false,
    placeholder: statusSelect.dataset.placeholder || 'Selecione o status',
    controlInput: null,
    sortField: [
      {
        field: '$order',
        direction: 'asc',
      },
    ],
  });
}

document.addEventListener('DOMContentLoaded', () => {
  initUsuarioStatusSelect();
});