// Showcase Section with Auto-Scroll and Rotating Circle Indicator
document.addEventListener('DOMContentLoaded', function() {
  const showcaseItems = document.querySelectorAll('.showcase-item-new');
  const itemsPerPageDesktop = 3;
  const itemsPerPageTablet = 2;
  const itemsPerPageMobile = 1;
  const AUTO_SCROLL_INTERVAL = 5000; // 5 seconds

  let currentPage = 0;
  let itemsPerPage = getItemsPerPage();
  let totalPages = Math.ceil(showcaseItems.length / itemsPerPage);
  let autoScrollTimer = null;
  let isAutoScrolling = true;

  const rotatingIndicator = document.getElementById('rotatingIndicator');
  const circleDots = rotatingIndicator?.querySelector('.circle-dots');

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

    // Update rotating circle indicator
    updateRotatingIndicator();

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

  function updateRotatingIndicator() {
    if (circleDots) {
      const rotationStep = (360 / totalPages) * currentPage;
      circleDots.style.transform = `rotate(${rotationStep}deg)`;
    }
  }

  function startAutoScroll() {
    if (autoScrollTimer) clearInterval(autoScrollTimer);
    isAutoScrolling = true;
    if (circleDots) {
      circleDots.classList.remove('paused');
    }

    autoScrollTimer = setInterval(() => {
      if (currentPage < totalPages - 1) {
        currentPage++;
      } else {
        currentPage = 0;
      }
      updateShowcaseDisplay();
    }, AUTO_SCROLL_INTERVAL);
  }

  function stopAutoScroll() {
    if (autoScrollTimer) {
      clearInterval(autoScrollTimer);
      autoScrollTimer = null;
    }
    isAutoScrolling = false;
    if (circleDots) {
      circleDots.classList.add('paused');
    }
  }

  function nextPage() {
    stopAutoScroll();
    if (currentPage < totalPages - 1) {
      currentPage++;
    } else {
      currentPage = 0;
    }
    updateShowcaseDisplay();
    // Resume auto-scroll after 2 seconds
    setTimeout(startAutoScroll, 2000);
  }

  function prevPage() {
    stopAutoScroll();
    if (currentPage > 0) {
      currentPage--;
    } else {
      currentPage = totalPages - 1;
    }
    updateShowcaseDisplay();
    // Resume auto-scroll after 2 seconds
    setTimeout(startAutoScroll, 2000);
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

  // Stop auto-scroll when hovering over showcase
  const showcaseGrid = document.querySelector('.showcase-grid');
  if (showcaseGrid) {
    showcaseGrid.addEventListener('mouseenter', stopAutoScroll);
    showcaseGrid.addEventListener('mouseleave', startAutoScroll);
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

  if (showcaseGrid) {
    showcaseGrid.addEventListener('touchstart', function(e) {
      stopAutoScroll();
      touchStartX = e.changedTouches[0].screenX;
    }, false);

    showcaseGrid.addEventListener('touchend', function(e) {
      touchEndX = e.changedTouches[0].screenX;
      handleSwipe();
      // Resume auto-scroll after swipe
      setTimeout(startAutoScroll, 2000);
    }, false);
  }

  function handleSwipe() {
    const swipeThreshold = 50;
    const diff = touchStartX - touchEndX;

    if (Math.abs(diff) > swipeThreshold) {
      if (diff > 0) {
        if (currentPage < totalPages - 1) {
          currentPage++;
        } else {
          currentPage = 0;
        }
      } else {
        if (currentPage > 0) {
          currentPage--;
        } else {
          currentPage = totalPages - 1;
        }
      }
      updateShowcaseDisplay();
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

  // Initial display and start auto-scroll
  updateShowcaseDisplay();
  startAutoScroll();

  // Add click handler to items for opening full view (optional)
  showcaseItems.forEach((item) => {
    item.style.cursor = 'pointer';
    item.addEventListener('click', function() {
      const img = this.querySelector('img');
      if (img && img.style.display !== 'none') {
        console.log('Clicked on:', this.querySelector('h3')?.textContent);
      }
    });
  });
});
