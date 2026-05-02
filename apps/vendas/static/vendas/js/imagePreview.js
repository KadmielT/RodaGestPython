let selectedNewImages = [];

function getImageInput() {
  return document.getElementById('id_imagens');
}

function getImageInputText() {
  return document.getElementById('id_imagens_text');
}

function getImagesWrapper() {
  return document.getElementById('imagens-wrapper');
}

function getVisibleExistingImagesCount() {
  return document.querySelectorAll('.js-existing-image-card:not([hidden])').length;
}

function updateImageInputFiles() {
  const input = getImageInput();

  if (!input) {
    return;
  }

  const dataTransfer = new DataTransfer();

  selectedNewImages.forEach((file) => {
    dataTransfer.items.add(file);
  });

  input.files = dataTransfer.files;
}

function updateImageInputText() {
  const textElement = getImageInputText();

  if (!textElement) {
    return;
  }

  if (selectedNewImages.length === 0) {
    textElement.textContent = 'Nenhum arquivo selecionado.';
    return;
  }

  if (selectedNewImages.length === 1) {
    textElement.textContent = selectedNewImages[0].name;
    return;
  }

  textElement.textContent = `${selectedNewImages.length} imagens selecionadas.`;
}

function removeNewImage(index) {
  selectedNewImages.splice(index, 1);
  updateImageInputFiles();
  updateImageInputText();
  renderNewImagePreview();
}

function renderNewImagePreview() {
  const wrapper = getImagesWrapper();

  if (!wrapper) {
    return;
  }

  wrapper.querySelectorAll('.js-new-image-card').forEach((card) => {
    card.remove();
  });

  selectedNewImages.forEach((file, index) => {
    const reader = new FileReader();

    reader.onload = function (event) {
      const card = document.createElement('div');
      card.className = 'rg-form-field rg-form-field--span-3 js-new-image-card';

      card.innerHTML = `
        <div style="border: 1px solid var(--border-color, #2f2f2f); border-radius: 14px; padding: 10px;">
          <img
            src="${event.target.result}"
            alt="Nova imagem da venda"
            style="width: 100%; height: 180px; object-fit: cover; border-radius: 10px; display: block; margin-bottom: 10px;"
          >

          <div style="font-size: 13px; opacity: .85; margin-bottom: 10px;">
            ${file.name}
          </div>

          <button
            type="button"
            class="rg-btn rg-btn--danger js-remove-new-image-btn"
            data-image-index="${index}"
            style="width: 100%;"
          >
            Remover
          </button>
        </div>
      `;

      wrapper.appendChild(card);

      const removeButton = card.querySelector('.js-remove-new-image-btn');

      removeButton.addEventListener('click', () => {
        removeNewImage(index);
      });
    };

    reader.readAsDataURL(file);
  });
}

function bindExistingImageRemoveButtons() {
  document.querySelectorAll('.js-remove-existing-image-btn').forEach((button) => {
    if (button.dataset.bound === 'true') {
      return;
    }

    button.addEventListener('click', () => {
      const imageId = button.dataset.imageId;
      const card = document.querySelector(`.js-existing-image-card[data-image-id="${imageId}"]`);

      if (!card) {
        return;
      }

      const input = card.querySelector('.js-remove-existing-image-input');

      if (input) {
        input.disabled = false;
      }

      card.hidden = true;
    });

    button.dataset.bound = 'true';
  });
}

function bindImageInputLimit() {
  const input = getImageInput();

  if (!input) {
    return;
  }

  input.addEventListener('change', () => {
    const newFiles = Array.from(input.files);
    const existingCount = getVisibleExistingImagesCount();
    const totalAfterSelection = existingCount + selectedNewImages.length + newFiles.length;

    if (totalAfterSelection > 10) {
      alert('A venda pode ter até 10 imagens no total.');
      input.value = '';
      return;
    }

    selectedNewImages = selectedNewImages.concat(newFiles);

    updateImageInputFiles();
    updateImageInputText();
    renderNewImagePreview();
  });
}