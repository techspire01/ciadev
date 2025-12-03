// Admin Dashboard JavaScript
let jobs = [];
let currentEditingId = null;

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    setupFormHandlers();
    setupMobileMenu();
});

// Mobile Menu Handler
function setupMobileMenu() {
    const mobileMenuToggle = document.getElementById('mobileMenuToggle');
    const sidebar = document.getElementById('sidebar');
    const mobileOverlay = document.getElementById('mobileOverlay');

    if (mobileMenuToggle) {
        mobileMenuToggle.addEventListener('click', function() {
            mobileMenuToggle.classList.toggle('active');
            sidebar.classList.toggle('active');
            if (mobileOverlay) {
                mobileOverlay.classList.toggle('active');
            }
        });

        // Close sidebar when a nav link is clicked
        const navLinks = document.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.addEventListener('click', function() {
                mobileMenuToggle.classList.remove('active');
                sidebar.classList.remove('active');
                if (mobileOverlay) {
                    mobileOverlay.classList.remove('active');
                }
            });
        });

        // Close sidebar when clicking the overlay
        if (mobileOverlay) {
            mobileOverlay.addEventListener('click', function() {
                mobileMenuToggle.classList.remove('active');
                sidebar.classList.remove('active');
                mobileOverlay.classList.remove('active');
            });
        }

        // Close sidebar when clicking outside
        document.addEventListener('click', function(event) {
            if (!sidebar.contains(event.target) && !mobileMenuToggle.contains(event.target)) {
                mobileMenuToggle.classList.remove('active');
                sidebar.classList.remove('active');
                if (mobileOverlay) {
                    mobileOverlay.classList.remove('active');
                }
            }
        });
    }
}

// Tab Switching
function switchTab(tabName) {
    // Hide all tab contents
    const tabContents = document.querySelectorAll('.tab-content');
    tabContents.forEach(tab => {
        tab.classList.remove('active');
    });

    // Remove active class from all nav links
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.classList.remove('active');
    });

    // Show the selected tab
    const selectedTab = document.getElementById(tabName);
    if (selectedTab) {
        selectedTab.classList.add('active');
    }

    // Add active class to clicked nav link
    event.target.classList.add('active');
}

// Load Internships - Removed localStorage caching
// Internships are now fully managed server-side



// Render Internships - Removed since internships are now rendered server-side
// function renderInternships() { ... }



// Add Internship
function addInternship() {
    const form = document.getElementById('internship-form');
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());

    fetch('/api/internships/add/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken(),
            'Cache-Control': 'no-cache, no-store, must-revalidate'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert(data.message);
            form.reset();
            location.reload(); // Reload to show new internship
        } else {
            alert('Error: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while adding the internship.');
    });
}

// Add Job
function addJob() {
    const form = document.getElementById('job-form');
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());

    fetch('/api/jobs/add/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken(),
            'Cache-Control': 'no-cache, no-store, must-revalidate'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert(data.message);
            form.reset();
            location.reload(); // Reload to show new job
        } else {
            alert('Error: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while adding the job.');
    });
}

// Setup Form Handlers
function setupFormHandlers() {
    const internshipForm = document.getElementById('internship-form');
    const jobForm = document.getElementById('job-form');
    if (internshipForm) {
        internshipForm.addEventListener('submit', function(e) {
            e.preventDefault();
            addInternship();
        });
    }
    if (jobForm) {
        jobForm.addEventListener('submit', function(e) {
            e.preventDefault();
            addJob();
        });
    }
}

// Edit Job
function editJob(id) {
    const job = jobs.find(j => j.id === id);
    if (!job) return;

    currentEditingId = id;
    const modal = document.getElementById('edit-job-modal');
    if (modal) {
        document.querySelector('#edit-job-modal input[name="title"]').value = job.title;
        document.querySelector('#edit-job-modal input[name="company"]').value = job.company;
        document.querySelector('#edit-job-modal input[name="experience"]').value = job.experience;
        document.querySelector('#edit-job-modal input[name="salary"]').value = job.salary;
        modal.classList.add('active');
    }
}


// Save Internship Changes (AJAX removed; handled server-side)

// Save Job Changes - Removed since jobs are now server-side

// Toggle Internship Status - Removed since internships are now server-side

// Toggle Job Status
function toggleJobStatus(id) {
    if (confirm('Are you sure you want to toggle the status of this job?')) {
        fetch(`/portal/api/jobs/${id}/toggle/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken(),
                'Cache-Control': 'no-cache, no-store, must-revalidate'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert(data.message);
                location.reload(); // Reload to reflect changes
            } else {
                alert('Error: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while toggling job status.');
        });
    }
}


// Toggle Internship Status (AJAX removed; handled server-side)


// Delete Internship (AJAX removed; handled server-side)

// Delete Job
function deleteJob(id) {
    if (confirm('Are you sure you want to delete this job?')) {
        fetch(`/portal/api/jobs/${id}/delete/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken(),
                'Cache-Control': 'no-cache, no-store, must-revalidate'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert(data.message);
                location.reload(); // Reload to show fresh data
            } else {
                alert('Error: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while deleting the job.');
        });
    }
}

// Close Modal
function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('active');
    }
    currentEditingId = null;
}

// Load Internships from API - Removed since internships are now loaded server-side
// function loadInternshipsFromAPI() { ... }

// Get CSRF Token
function getCSRFToken() {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
    return csrfToken ? csrfToken.value : '';
}

// Edit Internship Modal Functions
function openEditModal(id, title, company, duration, stipend, email, location, description, requirements, responsibilities) {
    document.getElementById('edit-id').value = id;
    document.getElementById('edit-title').value = title;
    document.getElementById('edit-company').value = company;
    document.getElementById('edit-duration').value = duration;
    document.getElementById('edit-stipend').value = stipend;
    document.getElementById('edit-email').value = email;
    document.getElementById('edit-location').value = location;
    document.getElementById('edit-description').value = description;
    document.getElementById('edit-requirements').value = requirements;
    document.getElementById('edit-responsibilities').value = responsibilities;

    document.getElementById('edit-modal').classList.add('active');
}

function submitEditForm() {
    const id = document.getElementById('edit-id').value;
    const form = document.getElementById('edit-form');

    form.action = `/portal-admin/edit-internship/${id}/`;
    form.method = "POST";

    form.submit();
}

function closeEditModal() {
    document.getElementById('edit-modal').classList.remove('active');
}

// Edit Job Modal Functions
function openEditJobModal(id, title, company, location, salary, email, description, requirements, responsibilities, experience) {
    document.getElementById('edit-job-id').value = id;
    document.getElementById('edit-job-title').value = title;
    document.getElementById('edit-job-company').value = company;
    document.getElementById('edit-job-location').value = location;
    document.getElementById('edit-job-salary').value = salary;
    document.getElementById('edit-job-email').value = email;
    document.getElementById('edit-job-description').value = description;
    document.getElementById('edit-job-requirements').value = requirements;
    document.getElementById('edit-job-responsibilities').value = responsibilities;
    document.getElementById('edit-job-experience').value = experience || '';

    document.getElementById('edit-job-modal').classList.add('active');
}

function submitEditJobForm() {
    const id = document.getElementById('edit-job-id').value;
    const form = document.getElementById('edit-job-form');

    form.method = "POST";
    form.action = `/portal-admin/edit-job/${id}/`;

    form.submit();
}

function closeEditJobModal() {
    document.getElementById('edit-job-modal').classList.remove('active');
}

// Job Filtering and Search
document.addEventListener("DOMContentLoaded", function () {
    const searchInput = document.getElementById("job-search");
    const statusFilter = document.getElementById("job-status-filter");

    if (searchInput && statusFilter) {
        searchInput.addEventListener("input", filterJobs);
        statusFilter.addEventListener("change", filterJobs);
    }
});

function filterJobs() {
    const query = document.getElementById("job-search").value.toLowerCase();
    const status = document.getElementById("job-status-filter").value;

    const cards = document.querySelectorAll("#jobs-container .opportunity-card");

    cards.forEach(card => {
        const title = card.dataset.title;
        const activeStatus = card.dataset.status;

        const matchesSearch = title.includes(query);
        const matchesStatus =
            status === "all" || status === activeStatus;

        if (matchesSearch && matchesStatus) {
            card.style.display = "block";
        } else {
            card.style.display = "none";
        }
    });
}

// Close modal when clicking outside of it
window.addEventListener('click', function(event) {
    const editModal = document.getElementById('edit-modal');
    const editJobModal = document.getElementById('edit-job-modal');

    if (event.target === editModal) {
        closeEditModal();
    }
    if (event.target === editJobModal) {
        closeEditJobModal();
    }
});
