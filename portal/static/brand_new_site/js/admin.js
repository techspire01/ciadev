// Admin Dashboard JavaScript
let internships = [];
let jobs = [];
let currentEditingId = null;

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    loadInternships();
    loadJobs();
    setupFormHandlers();
    setupMobileMenu();
});

// Mobile Menu Handler
function setupMobileMenu() {
    const mobileMenuToggle = document.getElementById('mobileMenuToggle');
    const sidebar = document.getElementById('sidebar');

    if (mobileMenuToggle) {
        mobileMenuToggle.addEventListener('click', function() {
            mobileMenuToggle.classList.toggle('active');
            sidebar.classList.toggle('active');
        });

        // Close sidebar when a nav link is clicked
        const navLinks = document.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.addEventListener('click', function() {
                mobileMenuToggle.classList.remove('active');
                sidebar.classList.remove('active');
            });
        });

        // Close sidebar when clicking outside
        document.addEventListener('click', function(event) {
            if (!sidebar.contains(event.target) && !mobileMenuToggle.contains(event.target)) {
                mobileMenuToggle.classList.remove('active');
                sidebar.classList.remove('active');
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

// Load Internships
function loadInternships() {
    // Fetch from JSON or load from localStorage
    const stored = localStorage.getItem('internships');
    if (stored) {
        internships = JSON.parse(stored);
        renderInternships();
    }
}

// Load Jobs
function loadJobs() {
    // Fetch from JSON or load from localStorage
    const stored = localStorage.getItem('jobs');
    if (stored) {
        jobs = JSON.parse(stored);
        renderJobs();
    }
}

// Render Internships
function renderInternships() {
    const container = document.getElementById('internships-container');
    const emptyState = document.getElementById('empty-internships');

    if (!internships || internships.length === 0) {
        container.innerHTML = '';
        if (emptyState) emptyState.style.display = 'block';
        return;
    }

    if (emptyState) emptyState.style.display = 'none';

    container.innerHTML = internships.map(internship => `
        <div class="opportunity-card">
            <div class="card-header">
                <div>
                    <div class="card-title">${internship.role || 'N/A'}</div>
                    <div class="card-company">${internship.company || 'N/A'}</div>
                </div>
            </div>
            <div class="card-details">
                <p><strong>Duration:</strong> ${internship.duration || 'N/A'}</p>
                <p><strong>Stipend:</strong> ${internship.stipend || 'N/A'}</p>
                <p><strong>Description:</strong> ${(internship.description || 'N/A').substring(0, 100)}...</p>
            </div>
            <div class="card-actions">
                <button class="btn btn-primary btn-small" onclick="editInternship('${internship.id}')">Edit</button>
                <button class="btn btn-danger btn-small" onclick="deleteInternship('${internship.id}')">Delete</button>
            </div>
        </div>
    `).join('');
}

// Render Jobs
function renderJobs() {
    const container = document.getElementById('jobs-container');
    const emptyState = document.getElementById('empty-jobs');

    if (!jobs || jobs.length === 0) {
        if (container) container.innerHTML = '';
        if (emptyState) emptyState.style.display = 'block';
        return;
    }

    if (emptyState) emptyState.style.display = 'none';

    if (container) {
        container.innerHTML = jobs.map(job => `
            <div class="opportunity-card">
                <div class="card-header">
                    <div>
                        <div class="card-title">${job.title || 'N/A'}</div>
                        <div class="card-company">${job.company || 'N/A'}</div>
                    </div>
                </div>
                <div class="card-details">
                    <p><strong>Experience:</strong> ${job.experience || 'N/A'}</p>
                    <p><strong>Salary:</strong> ${job.salary || 'N/A'}</p>
                    <p><strong>Description:</strong> ${(job.description || 'N/A').substring(0, 100)}...</p>
                </div>
                <div class="card-actions">
                    <button class="btn btn-primary btn-small" onclick="editJob('${job.id}')">Edit</button>
                    <button class="btn btn-danger btn-small" onclick="deleteJob('${job.id}')">Delete</button>
                </div>
            </div>
        `).join('');
    }
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

// Add Internship
function addInternship() {
    const form = document.getElementById('internship-form');
    const formData = new FormData(form);

    const newInternship = {
        id: 'int-' + Date.now(),
        role: formData.get('role'),
        company: formData.get('company'),
        duration: formData.get('duration'),
        stipend: formData.get('stipend'),
        description: formData.get('description')
    };

    internships.push(newInternship);
    localStorage.setItem('internships', JSON.stringify(internships));
    renderInternships();
    form.reset();
    alert('Internship added successfully!');
}

// Add Job
function addJob() {
    const form = document.getElementById('job-form');
    const formData = new FormData(form);

    const newJob = {
        id: 'job-' + Date.now(),
        title: formData.get('title'),
        company: formData.get('company'),
        experience: formData.get('experience'),
        salary: formData.get('salary'),
        description: formData.get('description')
    };

    jobs.push(newJob);
    localStorage.setItem('jobs', JSON.stringify(jobs));
    renderJobs();
    form.reset();
    alert('Job added successfully!');
}

// Edit Internship
function editInternship(id) {
    const internship = internships.find(i => i.id === id);
    if (!internship) return;

    currentEditingId = id;
    const modal = document.getElementById('edit-modal');
    if (modal) {
        document.querySelector('#edit-modal input[name="role"]').value = internship.role;
        document.querySelector('#edit-modal input[name="company"]').value = internship.company;
        document.querySelector('#edit-modal input[name="duration"]').value = internship.duration;
        document.querySelector('#edit-modal input[name="stipend"]').value = internship.stipend;
        modal.classList.add('active');
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

// Save Internship Changes
function saveInternshipChanges() {
    if (!currentEditingId) return;

    const form = document.querySelector('#edit-modal form');
    const formData = new FormData(form);

    const index = internships.findIndex(i => i.id === currentEditingId);
    if (index !== -1) {
        internships[index] = {
            ...internships[index],
            role: formData.get('role'),
            company: formData.get('company'),
            duration: formData.get('duration'),
            stipend: formData.get('stipend')
        };

        localStorage.setItem('internships', JSON.stringify(internships));
        renderInternships();
        closeModal('edit-modal');
        alert('Internship updated successfully!');
    }
}

// Save Job Changes
function saveJobChanges() {
    if (!currentEditingId) return;

    const form = document.querySelector('#edit-job-modal form');
    const formData = new FormData(form);

    const index = jobs.findIndex(j => j.id === currentEditingId);
    if (index !== -1) {
        jobs[index] = {
            ...jobs[index],
            title: formData.get('title'),
            company: formData.get('company'),
            experience: formData.get('experience'),
            salary: formData.get('salary')
        };

        localStorage.setItem('jobs', JSON.stringify(jobs));
        renderJobs();
        closeModal('edit-job-modal');
        alert('Job updated successfully!');
    }
}

// Delete Internship
function deleteInternship(id) {
    if (confirm('Are you sure you want to delete this internship?')) {
        internships = internships.filter(i => i.id !== id);
        localStorage.setItem('internships', JSON.stringify(internships));
        renderInternships();
        alert('Internship deleted successfully!');
    }
}

// Delete Job
function deleteJob(id) {
    if (confirm('Are you sure you want to delete this job?')) {
        jobs = jobs.filter(j => j.id !== id);
        localStorage.setItem('jobs', JSON.stringify(jobs));
        renderJobs();
        alert('Job deleted successfully!');
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

// Close modal when clicking outside of it
window.addEventListener('click', function(event) {
    const editModal = document.getElementById('edit-modal');
    const editJobModal = document.getElementById('edit-job-modal');

    if (event.target === editModal) {
        closeModal('edit-modal');
    }
    if (event.target === editJobModal) {
        closeModal('edit-job-modal');
    }
});
