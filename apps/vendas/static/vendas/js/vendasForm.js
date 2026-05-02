document.addEventListener('DOMContentLoaded', () => {
  initTomSelectInScope(document);
  loadInitialDynamicItems();
  bindDynamicItemButtons();
  bindExistingImageRemoveButtons();
  bindImageInputLimit();
  updateImageInputText();
});