const { createApp, ref, computed, onMounted } = Vue;

const app = createApp({
    compilerOptions: {
        delimiters: ['[[', ']]']
    },
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
        
        // Search & Filters
        const adminCompanySearch = ref('');
        const adminStudentSearch = ref('');
        const studentDriveSearch = ref('');

        // Data Models
        const adminStats = ref({});
        const adminData = ref({ companies: [], drives: [], students: [] });
        const companyData = ref({ drives: [], applications: [], selectedDriveId: null });
        const studentData = ref({ profile: {}, drives: [], applications: [] });

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
                if (res.ok) {
                    adminStats.value = await res.json();
                    setTimeout(() => renderAdminChart(), 100);
                }
                
                res = await fetch('/api/admin/companies', { headers: authHeaders() });
                if (res.ok) adminData.value.companies = await res.json();
                
                res = await fetch('/api/admin/students', { headers: authHeaders() });
                if (res.ok) adminData.value.students = await res.json();
                
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

        const updateStudentStatus = async (studentId, status) => {
            try {
                const res = await fetch(`/api/admin/students/${studentId}/status`, {
                    method: 'PUT',
                    headers: authHeaders(),
                    body: JSON.stringify({ status })
                });
                if (res.ok) {
                    showAlert(`Student ${status}`);
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

        // Computed for Search
        const filteredCompanies = computed(() => {
            if (!adminCompanySearch.value) return adminData.value.companies;
            return adminData.value.companies.filter(c => c.company_name.toLowerCase().includes(adminCompanySearch.value.toLowerCase()));
        });
        
        const filteredStudents = computed(() => {
            if (!adminStudentSearch.value) return adminData.value.students;
            return adminData.value.students.filter(s => s.full_name.toLowerCase().includes(adminStudentSearch.value.toLowerCase()) || s.roll_no.includes(adminStudentSearch.value));
        });

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
                const data = await res.json();
                if (res.ok) {
                    showAlert(data.message || 'Drive created');
                    driveForm.value = { job_title: '', job_description: '', min_cgpa: '', eligible_branches: '', deadline: '' };
                    fetchCompanyData();
                } else {
                    showAlert(data.message || 'Error creating drive');
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

        const generateOfferLetter = async (appId) => {
            try {
                const res = await fetch(`/api/applications/${appId}/offer_letter`, { headers: authHeaders() });
                if (res.ok) {
                    const html = await res.text();
                    const newWindow = window.open();
                    newWindow.document.write(html);
                    newWindow.document.close();
                } else {
                    showAlert('Failed to generate offer letter');
                }
            } catch (err) {
                showAlert('Failed to generate offer letter');
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
        
        const fetchStudentProfile = async () => {
            try {
                const res = await fetch('/api/student/profile', { headers: authHeaders() });
                if (res.ok) {
                    studentData.value.profile = await res.json();
                }
            } catch (err) {
                showAlert('Failed to fetch profile');
            }
        };
        
        const updateStudentProfile = async () => {
            try {
                const res = await fetch('/api/student/profile', {
                    method: 'PUT',
                    headers: authHeaders(),
                    body: JSON.stringify(studentData.value.profile)
                });
                const data = await res.json();
                showAlert(data.message);
            } catch (err) {
                showAlert('Failed to update profile');
            }
        };

        const fetchStudentApplications = async () => {
            try {
                // Pre-fetch profile so student details are populated in HTML/PDF reports
                fetchStudentProfile();
                
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
                const data = await res.json();
                if (res.ok) {
                    showAlert('Export task started successfully! Please wait...');
                    
                    // Poll the status endpoint until success or failure
                    const interval = setInterval(async () => {
                        try {
                            const statusRes = await fetch(`/api/export/status/${data.task_id}`, {
                                headers: authHeaders()
                            });
                            if (statusRes.ok) {
                                const statusData = await statusRes.json();
                                if (statusData.status === 'SUCCESS') {
                                    clearInterval(interval);
                                    showAlert('Export complete! Downloading file...');
                                    
                                    // Create a temporary hidden link to trigger the download
                                    const link = document.createElement('a');
                                    link.href = statusData.download_url;
                                    link.setAttribute('download', `applications_export.csv`);
                                    document.body.appendChild(link);
                                    link.click();
                                    document.body.removeChild(link);
                                } else if (statusData.status === 'FAILURE') {
                                    clearInterval(interval);
                                    showAlert('Export failed: ' + (statusData.error || 'unknown error'));
                                }
                            }
                        } catch (err) {
                            clearInterval(interval);
                            showAlert('Error checking export status');
                        }
                    }, 1000);
                } else {
                    showAlert(data.message || 'Failed to start export');
                }
            } catch (err) {
                showAlert('Failed to start export task');
            }
        };
        
        // Computed for Search
        const filteredDrives = computed(() => {
            if (!studentDriveSearch.value) return studentData.value.drives;
            return studentData.value.drives.filter(d => 
                d.job_title.toLowerCase().includes(studentDriveSearch.value.toLowerCase()) || 
                d.company_name.toLowerCase().includes(studentDriveSearch.value.toLowerCase())
            );
        });

        // --- CHARTS & REPORTS GENERATION ---
        let adminChartInstance = null;
        
        const renderAdminChart = () => {
            const ctx = document.getElementById('adminChart');
            if (!ctx) return;
            
            if (adminChartInstance) {
                adminChartInstance.destroy();
            }
            
            adminChartInstance = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: ['Students', 'Companies', 'Jobs Posted', 'Applications'],
                    datasets: [{
                        label: 'Stats Count',
                        data: [
                            adminStats.value.total_students || 0,
                            adminStats.value.total_companies || 0,
                            adminStats.value.total_jobs || 0,
                            adminStats.value.total_applications || 0
                        ],
                        backgroundColor: 'rgba(13, 76, 148, 0.7)',
                        borderColor: '#0d4c94',
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: { stepSize: 1 }
                        }
                    }
                }
            });
        };

        const downloadAdminReport = async (format) => {
            try {
                const res = await fetch('/api/admin/monthly_report', { headers: authHeaders() });
                if (res.ok) {
                    const html = await res.text();
                    if (format === 'html') {
                        const win = window.open();
                        win.document.write(html);
                        win.document.close();
                    } else if (format === 'pdf') {
                        const element = document.createElement('div');
                        element.innerHTML = html;
                        html2pdf().from(element).set({
                            margin: 0.5,
                            filename: `monthly_placement_report_${Date.now()}.pdf`,
                            image: { type: 'jpeg', quality: 0.98 },
                            html2canvas: { scale: 2 },
                            jsPDF: { unit: 'in', format: 'letter', orientation: 'portrait' }
                        }).save();
                    }
                } else {
                    showAlert('Failed to generate report');
                }
            } catch (err) {
                showAlert('Failed to generate report');
            }
        };

        const downloadStudentReport = (format) => {
            const profile = studentData.value.profile || {};
            const apps = studentData.value.applications || [];
            
            let htmlContent = `
            <!DOCTYPE html>
            <html>
            <head>
                <title>Applications Report - ${profile.full_name || 'Student'}</title>
                <style>
                    body { font-family: Arial, sans-serif; padding: 20px; color: #000; background-color: #ffffff; }
                    .container { max-width: 600px; margin: 0 auto; background: white; padding: 20px; border: 2px solid #000; }
                    .header { border-bottom: 2px solid #000; padding-bottom: 10px; margin-bottom: 15px; }
                    h2 { color: #000; margin: 0 0 5px 0; text-transform: uppercase; }
                    table { width: 100%; border-collapse: collapse; margin-top: 15px; border: 1px solid #000; }
                    th, td { border: 1px solid #000; padding: 8px; text-align: left; }
                    th { background-color: #f2f2f2; font-weight: bold; color: #000; }
                    .badge { padding: 3px 6px; border: 1px solid #000; font-weight: bold; color: white; font-size: 11px; display: inline-block; text-transform: uppercase; }
                    .selected { background-color: #27ae60; }
                    .rejected { background-color: #c0392b; }
                    .shortlisted { background-color: #f1c40f; color: #000; }
                    .applied { background-color: #2980b9; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h2>Placement Applications Report</h2>
                        <p style="margin: 5px 0;"><strong>Student Name:</strong> ${profile.full_name || 'N/A'}</p>
                        <p style="margin: 5px 0;"><strong>Roll Number:</strong> ${profile.roll_no || 'N/A'} | <strong>Branch:</strong> ${profile.branch || 'N/A'}</p>
                        <p style="margin: 5px 0;"><strong>CGPA:</strong> ${profile.cgpa || 'N/A'}</p>
                    </div>
                    <table>
                        <thead>
                            <tr>
                                <th>Company</th>
                                <th>Job Title</th>
                                <th>Applied On</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody>
            `;
            
            if (apps.length === 0) {
                htmlContent += `<tr><td colspan="4" style="text-align:center; color:#999;">No applications submitted yet.</td></tr>`;
            } else {
                apps.forEach(a => {
                    const statusClass = a.status.toLowerCase();
                    htmlContent += `
                        <tr>
                            <td><strong>${a.company_name}</strong></td>
                            <td>${a.job_title}</td>
                            <td>${a.applied_on}</td>
                            <td><span class="badge ${statusClass}">${a.status}</span></td>
                        </tr>
                    `;
                });
            }
            
            htmlContent += `
                        </tbody>
                    </table>
                </div>
            </body>
            </html>
            `;
            
            if (format === 'html') {
                const win = window.open();
                win.document.write(htmlContent);
                win.document.close();
            } else if (format === 'pdf') {
                const element = document.createElement('div');
                element.innerHTML = htmlContent;
                html2pdf().from(element).set({
                    margin: 0.5,
                    filename: `applications_report_${profile.roll_no || 'export'}.pdf`,
                    image: { type: 'jpeg', quality: 0.98 },
                    html2canvas: { scale: 2 },
                    jsPDF: { unit: 'in', format: 'letter', orientation: 'portrait' }
                }).save();
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
            adminCompanySearch, adminStudentSearch, studentDriveSearch,
            adminStats, adminData, companyData, studentData,
            filteredCompanies, filteredStudents, filteredDrives,
            login, logout, registerStudent, registerCompany,
            fetchAdminData, updateCompanyStatus, updateStudentStatus, updateDriveStatus,
            fetchCompanyData, createDrive, viewApplicants, updateApplicationStatus, generateOfferLetter,
            fetchStudentData, fetchStudentProfile, updateStudentProfile, fetchStudentApplications, applyDrive, exportCSV,
            downloadAdminReport, downloadStudentReport, renderAdminChart
        }
    }
});

app.mount('#app');
