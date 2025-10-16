/**
 * Simple Translation System for English and Tamil
 */

let currentLang = 'en';

/**
 * Google Translate initialization
 */
function googleTranslateElementInit() {
  new google.translate.TranslateElement({
    pageLanguage: 'en',
    includedLanguages: 'en,ta',
    layout: google.translate.TranslateElement.InlineLayout.SIMPLE,
    autoDisplay: false
  }, 'google_translate_element');

  console.log('Google Translate initialized');
  setTimeout(setupButtons, 1000);

  // If a pending translate request exists (from mobile toggle clicked before this script loaded), consume it
  try {
    const pending = localStorage.getItem('pendingTranslate');
    if (pending === 'en' || pending === 'ta') {
      console.log('Found pendingTranslate in localStorage:', pending, '– applying now');
      // Clear it so we don't loop
      localStorage.removeItem('pendingTranslate');
      // Apply translation
      setTimeout(() => translateTo(pending), 300);
    }
  } catch (err) {
    console.warn('Error reading pendingTranslate from localStorage:', err);
  }
}

/**
 * Setup translation buttons (desktop + mobile)
 */
function setupButtons() {
  console.log('[setupButtons] Starting button setup...');

  // Get all buttons (desktop and mobile)
  const btnEn = document.getElementById('translate-en');
  const btnTa = document.getElementById('translate-ta');
  const btnEnMobile = document.getElementById('translate-en-mobile');
  const btnTaMobile = document.getElementById('translate-ta-mobile');

  console.log('[setupButtons] Found buttons:', {
    'translate-en': btnEn ? 'FOUND' : 'NOT FOUND',
    'translate-ta': btnTa ? 'FOUND' : 'NOT FOUND',
    'translate-en-mobile': btnEnMobile ? 'FOUND' : 'NOT FOUND',
    'translate-ta-mobile': btnTaMobile ? 'FOUND' : 'NOT FOUND'
  });

  // Only retry if we have no buttons at all
  if ((!btnEn && !btnTa) && (!btnEnMobile && !btnTaMobile)) {
    console.log('[setupButtons] No translation buttons found, retrying in 1 second...');
    setTimeout(setupButtons, 1000);
    return;
  }

  currentLang = getCurrentLanguage();
  console.log('[setupButtons] Current language from cookie:', currentLang);
  updateButtonStyles();
  updateMobileLabel();

  // Setup click handler function for both desktop and mobile buttons
  function attachTranslateHandler(button, lang) {
    if (button) {
      console.log(`[setupButtons] Attaching handler to ${button.id} for language ${lang}`);

      // Remove any previous handler to avoid stacking
      button.onclick = null;
      if (button._translateHandler) {
        button.removeEventListener('click', button._translateHandler);
      }

      button._translateHandler = function handler(e) {
        console.log(`[BUTTON CLICK] ${button.id} clicked for language ${lang}`);
        console.log('[BUTTON CLICK] Event details:', e);
        console.log('[BUTTON CLICK] Current language:', currentLang);
        console.log('[BUTTON CLICK] Target language:', lang);

        e.preventDefault();
        e.stopPropagation();

        if (currentLang !== lang) {
          console.log('[BUTTON CLICK] Language different, calling translateTo');
          try {
            translateTo(lang);
            console.log('[BUTTON CLICK] translateTo called successfully');
          } catch (error) {
            console.error('[BUTTON CLICK] Error calling translateTo:', error);
          }
        } else {
          console.log('[BUTTON CLICK] Language same, no translation needed');
        }
      };

      button.addEventListener('click', button._translateHandler);
      console.log(`[setupButtons] Successfully attached click handler to ${button.id}`);
    } else {
      console.log(`[setupButtons] Button not found, skipping: ${button ? button.id : 'unknown'}`);
    }
  }

  // Set up all translation buttons
  console.log('[setupButtons] Setting up desktop buttons...');
  attachTranslateHandler(btnEn, 'en');
  attachTranslateHandler(btnTa, 'ta');

  console.log('[setupButtons] Setting up mobile buttons...');
  attachTranslateHandler(btnEnMobile, 'en');
  attachTranslateHandler(btnTaMobile, 'ta');

  // Extra: If mobile menu is open, re-attach after a short delay to catch dynamic DOM
  const mobileMenu = document.getElementById('mobileMenu');
  if (mobileMenu && mobileMenu.classList.contains('show')) {
    setTimeout(() => {
      console.log('[setupButtons] Mobile menu is open, re-attaching handlers...');
      const btnEnMobile2 = document.getElementById('translate-en-mobile');
      const btnTaMobile2 = document.getElementById('translate-ta-mobile');
      attachTranslateHandler(btnEnMobile2, 'en');
      attachTranslateHandler(btnTaMobile2, 'ta');
      console.log('[setupButtons] Re-attached mobile handlers after menu open');
    }, 350);
  }

  console.log('[setupButtons] Translation setup complete');
}

/**
 * Apply translation via Google Translate cookie
 */
function translateTo(lang) {
  console.log('Translating to:', lang, 'from:', currentLang);

  try {
    // Clear existing cookies first
    document.cookie = 'googtrans=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/;';
    document.cookie = 'googtrans=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/; domain=' + window.location.hostname + ';';

    // Set new translation cookies
    const cookieValue = lang === 'en' ? '/en/en' : '/en/' + lang;
    const cookieBase = 'googtrans=' + cookieValue + '; expires=Thu, 31 Dec 2099 23:59:59 GMT; path=/;';

    document.cookie = cookieBase;
    document.cookie = cookieBase + ' domain=' + window.location.hostname + ';';
    console.log('Translation cookies set successfully');

    currentLang = lang;
    updateButtonStyles();
    updateMobileLabel();

    // Check if we're in mobile view and close the mobile menu
    const mobileMenu = document.getElementById('mobileMenu');
    if (mobileMenu && mobileMenu.classList.contains('show')) {
      mobileMenu.classList.remove('show');
    }

    // Force re-translate: Remove and re-insert Google Translate widget
    const gteElem = document.getElementById('google_translate_element');
    if (gteElem) {
      gteElem.innerHTML = '';
      setTimeout(() => {
        if (typeof googleTranslateElementInit === 'function') {
          googleTranslateElementInit();
          console.log('[translateTo] Re-initialized Google Translate widget');
        }
        // Fallback: reload if still not translated after short delay
        setTimeout(() => {
          const iframe = document.querySelector('iframe.goog-te-menu-frame');
          if (!iframe) {
            console.log('[translateTo] No Google iframe after re-init, reloading page...');
            window.location.reload();
          }
        }, 1000);
      }, 200);
    } else {
      // If widget not found, reload as fallback
      console.log('[translateTo] google_translate_element not found, reloading...');
      setTimeout(() => window.location.reload(), 800);
    }
  } catch (err) {
    console.error('Error during translation:', err);
    setTimeout(() => window.location.reload(), 800);
  }
}

/**
 * Get language from cookie
 */
function getCurrentLanguage() {
  const cookies = document.cookie.split(';');
  for (let cookie of cookies) {
    const [name, value] = cookie.trim().split('=');
    if (name === 'googtrans') {
      const match = value.match(/\/en\/(\w+)/);
      return match ? match[1] : 'en';
    }
  }
  return 'en';
}

/**
 * Update desktop button styles
 */
function updateButtonStyles() {
  const btnEn = document.getElementById('translate-en');
  const btnTa = document.getElementById('translate-ta');
  const btnEnMobile = document.getElementById('translate-en-mobile');
  const btnTaMobile = document.getElementById('translate-ta-mobile');
  if (!btnEn || !btnTa) {
    // If desktop buttons are missing, still update mobile buttons if available
    if (!btnEnMobile || !btnTaMobile) return;
  }

  if (currentLang === 'ta') {
    // Desktop
    if (btnTa) {
      btnTa.classList.add('primary');
      btnTa.classList.remove('outline');
      btnTa.classList.add('translate-btn');
    }
    if (btnEn) {
      btnEn.classList.add('outline');
      btnEn.classList.remove('primary');
      btnEn.classList.add('translate-btn');
    }
    // Mobile
    if (btnTaMobile) {
      btnTaMobile.classList.add('primary');
      btnTaMobile.classList.remove('outline');
      btnTaMobile.classList.add('translate-btn');
    }
    if (btnEnMobile) {
      btnEnMobile.classList.add('outline');
      btnEnMobile.classList.remove('primary');
      btnEnMobile.classList.add('translate-btn');
    }
  } else {
    // Desktop
    if (btnEn) {
      btnEn.classList.add('primary');
      btnEn.classList.remove('outline');
      btnEn.classList.add('translate-btn');
    }
    if (btnTa) {
      btnTa.classList.add('outline');
      btnTa.classList.remove('primary');
      btnTa.classList.add('translate-btn');
    }
    // Mobile
    if (btnEnMobile) {
      btnEnMobile.classList.add('primary');
      btnEnMobile.classList.remove('outline');
      btnEnMobile.classList.add('translate-btn');
    }
    if (btnTaMobile) {
      btnTaMobile.classList.add('outline');
      btnTaMobile.classList.remove('primary');
      btnTaMobile.classList.add('translate-btn');
    }
  }
}

/**
 * Update mobile label
 */
function updateMobileLabel() {
  const mobileLangSpan = document.getElementById('mobileLang');
  if (mobileLangSpan) {
    mobileLangSpan.textContent = currentLang === 'ta' ? 'Ta' : 'En';
    mobileLangSpan.className = `text-sm font-semibold ${currentLang === 'ta' ? 'text-blue-600' : 'text-yellow-600'}`;
  }
  // Also ensure mobile buttons (if present) reflect current state
  const btnEnMobile = document.getElementById('translate-en-mobile');
  const btnTaMobile = document.getElementById('translate-ta-mobile');
  // ensure translate-btn class exists on mobile buttons
  if (btnEnMobile) btnEnMobile.classList.add('translate-btn');
  if (btnTaMobile) btnTaMobile.classList.add('translate-btn');
  // Delegate style changes to updateButtonStyles
  // (updateButtonStyles will set primary/outline)
  updateButtonStyles();
}

/**
 * On page load
 */
document.addEventListener('DOMContentLoaded', () => {
  currentLang = getCurrentLanguage();
  updateButtonStyles();
  updateMobileLabel();
  setTimeout(setupButtons, 1200);
  // Also check for any pending translate requests in case googleTranslateElementInit didn't run yet
  try {
    const pending = localStorage.getItem('pendingTranslate');
    if (pending === 'en' || pending === 'ta') {
      console.log('DOMContentLoaded: found pendingTranslate:', pending, '– applying');
      localStorage.removeItem('pendingTranslate');
      setTimeout(() => {
        if (typeof translateTo === 'function') translateTo(pending);
      }, 500);
    }
  } catch (err) {
    console.warn('Error reading pendingTranslate during DOMContentLoaded:', err);
  }

  // --- Fix: Re-run setupButtons when mobile menu is opened ---
  const mobileMenuBtn = document.getElementById('mobileMenuBtn');
  if (mobileMenuBtn) {
    mobileMenuBtn.addEventListener('click', () => {
      // Wait for menu to render, then re-attach handlers
      setTimeout(() => {
        setupButtons();
        console.log('[DOMContentLoaded] Re-ran setupButtons after mobile menu open');
      }, 350);
    });
  }

  // --- Additional Fix: Use MutationObserver to watch for dynamic DOM changes ---
  // This ensures mobile translation buttons get handlers when they appear
  const observer = new MutationObserver((mutations) => {
    let shouldReSetup = false;

    mutations.forEach((mutation) => {
      if (mutation.type === 'childList') {
        mutation.addedNodes.forEach((node) => {
          if (node.nodeType === Node.ELEMENT_NODE) {
            // Check if the added node or its descendants contain translation buttons
            const hasTranslationButtons = node.querySelector &&
              (node.querySelector('#translate-en-mobile') ||
               node.querySelector('#translate-ta-mobile') ||
               node.querySelector('#translate-en-mobile-menu') ||
               node.querySelector('#translate-ta-mobile-menu') ||
               node.id === 'translate-en-mobile' ||
               node.id === 'translate-ta-mobile' ||
               node.id === 'translate-en-mobile-menu' ||
               node.id === 'translate-ta-mobile-menu');

            if (hasTranslationButtons) {
              console.log('[MutationObserver] Translation buttons detected in DOM, re-running setupButtons');
              shouldReSetup = true;
            }
          }
        });
      }
    });

    if (shouldReSetup) {
      // Small delay to ensure DOM is fully updated
      setTimeout(() => {
        setupButtons();
      }, 100);
    }
  });

  // Start observing changes to the entire document
  observer.observe(document.body, {
    childList: true,
    subtree: true
  });

  console.log('[DOMContentLoaded] MutationObserver started to watch for translation buttons');

  // --- Fix for mobile: delay Google Translate widget init slightly ---
  setTimeout(() => {
    if (typeof googleTranslateElementInit === 'function') {
      googleTranslateElementInit();
      console.log('[Fix] Google Translate initialized after delay');
    } else {
      console.warn('[Fix] googleTranslateElementInit not yet defined');
    }
  }, 1500);
});
