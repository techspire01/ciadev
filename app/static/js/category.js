document.addEventListener('DOMContentLoaded', function() {
    // Handle View Companies button clicks
    const viewCompaniesButtons = document.querySelectorAll('.view-companies-btn');
    const viewSubcategoryCompaniesButtons = document.querySelectorAll('.view-subcategory-companies-btn');
    const companiesModal = document.getElementById('companiesModal');
    const modalTitle = document.getElementById('modalTitle');
    const modalCategory = document.getElementById('modalCategory');
    const companiesList = document.getElementById('companiesList');
    const closeModal = document.getElementById('closeModal');

    // Add ripple effect to buttons
    function addRippleEffect(e) {
        const button = e.currentTarget;
        const ripple = document.createElement('span');
        const rect = button.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = e.clientX - rect.left - size / 2;
        const y = e.clientY - rect.top - size / 2;

        ripple.style.width = ripple.style.height = size + 'px';
        ripple.style.left = x + 'px';
        ripple.style.top = y + 'px';
        ripple.classList.add('ripple');

        button.appendChild(ripple);
        setTimeout(() => ripple.remove(), 600);
    }

    // Smooth card animations on load
    const cards = document.querySelectorAll('.card-hover');
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -100px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    cards.forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'all 0.6s cubic-bezier(0.34, 1.56, 0.64, 1)';
        observer.observe(card);
    });

    viewCompaniesButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            addRippleEffect(e);
            const category = this.getAttribute('data-category');
            fetchCompaniesByCategory(category);
        });
    });

    viewSubcategoryCompaniesButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            addRippleEffect(e);
            const category = this.getAttribute('data-category');
            const subcategory = this.getAttribute('data-subcategory');
            fetchCompaniesByCategoryAndSubcategory(category, subcategory);
        });
    });

    // Close modal functionality with smooth animation
    closeModal.addEventListener('click', function() {
        companiesModal.classList.add('fade-out');
        setTimeout(() => {
            companiesModal.classList.add('hidden');
            companiesModal.classList.remove('fade-out');
        }, 300);
    });

    // Close modal when clicking outside
    companiesModal.addEventListener('click', function(e) {
        if (e.target === companiesModal) {
            companiesModal.classList.add('fade-out');
            setTimeout(() => {
                companiesModal.classList.add('hidden');
                companiesModal.classList.remove('fade-out');
            }, 300);
        }
    });

    // Escape key to close modal
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && !companiesModal.classList.contains('hidden')) {
            companiesModal.classList.add('fade-out');
            setTimeout(() => {
                companiesModal.classList.add('hidden');
                companiesModal.classList.remove('fade-out');
            }, 300);
        }
    });

    // Filter functionality with smooth animations
    const filterSelect = document.querySelector('select');
    const filterButton = document.querySelector('button[class*="bg-blue-500"]');
    const categoryCards = document.querySelectorAll('.bg-white.rounded-xl');

    if (filterButton) {
        filterButton.addEventListener('click', function(e) {
            addRippleEffect(e);
            const sortBy = filterSelect.value;
            sortCategories(sortBy);
        });
    }

    function sortCategories(sortBy) {
        const categoriesContainer = document.querySelector('.grid.grid-cols-1');
        const categories = Array.from(categoryCards);
        
        // Add fade-out animation
        categories.forEach(card => {
            card.style.animation = 'fadeOut 0.3s ease-out forwards';
        });

        setTimeout(() => {
            categories.sort((a, b) => {
                const aName = a.querySelector('h3').textContent;
                const bName = b.querySelector('h3').textContent;
                const aCount = parseInt(a.querySelector('p.text-gray-500').textContent) || 0;
                const bCount = parseInt(b.querySelector('p.text-gray-500').textContent) || 0;
                
                switch(sortBy) {
                    case 'Sort by: Name A-Z':
                        return aName.localeCompare(bName);
                    case 'Sort by: Name Z-A':
                        return bName.localeCompare(aName);
                    case 'Sort by: Most Products':
                        return bCount - aCount;
                    case 'Sort by: Popular':
                    default:
                        return 0;
                }
            });

            // Clear container and re-add sorted categories with animation
            categoriesContainer.innerHTML = '';
            categories.forEach((card, index) => {
                card.style.animation = 'none';
                card.style.opacity = '0';
                card.style.transform = 'translateY(20px)';
                categoriesContainer.appendChild(card);
                
                setTimeout(() => {
                    card.style.transition = 'all 0.5s cubic-bezier(0.34, 1.56, 0.64, 1)';
                    card.style.opacity = '1';
                    card.style.transform = 'translateY(0)';
                }, index * 50);
            });
        }, 300);
    }

    function fetchCompaniesByCategory(category) {
        // Show loading state with animation
        companiesList.innerHTML = `
            <div class="flex justify-center items-center py-12">
                <div class="relative w-12 h-12">
                    <div class="absolute inset-0 rounded-full border-4 border-blue-200"></div>
                    <div class="absolute inset-0 rounded-full border-4 border-transparent border-t-blue-500 animate-spin"></div>
                </div>
                <span class="ml-4 text-gray-600 font-medium">Loading companies...</span>
            </div>
        `;
        
        modalCategory.textContent = category;
        companiesModal.classList.remove('hidden');
        companiesModal.classList.add('fade-in');

        // Make AJAX request
        fetch(`/api/companies_by_category/?category=${encodeURIComponent(category)}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                displayCompanies(data.companies);
            })
            .catch(error => {
                console.error('Error fetching companies:', error);
                companiesList.innerHTML = `
                    <div class="text-center py-12 text-red-600">
                        <i class="fas fa-exclamation-triangle text-4xl mb-4"></i>
                        <p class="font-medium">Error loading companies. Please try again.</p>
                    </div>
                `;
            });
    }

    function fetchCompaniesByCategoryAndSubcategory(category, subcategory) {
        // Show loading state with animation
        companiesList.innerHTML = `
            <div class="flex justify-center items-center py-12">
                <div class="relative w-12 h-12">
                    <div class="absolute inset-0 rounded-full border-4 border-indigo-200"></div>
                    <div class="absolute inset-0 rounded-full border-4 border-transparent border-t-indigo-500 animate-spin"></div>
                </div>
                <span class="ml-4 text-gray-600 font-medium">Loading companies...</span>
            </div>
        `;

        modalCategory.textContent = `${category} - ${subcategory}`;
        companiesModal.classList.remove('hidden');
        companiesModal.classList.add('fade-in');

        // Make AJAX request with category and subcategory filters
        fetch(`/api/companies_by_category/?category=${encodeURIComponent(category)}&subcategory=${encodeURIComponent(subcategory)}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                displayCompanies(data.companies);
            })
            .catch(error => {
                console.error('Error fetching companies:', error);
                companiesList.innerHTML = `
                    <div class="text-center py-12 text-red-600">
                        <i class="fas fa-exclamation-triangle text-4xl mb-4"></i>
                        <p class="font-medium">Error loading companies. Please try again.</p>
                    </div>
                `;
            });
    }

    function displayCompanies(companies) {
        if (companies.length === 0) {
            companiesList.innerHTML = `
                <div class="text-center py-12 text-gray-500">
                    <i class="fas fa-building text-4xl mb-4"></i>
                    <p class="font-medium">No companies found in this category.</p>
                </div>
            `;
            return;
        }

        companiesList.innerHTML = `
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                ${companies.map((company, index) => `
                    <div class="bg-white rounded-lg shadow-md p-4 hover:shadow-xl transition-all duration-300 transform hover:-translate-y-2 company-item" style="animation: slideUp 0.5s ease-out forwards; animation-delay: ${index * 50}ms;">
                        <div class="flex items-center mb-3">
                            ${company.logo ? `
                                <img src="${company.logo}" alt="${company.name}" class="w-12 h-12 rounded-full object-cover mr-3 ring-2 ring-blue-200">
                            ` : `
                                <div class="w-12 h-12 bg-gradient-to-br from-blue-100 to-indigo-200 rounded-full flex items-center justify-center mr-3 ring-2 ring-blue-200">
                                    <i class="fas fa-building text-blue-600 text-sm"></i>
                                </div>
                            `}
                            <div>
                                <h4 class="font-semibold text-gray-800 hover:text-blue-600 transition-colors">${company.name}</h4>
                                <p class="text-sm text-gray-600">${company.category}</p>
                            </div>
                        </div>
                        
                        ${company.sub_categories.length > 0 ? `
                            <div class="mb-3 pb-3 border-b border-gray-200">
                                <p class="text-xs text-gray-500 mb-2 font-semibold">Subcategories:</p>
                                <div class="flex flex-wrap gap-1">
                                    ${company.sub_categories.map(sub => `
                                        <span class="bg-blue-100 text-blue-700 text-xs px-2 py-1 rounded-full font-medium transition-all hover:bg-blue-200">
                                            ${sub}
                                        </span>
                                    `).join('')}
                                </div>
                            </div>
                        ` : ''}
                        
                        <div class="space-y-2 text-sm mb-3">
                            ${company.email ? `
                                <p class="text-gray-600 flex items-center">
                                    <i class="fas fa-envelope mr-2 text-blue-500 flex-shrink-0"></i>
                                    <a href="mailto:${company.email}" class="hover:text-blue-600 transition-colors">${company.email}</a>
                                </p>
                            ` : ''}
                            
                            ${company.phone_number ? `
                                <p class="text-gray-600 flex items-center">
                                    <i class="fas fa-phone mr-2 text-blue-500 flex-shrink-0"></i>
                                    <a href="tel:${company.phone_number}" class="hover:text-blue-600 transition-colors">${company.phone_number}</a>
                                </p>
                            ` : ''}
                        </div>
                        
                        <div class="pt-3 border-t border-gray-200">
                            <button onclick="openCompanyModal(${company.id})" 
                               class="text-blue-600 hover:text-blue-800 text-sm font-bold transition-all hover:translate-x-1 inline-flex items-center gap-1">
                                View Details <i class="fas fa-arrow-right text-xs"></i>
                            </button>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;

        // Add animation styles
        const style = document.createElement('style');
        style.textContent = `
            @keyframes slideUp {
                from {
                    opacity: 0;
                    transform: translateY(20px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
            @keyframes fadeOut {
                to {
                    opacity: 0;
                    transform: scale(0.95);
                }
            }
            .ripple {
                position: absolute;
                border-radius: 50%;
                background: rgba(255, 255, 255, 0.6);
                transform: scale(0);
                animation: rippleEffect 0.6s ease-out;
                pointer-events: none;
            }
            @keyframes rippleEffect {
                to {
                    transform: scale(4);
                    opacity: 0;
                }
            }
            .fade-in {
                animation: fadeInModal 0.3s ease-out;
            }
            .fade-out {
                animation: fadeOutModal 0.3s ease-out;
            }
            @keyframes fadeInModal {
                from {
                    opacity: 0;
                }
                to {
                    opacity: 1;
                }
            }
            @keyframes fadeOutModal {
                from {
                    opacity: 1;
                }
                to {
                    opacity: 0;
                }
            }
        `;
        if (!document.querySelector('style[data-enhanced]')) {
            style.setAttribute('data-enhanced', 'true');
            document.head.appendChild(style);
        }
    }

    // Smooth scroll behavior
    window.addEventListener('scroll', () => {
        cards.forEach(card => {
            const rect = card.getBoundingClientRect();
            if (rect.top < window.innerHeight) {
                card.style.opacity = '1';
            }
        });
    });
});