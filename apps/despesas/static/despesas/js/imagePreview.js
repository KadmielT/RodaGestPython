let selectedImageFiles = [];

const MAX_FILES = 10;

function updateImageInputText() {
  const textElement = document.getElementById('id_imagens_text');

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
  const input = document.getElementById('id_imagens');

  if (!input) {
    return;
  }

  const dataTransfer = new DataTransfer();

  selectedImageFiles.forEach((file) => {
    dataTransfer.items.add(file);
  });

  input.files = dataTransfer.files;
  updateImageInputText();
}

function getFileExtension(fileName) {
  const parts = fileName.split('.');

  if (parts.length <= 1) {
    return 'ARQUIVO';
  }

  return parts.pop().toUpperCase();
}

function getExistingImagesCount() {
  return document.querySelectorAll('.js-existing-image-card:not([data-removed="true"])').length;
}

function getActiveExistingImagesCount() {
  return getExistingImagesCount();
}

function getTotalSelectedFilesCount() {
  return getActiveExistingImagesCount() + selectedImageFiles.length;
}

function removeNewPreviewCards() {
  document.querySelectorAll('.js-new-image-card').forEach((element) => {
    element.remove();
  });
}

function fileAlreadySelected(file) {
  return selectedImageFiles.some((selectedFile) => (
    selectedFile.name === file.name &&
    selectedFile.size === file.size &&
    selectedFile.lastModified === file.lastModified
  ));
}

function createPreviewElement(file) {
  if (file.type && file.type.startsWith('image/')) {
    const img = document.createElement('img');

    img.style.width = '100%';
    img.style.height = '72px';
    img.style.objectFit = 'cover';
    img.style.borderRadius = '10px';
    img.style.display = 'block';

    const reader = new FileReader();

    reader.onload = (event) => {
      img.src = event.target.result;
    };

    reader.readAsDataURL(file);

    return img;
  }

  const icon = document.createElement('div');

  icon.style.width = '100%';
  icon.style.height = '72px';
  icon.style.borderRadius = '10px';
  icon.style.display = 'flex';
  icon.style.alignItems = 'center';
  icon.style.justifyContent = 'center';
  icon.style.fontSize = '18px';
  icon.style.fontWeight = '700';
  icon.style.background = 'rgba(255, 255, 255, 0.06)';
  icon.style.border = '1px solid var(--border-color, #2f2f2f)';
  icon.textContent = getFileExtension(file.name);

  return icon;
}

function renderImagePreview() {
  const wrapper = document.getElementById('imagens-wrapper');

  if (!wrapper) {
    return;
  }

  removeNewPreviewCards();

  selectedImageFiles.forEach((file, index) => {
    const col = document.createElement('div');
    col.className = 'rg-form-field rg-form-field--span-3 js-new-image-card';

    const card = document.createElement('div');
    card.style.border = '1px solid var(--border-color, #2f2f2f)';
    card.style.borderRadius = '14px';
    card.style.padding = '12px';
    card.style.minHeight = '160px';
    card.style.display = 'flex';
    card.style.flexDirection = 'column';
    card.style.justifyContent = 'space-between';
    card.style.gap = '10px';

    const preview = createPreviewElement(file);

    const caption = document.createElement('div');
    caption.style.fontSize = '13px';
    caption.style.opacity = '.85';
    caption.style.wordBreak = 'break-word';
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

    card.appendChild(preview);
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

      if (!card || !hiddenInput) {
        return;
      }

      hiddenInput.disabled = false;
      card.setAttribute('data-removed', 'true');
      card.style.display = 'none';
    });
  });
}

function bindImageInputLimit() {
  const input = document.getElementById('id_imagens');

  if (!input) {
    return;
  }

  input.addEventListener('change', () => {
    const newFiles = Array.from(input.files);

    if (newFiles.length === 0) {
      return;
    }

    const validNewFiles = [];

    newFiles.forEach((file) => {
      if (!fileAlreadySelected(file)) {
        validNewFiles.push(file);
      }
    });

    const totalFinal = getActiveExistingImagesCount() + selectedImageFiles.length + validNewFiles.length;

    if (totalFinal > MAX_FILES) {
      const arquivosAtuais = getTotalSelectedFilesCount();
      const arquivosRestantes = Math.max(MAX_FILES - arquivosAtuais, 0);

      alert(
        `A despesa pode ter no máximo ${MAX_FILES} arquivos no total. ` +
        `Você ainda pode adicionar ${arquivosRestantes} arquivo(s).`
      );

      input.value = '';
      updateImageInputFiles();
      renderImagePreview();
      return;
    }

    selectedImageFiles = [...selectedImageFiles, ...validNewFiles];

    updateImageInputFiles();
    renderImagePreview();
  });
}