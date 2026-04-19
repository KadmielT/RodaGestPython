document.addEventListener('DOMContentLoaded', () => {
  const fields = document.querySelectorAll('.js-only-integer');

  fields.forEach((field) => {
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
  });
});