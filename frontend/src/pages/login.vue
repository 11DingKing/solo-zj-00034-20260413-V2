<template>
  <div id="auth-container">
    <h2 class="title">Login</h2>
    
    <v-alert
      v-if="errorMessage"
      type="error"
      dense
      class="alert"
      dismissible
      @update:model-value="errorMessage = ''"
    >
      {{ errorMessage }}
    </v-alert>
    
    <v-alert
      v-if="successMessage"
      type="success"
      dense
      class="alert"
      dismissible
      @update:model-value="successMessage = ''"
    >
      {{ successMessage }}
    </v-alert>
    
    <form @submit.prevent="handleLogin">
      <v-text-field
        v-model="email"
        label="Email"
        type="email"
        required
        :disabled="loading"
        class="input-field"
        variant="outlined"
      />
      
      <v-text-field
        v-model="password"
        label="Password"
        :type="showPassword ? 'text' : 'password'"
        required
        :disabled="loading"
        class="input-field"
        variant="outlined"
        :append-inner-icon="showPassword ? 'mdi-eye' : 'mdi-eye-off'"
        @click:append-inner="showPassword = !showPassword"
      />
      
      <div class="forgot-password-link">
        <router-link to="/forgot-password">Forgot your password?</router-link>
      </div>
      
      <button
        type="submit"
        class="button"
        :disabled="loading"
      >
        <span v-if="loading">Logging in...</span>
        <span v-else>Login</span>
      </button>
    </form>
    
    <div class="register-link">
      Don't have an account? <router-link to="/register">Register</router-link>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted } from "vue";
import { useRoute } from "vue-router";

const route = useRoute();

const email = ref("");
const password = ref("");
const showPassword = ref(false);
const loading = ref(false);
const errorMessage = ref("");
const successMessage = ref("");

onMounted(() => {
  if (route.query.reset === "success") {
    successMessage.value = "Password reset successful! Please login with your new password.";
  }
  if (route.query.registered === "true") {
    successMessage.value = "Registration successful! Please login.";
  }
});

const handleLogin = async () => {
  if (!email.value || !password.value) {
    errorMessage.value = "Please fill in all fields";
    return;
  }

  loading.value = true;
  errorMessage.value = "";

  try {
    const response = await fetch(
      import.meta.env.VITE_APP_BACKEND_ROOT_ENDPOINT + "v1/auth/login",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email: email.value,
          password: password.value,
        }),
      }
    );

    const data = await response.json();

    if (response.ok) {
      successMessage.value = "Login successful!";
      console.log("User logged in:", data.user);
    } else {
      errorMessage.value = data.detail || "Login failed";
    }
  } catch (error) {
    errorMessage.value = "Network error. Please try again.";
    console.error("Login error:", error);
  } finally {
    loading.value = false;
  }
};
</script>

<style lang="scss" scoped>
#auth-container {
  display: flex;
  flex-direction: column;
  border: 1px solid black;
  border-radius: 20px;
  margin: auto;
  margin-top: 10%;
  padding: 30px;
  width: fit-content;
  min-width: 400px;
  text-align: center;
  align-items: center;
  justify-content: space-around;
}

.title {
  margin: 0 0 20px 0;
  color: #333;
}

.alert {
  width: 100%;
  margin-bottom: 15px;
}

form {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.input-field {
  width: 100%;
}

.forgot-password-link {
  text-align: right;
  font-size: 14px;
  
  a {
    color: #4caf50;
    text-decoration: none;
    
    &:hover {
      text-decoration: underline;
    }
  }
}

.button {
  padding: 12px 24px;
  text-align: center;
  text-decoration: none;
  display: inline-block;
  font-size: 16px;
  border-radius: 10px;
  cursor: pointer;
  border: 3px double #4caf50;
  transition-duration: 0.4s;
  background-color: #c1eec2;
  color: black;
  margin-top: 10px;

  &:hover {
    color: white;
    background-color: #4caf50;
  }

  &:active {
    transform: scale(0.95);
  }

  &:disabled {
    cursor: not-allowed;
    background-color: #ccc;
    border-color: #aaa;
    color: #888;
  }
}

.register-link {
  margin-top: 20px;
  font-size: 14px;
  color: #666;
  
  a {
    color: #4caf50;
    text-decoration: none;
    font-weight: bold;
    
    &:hover {
      text-decoration: underline;
    }
  }
}
</style>
