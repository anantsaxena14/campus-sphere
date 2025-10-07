const sidebarToggle = document.getElementById('sidebar-toggle');
const sidebar = document.getElementById('sidebar');
const profileDropdownBtn = document.getElementById('profile-dropdown-btn');
const profileDropdown = document.getElementById('profile-dropdown');

if (sidebarToggle) {
    sidebarToggle.addEventListener('click', () => {
        sidebar.classList.toggle('collapsed');
    });
}

if (profileDropdownBtn) {
    profileDropdownBtn.addEventListener('click', () => {
        profileDropdown.classList.toggle('hidden');
    });
    
    document.addEventListener('click', (e) => {
        if (!profileDropdownBtn.contains(e.target) && !profileDropdown.contains(e.target)) {
            profileDropdown.classList.add('hidden');
        }
    });
}
