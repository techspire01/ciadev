document.addEventListener('DOMContentLoaded', function() {
    // Function to handle image preview for new uploads
    function setupImagePreview() {
        const imageInput = document.querySelector('input[type="file"][name="image"]');
        if (!imageInput) return;

        // Create preview container
        const previewContainer = document.createElement('div');
        previewContainer.id = 'image-preview-container';
        previewContainer.style.marginTop = '10px';
        previewContainer.style.padding = '10px';
        previewContainer.style.border = '1px solid #ccc';
        previewContainer.style.borderRadius = '4px';
        previewContainer.style.backgroundColor = '#f9f9f9';

        const previewTitle = document.createElement('h4');
        previewTitle.textContent = 'Image Preview:';
        previewTitle.style.margin = '0 0 10px 0';
        previewTitle.style.fontSize = '14px';
        previewTitle.style.fontWeight = 'bold';

        const previewImg = document.createElement('img');
        previewImg.id = 'image-preview';
        previewImg.style.maxWidth = '200px';
        previewImg.style.maxHeight = '200px';
        previewImg.style.objectFit = 'cover';
        previewImg.style.border = '1px solid #ddd';
        previewImg.style.display = 'none'; // Hidden initially

        previewContainer.appendChild(previewTitle);
        previewContainer.appendChild(previewImg);

        // Insert after the file input
        imageInput.parentNode.insertBefore(previewContainer, imageInput.nextSibling);

        // Handle file selection
        imageInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file && file.type.startsWith('image/')) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    previewImg.src = e.target.result;
                    previewImg.style.display = 'block';
                };
                reader.readAsDataURL(file);
            } else {
                previewImg.style.display = 'none';
            }
        });
    }

    // Setup preview for add form
    if (window.location.pathname.includes('/add/') || window.location.pathname.includes('/change/')) {
        setupImagePreview();
    }
});
