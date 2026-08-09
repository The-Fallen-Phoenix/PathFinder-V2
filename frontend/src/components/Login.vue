<template>
  <div class="login-container">
    <!-- Login View -->
    <div v-if="currentView === 'login'" class="card">
      <h2>Welcome Back</h2>
      <form @submit.prevent="handleLogin">
        <div class="form-group">
          <label>Username</label>
          <input type="text" class="form-control" v-model="loginForm.username" required />
        </div>
        <div class="form-group">
          <label>Password</label>
          <input type="password" class="form-control" v-model="loginForm.password" required />
        </div>
        <button type="submit" class="btn btn-primary">LOGIN</button>
      </form>
    </div>

    <!-- Register View -->
    <div v-else-if="currentView === 'register'" class="card">
      <h2>Create an Account</h2>
      <div class="btn-group">
        <button class="btn" :class="regRole === 'student' ? 'btn-primary' : 'btn-outline'" @click="regRole = 'student'">Student</button>
        <button class="btn" :class="regRole === 'company' ? 'btn-primary' : 'btn-outline'" @click="regRole = 'company'">Company</button>
      </div>

      <!-- Student Register -->
      <form v-if="regRole === 'student'" @submit.prevent="handleRegisterStudent">
        <input type="text" class="form-control" v-model="regForm.username" placeholder="Username" required />
        <input type="password" class="form-control" v-model="regForm.password" placeholder="Password" required />
        <input type="text" class="form-control" v-model="regForm.full_name" placeholder="Full Name" required />
        <input type="text" class="form-control" v-model="regForm.roll_no" placeholder="Roll No" required />
        <input type="text" class="form-control" v-model="regForm.branch" placeholder="Branch" required />
        <input type="number" step="0.01" class="form-control" v-model="regForm.cgpa" placeholder="CGPA" required />
        <input type="number" class="form-control" v-model="regForm.graduation_year" placeholder="Graduation Year" required />
        <button type="submit" class="btn btn-primary">REGISTER AS STUDENT</button>
      </form>

      <!-- Company Register -->
      <form v-if="regRole === 'company'" @submit.prevent="handleRegisterCompany">
        <input type="text" class="form-control" v-model="regForm.username" placeholder="Username" required />
        <input type="password" class="form-control" v-model="regForm.password" placeholder="Password" required />
        <input type="text" class="form-control" v-model="regForm.company_name" placeholder="Company Name" required />
        <input type="email" class="form-control" v-model="regForm.hr_contact" placeholder="HR Contact Email" required />
        <input type="url" class="form-control" v-model="regForm.website" placeholder="Website (Optional)" />
        <button type="submit" class="btn btn-primary">REGISTER AS COMPANY</button>
      </form>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Login',
  data() {
    return {
      currentView: 'login',
      regRole: 'student',
      loginForm: { username: '', password: '' },
      regForm: {}
    }
  },
  methods: {
    handleLogin() {
      this.$emit('login', this.loginForm);
    },
    handleRegisterStudent() {
      this.$emit('register-student', this.regForm);
    },
    handleRegisterCompany() {
      this.$emit('register-company', this.regForm);
    }
  }
}
</script>

<style scoped>
.login-container {
  max-width: 500px;
  margin: 40px auto;
}
.form-group {
  margin-bottom: 15px;
}
.btn-group {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}
</style>
