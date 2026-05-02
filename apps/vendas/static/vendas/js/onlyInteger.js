function bindOnlyIntegerField(field) {
  if (!field || field.dataset.onlyIntegerBound === 'true') {
    return;
  }

  field.addEventListener('keydown', (event) => {
    const blockedKeys = ['e', 'E', '+', '-', ',', '.'];

    if (blockedKeys.includes(event.key)) {
      event.preventDefault();
    }
  });

  field.addEventListener('input', (event) => {
    event.target.value = event.target.value.replace(/\D/g, '');
  });

  field.addEventListener('paste', (event) => {
    event.preventDefault();
    const pastedText = (event.clipboardData || window.clipboardData).getData('text');
    const onlyDigits = pastedText.replace(/\D/g, '');
    event.target.value = onlyDigits;
    event.target.dispatchEvent(new Event('input', { bubbles: true }));
  });

  field.dataset.onlyIntegerBound = 'true';
}

function initOnlyIntegerFields(scope = document) {
  const fields = scope.querySelectorAll('.js-only-integer');
  fields.forEach((field) => bindOnlyIntegerField(field));
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => initOnlyIntegerFields(document));
} else {
  initOnlyIntegerFields(document);
}