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

function addInsumoRow(selectedValue = '', quantidadeValue = '') {
  const wrapper = document.getElementById('insumos-wrapper');
  const row = createRowFromTemplate('insumo-row-template');

  if (!wrapper || !row) {
    return;
  }

  const select = row.querySelector('select[name="insumo_id[]"]');
  const input = row.querySelector('input[name="insumo_quantidade[]"]');

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
  const insumosWrapper = document.getElementById('insumos-wrapper');

  if (!rodasWrapper || !insumosWrapper) {
    return;
  }

  if (rodasWrapper.dataset.loaded === 'true' && insumosWrapper.dataset.loaded === 'true') {
    return;
  }

  const rodasExistentes = getJsonDataFromScript('rodas-iniciais-data');
  const insumosExistentes = getJsonDataFromScript('insumos-iniciais-data');

  if (rodasWrapper.dataset.loaded !== 'true') {
    if (rodasExistentes.length > 0) {
      rodasExistentes.forEach((item) => {
        addRodaRow(String(item.id), String(item.quantidade));
      });
    } else {
      addRodaRow();
    }

    rodasWrapper.dataset.loaded = 'true';
  }

  if (insumosWrapper.dataset.loaded !== 'true') {
    if (insumosExistentes.length > 0) {
      insumosExistentes.forEach((item) => {
        addInsumoRow(String(item.id), String(item.quantidade));
      });
    } else {
      addInsumoRow();
    }

    insumosWrapper.dataset.loaded = 'true';
  }
}

function bindDynamicItemButtons() {
  const addRodaBtn = document.getElementById('add-roda-btn');
  const addInsumoBtn = document.getElementById('add-insumo-btn');
  const removeRodaBtn = document.getElementById('remove-roda-btn');
  const removeInsumoBtn = document.getElementById('remove-insumo-btn');

  if (addRodaBtn && addRodaBtn.dataset.bound !== 'true') {
    addRodaBtn.addEventListener('click', (event) => {
      event.preventDefault();
      addRodaRow();
    });

    addRodaBtn.dataset.bound = 'true';
  }

  if (addInsumoBtn && addInsumoBtn.dataset.bound !== 'true') {
    addInsumoBtn.addEventListener('click', (event) => {
      event.preventDefault();
      addInsumoRow();
    });

    addInsumoBtn.dataset.bound = 'true';
  }

  if (removeRodaBtn && removeRodaBtn.dataset.bound !== 'true') {
    removeRodaBtn.addEventListener('click', (event) => {
      event.preventDefault();
      removeLastRow('rodas-wrapper');
    });

    removeRodaBtn.dataset.bound = 'true';
  }

  if (removeInsumoBtn && removeInsumoBtn.dataset.bound !== 'true') {
    removeInsumoBtn.addEventListener('click', (event) => {
      event.preventDefault();
      removeLastRow('insumos-wrapper');
    });

    removeInsumoBtn.dataset.bound = 'true';
  }
}

function initDynamicItems() {
  const rodasWrapper = document.getElementById('rodas-wrapper');
  const insumosWrapper = document.getElementById('insumos-wrapper');

  if (!rodasWrapper || !insumosWrapper) {
    return;
  }

  loadInitialDynamicItems();
  bindDynamicItemButtons();
}

document.addEventListener('DOMContentLoaded', initDynamicItems);