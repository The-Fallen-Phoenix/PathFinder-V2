<template>
  <div class="student-dashboard">
    <!-- View Navigation -->
    <div class="sub-nav">
      <button @click="currentTab = 'drives'">Drives</button>
      <button @click="currentTab = 'applications'">My Applications</button>
      <button @click="currentTab = 'profile'">Profile</button>
    </div>

    <!-- Available Drives Tab -->
    <div v-if="currentTab === 'drives'">
      <h2>Available Placement Drives</h2>
      <input type="text" v-model="searchQuery" placeholder="Search by company or job..." class="form-control" />
      
      <div class="row">
        <div class="col" v-for="drive in filteredDrives" :key="drive.id">
          <div class="card">
            <h3>{{ drive.company_name }}</h3>
            <h5>{{ drive.job_title }}</h5>
            <p>{{ drive.job_description }}</p>
            <p>Min CGPA: {{ drive.min_cgpa }} | Deadline: {{ drive.deadline }}</p>
            <button class="btn btn-primary" @click="apply(drive.id)">APPLY NOW</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Applications Tab -->
    <div v-else-if="currentTab === 'applications'">
      <div class="header-row">
        <h2>My Applications</h2>
        <div class="btn-group">
          <button class="btn btn-outline" @click="$emit('download-student-report', 'html')">View HTML Report</button>
          <button class="btn btn-outline" @click="$emit('download-student-report', 'pdf')">Download PDF Report</button>
          <button class="btn btn-success" @click="$emit('export-csv')">Export CSV</button>
        </div>
      </div>

      <table>
        <thead>
          <tr>
            <th>Company</th>
            <th>Job Title</th>
            <th>Applied On</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="app in applications" :key="app.id">
            <td>{{ app.company_name }}</td>
            <td>{{ app.job_title }}</td>
            <td>{{ app.applied_on }}</td>
            <td><span class="badge">{{ app.status }}</span></td>
            <td>
              <button v-if="app.status === 'SELECTED'" class="btn btn-success" @click="$emit('view-offer', app.id)">
                View Offer Letter
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Profile Tab -->
    <div v-else-if="currentTab === 'profile'">
      <h2>My Profile</h2>
      <form @submit.prevent="saveProfile" class="card">
        <label>Full Name</label>
        <input type="text" class="form-control" v-model="profile.full_name" required />
        
        <label>Branch</label>
        <input type="text" class="form-control" v-model="profile.branch" required />
        
        <label>CGPA</label>
        <input type="number" step="0.01" class="form-control" v-model="profile.cgpa" required />
        
        <label>Resume Link</label>
        <input type="url" class="form-control" v-model="profile.resume_link" />
        
        <button type="submit" class="btn btn-primary">SAVE PROFILE</button>
      </form>
    </div>
  </div>
</template>

<script>
export default {
  name: 'StudentDashboard',
  props: {
    drives: Array,
    applications: Array,
    profile: Object
  },
  data() {
    return {
      currentTab: 'drives',
      searchQuery: ''
    }
  },
  computed: {
    filteredDrives() {
      if (!this.searchQuery) return this.drives;
      return this.drives.filter(d => 
        d.company_name.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
        d.job_title.toLowerCase().includes(this.searchQuery.toLowerCase())
      );
    }
  },
  methods: {
    apply(driveId) {
      this.$emit('apply', driveId);
    },
    saveProfile() {
      this.$emit('save-profile', this.profile);
    }
  }
}
</script>
