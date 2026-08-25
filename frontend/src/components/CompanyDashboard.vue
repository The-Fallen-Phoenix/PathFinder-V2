<template>
  <div class="company-dashboard">
    <h2>Company Dashboard</h2>
    
    <!-- Post Drive -->
    <div class="card">
      <h3>Post a New Job Drive</h3>
      <form @submit.prevent="handleCreateDrive">
        <input type="text" class="form-control" v-model="driveForm.job_title" placeholder="Job Title" required />
        <input type="date" class="form-control" v-model="driveForm.deadline" required />
        <textarea class="form-control" v-model="driveForm.job_description" placeholder="Job Description" required></textarea>
        <input type="number" step="0.1" class="form-control" v-model="driveForm.min_cgpa" placeholder="Min CGPA" />
        <input type="text" class="form-control" v-model="driveForm.eligible_branches" placeholder="Eligible Branches" />
        <button type="submit" class="btn btn-primary">CREATE DRIVE</button>
      </form>
    </div>

    <!-- Drives List -->
    <div class="card">
      <h3>Your Active Drives</h3>
      <table>
        <thead>
          <tr>
            <th>Job Title</th>
            <th>Deadline</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="drive in drives" :key="drive.id">
            <td>{{ drive.job_title }}</td>
            <td>{{ drive.deadline }}</td>
            <td><span class="badge">{{ drive.status }}</span></td>
            <td><button class="btn btn-outline" @click="$emit('view-applicants', drive.id)">View Applicants</button></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CompanyDashboard',
  props: {
    drives: Array
  },
  data() {
    return {
      driveForm: { job_title: '', job_description: '', min_cgpa: '', eligible_branches: '', deadline: '' }
    }
  },
  methods: {
    handleCreateDrive() {
      this.$emit('create-drive', this.driveForm);
      this.driveForm = { job_title: '', job_description: '', min_cgpa: '', eligible_branches: '', deadline: '' };
    }
  }
}
</script>
