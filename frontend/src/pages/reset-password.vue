<template>
  <div id="auth-container">
    <h2 class="title">Reset Password</h2>
    
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
    
    <template v-if="!tokenValidated && !loadingToken">
      <v-progress-circular indeterminate color="#4caf50" />
      <p class="validating-text">Validating reset link...</p>
    </template>
    
    <template v-else-if="tokenValid && !passwordReset">
      <form @submit.prevent="handleResetPassword">
        <p class="description">
          Please enter your new password below.
        </p>
        
        <v-text-field
          v-model="newPassword"
          label="New Password"
          :type="showNewPassword ? 'text' : 'password'"
          required
          :disabled="loading"
          class="input-field"
          variant="outlined"
          :append-inner-icon="showNewPassword ? 'mdi-eye' : 'mdi-eye-off'"
          @click:append-inner="showNewPassword = !showNewPassword"
          @input="updatePasswordStrength"
        />
        
        <div v-if="newPassword" class="password-strength">
          <div class="strength-label" :style="{ color: passwordStrength.color }">
            Password strength: {{ passwordStrength.label }}
          </div>
          <div class="strength-bar">
            <div 
              class="strength-fill" 
              :style="{ 
                width: strengthPercentage, 
                backgroundColor: passwordStrength.color 
              }"
            ></div>
          </div>
          <div class="password-requirements">
            <div :class="{ valid: newPassword.length >= 8 }">
              <v-icon>{{ newPassword.length >= 8 ? 'mdi-check' : 'mdi-close' }}</v-icon>
              At least 8 characters
            </div>
            <div :class="{ valid: hasNumber }">
              <v-icon>{{ hasNumber ? 'mdi-check' : 'mdi-close' }}</v-icon>
              Contains at least one digit
            </div>
            <div :class="{ valid: hasLetter }">
              <v-icon>{{ hasLetter ? 'mdi-check' : 'mdi-close' }}</v-icon>
              Contains at least one letter
            </div>
          </div>
        </div>
        
        <v-text-field
          v-model="confirmPassword"
          label="Confirm New Password"
          :type="showConfirmPassword ? 'text' : 'password'"
          required
          :disabled="loading"
          class="input-field"
          variant="outlined"
          :append-inner-icon="showConfirmPassword ? 'mdi-eye' : 'mdi-eye-off'"
          @click:append-inner="showConfirmPassword = !showConfirmPassword"
        />
        
        <button
          type="submit"
          class="button"
          :disabled="loading || !isFormValid"
        >
          <span v-if="loading">Resetting Password...</span>
          <span v-else>Reset Password</span>
        </button>
      </form>
    </template>
    
    <template v-else-if="passwordReset">
      <div class="success-container">
        <v-icon size="64" color="#4caf50">mdi-check-circle</v-icon>
        <p class="success-text">
          Your password has been reset successfully!
        </p>
        <button class="button" @click="goToLogin">
          Go to Login
        </button>
      </div>
    </template>
    
    <template v-else-if="!tokenValid && !loadingToken">
      <div class="error-container">
        <v-icon size="64" color="#f44336">mdi-alert-circle</v-icon>
        <p class="error-text">
          {{ tokenErrorMessage || "Invalid or expired reset link" }}
        </p>
        <p class="note">
          The link may have expired or already been used. Please request a new password reset.
        </p>
        <button class="button" @click="goToForgotPassword">
          Request New Reset Link
        </button>
      </div>
    </template>
    
    <div v-if="!passwordReset && tokenValid" class="login-link">
      Remember your password? <router-link to="/login">Login</router-link>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref, computed, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { validatePasswordStrength, getPasswordStrength } from "@/utils/passwordValidator";

const route = useRoute();
const router = useRouter();

const token = ref("");
const newPassword = ref("");
const confirmPassword = ref("");
const showNewPassword = ref(false);
const showConfirmPassword = ref(false);
const loading = ref(false);
const loadingToken = ref(true);
const errorMessage = ref("");
const successMessage = ref("");
const tokenValid = ref(false);
const tokenValidated = ref(false);
const tokenErrorMessage = ref("");
const passwordReset = ref(false);
const passwordStrength = ref({ level: 0, label: "", color: "#999" });

const hasNumber = computed(() => /\d/.test(newPassword.value));
const hasLetter = computed(() => /[a-zA-Z]/.test(newPassword.value));

const strengthPercentage = computed(() => {
  const level = passwordStrength.value.level;
  if (level === 1) return "33%";
  if (level === 2) return "66%";
  if (level === 3) return "100%";
  return "0%";
});

const isFormValid = computed(() => {
  if (!newPassword.value || !confirmPassword.value) return false;
  if (newPassword.value !== confirmPassword.value) return false;
  const validation = validatePasswordStrength(newPassword.value);
  return validation.valid;
});

const updatePasswordStrength = () => {
  if (newPassword.value) {
    passwordStrength.value = getPasswordStrength(newPassword.value);
  } else {
    passwordStrength.value = { level: 0, label: "", color: "#999" };
  }
};

const validateToken = async () => {
  const tokenParam = route.query.token as string;
  if (!tokenParam) {
    tokenValid.value = false;
    tokenValidated.value = true;
    loadingToken.value = false;
    tokenErrorMessage.value = "No reset token provided";
    return;
  }

  token.value = tokenParam;

  try {
    const response = await fetch(
      `${import.meta.env.VITE_APP_BACKEND_ROOT_ENDPOINT}v1/auth/password-reset/validate?token=${encodeURIComponent(tokenParam)}`,
      {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
      }
    );

    const data = await response.json();

    if (response.ok && data.valid) {
      tokenValid.value = true;
    } else {
      tokenValid.value = false;
      tokenErrorMessage.value = data.message || "Invalid or expired reset link";
    }
  } catch (error) {
    tokenValid.value = false;
    tokenErrorMessage.value = "Network error. Please try again.";
    console.error("Token validation error:", error);
  } finally {
    tokenValidated.value = true;
    loadingToken.value = false;
  }
};

const handleResetPassword = async () => {
  const validation = validatePasswordStrength(newPassword.value);
  if (!validation.valid) {
    errorMessage.value = validation.message;
    return;
  }

  if (newPassword.value !== confirmPassword.value) {
    errorMessage.value = "Passwords do not match";
    return;
  }

  loading.value = true;
  errorMessage.value = "";

  try {
    const response = await fetch(
      import.meta.env.VITE_APP_BACKEND_ROOT_ENDPOINT + "v1/auth/password-reset/confirm",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          token: token.value,
          new_password: newPassword.value,
          confirm_password: confirmPassword.value,
        }),
      }
    );

    const data = await response.json();

    if (response.ok) {
      passwordReset.value = true;
      successMessage.value = data.message;
    } else {
      errorMessage.value = data.detail || "Failed to reset password";
    }
  } catch (error) {
    errorMessage.value = "Network error. Please try again.";
    console.error("Password reset error:", error);
  } finally {
    loading.value = false;
  }
};

const goToLogin = () => {
  router.push({ path: "/login", query: { reset: "success" } });
};

const goToForgotPassword = () => {
  router.push("/forgot-password");
};

onMounted(() => {
  validateToken();
});
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

.validating-text {
  color: #666;
  margin-top: 15px;
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

.password-strength {
  text-align: left;
  padding: 10px;
  background: #f9f9f9;
  border-radius: 8px;
}

.strength-label {
  font-size: 14px;
  font-weight: bold;
  margin-bottom: 8px;
}

.strength-bar {
  height: 6px;
  background: #e0e0e0;
  border-radius: 3px;
  overflow: hidden;
  margin-bottom: 10px;
}

.strength-fill {
  height: 100%;
  transition: width 0.3s ease;
}

.password-requirements {
  font-size: 12px;
  color: #666;
  
  div {
    display: flex;
    align-items: center;
    gap: 5px;
    margin: 3px 0;
    
    &.valid {
      color: #4caf50;
    }
    
    .v-icon {
      font-size: 14px;
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

.success-container,
.error-container {
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

.error-text {
  color: #f44336;
  font-size: 15px;
  line-height: 1.6;
  font-weight: bold;
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
