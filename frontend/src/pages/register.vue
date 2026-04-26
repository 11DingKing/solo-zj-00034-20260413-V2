<template>
  <div id="auth-container">
    <h2 class="title">Register</h2>

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

    <form @submit.prevent="handleRegister">
      <v-text-field
        v-model="username"
        label="Username"
        required
        :disabled="loading"
        class="input-field"
        variant="outlined"
        :rules="[usernameRule]"
      />

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
        @input="updatePasswordStrength"
      />

      <div v-if="password" class="password-strength">
        <div class="strength-label" :style="{ color: passwordStrength.color }">
          Password strength: {{ passwordStrength.label }}
        </div>
        <div class="strength-bar">
          <div
            class="strength-fill"
            :style="{
              width: strengthPercentage,
              backgroundColor: passwordStrength.color,
            }"
          ></div>
        </div>
        <div class="password-requirements">
          <div :class="{ valid: password.length >= 8 }">
            <v-icon>{{
              password.length >= 8 ? "mdi-check" : "mdi-close"
            }}</v-icon>
            At least 8 characters
          </div>
          <div :class="{ valid: hasNumber }">
            <v-icon>{{ hasNumber ? "mdi-check" : "mdi-close" }}</v-icon>
            Contains at least one digit
          </div>
          <div :class="{ valid: hasLetter }">
            <v-icon>{{ hasLetter ? "mdi-check" : "mdi-close" }}</v-icon>
            Contains at least one letter
          </div>
          <div :class="{ valid: hasSpecialChar }">
            <v-icon>{{ hasSpecialChar ? "mdi-check" : "mdi-close" }}</v-icon>
            Contains at least one special character
          </div>
        </div>
      </div>

      <v-text-field
        v-model="confirmPassword"
        label="Confirm Password"
        :type="showConfirmPassword ? 'text' : 'password'"
        required
        :disabled="loading"
        class="input-field"
        variant="outlined"
        :append-inner-icon="showConfirmPassword ? 'mdi-eye' : 'mdi-eye-off'"
        @click:append-inner="showConfirmPassword = !showConfirmPassword"
      />

      <button type="submit" class="button" :disabled="loading || !isFormValid">
        <span v-if="loading">Registering...</span>
        <span v-else>Register</span>
      </button>
    </form>

    <div class="login-link">
      Already have an account? <router-link to="/login">Login</router-link>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref, computed } from "vue";
import { useRouter } from "vue-router";
import {
  validatePasswordStrength,
  getPasswordStrength,
} from "@/utils/passwordValidator";

const router = useRouter();

const username = ref("");
const email = ref("");
const password = ref("");
const confirmPassword = ref("");
const showPassword = ref(false);
const showConfirmPassword = ref(false);
const loading = ref(false);
const errorMessage = ref("");
const passwordStrength = ref({ level: 0, label: "", color: "#999" });

const usernameRule = (v: string) => {
  if (!v) return true;
  const regex = /^[a-zA-Z0-9_]{3,20}$/;
  return (
    regex.test(v) ||
    "Username must be 3-20 characters, letters, numbers and underscore only"
  );
};

const hasNumber = computed(() => /\d/.test(password.value));
const hasLetter = computed(() => /[a-zA-Z]/.test(password.value));
const hasSpecialChar = computed(() => /[^a-zA-Z0-9]/.test(password.value));

const strengthPercentage = computed(() => {
  const level = passwordStrength.value.level;
  if (level === 1) return "33%";
  if (level === 2) return "66%";
  if (level === 3) return "100%";
  return "0%";
});

const isFormValid = computed(() => {
  if (
    !username.value ||
    !email.value ||
    !password.value ||
    !confirmPassword.value
  )
    return false;
  if (!/^[a-zA-Z0-9_]{3,20}$/.test(username.value)) return false;
  if (password.value !== confirmPassword.value) return false;
  const validation = validatePasswordStrength(password.value);
  return validation.valid;
});

const updatePasswordStrength = () => {
  if (password.value) {
    passwordStrength.value = getPasswordStrength(password.value);
  } else {
    passwordStrength.value = { level: 0, label: "", color: "#999" };
  }
};

const handleRegister = async () => {
  if (!username.value || !/^[a-zA-Z0-9_]{3,20}$/.test(username.value)) {
    errorMessage.value =
      "Username must be 3-20 characters, letters, numbers and underscore only";
    return;
  }

  const validation = validatePasswordStrength(password.value);
  if (!validation.valid) {
    errorMessage.value = validation.message;
    return;
  }

  if (password.value !== confirmPassword.value) {
    errorMessage.value = "Passwords do not match";
    return;
  }

  loading.value = true;
  errorMessage.value = "";

  try {
    const response = await fetch(
      import.meta.env.VITE_APP_BACKEND_ROOT_ENDPOINT + "v1/auth/register",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          username: username.value,
          email: email.value,
          password: password.value,
          confirm_password: confirmPassword.value,
        }),
      },
    );

    const data = await response.json();

    if (response.ok) {
      router.push({ path: "/login", query: { registered: "true" } });
    } else {
      errorMessage.value = data.detail || "Registration failed";
    }
  } catch (error) {
    errorMessage.value = "Network error. Please try again.";
    console.error("Registration error:", error);
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
