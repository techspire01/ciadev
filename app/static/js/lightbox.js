(function () {
  const state = {
    container: null,
    image: null,
    caption: null,
    isInitialised: false,
  };

  function initialise() {
    if (state.isInitialised) {
      return;
    }
    state.container = document.getElementById('imageLightbox');
    if (!state.container) {
      return;
    }
    state.image = state.container.querySelector('[data-lightbox-target="image"]');
    state.caption = state.container.querySelector('[data-lightbox-target="caption"]');

    const closeButton = state.container.querySelector('[data-lightbox-action="close"]');
    if (closeButton) {
      closeButton.addEventListener('click', closeLightbox);
    }

    state.container.addEventListener('click', (event) => {
      if (event.target === state.container) {
        closeLightbox();
      }
    });

    document.addEventListener('keydown', (event) => {
      if (event.key === 'Escape') {
        closeLightbox();
      }
    });

    state.isInitialised = true;
  }

  function openLightbox(src, captionText) {
    initialise();
    if (!state.container || !state.image) {
      return;
    }

    state.image.src = src;
    state.image.alt = captionText || '';

    if (state.caption) {
      const text = captionText ? captionText.trim() : '';
      state.caption.textContent = text;
      state.caption.classList.toggle('hidden', text.length === 0);
    }

    state.container.classList.remove('hidden');
    document.body.classList.add('overflow-hidden');
  }

  function closeLightbox() {
    if (!state.container) {
      return;
    }
    state.container.classList.add('hidden');
    document.body.classList.remove('overflow-hidden');
    if (state.image) {
      state.image.src = '';
      state.image.alt = '';
    }
    if (state.caption) {
      state.caption.textContent = '';
      state.caption.classList.add('hidden');
    }
  }

  function normaliseSource(element) {
    const direct = element.dataset.lightboxSrc || element.getAttribute('src') || '';
    return direct.trim();
  }

  function getCaption(element) {
    const text = element.dataset.lightboxCaption || element.getAttribute('alt') || '';
    return text.trim();
  }

  function bindTarget(element) {
    if (element.dataset.lightboxBound === 'true') {
      return;
    }
    element.addEventListener('click', (event) => {
      event.preventDefault();
      const source = normaliseSource(element);
      if (!source) {
        return;
      }
      const caption = getCaption(element);
      openLightbox(source, caption);
    });
    element.dataset.lightboxBound = 'true';
  }

  function registerLightboxTargets(root) {
    initialise();
    const scope = root instanceof Element ? root : document;
    scope.querySelectorAll('[data-lightbox-src]').forEach(bindTarget);
  }

  window.registerLightboxTargets = registerLightboxTargets;

  document.addEventListener('DOMContentLoaded', () => {
    initialise();
    registerLightboxTargets(document);
  });
})();
