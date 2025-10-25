document.addEventListener('DOMContentLoaded', function() {
  // Read images data from template-injected BOOK_IMAGES array
  const IMAGES = window.BOOK_IMAGES && Array.isArray(window.BOOK_IMAGES) ? window.BOOK_IMAGES : [];

  const leftPage = document.querySelector('.book-page.left');
  const rightPage = document.querySelector('.book-page.right');
  const prevBtn = document.getElementById('prevPage');
  const nextBtn = document.getElementById('nextPage');

  if (!leftPage || !rightPage) return; // nothing to do

  let pairIndex = 0;
  const totalPairs = Math.max(1, Math.ceil(IMAGES.length / 2));
  let animating = false;

  function getImage(i) {
    return IMAGES[i] || null;
  }

  function setPageContent(pageEl, data) {
    if (!pageEl) return;
    const imgEl = pageEl.querySelector('img.book-image');
    const fallback = pageEl.querySelector('[style*="display: none"]');
    const titleEl = pageEl.querySelector('.image-title h3');

    if (data && data.url) {
      if (imgEl) {
        imgEl.src = data.url;
        imgEl.style.display = '';
      }
      if (fallback) fallback.style.display = 'none';
    } else {
      if (imgEl) imgEl.style.display = 'none';
      if (fallback) fallback.style.display = '';
    }

    if (titleEl) titleEl.textContent = data && data.title ? data.title : '';
  }

  function renderPair(idx) {
    const leftData = getImage(idx * 2);
    const rightData = getImage(idx * 2 + 1);
    setPageContent(leftPage, leftData);
    setPageContent(rightPage, rightData);

    const leftNum = leftPage.querySelector('.page-number');
    const rightNum = rightPage.querySelector('.page-number');
    if (leftNum) leftNum.textContent = idx * 2 + 1;
    if (rightNum) rightNum.textContent = idx * 2 + 2;

    if (prevBtn) prevBtn.disabled = idx === 0;
    if (nextBtn) nextBtn.disabled = idx >= totalPairs - 1;
  }

  function flipForward() {
    if (animating) return;
    if (pairIndex >= totalPairs - 1) return;
    animating = true;
    rightPage.classList.add('flip');

    function onEnd(e) {
      if (e.propertyName !== 'transform') return;
      rightPage.removeEventListener('transitionend', onEnd);
      pairIndex++;
      renderPair(pairIndex);
      // remove flip class after re-render so page sits normal
      rightPage.classList.remove('flip');
      animating = false;
    }

    rightPage.addEventListener('transitionend', onEnd);
  }

  function flipBackward() {
    if (animating) return;
    if (pairIndex <= 0) return;
    animating = true;
    leftPage.classList.add('flip-left');

    function onEnd(e) {
      if (e.propertyName !== 'transform') return;
      leftPage.removeEventListener('transitionend', onEnd);
      pairIndex--;
      renderPair(pairIndex);
      leftPage.classList.remove('flip-left');
      animating = false;
    }

    leftPage.addEventListener('transitionend', onEnd);
  }

  if (prevBtn) prevBtn.addEventListener('click', flipBackward);
  if (nextBtn) nextBtn.addEventListener('click', flipForward);

  document.addEventListener('keydown', function (e) {
    if (e.key === 'ArrowLeft') flipBackward();
    if (e.key === 'ArrowRight') flipForward();
  });

  // initial render
  renderPair(pairIndex);
});
