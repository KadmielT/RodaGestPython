function initTomSelectInScope(scope = document) {
  scope.querySelectorAll('.js-tom-select').forEach((element) => {
    if (!element.tomselect) {
      new TomSelect(element, {
        create: false
      });
    }
  });
}

document.addEventListener('DOMContentLoaded', () => {
  initTomSelectInScope(document);
  bindExistingImageRemoveButtons();
  bindImageInputLimit();
  updateImageInputText();
});