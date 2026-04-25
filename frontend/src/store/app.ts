import { defineStore } from "pinia";
import { ref, computed, watch } from "vue";

const STORAGE_KEY = "auth_token";
const STORAGE_USER_KEY = "auth_user";

export const useAppStore = defineStore("app", () => {
  const token = ref<string | null>(localStorage.getItem(STORAGE_KEY));
  const user = ref<{ id: number; email: string; is_active: boolean } | null>(
    null,
  );

  const isAuthenticated = computed(() => !!token.value);

  watch(token, (newToken) => {
    if (newToken) {
      localStorage.setItem(STORAGE_KEY, newToken);
    } else {
      localStorage.removeItem(STORAGE_KEY);
    }
  });

  watch(user, (newUser) => {
    if (newUser) {
      localStorage.setItem(STORAGE_USER_KEY, JSON.stringify(newUser));
    } else {
      localStorage.removeItem(STORAGE_USER_KEY);
    }
  });

  function initializeAuth() {
    const savedToken = localStorage.getItem(STORAGE_KEY);
    const savedUser = localStorage.getItem(STORAGE_USER_KEY);

    if (savedToken) {
      token.value = savedToken;
    }

    if (savedUser) {
      try {
        user.value = JSON.parse(savedUser);
      } catch {
        user.value = null;
      }
    }
  }

  function setAuth(
    newToken: string,
    newUser: { id: number; email: string; is_active: boolean },
  ) {
    token.value = newToken;
    user.value = newUser;
  }

  function clearAuth() {
    token.value = null;
    user.value = null;
    localStorage.removeItem(STORAGE_KEY);
    localStorage.removeItem(STORAGE_USER_KEY);
  }

  function generateToken(userId: number, email: string): string {
    const timestamp = Date.now();
    const payload = btoa(JSON.stringify({ userId, email, timestamp }));
    return `token_${payload}`;
  }

  return {
    token,
    user,
    isAuthenticated,
    initializeAuth,
    setAuth,
    clearAuth,
    generateToken,
  };
});
