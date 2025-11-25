console.log("script.js loaded successfully."); // Added for debugging
// Hero Carousel functionality
let currentSlide = 1;
const totalSlides = 3;

// Container sets for different slides - Updated for 5 containers (7x2 grid)
const containerSets = [
    // Slide 1 - Industrial Excellence (5 containers)
    `
      <!-- Container 1 - Large hero (spans 3x2) -->
      <div class="col-span-3 row-span-2 rounded-xl overflow-hidden shadow-lg bg-black relative hero-container cursor-pointer">
        <img src="https://images.pexels.com/photos/532079/pexels-photo-532079.jpeg" alt="Industrial Excellence" class="w-full h-full object-cover" />
        <div class="absolute inset-0 bg-gradient-to-t from-black/80 to-black/30 w-full h-auto flex-grow"></div>
        <div class="absolute bottom-8 left-8 text-white">
          <h3 class="text-2xl font-bold mb-2">Industrial Excellence</h3>
          <p class="text-base opacity-90">Connecting industries and fostering growth in Coimbatore's manufacturing sector</p>
        </div>
      </div>
      <!-- Container 2 - Medium (spans 2x1) -->
      <div class="col-span-2 row-span-1 rounded-xl overflow-hidden shadow-lg bg-black relative cursor-pointer">
        <img src="https://images.pexels.com/photos/236089/pexels-photo-236089.jpeg" alt="Electrical Power Equipment" class="w-full h-full object-cover" />
        <div class="absolute inset-0 bg-gradient-to-t from-black/60 to-black/20"></div>
        <div class="absolute bottom-4 left-4 text-white">
          <h4 class="text-lg font-bold">Electrical</h4>
          <p class="text-sm opacity-80">Power solutions & equipment</p>
        </div>
      </div>
      <!-- Container 3 - Small (spans 2x1) -->
      <div class="col-span-2 row-span-1 rounded-xl overflow-hidden shadow-lg bg-black relative cursor-pointer">
        <img src="https://images.pexels.com/photos/31115985/pexels-photo-31115985.jpeg" alt="Plastic Manufacturing" class="w-full h-full object-cover" />
        <div class="absolute inset-0 bg-gradient-to-t from-black/60 to-black/20"></div>
        <div class="absolute bottom-4 left-4 text-white">
          <h4 class="text-lg font-bold">Plastic</h4>
          <p class="text-sm opacity-80">Manufacturing & molding</p>
        </div>
      </div>
      <!-- Container 4 - Medium tall (spans 2x1) -->
      <div class="col-span-2 row-span-1 rounded-xl overflow-hidden shadow-lg bg-black relative cursor-pointer">
        <img src="https://images.pexels.com/photos/31199566/pexels-photo-31199566.jpeg" alt="Textile Manufacturing" class="w-full h-full object-cover" />
        <div class="absolute inset-0 bg-gradient-to-t from-black/60 to-black/20"></div>
        <div class="absolute bottom-4 left-4 text-white">
          <h4 class="text-lg font-bold">Textile</h4>
          <p class="text-sm opacity-80">Fabric & garment industry</p>
        </div>
      </div>
      <!-- Container 5 - Small (spans 2x1) -->
      <div class="col-span-2 row-span-1 rounded-xl overflow-hidden shadow-lg bg-black relative cursor-pointer">
        <img src="https://images.pexels.com/photos/8982670/pexels-photo-8982670.jpeg" alt="Automation Equipment" class="w-full h-full object-cover" />
        <div class="absolute inset-0 bg-gradient-to-t from-black/60 to-black/20"></div>
        <div class="absolute bottom-4 left-4 text-white">
          <h4 class="text-lg font-bold">Automation</h4>
          <p class="text-sm opacity-80">Smart manufacturing</p>
        </div>
      </div>
    `,
    // Slide 2 - Metal Working & Production (5 containers)
    `
      <!-- Container 1 - Small (spans 2x1) -->
      <div class="col-span-2 row-span-1 rounded-xl overflow-hidden shadow-lg bg-black relative cursor-pointer">
        <img src="https://images.pexels.com/photos/33559313/pexels-photo-33559313.jpeg" alt="Engineering Equipment" class="w-full h-full object-cover" />
        <div class="absolute inset-0 bg-gradient-to-t from-black/60 to-black/20"></div>
        <div class="absolute bottom-4 left-4 text-white">
          <h4 class="text-lg font-bold">Engineering</h4>
          <p class="text-sm opacity-80">Technical solutions</p>
        </div>
      </div>
      <!-- Container 2 - Large metal working hero (spans 3x2) -->
      <div class="col-span-3 row-span-2 rounded-xl overflow-hidden shadow-lg bg-black relative hero-container cursor-pointer">
        <img src="https://images.pexels.com/photos/1145434/pexels-photo-1145434.jpeg" alt="Metal Working Operations" class="w-full h-full object-cover" />
        <div class="absolute inset-0 bg-gradient-to-t from-black/80 to-black/30 w-full h-auto flex-grow"></div>
        <div class="absolute bottom-8 left-8 text-white">
          <h3 class="text-2xl font-bold mb-2">Metal Working & Production</h3>
          <p class="text-base opacity-90">Advanced metalworking solutions and production equipment</p>
        </div>
      </div>
      <!-- Container 3 - Small (spans 2x1) -->
      <div class="col-span-2 row-span-1 rounded-xl overflow-hidden shadow-lg bg-black relative cursor-pointer">
        <img src="https://images.pexels.com/photos/9550574/pexels-photo-9550574.jpeg" alt="Kitchen Equipment" class="w-full h-full object-cover" />
        <div class="absolute inset-0 bg-gradient-to-t from-black/60 to-black/20"></div>
        <div class="absolute bottom-4 left-4 text-white">
          <h4 class="text-lg font-bold">Kitchen</h4>
          <p class="text-sm opacity-80">Commercial equipment</p>
        </div>
      </div>
      <!-- Container 4 - Small (spans 2x1) -->
      <div class="col-span-2 row-span-1 rounded-xl overflow-hidden shadow-lg bg-black relative cursor-pointer">
        <img src="https://images.pexels.com/photos/3862627/pexels-photo-3862627.jpeg" alt="Production Systems" class="w-full h-full object-cover" />
        <div class="absolute inset-0 bg-gradient-to-t from-black/60 to-black/20"></div>
        <div class="absolute bottom-4 left-4 text-white">
          <h4 class="text-lg font-bold">Production</h4>
          <p class="text-sm opacity-80">Manufacturing systems</p>
        </div>
      </div>
      <!-- Container 5 - Small (spans 2x1) -->
      <div class="col-span-2 row-span-1 rounded-xl overflow-hidden shadow-lg bg-black relative cursor-pointer">
        <img src="https://images.pexels.com/photos/1267338/pexels-photo-1267338.jpeg" alt="Packaging Equipment" class="w-full h-full object-cover" />
        <div class="absolute inset-0 bg-gradient-to-t from-black/60 to-black/20"></div>
        <div class="absolute bottom-4 left-4 text-white">
          <h4 class="text-lg font-bold">Packing</h4>
          <p class="text-sm opacity-80">Packaging solutions</p>
        </div>
      </div>
    `,
    // Slide 3 - Advanced Manufacturing (5 containers)
    `
      <!-- Container 1 - Small (spans 2x1) -->
      <div class="col-span-2 row-span-1 rounded-xl overflow-hidden shadow-lg bg-black relative cursor-pointer">
        <img src="https://images.pexels.com/photos/31115985/pexels-photo-31115985.jpeg" alt="Plastic Manufacturing" class="w-full h-full object-cover" />
        <div class="absolute inset-0 bg-gradient-to-t from-black/60 to-black/20"></div>
        <div class="absolute bottom-4 left-4 text-white">
          <h4 class="text-lg font-bold">Plastic</h4>
          <p class="text-sm opacity-80">Manufacturing & molding</p>
        </div>
      </div>
      <!-- Container 2 - Small (spans 2x1) -->
      <div class="col-span-2 row-span-1 rounded-xl overflow-hidden shadow-lg bg-black relative cursor-pointer">
        <img src="https://images.pexels.com/photos/31199566/pexels-photo-31199566.jpeg" alt="Textile Manufacturing" class="w-full h-full object-cover" />
        <div class="absolute inset-0 bg-gradient-to-t from-black/60 to-black/20"></div>
        <div class="absolute bottom-4 left-4 text-white">
          <h4 class="text-lg font-bold">Textile</h4>
          <p class="text-sm opacity-80">Fabric & garment industry</p>
        </div>
      </div>
      <!-- Container 3 - Large hero (spans 3x2) -->
      <div class="col-span-3 row-span-2 rounded-xl overflow-hidden shadow-lg bg-black relative hero-container cursor-pointer">
        <img src="https://images.pexels.com/photos/8982670/pexels-photo-8982670.jpeg" alt="Smart Manufacturing" class="w-full h-full object-cover" />
        <div class="absolute inset-0 bg-gradient-to-t from-black/80 to-black/30 w-full h-auto flex-grow"></div>
        <div class="absolute bottom-8 left-8 text-white">
          <h3 class="text-2xl font-bold mb-2">Smart Manufacturing</h3>
          <p class="text-base opacity-90">AI-powered automation and intelligent manufacturing systems</p>
        </div>
      </div>
      <!-- Container 4 - Small (spans 2x1) -->
      <div class="col-span-2 row-span-1 rounded-xl overflow-hidden shadow-lg bg-black relative cursor-pointer">
        <img src="https://images.pexels.com/photos/236089/pexels-photo-236089.jpeg" alt="Electrical Systems" class="w-full h-full object-cover" />
        <div class="absolute inset-0 bg-gradient-to-t from-black/60 to-black/20"></div>
        <div class="absolute bottom-4 left-4 text-white">
          <h4 class="text-lg font-bold">Electrical</h4>
          <p class="text-sm opacity-80">Power solutions & equipment</p>
        </div>
      </div>
      <!-- Container 5 - Small (spans 2x1) -->
      <div class="col-span-2 row-span-1 rounded-xl overflow-hidden shadow-lg bg-black relative cursor-pointer">
        <img src="https://images.pexels.com/photos/532079/pexels-photo-532079.jpeg" alt="Industrial Equipment" class="w-full h-full object-cover" />
        <div class="absolute inset-0 bg-gradient-to-t from-black/60 to-black/20"></div>
        <div class="absolute bottom-4 left-4 text-white">
          <h4 class="text-lg font-bold">Industrial</h4>
          <p class="text-sm opacity-80">Heavy equipment solutions</p>
        </div>
      </div>
    `
];

/* New multi-item carousel: show a fixed number of visible cards (e.g. 3)
   and allow iterating through all items. This replaces the old slide-set
   behavior which swapped groups of markup.
*/
function setupMultiVisibleCarousel(visibleCount = 3) {
    const carousel = document.getElementById('heroCarousel');
    if (!carousel) return;

    // Build a flat list of item elements from containerSets
    const temp = document.createElement('div');
    temp.innerHTML = containerSets.join('\n');
    const items = Array.from(temp.children);
    if (items.length === 0) return;

    // Responsive helper: choose visible count based on viewport
    function chooseVisibleCount() {
        if (window.matchMedia('(min-width:420px) and (max-width:768px)').matches) {
            return 5;
        }
        if (window.matchMedia('(max-width:419px)').matches) {
            return 2;
        }
        return 3; // default for desktop/tablet when carousel is used
    }

    // If caller didn't pass an explicit count, determine it now
    visibleCount = visibleCount || chooseVisibleCount();

    // Build viewport + track
    carousel.innerHTML = '';
    const viewport = document.createElement('div');
    viewport.className = 'carousel-viewport';
    const track = document.createElement('div');
    track.className = 'carousel-track';

    // Append items into the track
    items.forEach(item => {
        item.classList.add('carousel-slide-item');
        // ensure slides have no width overrides
        item.style.boxSizing = 'border-box';
        track.appendChild(item);
    });

    viewport.appendChild(track);
    carousel.appendChild(viewport);

    // Insert controls (prev/next) if not present
    let prevBtn = document.getElementById('heroPrevBtn');
    let nextBtn = document.getElementById('heroNextBtn');
    if (!prevBtn) {
        prevBtn = document.createElement('button');
        prevBtn.id = 'heroPrevBtn';
        prevBtn.className = 'hero-nav-btn prev-btn';
        prevBtn.innerHTML = '<i class="fas fa-chevron-left"></i>';
        carousel.appendChild(prevBtn);
    }
    if (!nextBtn) {
        nextBtn = document.createElement('button');
        nextBtn.id = 'heroNextBtn';
        nextBtn.className = 'hero-nav-btn next-btn';
        nextBtn.innerHTML = '<i class="fas fa-chevron-right"></i>';
        carousel.appendChild(nextBtn);
    }

    // Apply CSS rules for viewport/track/slide sizing (flex-based).
    // To avoid fractional / partially visible slides, use exact percentage widths and remove gaps.
    function injectCarouselStyles(count) {
        const gap = 0; // no gap to ensure exact visibleCount fit
        const injectedId = 'multiCarouselStyles';
        let s = document.getElementById(injectedId);
        if (s) s.remove();
        const slidePct = (100 / count).toFixed(6);
        const css = `
        .carousel-viewport{overflow:hidden;width:100%;}
        .carousel-track{display:flex;gap:${gap}px;transition:transform 0.45s ease;will-change:transform}
        .carousel-track .carousel-slide-item{flex:0 0 ${slidePct}%; max-width:${slidePct}%; box-sizing:border-box;}
        .hero-nav-btn{position:absolute;top:50%;transform:translateY(-50%);background:rgba(255,255,255,0.9);border-radius:999px;border:none;padding:0.45rem 0.6rem;cursor:pointer;box-shadow:0 6px 18px rgba(0,0,0,0.12);z-index:50}
        .hero-nav-btn.prev-btn{left:8px}
        .hero-nav-btn.next-btn{right:8px}
        @media (max-width:420px){ .carousel-track .carousel-slide-item{flex:0 0 50%; max-width:50%;} }
        `;
        s = document.createElement('style');
        s.id = injectedId;
        s.textContent = css;
        document.head.appendChild(s);
    }

    // inject styles for current visibleCount
    injectCarouselStyles(visibleCount);

    // State
    let index = 0;
    const maxIndex = Math.max(0, items.length - visibleCount);

    function showIndex(i) {
        index = Math.min(Math.max(0, i), maxIndex);
        const slidePct = (100 / visibleCount);
        const pct = index * slidePct;
        track.style.transform = `translateX(-${pct}%)`;
    }

    function next() { showIndex(index + 1); }
    function prev() { showIndex(index - 1); }

    nextBtn.onclick = next;
    prevBtn.onclick = prev;

    // make slides clickable to navigate to category
    Array.from(track.children).forEach(child => {
        child.onclick = function(){ window.location.href = '/category/'; };
    });

    // expose for autoplay
    carousel._mc = { next, prev, showIndex };

    // initialize
    showIndex(0);

    // Rebuild on resize when crossing breakpoints (debounced)
    let resizeTimer = null;
    function handleResize() {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(() => {
            const newVisible = chooseVisibleCount();
            if (newVisible !== visibleCount) {
                // rebuild carousel with new visible count
                setupMultiVisibleCarousel(newVisible);
            } else {
                // ensure styles reflect current count (e.g., after zoom)
                injectCarouselStyles(visibleCount);
            }
        }, 150);
    }

    // attach resize handler (store reference so we can remove if rebuilding)
    window.removeEventListener('resize', carousel._mc && carousel._mc._resizeHandler);
    carousel._mc._resizeHandler = handleResize;
    window.addEventListener('resize', handleResize);
}

function nextSlide() {
    currentSlide = (currentSlide + 1) % totalSlides;
    // initialize the new multi-visible carousel showing 3 items
    setupMultiVisibleCarousel(3);
}

function prevSlide() {
    currentSlide = (currentSlide - 1 + totalSlides) % totalSlides;
    // ensure the multi-visible carousel is initialized
    setupMultiVisibleCarousel(3);
}

// Language Toggle Functionality
let currentLanguage = 'EN';

function toggleLanguage() {
    const currentLangEl = document.getElementById('currentLang');
    const nextLangEl = document.getElementById('nextLang');
    const mobileLangEl = document.getElementById('mobileLang');

    if (currentLanguage === 'EN') {
        currentLanguage = 'TM';
        if (currentLangEl) currentLangEl.textContent = 'தமிழ்';
        if (nextLangEl) nextLangEl.textContent = 'EN';
        if (mobileLangEl) mobileLangEl.textContent = 'தமிழ்';
    } else {
        currentLanguage = 'EN';
        if (currentLangEl) currentLangEl.textContent = 'EN';
        if (nextLangEl) nextLangEl.textContent = 'தமிழ்';
        if (mobileLangEl) mobileLangEl.textContent = 'EN';
    }
}

// Preload carousel images for faster transitions
function preloadImages() {
    const imageUrls = [
        'https://images.pexels.com/photos/532079/pexels-photo-532079.jpeg',
        'https://images.pexels.com/photos/236089/pexels-photo-236089.jpeg',
        'https://images.pexels.com/photos/31115985/pexels-photo-31115985.jpeg',
        'https://images.pexels.com/photos/31199566/pexels-photo-31199566.jpeg',
        'https://images.pexels.com/photos/8982670/pexels-photo-8982670.jpeg',
        'https://images.pexels.com/photos/33559313/pexels-photo-33559313.jpeg',
        'https://images.pexels.com/photos/1145434/pexels-photo-1145434.jpeg',
        'https://images.pexels.com/photos/9550574/pexels-photo-9550574.jpeg',
        'https://images.pexels.com/photos/3862627/pexels-photo-3862627.jpeg',
        'https://images.pexels.com/photos/1267338/pexels-photo-1267338.jpeg'
    ];

    imageUrls.forEach(url => {
        const img = new Image();
        img.src = url;
    });
}

// Add loading animation and fallback for images
function setupImageLoading() {
    const images = document.querySelectorAll('#heroCarousel img');
    images.forEach(img => {
        img.style.opacity = '0'; // Always reset opacity before load
        img.addEventListener('load', function() {
            this.style.opacity = '1';
        });
        img.addEventListener('error', function() {
            this.style.display = 'none';
            // Optionally, show a fallback element or message
            if (this.parentNode) {
                const fallback = document.createElement('div');
                fallback.className = 'flex items-center justify-center w-full h-full bg-gray-200';
                fallback.innerHTML = '<span class="text-gray-500 text-lg">Image not available</span>';
                this.parentNode.appendChild(fallback);
            }
        });
        // If already loaded (from cache), trigger fade-in
        if (img.complete && img.naturalWidth !== 0) {
            img.style.opacity = '1';
        }
    });
}

function setupCarouselImageRedirect() {
    const carousel = document.getElementById('heroCarousel');
    if (!carousel) return;
    Array.from(carousel.children).forEach(container => {
        container.onclick = function() {
            window.location.href = "/category/";
        };
    });
}

// Main initialization
document.addEventListener('DOMContentLoaded', function() {
    // Preload images first
    preloadImages();

    // Initialize carousel (use multi-visible carousel)
    setupMultiVisibleCarousel(3);
    setupImageLoading();
    setupCarouselImageRedirect();

    // Language Toggle Event Listeners
    const languageToggle = document.getElementById('languageToggle');
    const mobileLanguageToggle = document.getElementById('mobileLanguageToggle');
    const btnEnMobile = document.getElementById('translate-en-mobile');
    const btnTaMobile = document.getElementById('translate-ta-mobile');

    if (languageToggle) {
        languageToggle.addEventListener('click', toggleLanguage);
    }

    // Keep the visual toggle on the mobileLanguageToggle container (if clicked)
    if (mobileLanguageToggle) {
        mobileLanguageToggle.addEventListener('click', function(e) {
            // only toggle labels; explicit mobile EN/TA buttons handle translation
            toggleLanguage();
        });
    }

    // Attach handlers to new mobile EN/TA buttons. These will call translateTo when available
    function handleMobileTranslate(target) {
        // update UI labels immediately
        toggleLanguage();
        try {
            if (typeof translateTo === 'function') {
                console.log('Mobile button calling translateTo target=', target);
                translateTo(target);
            } else {
                console.log('translateTo not available; saving pendingTranslate=', target);
                try { localStorage.setItem('pendingTranslate', target); } catch (err) { console.warn('localStorage set failed', err); }
            }
        } catch (err) {
            console.error('Error invoking translateTo from mobile button:', err);
            try { localStorage.setItem('pendingTranslate', target); } catch (err2) { console.warn('localStorage set failed', err2); }
        }
    }

    if (btnEnMobile) {
        btnEnMobile.addEventListener('click', function(e){ e.preventDefault(); handleMobileTranslate('en'); });
    }
    if (btnTaMobile) {
        btnTaMobile.addEventListener('click', function(e){ e.preventDefault(); handleMobileTranslate('ta'); });
    }

    // Dot navigation
    const dots = document.querySelectorAll('.carousel-dot');
    dots.forEach((dot, index) => {
        dot.addEventListener('click', () => {
            currentSlide = index;
            // ensure the multi-visible carousel is initialized
            setupMultiVisibleCarousel(3);
        });
    });

    // Auto-play carousel
    let carouselInterval;
    let isPageVisible = true;

    function startCarousel() {
        if (carouselInterval) clearInterval(carouselInterval);
        carouselInterval = setInterval(() => {
            if (isPageVisible) {
                // Prefer the new carousel API if available
                const carouselEl = document.getElementById('heroCarousel');
                if (carouselEl && carouselEl._mc && typeof carouselEl._mc.next === 'function') {
                    carouselEl._mc.next();
                } else {
                    nextSlide();
                }
            }
        }, 2000); // Changed to 2 seconds
    }

    function stopCarousel() {
        if (carouselInterval) {
            clearInterval(carouselInterval);
            carouselInterval = null;
        }
    }

    // Handle page visibility changes
    document.addEventListener('visibilitychange', function() {
        if (document.hidden) {
            isPageVisible = false;
            stopCarousel();
        } else {
            isPageVisible = true;
            startCarousel();
        }
    });

    // Pause carousel on hover
    const heroSection = document.querySelector('#heroCarousel');
    if (heroSection) {
        heroSection.addEventListener('mouseenter', stopCarousel);
        heroSection.addEventListener('mouseleave', startCarousel);
    }

    // Start carousel initially
    startCarousel();

    // Animate elements on scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, observerOptions);

    // Add scroll animation class to elements
    const animateElements = document.querySelectorAll('.supplier-card, .card-hover');
    animateElements.forEach(el => {
        el.classList.add('animate-on-scroll');
        observer.observe(el);
    });

    // Stagger animation for category cards
    const categoryCards = document.querySelectorAll('.card-hover');
    categoryCards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
    });

    // Stagger animation for supplier cards
    const supplierCards = document.querySelectorAll('.supplier-card');
    supplierCards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.2}s`;
    });

    // Navbar scroll effect
    let lastScrollTop = 0;
    const navbar = document.querySelector('.fixed-header');

    window.addEventListener('scroll', function() {
        let scrollTop = window.pageYOffset || document.documentElement.scrollTop;

        if (scrollTop > lastScrollTop && scrollTop > 100) {
            // Scrolling down
            navbar.style.transform = 'translateY(-100%)';
        } else {
            // Scrolling up
            navbar.style.transform = 'translateY(0)';
        }

        // Add background blur when scrolled
        if (scrollTop > 50) {
            navbar.style.backgroundColor = 'rgba(255, 255, 255, 0.95)';
            navbar.style.backdropFilter = 'blur(10px)';
        } else {
            navbar.style.backgroundColor = 'rgba(255, 255, 255, 1)';
            navbar.style.backdropFilter = 'none';
        }

        lastScrollTop = scrollTop;
    });

    // Smooth hover effects for buttons
    const buttons = document.querySelectorAll('button, .inline-block:not(.center-logo)');
    buttons.forEach(button => {
        button.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px) scale(1.02)';
        });

        button.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });

    // Mobile menu functionality
    const mobileMenuBtn = document.getElementById('mobileMenuBtn');
    const mobileMenu = document.getElementById('mobileMenu');
    const mobileProductsBtn = document.getElementById('mobileProductsBtn');
    const mobileProductsMenu = document.getElementById('mobileProductsMenu');

    if (mobileMenuBtn && mobileMenu) {
        mobileMenuBtn.addEventListener('click', function() {
            mobileMenu.classList.toggle('hidden');
            mobileMenuBtn.classList.toggle('active');
        });
    }

    if (mobileProductsBtn && mobileProductsMenu) {
        mobileProductsBtn.addEventListener('click', function() {
            mobileProductsMenu.classList.toggle('hidden');
            const icon = mobileProductsBtn.querySelector('i');
            if (mobileProductsMenu.classList.contains('hidden')) {
                icon.classList.remove('fa-chevron-up');
                icon.classList.add('fa-chevron-down');
            } else {
                icon.classList.remove('fa-chevron-down');
                icon.classList.add('fa-chevron-up');
            }
        });
    }

    // Close mobile menu when clicking outside
    document.addEventListener('click', function(event) {
        if (mobileMenu && !mobileMenu.contains(event.target) && !mobileMenuBtn.contains(event.target)) {
            mobileMenu.classList.add('hidden');
            mobileMenuBtn.classList.remove('active');
        }
    });

    // Announcement button redirect logic
    const announcementBtn = document.getElementById('announcementBtn');
    if (announcementBtn) {
        announcementBtn.addEventListener('click', function() {
            window.location.href = "/announcement/";
        });
    }

    // Smooth scroll for anchor links (only valid anchors, not empty #)
    document.querySelectorAll('a[href^="#"]:not([href="#"])').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const href = this.getAttribute('href');

            if (href && href.length > 1 && href !== '#') {
                try {
                    const target = document.querySelector(href);
                    if (target) {
                        target.scrollIntoView({
                            behavior: 'smooth',
                            block: 'start'
                        });
                    }
                } catch (error) {
                    console.warn('Invalid selector for smooth scroll:', href);
                }
            }
        });
    });

    // Prevent default behavior for empty anchor links
    document.querySelectorAll('a[href="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
        });
    });

    // Setup profile/logout functionality
    setupProfileLogoutListeners();

    // Browse Catalog button functionality
    const browseBtn = document.getElementById('browseBtn');
    if (browseBtn) {
        browseBtn.addEventListener('click', function(e) {
            e.preventDefault();
            console.log("Browse Catalog button clicked."); // Added for debugging
            const categoriesSection = document.getElementById('categories');
            if (categoriesSection) {
                categoriesSection.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    }

    // Initialize search functionality
    setupSearchFunctionality();
});


// Profile/Logout Toggle Functionality
let isLogoutMode = false;

function toggleProfileLogout() {
    const profileBtn = document.getElementById('profileBtn');
    const logoutBtn = document.getElementById('logoutBtn');

    if (isLogoutMode) {
        // Switch back to profile mode
        profileBtn.classList.remove('hidden');
        logoutBtn.classList.add('hidden');
        isLogoutMode = false;
    } else {
        // Switch to logout mode
        profileBtn.classList.add('hidden');
        logoutBtn.classList.remove('hidden');
        isLogoutMode = true;

        // Auto-switch back after 3 seconds
        setTimeout(() => {
            if (isLogoutMode) {
                profileBtn.classList.remove('hidden');
                logoutBtn.classList.add('hidden');
                isLogoutMode = false;
            }
        }, 3000);
    }
}

function performLogout() {
    // Perform logout via AJAX
    fetch('/logout/', {
        method: 'GET',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
        },
        credentials: 'same-origin'
    })
    .then(response => {
        if (response.redirected) {
            window.location.href = response.url;
        } else {
            window.location.reload();
        }
    })
    .catch(error => {
        console.error('Logout error:', error);
        window.location.href = '/logout/';
    });
}

// Add event listeners for profile/logout functionality
function setupProfileLogoutListeners() {
    const profileBtn = document.getElementById('profileBtn');
    const logoutBtn = document.getElementById('logoutBtn');

    if (profileBtn) {
        profileBtn.addEventListener('click', function(e) {
            e.stopPropagation(); // Prevent event bubbling
            toggleProfileLogout();
        });
    }

    if (logoutBtn) {
        logoutBtn.addEventListener('click', function(e) {
            e.stopPropagation(); // Prevent event bubbling
            performLogout();
        });
    }

    // Close logout mode when clicking anywhere else on the page
    document.addEventListener('click', function() {
        if (isLogoutMode) {
            const profileBtn = document.getElementById('profileBtn');
            const logoutBtn = document.getElementById('logoutBtn');
            if (profileBtn && logoutBtn) {
                profileBtn.classList.remove('hidden');
                logoutBtn.classList.add('hidden');
                isLogoutMode = false;
            }
        }
    });

    // Prevent the profile button container from closing when clicking inside it
    const profileContainer = document.querySelector('.relative.group');
    if (profileContainer) {
        profileContainer.addEventListener('click', function(e) {
            e.stopPropagation();
        });
    }
}


// Add CSS for smooth transitions and hover effects
const carouselCSS = `
    #heroCarousel.transitioning {
        opacity: 0.9;
        transition: opacity 0.15s ease-in-out;
    }

    .carousel-dot {
        transition: all 0.3s ease;
        cursor: pointer;
    }

    .carousel-dot:hover {
        transform: scale(1.1) !important;
        opacity: 0.8;
    }

    /* Hover effects for carousel images */
    #heroCarousel > div {
        transition: all 0.3s ease;
        cursor: pointer;
    }

    #heroCarousel > div:hover {
        transform: scale(1.03);
        z-index: 10;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
    }

    #heroCarousel > div img {
        transition: all 0.3s ease;
    }

    #heroCarousel > div:hover img {
        transform: scale(1.02);
    }

    .animate-on-scroll {
        opacity: 0;
        transform: translateY(20px);
        transition: all 0.6s ease;
    }

    .animate-on-scroll.visible {
        opacity: 1;
        transform: translateY(0);
    }
`;

const style = document.createElement('style');
style.textContent = carouselCSS;
document.head.appendChild(style);

// Search functionality
function setupSearchFunctionality() {
    const searchInput = document.getElementById('searchInput');
    const searchResults = document.getElementById('searchResults');
    
    if (!searchInput || !searchResults) return;

    let searchTimeout;
    let currentSearchQuery = '';

    searchInput.addEventListener('input', function(e) {
        const query = e.target.value.trim();
        currentSearchQuery = query;
        
        // Clear previous timeout
        clearTimeout(searchTimeout);
        
        // Hide results if query is empty
        if (!query) {
            searchResults.classList.add('hidden');
            return;
        }

        // Show loading state
        searchResults.classList.remove('hidden');
        searchResults.innerHTML = '<div class="p-4 text-center text-gray-500">Searching...</div>';

        // Debounce search requests
        searchTimeout = setTimeout(() => {
            fetchSearchSuggestions(query);
        }, 150);
    });

    searchInput.addEventListener('focus', function() {
        if (currentSearchQuery && searchResults.children.length > 0) {
            searchResults.classList.remove('hidden');
        }
    });

    searchInput.addEventListener('blur', function() {
        // Hide results after a short delay to allow clicking on them
        setTimeout(() => {
            searchResults.classList.add('hidden');
        }, 200);
    });

    // Prevent hiding results when clicking inside them
    searchResults.addEventListener('mousedown', function(e) {
        e.preventDefault();
    });

    // Handle keyboard navigation
    searchInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            performSearch(currentSearchQuery);
        } else if (e.key === 'Escape') {
            searchResults.classList.add('hidden');
            searchInput.blur();
        }
    });

    // Handle search button click
    const searchButton = searchInput.parentElement.querySelector('button[title="Search"]');
    if (searchButton) {
        searchButton.addEventListener('click', function() {
            const query = searchInput.value.trim();
            if (query) {
                performSearch(query);
            }
        });
    }
}

function fetchSearchSuggestions(query) {
    fetch(`/api/search/?q=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(data => {
            displaySearchResults(data.results, query);
        })
        .catch(error => {
            console.error('Search error:', error);
            const searchResults = document.getElementById('searchResults');
            searchResults.innerHTML = '<div class="p-4 text-center text-red-500">Search failed. Please try again.</div>';
        });
}

function displaySearchResults(results, query) {
    const searchResults = document.getElementById('searchResults');
    
    if (!results || results.length === 0) {
        searchResults.innerHTML = `
            <div class="p-4 text-center text-gray-500">
                No results found for "${query}"
            </div>
        `;
        return;
    }

    let html = '';
    results.forEach(result => {
        let iconClass = 'fas fa-building';
        let typeText = 'Supplier';
        
        if (result.type === 'category') {
            iconClass = 'fas fa-th-large';
            typeText = 'Category';
        } else if (result.type === 'product') {
            iconClass = 'fas fa-cog';
            typeText = 'Product';
        } else if (result.type === 'html') {
            iconClass = 'fas fa-file-alt';
            typeText = 'Page Content';
        }

        html += `
            <a href="${result.url}" class="block p-3 hover:bg-gray-50 border-b border-gray-100 last:border-b-0 transition-colors">
                <div class="flex items-center">
                    <i class="${iconClass} text-blue-600 mr-3"></i>
                    <div>
                        <div class="font-medium text-gray-900">${result.title}</div>
                        <div class="text-sm text-gray-500 capitalize">${typeText}</div>
                        ${result.description ? `<div class="text-xs text-gray-400 mt-1">${result.description}</div>` : ''}
                    </div>
                </div>
            </a>
        `;
    });

    // Add a "View all results" link
    html += `
        <a href="/search/?q=${encodeURIComponent(query)}" class="block p-3 bg-gray-50 hover:bg-gray-100 text-center text-blue-600 font-medium transition-colors">
            View all results for "${query}"
        </a>
    `;

    searchResults.innerHTML = html;
}

function performSearch(query) {
    if (query.trim()) {
        window.location.href = `/search/?q=${encodeURIComponent(query)}`;
    }
}
