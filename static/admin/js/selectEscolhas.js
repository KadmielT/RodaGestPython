document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("changelist-form");
  if (!form) return;

  const actionsSelect = form.querySelector("select[name='action']");
  if (!actionsSelect) return;

  // Esconde a dropdown "Action" padrão (você já estava fazendo isso via CSS, ok)
  // Mas aqui não precisamos remover do DOM: só vamos usar por trás.

  // Container de ações custom
  const container = document.createElement("div");
  container.className = "rodagest-actions";

  // Botão de excluir selecionados
  const deleteBtn = document.createElement("button");
  deleteBtn.type = "button";
  deleteBtn.className = "button rodagest-delete-btn";
  deleteBtn.id = "rg-delete-selected";
  deleteBtn.style.display = "none";
  deleteBtn.textContent = "Excluir selecionados";

  // Contador
  const countEl = document.createElement("span");
  countEl.id = "rg-selected-count";
  countEl.className = "rodagest-selected-count";
  countEl.style.display = "none";

  container.appendChild(deleteBtn);
  container.appendChild(countEl);

  // Insere o container perto do topo (acima da tabela)
  const defaultActions = form.querySelector(".actions");
  if (defaultActions && defaultActions.parentNode) {
    defaultActions.parentNode.insertBefore(container, defaultActions);
  } else {
    form.insertBefore(container, form.firstChild);
  }

  // ---------- Modal ----------
  function ensureModal() {
    let modal = document.getElementById("rg-modal");
    if (modal) return modal;

    modal = document.createElement("div");
    modal.id = "rg-modal";
    modal.className = "rg-modal";
    modal.innerHTML = `
      <div class="rg-modal__backdrop" data-rg-close="1"></div>
      <div class="rg-modal__panel" role="dialog" aria-modal="true" aria-labelledby="rg-modal-title">
        <div class="rg-modal__header">
          <h2 id="rg-modal-title">Confirmar exclusão</h2>
        </div>
        <div class="rg-modal__body">
          <p id="rg-modal-text"></p>
          <p class="rg-modal__hint">Essa ação não pode ser desfeita.</p>
        </div>
        <div class="rg-modal__footer">
          <button type="button" class="button rg-btn rg-btn--ghost" data-rg-close="1">Cancelar</button>
          <button type="button" class="button rg-btn rg-btn--danger" id="rg-modal-confirm">Excluir</button>
        </div>
      </div>
    `;

    document.body.appendChild(modal);

    // Fechar ao clicar fora / cancelar / ESC
    modal.addEventListener("click", (e) => {
      const close = e.target && e.target.getAttribute("data-rg-close");
      if (close) closeModal();
    });

    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") closeModal();
    });

    return modal;
  }

  function openModal(message, onConfirm) {
    const modal = ensureModal();
    const text = modal.querySelector("#rg-modal-text");
    const confirmBtn = modal.querySelector("#rg-modal-confirm");

    text.textContent = message;

    // Evita múltiplos listeners acumulados
    confirmBtn.onclick = () => {
      closeModal();
      onConfirm();
    };

    modal.classList.add("is-open");
  }

  function closeModal() {
    const modal = document.getElementById("rg-modal");
    if (!modal) return;
    modal.classList.remove("is-open");
  }

  // ---------- seleção ----------
  function selectedCount() {
    const boxes = form.querySelectorAll("input.action-select[type='checkbox']");
    let count = 0;
    boxes.forEach((b) => {
      if (b.checked) count++;
    });
    return count;
  }

  function updateUI() {
    const count = selectedCount();
    const show = count > 0;

    deleteBtn.style.display = show ? "inline-flex" : "none";
    countEl.style.display = show ? "inline-block" : "none";
    countEl.textContent = show ? `(${count} selecionado(s))` : "";
  }

  form.addEventListener("change", function (e) {
    if (e.target && e.target.type === "checkbox") updateUI();
  });

  // Abre modal de confirmação
  deleteBtn.addEventListener("click", function () {
    const count = selectedCount();
    if (count === 0) return;

    openModal(
      `Tem certeza que deseja excluir ${count} item(ns) selecionado(s)?`,
      () => {
        actionsSelect.value = "rg_delete_selected";
        form.submit();
      }
    );
  });

  updateUI();
});

document.addEventListener("DOMContentLoaded", () => {
  const input = document.getElementById("searchbar");
  if (input) input.placeholder = "Buscar cliente";
});
