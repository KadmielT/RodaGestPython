document.addEventListener('DOMContentLoaded', () => {
  const toasts = document.querySelectorAll('[data-toast]');

  const hideToast = (toast) => {
    if (toast.classList.contains('is-hiding')) {
      return;
    }

    toast.classList.add('is-hiding');

    setTimeout(() => {
      toast.remove();
    }, 450);
  };

  toasts.forEach((toast, index) => {
    const closeButton = toast.querySelector('[data-toast-close]');

    toast.style.animationDelay = `${index * 90}ms`;

    if (closeButton) {
      closeButton.addEventListener('click', () => hideToast(toast));
    }

    setTimeout(() => hideToast(toast), 4000 + (index * 120));
  });
});