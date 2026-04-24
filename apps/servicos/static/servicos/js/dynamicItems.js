function initTomSelectInScope(scope = document) {
  scope.querySelectorAll('.js-tom-select').forEach((element) => {
    if (!element.tomselect) {
      new TomSelect(element, {
        create: false
      });
    }
  });
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

  if (!wrapper || !row) return;

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
  initOnlyIntegerFields(row);
}

function addInsumoRow(selectedValue = '', quantidadeValue = '') {
  const wrapper = document.getElementById('insumos-wrapper');
  const row = createRowFromTemplate('insumo-row-template');

  if (!wrapper || !row) return;

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
  initOnlyIntegerFields(row);
}

function removeLastRow(wrapperId) {
  const wrapper = document.getElementById(wrapperId);
  if (!wrapper) return;

  const rows = wrapper.querySelectorAll('.item-row');

  if (rows.length > 1) {
    const lastRow = rows[rows.length - 1];

    lastRow.querySelectorAll('select').forEach((select) => {
      if (select.tomselect) {
        select.tomselect.destroy();
      }
    });

    lastRow.remove();
  }
}

function loadInitialDynamicItems() {
  const rodasDataElement = document.getElementById('rodas-iniciais-data');
  const insumosDataElement = document.getElementById('insumos-iniciais-data');

  const rodasExistentes = rodasDataElement
    ? JSON.parse(rodasDataElement.textContent)
    : [];

  const insumosExistentes = insumosDataElement
    ? JSON.parse(insumosDataElement.textContent)
    : [];

  if (rodasExistentes.length > 0) {
    rodasExistentes.forEach((item) => {
      addRodaRow(String(item.id), String(item.quantidade));
    });
  } else {
    addRodaRow();
  }

  if (insumosExistentes.length > 0) {
    insumosExistentes.forEach((item) => {
      addInsumoRow(String(item.id), String(item.quantidade));
    });
  } else {
    addInsumoRow();
  }
}

function bindDynamicItemButtons() {
  const addRodaBtn = document.getElementById('add-roda-btn');
  const addInsumoBtn = document.getElementById('add-insumo-btn');
  const removeRodaBtn = document.getElementById('remove-roda-btn');
  const removeInsumoBtn = document.getElementById('remove-insumo-btn');

  if (addRodaBtn) {
    addRodaBtn.addEventListener('click', () => {
      addRodaRow();
    });
  }

  if (addInsumoBtn) {
    addInsumoBtn.addEventListener('click', () => {
      addInsumoRow();
    });
  }

  if (removeRodaBtn) {
    removeRodaBtn.addEventListener('click', () => {
      removeLastRow('rodas-wrapper');
    });
  }

  if (removeInsumoBtn) {
    removeInsumoBtn.addEventListener('click', () => {
      removeLastRow('insumos-wrapper');
    });
  }
}