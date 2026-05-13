(function () {
  const MAX_IMAGES = 10;
  let selectedImageFiles = [];

  function getImageInput() {
    return document.getElementById('id_imagens');
  }

  function getImageTextElement() {
    return document.getElementById('id_imagens_text');
  }

  function getImageWrapper() {
    return document.getElementById('imagens-wrapper');
  }

  function updateImageInputText() {
    const textElement = getImageTextElement();

    if (!textElement) {
      return;
    }

    if (selectedImageFiles.length === 0) {
      textElement.textContent = 'Nenhum arquivo selecionado.';
      return;
    }

    if (selectedImageFiles.length === 1) {
      textElement.textContent = selectedImageFiles[0].name;
      return;
    }

    textElement.textContent = `${selectedImageFiles.length} arquivos selecionados.`;
  }

  function updateImageInputFiles() {
    const input = getImageInput();

    if (!input) {
      return;
    }

    if (typeof DataTransfer === 'undefined') {
      updateImageInputText();
      return;
    }

    const dataTransfer = new DataTransfer();

    selectedImageFiles.forEach((file) => {
      dataTransfer.items.add(file);
    });

    input.files = dataTransfer.files;
    updateImageInputText();
  }

  function getExistingImagesCount() {
    return document.querySelectorAll(
      '.js-existing-image-card:not([data-removed="true"])'
    ).length;
  }

  function getActiveExistingImagesCount() {
    return getExistingImagesCount();
  }

  function removeNewPreviewCards() {
    document.querySelectorAll('.js-new-image-card').forEach((element) => {
      element.remove();
    });
  }

  function createImageCard(file, index) {
    const col = document.createElement('div');
    col.className = 'rg-form-field rg-form-field--span-3 js-new-image-card';

    const card = document.createElement('div');
    card.style.border = '1px solid var(--border-color, #2f2f2f)';
    card.style.borderRadius = '14px';
    card.style.padding = '10px';

    const img = document.createElement('img');
    img.alt = file.name;
    img.style.width = '100%';
    img.style.height = '180px';
    img.style.objectFit = 'cover';
    img.style.borderRadius = '10px';
    img.style.display = 'block';
    img.style.marginBottom = '10px';

    const caption = document.createElement('div');
    caption.style.fontSize = '13px';
    caption.style.opacity = '.85';
    caption.style.marginBottom = '10px';
    caption.textContent = file.name;

    const removeButton = document.createElement('button');
    removeButton.type = 'button';
    removeButton.className = 'rg-btn rg-btn--danger';
    removeButton.textContent = 'Remover';
    removeButton.style.width = '100%';

    removeButton.addEventListener('click', () => {
      selectedImageFiles.splice(index, 1);
      updateImageInputFiles();
      renderImagePreview();
    });

    const reader = new FileReader();

    reader.onload = (event) => {
      img.src = event.target.result;
    };

    reader.readAsDataURL(file);

    card.appendChild(img);
    card.appendChild(caption);
    card.appendChild(removeButton);

    col.appendChild(card);

    return col;
  }

  function renderImagePreview() {
    const wrapper = getImageWrapper();

    if (!wrapper) {
      return;
    }

    removeNewPreviewCards();

    selectedImageFiles.forEach((file, index) => {
      const card = createImageCard(file, index);
      wrapper.appendChild(card);
    });
  }

  function bindExistingImageRemoveButtons() {
    document.querySelectorAll('.js-remove-existing-image-btn').forEach((button) => {
      if (button.dataset.bound === 'true') {
        return;
      }

      button.addEventListener('click', () => {
        const imageId = button.dataset.imageId;
        const card = document.querySelector(
          `.js-existing-image-card[data-image-id="${imageId}"]`
        );
        const hiddenInput = card?.querySelector('.js-remove-existing-image-input');

        if (!card || !hiddenInput) {
          return;
        }

        hiddenInput.disabled = false;
        card.setAttribute('data-removed', 'true');
        card.style.display = 'none';
        updateImageInputText();
      });

      button.dataset.bound = 'true';
    });
  }

  function bindImageInputLimit() {
    const input = getImageInput();

    if (!input || input.dataset.bound === 'true') {
      return;
    }

    input.addEventListener('change', () => {
      const newFiles = Array.from(input.files || []).filter((file) => {
        return file.type && file.type.startsWith('image/');
      });

      if (newFiles.length === 0) {
        updateImageInputText();
        return;
      }

      const totalFinal =
        getActiveExistingImagesCount() +
        selectedImageFiles.length +
        newFiles.length;

      if (totalFinal > MAX_IMAGES) {
        alert(`A venda pode ter no máximo ${MAX_IMAGES} imagens no total.`);
        input.value = '';
        updateImageInputText();
        return;
      }

      selectedImageFiles = [...selectedImageFiles, ...newFiles];

      updateImageInputFiles();
      renderImagePreview();
    });

    input.dataset.bound = 'true';
  }

  function initVendaImagePreview() {
    bindExistingImageRemoveButtons();
    bindImageInputLimit();
    updateImageInputText();
    renderImagePreview();
  }

  window.updateImageInputText = updateImageInputText;
  window.updateImageInputFiles = updateImageInputFiles;
  window.getExistingImagesCount = getExistingImagesCount;
  window.getActiveExistingImagesCount = getActiveExistingImagesCount;
  window.removeNewPreviewCards = removeNewPreviewCards;
  window.renderImagePreview = renderImagePreview;
  window.bindExistingImageRemoveButtons = bindExistingImageRemoveButtons;
  window.bindImageInputLimit = bindImageInputLimit;
  window.initVendaImagePreview = initVendaImagePreview;

  document.addEventListener('DOMContentLoaded', initVendaImagePreview);
})();