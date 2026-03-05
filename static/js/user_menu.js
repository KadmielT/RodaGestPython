document.addEventListener("DOMContentLoaded", () => {
  const btn = document.getElementById("userMenuBtn");
  const dropdown = document.getElementById("userMenuDropdown");

  if (!btn || !dropdown) return;

  const close = () => {
    dropdown.hidden = true;
    btn.setAttribute("aria-expanded", "false");
  };

  const open = () => {
    dropdown.hidden = false;
    btn.setAttribute("aria-expanded", "true");
  };

  btn.addEventListener("click", (e) => {
    e.stopPropagation();
    const isOpen = btn.getAttribute("aria-expanded") === "true";
    isOpen ? close() : open();
  });

  document.addEventListener("click", () => close());
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") close();
  });
});