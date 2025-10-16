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
  const btnEn = document.getElementById('translate-en');
  const btnTa = document.getElementById('translate-ta');
  const mobileToggle = document.getElementById('mobileLanguageToggle');
  const mobileLangSpan = document.getElementById('mobileLang');
  const btnEnMobile = document.getElementById('translate-en-mobile');
  const btnTaMobile = document.getElementById('translate-ta-mobile');

  if (!btnEn && !btnTa && !mobileToggle && !btnEnMobile && !btnTaMobile) {
    console.log('Translation controls not found, retrying...');
    setTimeout(setupButtons, 1000);
    return;
  }

  currentLang = getCurrentLanguage();
  updateButtonStyles();
  updateMobileLabel();

  // --- Desktop buttons ---
  if (btnEn && btnTa) {
    btnEn.onclick = (e) => {
      e.preventDefault();
      if (currentLang !== 'en') translateTo('en');
    };
    btnTa.onclick = (e) => {
      e.preventDefault();
      if (currentLang !== 'ta') translateTo('ta');
    };
  }

  // --- Mobile buttons (explicit EN/TA buttons inside mobile menu) ---
  if (btnEnMobile) {
    btnEnMobile.onclick = (e) => {
      e.preventDefault();
      if (currentLang !== 'en') translateTo('en');
    };
  }
  if (btnTaMobile) {
    btnTaMobile.onclick = (e) => {
      e.preventDefault();
      if (currentLang !== 'ta') translateTo('ta');
    };
  }

  console.log('Translation setup complete');
}

/**
 * Apply translation via Google Translate cookie
 */
function translateTo(lang) {
  console.log('Translating to:', lang);

  // Correctly set cookies at all levels
  const cookieValue = lang === 'en' ? '/en/en' : '/en/' + lang;
  const cookieBase = 'googtrans=' + cookieValue + '; expires=Thu, 31 Dec 2099 23:59:59 GMT; path=/;';

  document.cookie = cookieBase;
  document.cookie = cookieBase + ' domain=' + window.location.hostname + ';';

  currentLang = lang;
  updateButtonStyles();
  updateMobileLabel();

  // Force re-translate if Google Translate is ready
  const iframe = document.querySelector('iframe.goog-te-menu-frame');
  if (iframe) {
    console.log('Google iframe detected, forcing reload...');
    setTimeout(() => window.location.reload(), 500);
  } else {
    console.log('No Google iframe yet, reloading...');
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
});
