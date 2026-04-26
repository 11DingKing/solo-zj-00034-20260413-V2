<template>
  <v-app-bar :elevation="2" location="top">
    <v-app-bar-title> Application Bar </v-app-bar-title>

    <template v-slot:append>
      <v-btn v-if="isAuthenticated" icon="mdi-view-dashboard" to="/"></v-btn>
      <v-btn v-if="isAuthenticated" icon="mdi-approximately-equal-box" to="/double-random"></v-btn>
      <v-btn v-if="isAuthenticated" icon="mdi-logout" @click="handleLogout" text>
        Logout
      </v-btn>
      <template v-else>
        <v-btn to="/login" text>Login</v-btn>
        <v-btn to="/register" variant="outlined">Register</v-btn>
      </template>
    </template>
  </v-app-bar>
</template>

<script lang="ts" setup>
import { computed } from "vue";
import { useRouter } from "vue-router";
import { useAppStore } from "@/store/app";

const router = useRouter();
const appStore = useAppStore();

const isAuthenticated = computed(() => appStore.isAuthenticated);

const handleLogout = () => {
  appStore.clearAuth();
  window.location.replace("/login");
};
</script>
