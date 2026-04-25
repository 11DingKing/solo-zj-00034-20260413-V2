<template>
  <div id="auth-container">
    <h2 class="title">Forgot Password</h2>
    
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
    >
      {{ successMessage }}
    </v-alert>
    
    <form v-if="!emailSent" @submit.prevent="handleRequestReset">
      <p class="description">
        Enter your email address and we'll send you a link to reset your password.
      </p>
      
      <v-text-field
        v-model="email"
        label="Email"
        type="email"
        required
        :disabled="loading"
        class="input-field"
        variant="outlined"
      />
      
      <button
        type="submit"
        class="button"
        :disabled="loading || !email"
      >
        <span v-if="loading">Sending...</span>
        <span v-else>Send Reset Link</span>
      </button>
    </form>
    
    <div v-else class="success-container">
      <v-icon size="64" color="#4caf50">mdi-email-check</v-icon>
      <p class="success-text">
        If an account exists for <strong>{{ email }}</strong>, you will receive a password reset email shortly.
      </p>
      <p class="note">
        The link will expire in 15 minutes and can only be used once.
      </p>
    </div>
    
    <div class="login-link">
      Remember your password? <router-link to="/login">Login</router-link>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref } from "vue";

const email = ref("");
const loading = ref(false);
const errorMessage = ref("");
const successMessage = ref("");
const emailSent = ref(false);

const handleRequestReset = async () => {
  if (!email.value) {
    errorMessage.value = "Please enter your email address";
    return;
  }

  loading.value = true;
  errorMessage.value = "";

  try {
    const response = await fetch(
      import.meta.env.VITE_APP_BACKEND_ROOT_ENDPOINT + "v1/auth/password-reset/request",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email: email.value,
        }),
      }
    );

    const data = await response.json();

    if (response.ok) {
      emailSent.value = true;
      successMessage.value = data.message;
    } else {
      errorMessage.value = data.detail || "Failed to send reset link";
    }
  } catch (error) {
    errorMessage.value = "Network error. Please try again.";
    console.error("Password reset request error:", error);
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

.description {
  color: #666;
  font-size: 14px;
  margin-bottom: 15px;
  text-align: left;
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

.success-container {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 15px;
}

.success-text {
  color: #333;
  font-size: 15px;
  line-height: 1.6;
}

.note {
  color: #666;
  font-size: 13px;
  font-style: italic;
}

.login-link {
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
