function initTomSelectInScope(scope = document) {
  if (typeof TomSelect === 'undefined') {
    return;
  }

  scope.querySelectorAll('.js-tom-select').forEach((element) => {
    if (!element.tomselect) {
      new TomSelect(element, {
        create: false,
      });
    }
  });
}

function initOnlyIntegerInScope(scope = document) {
  if (typeof initOnlyIntegerFields === 'function') {
    initOnlyIntegerFields(scope);
  }
}

function createRowFromTemplate(templateId) {
  const template = document.getElementById(templateId);

  if (!template) {
    return null;
  }

  return template.content.firstElementChild.cloneNode(true);
}

function addRodaRow(selectedValue = '', quantidadeValue = '') {
  const wrapper = document.getElementById('rodas-wrapper');
  const row = createRowFromTemplate('roda-row-template');

  if (!wrapper || !row) {
    return;
  }

  const select = row.querySelector('select[name="roda_id[]"]');
  const input = row.querySelector('input[name="roda_quantidade[]"]');

  if (select) {
    select.value = selectedValue;
  }

  if (input) {
    input.value = quantidadeValue;
  }

  wrapper.appendChild(row);

  initTomSelectInScope(row);
  initOnlyIntegerInScope(row);
}

function destroyTomSelectInRow(row) {
  row.querySelectorAll('select').forEach((select) => {
    if (select.tomselect) {
      select.tomselect.destroy();
    }
  });
}

function removeLastRow(wrapperId) {
  const wrapper = document.getElementById(wrapperId);

  if (!wrapper) {
    return;
  }

  const rows = wrapper.querySelectorAll('.item-row');

  if (rows.length > 1) {
    const lastRow = rows[rows.length - 1];

    destroyTomSelectInRow(lastRow);
    lastRow.remove();
  }
}

function getJsonDataFromScript(scriptId) {
  const dataElement = document.getElementById(scriptId);

  if (!dataElement) {
    return [];
  }

  try {
    return JSON.parse(dataElement.textContent);
  } catch (error) {
    return [];
  }
}

function loadInitialDynamicItems() {
  const rodasWrapper = document.getElementById('rodas-wrapper');

  if (!rodasWrapper) {
    return;
  }

  if (rodasWrapper.dataset.loaded === 'true') {
    return;
  }

  const rodasExistentes = getJsonDataFromScript('rodas-iniciais-data');

  if (rodasExistentes.length > 0) {
    rodasExistentes.forEach((item) => {
      addRodaRow(String(item.id), String(item.quantidade));
    });
  } else {
    addRodaRow();
  }

  rodasWrapper.dataset.loaded = 'true';
}

function bindDynamicItemButtons() {
  const addRodaBtn = document.getElementById('add-roda-btn');
  const removeRodaBtn = document.getElementById('remove-roda-btn');

  if (addRodaBtn && addRodaBtn.dataset.bound !== 'true') {
    addRodaBtn.addEventListener('click', (event) => {
      event.preventDefault();
      addRodaRow();
    });

    addRodaBtn.dataset.bound = 'true';
  }

  if (removeRodaBtn && removeRodaBtn.dataset.bound !== 'true') {
    removeRodaBtn.addEventListener('click', (event) => {
      event.preventDefault();
      removeLastRow('rodas-wrapper');
    });

    removeRodaBtn.dataset.bound = 'true';
  }
}

function initVendaDynamicItems() {
  const rodasWrapper = document.getElementById('rodas-wrapper');

  if (!rodasWrapper) {
    return;
  }

  loadInitialDynamicItems();
  bindDynamicItemButtons();
}

document.addEventListener('DOMContentLoaded', initVendaDynamicItems);