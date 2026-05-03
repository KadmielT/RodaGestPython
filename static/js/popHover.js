function createPopHoverElement() {
  const tooltip = document.createElement('div');
  tooltip.className = 'rg-pop-hover-floating';
  document.body.appendChild(tooltip);
  return tooltip;
}

function positionPopHover(tooltip, trigger) {
  const rect = trigger.getBoundingClientRect();
  const tooltipRect = tooltip.getBoundingClientRect();

  const spacing = 10;
  const viewportPadding = 12;

  let top = rect.top - tooltipRect.height - spacing;
  let left = rect.left;

  tooltip.classList.remove('is-below');

  if (top < viewportPadding) {
    top = rect.bottom + spacing;
    tooltip.classList.add('is-below');
  }

  if (left + tooltipRect.width > window.innerWidth - viewportPadding) {
    left = window.innerWidth - tooltipRect.width - viewportPadding;
  }

  if (left < viewportPadding) {
    left = viewportPadding;
  }

  tooltip.style.top = `${top}px`;
  tooltip.style.left = `${left}px`;
}

function showPopHover(tooltip, trigger) {
  const text = trigger.dataset.popHover;

  if (!text || !text.trim()) {
    return;
  }

  tooltip.textContent = text;

  tooltip.style.top = '-9999px';
  tooltip.style.left = '-9999px';

  tooltip.classList.add('is-visible');

  positionPopHover(tooltip, trigger);
}

function hidePopHover(tooltip) {
  tooltip.classList.remove('is-visible');
}

function initPopHover() {
  const triggers = document.querySelectorAll('.rg-pop-hover');

  if (!triggers.length) {
    return;
  }

  const tooltip = createPopHoverElement();

  triggers.forEach((trigger) => {
    trigger.addEventListener('mouseenter', () => {
      showPopHover(tooltip, trigger);
    });

    trigger.addEventListener('mouseleave', () => {
      hidePopHover(tooltip);
    });

    trigger.addEventListener('focus', () => {
      showPopHover(tooltip, trigger);
    });

    trigger.addEventListener('blur', () => {
      hidePopHover(tooltip);
    });
  });

  window.addEventListener('scroll', () => {
    hidePopHover(tooltip);
  }, true);

  window.addEventListener('resize', () => {
    hidePopHover(tooltip);
  });
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initPopHover);
} else {
  initPopHover();
}