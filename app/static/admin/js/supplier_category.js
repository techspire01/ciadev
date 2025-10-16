// JavaScript for dynamic category field in Supplier admin
(function($) {
    $(document).ready(function() {
        console.log('Supplier category JS loaded');

        var categoryField = $('#id_category');
        var newCategoryField = $('#id_new_category').closest('.form-row, .form-group');

        if (!newCategoryField.length) {
            newCategoryField = $('#id_new_category').parent();
        }

        if (!categoryField.length) {
            console.log('Category field not found, exiting');
            return;
        }

        console.log('Category field found:', categoryField.length, 'elements');

        function toggleNewCategory() {
            if (categoryField.val() === '__add_new__') {
                newCategoryField.show();
            } else {
                newCategoryField.hide();
            }
        }

        function refreshCategoryDropdown() {
            console.log('Refreshing category dropdown...');

            // Make AJAX call to get updated categories
            $.ajax({
                url: '/get_supplier_categories/',  // URL to our new AJAX endpoint
                type: 'GET',
                timeout: 5000,
                success: function(response) {
                    console.log('AJAX response received:', response);
                    if (response.success) {
                        var categories = response.categories;
                        var currentValue = categoryField.val();

                        console.log('Current categories:', categories);
                        console.log('Current selected value:', currentValue);

                        // Clear existing options (except the first empty option if it exists)
                        categoryField.find('option').not(':first').remove();

                        // Add "Add new category" option
                        categoryField.append($('<option>', {
                            value: '__add_new__',
                            text: 'Add new category'
                        }));

                        // Add updated categories
                        categories.forEach(function(category) {
                            categoryField.append($('<option>', {
                                value: category,
                                text: category
                            }));
                        });

                        // Restore the previously selected value if it still exists
                        if (currentValue && currentValue !== '__add_new__') {
                            categoryField.val(currentValue);
                        }

                        console.log('Category dropdown refreshed successfully');
                    } else {
                        console.error('Failed to refresh categories:', response.error);
                    }
                },
                error: function(xhr, status, error) {
                    console.error('AJAX error while refreshing categories:', error);
                    console.error('Status:', status);
                    console.error('Response:', xhr.responseText);
                }
            });
        }

        // Test AJAX endpoint on page load
        function testAjaxEndpoint() {
            console.log('Testing AJAX endpoint...');
            $.ajax({
                url: '/get_supplier_categories/',
                type: 'GET',
                success: function(response) {
                    console.log('✅ AJAX endpoint working:', response);
                },
                error: function(xhr, status, error) {
                    console.error('❌ AJAX endpoint not working:', error, status, xhr.responseText);
                }
            });
        }

        function handleFormSubmission() {
            console.log('Setting up form submission handler');

            var form = categoryField.closest('form');
            if (!form.length) {
                console.log('Form not found');
                return;
            }

            console.log('Form found, setting up submission handler');

            // Method 1: Listen for submit button clicks
            form.find('input[type="submit"], button[type="submit"]').on('click', function(e) {
                console.log('Submit button clicked, will refresh dropdown after submission');
                // Refresh dropdown after a delay to allow form submission to complete
                setTimeout(function() {
                    refreshCategoryDropdown();
                }, 2000);
            });

            // Method 2: Listen for successful admin messages
            var observer = new MutationObserver(function(mutations) {
                mutations.forEach(function(mutation) {
                    if (mutation.type === 'childList') {
                        $(mutation.addedNodes).each(function() {
                            var $node = $(this);
                            if ($node.find('.messagelist .success, .alert-success, .success').length > 0 ||
                                $node.hasClass('success') ||
                                $node.text().toLowerCase().includes('success')) {
                                console.log('Success message detected, refreshing dropdown');
                                setTimeout(function() {
                                    refreshCategoryDropdown();
                                }, 1000);
                            }
                        });
                    }
                });
            });

            // Start observing for success messages
            observer.observe(document.body, {
                childList: true,
                subtree: true
            });

            // Method 3: Periodic refresh for real-time updates
            setInterval(function() {
                var currentOptionsCount = categoryField.find('option').length;
                var newCategoryValue = $('#id_new_category').val();

                if (newCategoryValue && newCategoryValue.trim() !== '') {
                    console.log('New category detected, refreshing dropdown');
                    setTimeout(function() {
                        refreshCategoryDropdown();
                    }, 1500);
                }
            }, 3000);
        }

        // Initialize existing functionality
        toggleNewCategory();
        categoryField.change(toggleNewCategory);

        // Add new functionality for dropdown refresh
        handleFormSubmission();

        // Refresh dropdown when the page loads (in case of validation errors)
        if (window.location.href.indexOf('supplier') !== -1) {
            console.log('Supplier page detected, refreshing dropdown on load');
            setTimeout(function() {
                refreshCategoryDropdown();
            }, 1000);
        }

        // Test AJAX endpoint
        testAjaxEndpoint();
    });
})(django.jQuery);
