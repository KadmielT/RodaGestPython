let selectedImageFiles = [];

function updateImageInputText() {
  const textElement = document.getElementById('id_imagens_text');
  if (!textElement) return;

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
  const input = document.getElementById('id_imagens');
  if (!input) return;

  const dataTransfer = new DataTransfer();

  selectedImageFiles.forEach((file) => {
    dataTransfer.items.add(file);
  });

  input.files = dataTransfer.files;
  updateImageInputText();
}

function getExistingImagesCount() {
  return document.querySelectorAll('.js-existing-image-card:not([data-removed="true"])').length;
}

function getActiveExistingImagesCount() {
  return getExistingImagesCount();
}

function removeNewPreviewCards() {
  document.querySelectorAll('.js-new-image-card').forEach((element) => {
    element.remove();
  });
}

function renderImagePreview() {
  const wrapper = document.getElementById('imagens-wrapper');
  if (!wrapper) return;

  removeNewPreviewCards();

  selectedImageFiles.forEach((file, index) => {
    const col = document.createElement('div');
    col.className = 'rg-form-field rg-form-field--span-3 js-new-image-card';

    const card = document.createElement('div');
    card.style.border = '1px solid var(--border-color, #2f2f2f)';
    card.style.borderRadius = '14px';
    card.style.padding = '10px';

    const img = document.createElement('img');
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
    reader.onload = (e) => {
      img.src = e.target.result;
    };
    reader.readAsDataURL(file);

    card.appendChild(img);
    card.appendChild(caption);
    card.appendChild(removeButton);
    col.appendChild(card);
    wrapper.appendChild(col);
  });
}

function bindExistingImageRemoveButtons() {
  document.querySelectorAll('.js-remove-existing-image-btn').forEach((button) => {
    button.addEventListener('click', () => {
      const imageId = button.dataset.imageId;
      const card = document.querySelector(`.js-existing-image-card[data-image-id="${imageId}"]`);
      const hiddenInput = card?.querySelector('.js-remove-existing-image-input');

      if (!card || !hiddenInput) return;

      hiddenInput.disabled = false;
      card.setAttribute('data-removed', 'true');
      card.style.display = 'none';
    });
  });
}

function bindImageInputLimit() {
  const input = document.getElementById('id_imagens');
  if (!input) return;

  input.addEventListener('change', () => {
    const newFiles = Array.from(input.files);

    if (newFiles.length === 0) {
      return;
    }

    const totalFinal = getActiveExistingImagesCount() + selectedImageFiles.length + newFiles.length;

    if (totalFinal > 10) {
      alert('O serviço pode ter no máximo 10 imagens no total.');
      input.value = '';
      updateImageInputText();
      return;
    }

    selectedImageFiles = [...selectedImageFiles, ...newFiles];
    updateImageInputFiles();
    renderImagePreview();
  });
}