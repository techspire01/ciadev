// Book Showcase Flip Animation Script
document.addEventListener('DOMContentLoaded', function() {
  const showcaseItems = document.querySelectorAll('.showcase-item');
  const showcaseBooks = document.querySelectorAll('.showcase-book');

  // Add flip animation on hover
  showcaseBooks.forEach(book => {
    const pageFlip = book.querySelector('.showcase-page-flip');
    let isFlipped = false;

    book.addEventListener('mouseenter', function() {
      if (!isFlipped) {
        pageFlip.style.transform = 'rotateY(180deg)';
        isFlipped = true;
      }
    });

    book.addEventListener('mouseleave', function() {
      if (isFlipped) {
        pageFlip.style.transform = 'rotateY(0deg)';
        isFlipped = false;
      }
    });
  });

  // Touch/swipe support for flip on mobile
  showcaseBooks.forEach(book => {
    let startX = 0;
    let startY = 0;
    const pageFlip = book.querySelector('.showcase-page-flip');
    let isFlipped = false;

    book.addEventListener('touchstart', function(e) {
      startX = e.touches[0].clientX;
      startY = e.touches[0].clientY;
    });

    book.addEventListener('touchend', function(e) {
      const endX = e.changedTouches[0].clientX;
      const endY = e.changedTouches[0].clientY;
      const diffX = Math.abs(startX - endX);
      const diffY = Math.abs(startY - endY);

      // Only trigger flip if swipe is more horizontal than vertical
      if (diffX > diffY && diffX > 30) {
        isFlipped = !isFlipped;
        pageFlip.style.transform = isFlipped ? 'rotateY(180deg)' : 'rotateY(0deg)';
      }
    });
  });

  // Handle window resize for responsive pagination updates
  let resizeTimeout;
  window.addEventListener('resize', function() {
    clearTimeout(resizeTimeout);
    resizeTimeout = setTimeout(function() {
      updatePagination();
    }, 250);
  });

  function updatePagination() {
    const itemsPerPage = window.innerWidth < 768 ? 1 : (window.innerWidth < 1024 ? 2 : 3);
    const totalPages = Math.ceil(showcaseItems.length / itemsPerPage);
    const currentPageEl = document.getElementById('currentPage');
    const totalPagesEl = document.getElementById('totalPages');

    if (totalPagesEl && currentPageEl) {
      totalPagesEl.textContent = totalPages;
      currentPageEl.textContent = Math.min(parseInt(currentPageEl.textContent), totalPages) || 1;
    }
  }

  // Initialize pagination on load
  updatePagination();

  // Keyboard navigation for showcase
  document.addEventListener('keydown', function(e) {
    const showcasePrevBtn = document.getElementById('showcasePrevBtn');
    const showcaseNextBtn = document.getElementById('showcaseNextBtn');

    if (e.key === 'ArrowLeft' && showcasePrevBtn) {
      e.preventDefault();
      showcasePrevBtn.click();
    } else if (e.key === 'ArrowRight' && showcaseNextBtn) {
      e.preventDefault();
      showcaseNextBtn.click();
    }
  });
});
