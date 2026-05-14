(function () {
  const SELECTOR = [
    '.js-tom-select',
    '.js-servico-tom-select',
    '.js-despesa-tom-select',
    '.js-usuario-status-select'
  ].join(', ');

  function getSelectPlaceholder(select) {
    if (!select) {
      return 'Selecione uma opção';
    }

    if (select.dataset.placeholder) {
      return select.dataset.placeholder;
    }

    const firstEmptyOption = select.querySelector('option[value=""]');

    if (firstEmptyOption && firstEmptyOption.textContent.trim()) {
      const text = firstEmptyOption.textContent.trim();

      if (text === '---------') {
        return 'Selecione uma opção';
      }

      return text;
    }

    return 'Selecione uma opção';
  }

  function shouldDisableSearch(select) {
    if (!select) {
      return false;
    }

    return (
      select.dataset.noSearch === 'true' ||
      select.dataset.noSearch === '1' ||
      select.classList.contains('js-tom-select-no-search') ||
      select.classList.contains('js-usuario-status-select')
    );
  }

  function getOptionsFromSelect(select) {
    return Array.from(select.options)
      .filter(function (option) {
        return option.value !== '';
      })
      .map(function (option, index) {
        return {
          value: option.value,
          text: option.textContent.trim(),
          disabled: option.disabled,
          $order: index,
        };
      });
  }

  function initRgTomSelects(scope = document) {
    if (typeof TomSelect === 'undefined') {
      return;
    }

    const root = scope || document;

    root.querySelectorAll(SELECTOR).forEach(function (select) {
      if (!select || select.tomselect) {
        return;
      }

      const currentValue = select.value || '';
      const options = getOptionsFromSelect(select);

      const config = {
        create: false,
        allowEmptyOption: false,
        maxOptions: null,

        valueField: 'value',
        labelField: 'text',
        searchField: ['text'],

        placeholder: getSelectPlaceholder(select),

        sortField: [
          {
            field: '$order',
            direction: 'asc',
          },
        ],

        render: {
          option: function (data, escape) {
            return `<div>${escape(data.text || '')}</div>`;
          },
          item: function (data, escape) {
            return `<div>${escape(data.text || '')}</div>`;
          },
        },
      };

      if (shouldDisableSearch(select)) {
        config.controlInput = null;
      }

      const tomSelect = new TomSelect(select, config);

      tomSelect.clearOptions();

      options.forEach(function (option) {
        tomSelect.addOption(option);
      });

      tomSelect.refreshOptions(false);

      if (
        currentValue &&
        options.some(function (option) {
          return option.value === currentValue;
        })
      ) {
        tomSelect.setValue(currentValue, true);
      } else {
        tomSelect.clear(true);
        select.value = '';
      }
    });
  }

  window.initRgTomSelects = initRgTomSelects;
  window.initTomSelectInScope = initRgTomSelects;
  window.initServicoTomSelectInScope = initRgTomSelects;
  window.initDespesaTomSelects = initRgTomSelects;

  document.addEventListener('DOMContentLoaded', function () {
    initRgTomSelects(document);
  });
})();