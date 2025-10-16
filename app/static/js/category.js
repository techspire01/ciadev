document.addEventListener('DOMContentLoaded', function() {
    // Handle View Companies button clicks
    const viewCompaniesButtons = document.querySelectorAll('.view-companies-btn');
    const viewSubcategoryCompaniesButtons = document.querySelectorAll('.view-subcategory-companies-btn');
    const companiesModal = document.getElementById('companiesModal');
    const modalTitle = document.getElementById('modalTitle');
    const modalCategory = document.getElementById('modalCategory');
    const companiesList = document.getElementById('companiesList');
    const closeModal = document.getElementById('closeModal');

    viewCompaniesButtons.forEach(button => {
        button.addEventListener('click', function() {
            const category = this.getAttribute('data-category');
            fetchCompaniesByCategory(category);
        });
    });

    viewSubcategoryCompaniesButtons.forEach(button => {
        button.addEventListener('click', function() {
            const category = this.getAttribute('data-category');
            const subcategory = this.getAttribute('data-subcategory');
            fetchCompaniesByCategoryAndSubcategory(category, subcategory);
        });
    });

    // Close modal functionality
    closeModal.addEventListener('click', function() {
        companiesModal.classList.add('hidden');
    });

    // Close modal when clicking outside
    companiesModal.addEventListener('click', function(e) {
        if (e.target === companiesModal) {
            companiesModal.classList.add('hidden');
        }
    });

    // Escape key to close modal
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && !companiesModal.classList.contains('hidden')) {
            companiesModal.classList.add('hidden');
        }
    });

    // Filter functionality
    const filterSelect = document.querySelector('select');
    const filterButton = document.querySelector('button[class*="bg-blue-500"]');
    const categoryCards = document.querySelectorAll('.bg-white.rounded-xl');

    if (filterButton) {
        filterButton.addEventListener('click', function() {
            const sortBy = filterSelect.value;
            sortCategories(sortBy);
        });
    }

    function sortCategories(sortBy) {
        const categoriesContainer = document.querySelector('.grid.grid-cols-1');
        const categories = Array.from(categoryCards);
        
        categories.sort((a, b) => {
            const aName = a.querySelector('h3').textContent;
            const bName = b.querySelector('h3').textContent;
            const aCount = parseInt(a.querySelector('p.text-gray-500').textContent);
            const bCount = parseInt(b.querySelector('p.text-gray-500').textContent);
            
            switch(sortBy) {
                case 'Sort by: Name A-Z':
                    return aName.localeCompare(bName);
                case 'Sort by: Name Z-A':
                    return bName.localeCompare(aName);
                case 'Sort by: Most Products':
                    return bCount - aCount;
                case 'Sort by: Popular':
                default:
                    return 0; // Keep original order
            }
        });

        // Clear container and re-add sorted categories
        categoriesContainer.innerHTML = '';
        categories.forEach(card => {
            categoriesContainer.appendChild(card);
        });
    }

    function fetchCompaniesByCategory(category) {
        // Show loading state
        companiesList.innerHTML = `
            <div class="flex justify-center items-center py-8">
                <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
                <span class="ml-2 text-gray-600">Loading companies...</span>
            </div>
        `;
        
        modalCategory.textContent = category;
        companiesModal.classList.remove('hidden');

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
                    <div class="text-center py-8 text-red-600">
                        <i class="fas fa-exclamation-triangle text-2xl mb-2"></i>
                        <p>Error loading companies. Please try again.</p>
                    </div>
                `;
            });
    }

    function fetchCompaniesByCategoryAndSubcategory(category, subcategory) {
        // Show loading state
        companiesList.innerHTML = `
            <div class="flex justify-center items-center py-8">
                <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
                <span class="ml-2 text-gray-600">Loading companies...</span>
            </div>
        `;

        modalCategory.textContent = `${category} - ${subcategory}`;
        companiesModal.classList.remove('hidden');

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
                    <div class="text-center py-8 text-red-600">
                        <i class="fas fa-exclamation-triangle text-2xl mb-2"></i>
                        <p>Error loading companies. Please try again.</p>
                    </div>
                `;
            });
    }

    function displayCompanies(companies) {
        if (companies.length === 0) {
            companiesList.innerHTML = `
                <div class="text-center py-8 text-gray-500">
                    <i class="fas fa-building text-2xl mb-2"></i>
                    <p>No companies found in this category.</p>
                </div>
            `;
            return;
        }

        companiesList.innerHTML = `
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                ${companies.map(company => `
                    <div class="bg-white rounded-lg shadow-md p-4 hover:shadow-lg transition-shadow">
                        <div class="flex items-center mb-3">
                            ${company.logo ? `
                                <img src="${company.logo}" alt="${company.name}" class="w-12 h-12 rounded-full object-cover mr-3">
                            ` : `
                                <div class="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mr-3">
                                    <i class="fas fa-building text-blue-500"></i>
                                </div>
                            `}
                            <div>
                                <h4 class="font-semibold text-gray-800">${company.name}</h4>
                                <p class="text-sm text-gray-600">${company.category}</p>
                            </div>
                        </div>
                        
                        ${company.sub_categories.length > 0 ? `
                            <div class="mb-3">
                                <p class="text-xs text-gray-500 mb-1">Subcategories:</p>
                                <div class="flex flex-wrap gap-1">
                                    ${company.sub_categories.map(sub => `
                                        <span class="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full">
                                            ${sub}
                                        </span>
                                    `).join('')}
                                </div>
                            </div>
                        ` : ''}
                        
                        <div class="space-y-1 text-sm">
                            ${company.email ? `
                                <p class="text-gray-600">
                                    <i class="fas fa-envelope mr-2 text-blue-500"></i>
                                    ${company.email}
                                </p>
                            ` : ''}
                            
                            ${company.phone_number ? `
                                <p class="text-gray-600">
                                    <i class="fas fa-phone mr-2 text-blue-500"></i>
                                    ${company.phone_number}
                                </p>
                            ` : ''}
                        </div>
                        
                        <div class="mt-3 pt-3 border-t border-gray-100">
                            <button onclick="openCompanyModal(${company.id})" 
                               class="text-blue-600 hover:text-blue-800 text-sm font-medium">
                                View Details →
                            </button>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    }
});