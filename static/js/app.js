const { createApp, ref, onMounted } = Vue;

const app = createApp({
    setup() {
        const currentView = ref('login');
        const token = ref(localStorage.getItem('jwt_token') || '');
        const role = ref(localStorage.getItem('user_role') || '');
        const alertMessage = ref('');
        
        // Forms
        const loginForm = ref({ username: '', password: '' });
        const regRole = ref('student');
        const regForm = ref({});
        const driveForm = ref({ job_title: '', job_description: '', min_cgpa: '', eligible_branches: '', deadline: '' });

        // Data Models
        const adminStats = ref({});
        const adminData = ref({ companies: [], drives: [] });
        const companyData = ref({ drives: [], applications: [], selectedDriveId: null });
        const studentData = ref({ drives: [], applications: [] });

        const showAlert = (msg) => {
            alertMessage.value = msg;
            setTimeout(() => { alertMessage.value = ''; }, 3000);
        };

        const authHeaders = () => ({
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token.value}`
        });

        const routeBasedOnRole = () => {
            if (role.value === 'admin') {
                currentView.value = 'admin_dashboard';
                fetchAdminData();
            } else if (role.value === 'student') {
                currentView.value = 'student_dashboard';
                fetchStudentData();
            } else if (role.value === 'company') {
                currentView.value = 'company_dashboard';
                fetchCompanyData();
            }
        };

        // --- AUTH ---

        const login = async () => {
            try {
                const res = await fetch('/api/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(loginForm.value)
                });
                const data = await res.json();
                
                if (res.ok) {
                    token.value = data.access_token;
                    role.value = data.role;
                    localStorage.setItem('jwt_token', token.value);
                    localStorage.setItem('user_role', role.value);
                    showAlert('Login successful');
                    routeBasedOnRole();
                } else {
                    showAlert(data.message || 'Login failed');
                }
            } catch (err) {
                showAlert('An error occurred during login');
            }
        };

        const logout = () => {
            token.value = '';
            role.value = '';
            localStorage.removeItem('jwt_token');
            localStorage.removeItem('user_role');
            currentView.value = 'login';
        };

        const registerStudent = async () => {
            try {
                const res = await fetch('/api/register/student', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(regForm.value)
                });
                const data = await res.json();
                showAlert(data.message);
                if (res.ok) currentView.value = 'login';
            } catch (err) {
                showAlert('Registration failed');
            }
        };

        const registerCompany = async () => {
            try {
                const res = await fetch('/api/register/company', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(regForm.value)
                });
                const data = await res.json();
                showAlert(data.message);
                if (res.ok) currentView.value = 'login';
            } catch (err) {
                showAlert('Registration failed');
            }
        };

        // --- ADMIN ---

        const fetchAdminData = async () => {
            try {
                let res = await fetch('/api/admin/dashboard', { headers: authHeaders() });
                if (res.ok) adminStats.value = await res.json();
                
                res = await fetch('/api/admin/companies', { headers: authHeaders() });
                if (res.ok) adminData.value.companies = await res.json();
                
                res = await fetch('/api/admin/drives', { headers: authHeaders() });
                if (res.ok) adminData.value.drives = await res.json();
            } catch (err) {
                showAlert('Failed to fetch admin data');
            }
        };

        const updateCompanyStatus = async (companyId, status) => {
            try {
                const res = await fetch(`/api/admin/companies/${companyId}/status`, {
                    method: 'PUT',
                    headers: authHeaders(),
                    body: JSON.stringify({ status })
                });
                if (res.ok) {
                    showAlert(`Company ${status}`);
                    fetchAdminData();
                }
            } catch (err) {
                showAlert('Failed to update status');
            }
        };

        const updateDriveStatus = async (driveId, status) => {
            try {
                const res = await fetch(`/api/admin/drives/${driveId}/status`, {
                    method: 'PUT',
                    headers: authHeaders(),
                    body: JSON.stringify({ status })
                });
                if (res.ok) {
                    showAlert(`Drive ${status}`);
                    fetchAdminData();
                }
            } catch (err) {
                showAlert('Failed to update status');
            }
        };

        // --- COMPANY ---

        const fetchCompanyData = async () => {
            try {
                const res = await fetch('/api/company/drives', { headers: authHeaders() });
                if (res.ok) {
                    companyData.value.drives = await res.json();
                }
            } catch (err) {
                showAlert('Failed to fetch company drives');
            }
        };

        const createDrive = async () => {
            try {
                const res = await fetch('/api/company/drives', {
                    method: 'POST',
                    headers: authHeaders(),
                    body: JSON.stringify(driveForm.value)
                });
                if (res.ok) {
                    showAlert('Drive created, pending approval');
                    driveForm.value = { job_title: '', job_description: '', min_cgpa: '', eligible_branches: '', deadline: '' };
                    fetchCompanyData();
                }
            } catch (err) {
                showAlert('Failed to create drive');
            }
        };

        const viewApplicants = async (driveId) => {
            companyData.value.selectedDriveId = driveId;
            try {
                const res = await fetch(`/api/company/drives/${driveId}/applications`, { headers: authHeaders() });
                if (res.ok) {
                    companyData.value.applications = await res.json();
                }
            } catch (err) {
                showAlert('Failed to fetch applicants');
            }
        };

        const updateApplicationStatus = async (appId, status) => {
            if(!status) return;
            try {
                const res = await fetch(`/api/company/applications/${appId}/status`, {
                    method: 'PUT',
                    headers: authHeaders(),
                    body: JSON.stringify({ status })
                });
                if (res.ok) {
                    showAlert(`Application updated to ${status}`);
                    // Refresh current drive applicants
                    if (companyData.value.selectedDriveId) {
                        viewApplicants(companyData.value.selectedDriveId);
                    }
                }
            } catch (err) {
                showAlert('Failed to update application');
            }
        };

        // --- STUDENT ---

        const fetchStudentData = async () => {
            try {
                const res = await fetch('/api/drives', { headers: authHeaders() });
                if (res.ok) {
                    studentData.value.drives = await res.json();
                }
            } catch (err) {
                showAlert('Failed to fetch drives');
            }
        };

        const fetchStudentApplications = async () => {
            try {
                const res = await fetch('/api/student/applications', { headers: authHeaders() });
                if (res.ok) {
                    studentData.value.applications = await res.json();
                }
            } catch (err) {
                showAlert('Failed to fetch applications');
            }
        };

        const applyDrive = async (driveId) => {
            try {
                const res = await fetch(`/api/drives/${driveId}/apply`, {
                    method: 'POST',
                    headers: authHeaders()
                });
                const data = await res.json();
                showAlert(data.message);
            } catch (err) {
                showAlert('Failed to apply for drive');
            }
        };

        const exportCSV = async () => {
            try {
                const res = await fetch('/api/export/applications', {
                    method: 'POST',
                    headers: authHeaders()
                });
                if (res.ok) {
                    showAlert('Export task started successfully! You will receive a notification.');
                }
            } catch (err) {
                showAlert('Failed to start export task');
            }
        };

        onMounted(() => {
            if (token.value) {
                routeBasedOnRole();
            }
        });

        return {
            currentView, token, role, alertMessage, 
            loginForm, regRole, regForm, driveForm,
            adminStats, adminData, companyData, studentData,
            login, logout, registerStudent, registerCompany,
            fetchAdminData, updateCompanyStatus, updateDriveStatus,
            fetchCompanyData, createDrive, viewApplicants, updateApplicationStatus,
            fetchStudentData, fetchStudentApplications, applyDrive, exportCSV
        }
    }
});

app.mount('#app');
