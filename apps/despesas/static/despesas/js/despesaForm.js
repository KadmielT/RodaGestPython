function initDespesaTomSelects(scope = document) {
  if (typeof TomSelect === 'undefined') {
    return;
  }

  scope.querySelectorAll('.js-despesa-tom-select').forEach((element) => {
    if (element.tomselect) {
      element.tomselect.destroy();
    }

    const currentValue = element.dataset.current || '';

    const tomSelect = new TomSelect(element, {
      create: false,
      allowEmptyOption: true,
      placeholder: element.dataset.placeholder || 'Selecione uma opção',
      searchField: ['text'],
      sortField: [
        {
          field: '$order',
          direction: 'asc',
        },
      ],
    });

    if (currentValue) {
      tomSelect.setValue(currentValue, true);
    } else {
      tomSelect.clear(true);
      element.value = '';
    }
  });
}

document.addEventListener('DOMContentLoaded', () => {
  initDespesaTomSelects(document);

  if (typeof bindExistingImageRemoveButtons === 'function') {
    bindExistingImageRemoveButtons();
  }

  if (typeof bindImageInputLimit === 'function') {
    bindImageInputLimit();
  }

  if (typeof updateImageInputText === 'function') {
    updateImageInputText();
  }
});