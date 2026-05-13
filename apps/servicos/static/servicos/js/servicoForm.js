document.addEventListener('DOMContentLoaded', () => {
  if (typeof initTomSelectInScope === 'function') {
    initTomSelectInScope(document);
  }

  if (typeof loadInitialDynamicItems === 'function') {
    loadInitialDynamicItems();
  }

  if (typeof bindDynamicItemButtons === 'function') {
    bindDynamicItemButtons();
  }

  if (typeof initServiceImagePreview === 'function') {
    initServiceImagePreview();
  } else {
    if (typeof bindExistingImageRemoveButtons === 'function') {
      bindExistingImageRemoveButtons();
    }

    if (typeof bindImageInputLimit === 'function') {
      bindImageInputLimit();
    }

    if (typeof updateImageInputText === 'function') {
      updateImageInputText();
    }
  }
});