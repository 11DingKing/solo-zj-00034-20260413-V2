import { defineStore } from "pinia";
import { ref, computed } from "vue";

const STORAGE_KEY = "auth_token";
const STORAGE_USER_KEY = "auth_user";

interface User {
  id: number;
  email: string;
  username: string;
  is_active: boolean;
}

let isInitialized = false;

export const useAppStore = defineStore("app", () => {
  const token = ref<string | null>(null);
  const user = ref<User | null>(null);

  const isAuthenticated = computed(() => !!token.value);

  function saveToStorage() {
    if (token.value) {
      localStorage.setItem(STORAGE_KEY, token.value);
    } else {
      localStorage.removeItem(STORAGE_KEY);
    }
    if (user.value) {
      localStorage.setItem(STORAGE_USER_KEY, JSON.stringify(user.value));
    } else {
      localStorage.removeItem(STORAGE_USER_KEY);
    }
  }

  function initializeAuth() {
    if (isInitialized) return;
    
    try {
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
    } catch (e) {
      console.error("Failed to initialize auth:", e);
    }
    
    isInitialized = true;
  }

  function setAuth(newToken: string, newUser: User) {
    token.value = newToken;
    user.value = newUser;
    saveToStorage();
  }

  function clearAuth() {
    token.value = null;
    user.value = null;
    localStorage.removeItem(STORAGE_KEY);
    localStorage.removeItem(STORAGE_USER_KEY);
    isInitialized = false;
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
