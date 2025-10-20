// Book Showcase Animation Script
document.addEventListener('DOMContentLoaded', function() {
  const bookPages = document.querySelectorAll('.book-page');
  const prevBtn = document.querySelector('.prev-page');
  const nextBtn = document.querySelector('.next-page');

  if (!bookPages.length || !prevBtn || !nextBtn) return;

  let currentPage = 0;
  const totalPages = bookPages.length;

  function updatePages() {
    bookPages.forEach((page, index) => {
      if (index === currentPage) {
        page.classList.add('active');
        page.classList.remove('inactive');
        page.style.transform = 'rotateY(0deg) translateZ(0px)';
        page.style.zIndex = totalPages;
      } else if (index < currentPage) {
        page.classList.remove('active');
        page.classList.add('inactive');
        const rotation = -10 * (currentPage - index);
        const translateZ = -50 * (currentPage - index);
        page.style.transform = `rotateY(${rotation}deg) translateZ(${translateZ}px)`;
        page.style.zIndex = totalPages - (currentPage - index);
      } else {
        page.classList.remove('active', 'inactive');
        page.style.transform = 'rotateY(10deg) translateZ(-50px)';
        page.style.zIndex = totalPages - (index - currentPage);
      }
    });
  }

  function nextPage() {
    if (currentPage < totalPages - 1) {
      currentPage++;
      updatePages();
    }
  }

  function prevPage() {
    if (currentPage > 0) {
      currentPage--;
      updatePages();
    }
  }

  // Event listeners
  nextBtn.addEventListener('click', nextPage);
  prevBtn.addEventListener('click', prevPage);

  // Keyboard navigation
  document.addEventListener('keydown', function(e) {
    if (e.key === 'ArrowRight' || e.key === ' ') {
      e.preventDefault();
      nextPage();
    } else if (e.key === 'ArrowLeft') {
      e.preventDefault();
      prevPage();
    }
  });

  // Touch/swipe support
  let startX = 0;
  let endX = 0;

  document.querySelector('.book-pages').addEventListener('touchstart', function(e) {
    startX = e.touches[0].clientX;
  });

  document.querySelector('.book-pages').addEventListener('touchend', function(e) {
    endX = e.changedTouches[0].clientX;
    const diffX = startX - endX;

    if (Math.abs(diffX) > 50) { // Minimum swipe distance
      if (diffX > 0) {
        nextPage(); // Swipe left
      } else {
        prevPage(); // Swipe right
      }
    }
  });

  // Auto-play functionality (optional)
  let autoPlayInterval;

  function startAutoPlay() {
    autoPlayInterval = setInterval(() => {
      if (currentPage < totalPages - 1) {
        nextPage();
      } else {
        currentPage = 0;
        updatePages();
      }
    }, 3000); // Change page every 3 seconds
  }

  function stopAutoPlay() {
    clearInterval(autoPlayInterval);
  }

  // Pause auto-play on hover
  document.querySelector('.book-container').addEventListener('mouseenter', stopAutoPlay);
  document.querySelector('.book-container').addEventListener('mouseleave', startAutoPlay);

  // Initialize
  updatePages();
  startAutoPlay();
});
