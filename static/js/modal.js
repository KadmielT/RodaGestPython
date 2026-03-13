document.addEventListener("DOMContentLoaded", () => {
  const openButtons = document.querySelectorAll("[data-modal-target]");
  const closeButtons = document.querySelectorAll("[data-modal-close]");

  const openModal = (modal) => {
    if (!modal) return;
    modal.hidden = false;
    document.body.style.overflow = "hidden";
  };

  const closeModal = (modal) => {
    if (!modal) return;
    modal.hidden = true;
    document.body.style.overflow = "";
  };

  openButtons.forEach((button) => {
    button.addEventListener("click", () => {
      const targetId = button.getAttribute("data-modal-target");
      const modal = document.getElementById(targetId);
      openModal(modal);
    });
  });

  closeButtons.forEach((button) => {
    button.addEventListener("click", () => {
      const modal = button.closest(".rg-modal");
      closeModal(modal);
    });
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      document.querySelectorAll(".rg-modal").forEach((modal) => {
        if (!modal.hidden) closeModal(modal);
      });
    }
  });
});