// Showcase Section with Fade-In and Slide Animations
document.addEventListener('DOMContentLoaded', function() {
  const showcaseItems = document.querySelectorAll('.showcase-item-new');
  const itemsPerPageDesktop = 3;
  const itemsPerPageTablet = 2;
  const itemsPerPageMobile = 1;

  let currentPage = 0;
  let itemsPerPage = getItemsPerPage();
  let totalPages = Math.ceil(showcaseItems.length / itemsPerPage);

  function getItemsPerPage() {
    if (window.innerWidth < 768) return itemsPerPageMobile;
    if (window.innerWidth < 1024) return itemsPerPageTablet;
    return itemsPerPageDesktop;
  }

  function updateShowcaseDisplay() {
    const startIdx = currentPage * itemsPerPage;
    const endIdx = startIdx + itemsPerPage;

    showcaseItems.forEach((item, idx) => {
      if (idx >= startIdx && idx < endIdx) {
        item.style.display = 'block';
        // Trigger fade-in animation
        setTimeout(() => {
          item.style.opacity = '1';
          item.style.transform = 'translateY(0)';
        }, 10);
      } else {
        item.style.display = 'none';
      }
    });

    // Update page counter
    document.getElementById('currentPage').textContent = currentPage + 1;
    document.getElementById('totalPages').textContent = totalPages;

    // Update button states
    const prevBtn = document.getElementById('showcasePrevBtn');
    const nextBtn = document.getElementById('showcaseNextBtn');

    if (prevBtn) {
      prevBtn.style.opacity = currentPage === 0 ? '0.5' : '1';
      prevBtn.style.pointerEvents = currentPage === 0 ? 'none' : 'auto';
    }
    if (nextBtn) {
      nextBtn.style.opacity = currentPage === totalPages - 1 ? '0.5' : '1';
      nextBtn.style.pointerEvents = currentPage === totalPages - 1 ? 'none' : 'auto';
    }
  }

  function nextPage() {
    if (currentPage < totalPages - 1) {
      currentPage++;
      updateShowcaseDisplay();
    }
  }

  function prevPage() {
    if (currentPage > 0) {
      currentPage--;
      updateShowcaseDisplay();
    }
  }

  // Event listeners for navigation buttons
  const prevBtn = document.getElementById('showcasePrevBtn');
  const nextBtn = document.getElementById('showcaseNextBtn');

  if (prevBtn) {
    prevBtn.addEventListener('click', prevPage);
    prevBtn.addEventListener('keydown', function(e) {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        prevPage();
      }
    });
  }

  if (nextBtn) {
    nextBtn.addEventListener('click', nextPage);
    nextBtn.addEventListener('keydown', function(e) {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        nextPage();
      }
    });
  }

  // Keyboard navigation
  document.addEventListener('keydown', function(e) {
    if (e.key === 'ArrowLeft') {
      e.preventDefault();
      prevPage();
    } else if (e.key === 'ArrowRight') {
      e.preventDefault();
      nextPage();
    }
  });

  // Touch/swipe support for mobile
  let touchStartX = 0;
  let touchEndX = 0;
  const showcaseGrid = document.querySelector('.showcase-grid');

  if (showcaseGrid) {
    showcaseGrid.addEventListener('touchstart', function(e) {
      touchStartX = e.changedTouches[0].screenX;
    }, false);

    showcaseGrid.addEventListener('touchend', function(e) {
      touchEndX = e.changedTouches[0].screenX;
      handleSwipe();
    }, false);
  }

  function handleSwipe() {
    const swipeThreshold = 50;
    const diff = touchStartX - touchEndX;

    if (Math.abs(diff) > swipeThreshold) {
      if (diff > 0) {
        nextPage(); // Swiped left
      } else {
        prevPage(); // Swiped right
      }
    }
  }

  // Handle window resize
  let resizeTimeout;
  window.addEventListener('resize', function() {
    clearTimeout(resizeTimeout);
    resizeTimeout = setTimeout(function() {
      const newItemsPerPage = getItemsPerPage();
      if (newItemsPerPage !== itemsPerPage) {
        itemsPerPage = newItemsPerPage;
        totalPages = Math.ceil(showcaseItems.length / itemsPerPage);
        currentPage = Math.min(currentPage, totalPages - 1);
        updateShowcaseDisplay();
      }
    }, 250);
  });

  // Initial display
  updateShowcaseDisplay();

  // Add click handler to items for opening full view (optional)
  showcaseItems.forEach((item) => {
    item.style.cursor = 'pointer';
    item.addEventListener('click', function() {
      const img = this.querySelector('img');
      if (img && img.style.display !== 'none') {
        // Could open lightbox here if desired
        console.log('Clicked on:', this.querySelector('h3')?.textContent);
      }
    });
  });
});
