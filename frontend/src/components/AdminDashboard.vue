<template>
  <div class="admin-dashboard">
    <div class="header-row">
      <h2>Admin Dashboard</h2>
      <button @click="refreshData" class="btn btn-outline">Refresh Data</button>
    </div>

    <!-- Stats Row -->
    <div class="row">
      <div class="col"><div class="card stat-card"><h3>{{ stats.total_students }}</h3><p>Students</p></div></div>
      <div class="col"><div class="card stat-card"><h3>{{ stats.total_companies }}</h3><p>Companies</p></div></div>
      <div class="col"><div class="card stat-card"><h3>{{ stats.total_jobs }}</h3><p>Jobs Posted</p></div></div>
      <div class="col"><div class="card stat-card"><h3>{{ stats.total_applications }}</h3><p>Applications</p></div></div>
    </div>

    <!-- Reports Section -->
    <div class="row">
      <div class="col chart-col">
        <div class="card">
          <h3>Placement Stats Visualizer</h3>
          <canvas id="adminChart"></canvas>
        </div>
      </div>
      <div class="col report-col">
        <div class="card">
          <h3>Monthly Activity Report</h3>
          <p>Download a summary of student registrations, company partnerships, and drive success rates.</p>
          <button class="btn btn-primary" @click="$emit('download-report', 'html')">View HTML Report</button>
          <button class="btn btn-success" @click="$emit('download-report', 'pdf')">Download PDF Report</button>
        </div>
      </div>
    </div>

    <!-- Companies Management -->
    <div class="card">
      <h3>Companies Management</h3>
      <table>
        <thead>
          <tr>
            <th>Company Name</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="comp in companies" :key="comp.id">
            <td>{{ comp.company_name }}<br><small>{{ comp.hr_contact }}</small></td>
            <td><span class="badge">{{ comp.status }}</span></td>
            <td>
              <button v-if="comp.status !== 'approved'" class="btn btn-success" @click="updateCompany(comp.id, 'approved')">Approve</button>
              <button v-if="comp.status !== 'blacklisted'" class="btn btn-danger" @click="updateCompany(comp.id, 'blacklisted')">Blacklist</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Drives Management -->
    <div class="card">
      <h3>Placement Drives</h3>
      <table>
        <thead>
          <tr>
            <th>Company & Role</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="drive in drives" :key="drive.id">
            <td><strong>{{ drive.company_name }}</strong><br><small>{{ drive.job_title }}</small></td>
            <td><span class="badge">{{ drive.status }}</span></td>
            <td>
              <button v-if="drive.status === 'pending'" class="btn btn-success" @click="updateDrive(drive.id, 'approved')">Approve</button>
              <button v-if="drive.status === 'pending'" class="btn btn-danger" @click="updateDrive(drive.id, 'rejected')">Reject</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AdminDashboard',
  props: {
    stats: Object,
    companies: Array,
    drives: Array,
    students: Array
  },
  methods: {
    refreshData() {
      this.$emit('refresh');
    },
    updateCompany(id, status) {
      this.$emit('update-company', { id, status });
    },
    updateDrive(id, status) {
      this.$emit('update-drive', { id, status });
    }
  }
}
</script>
