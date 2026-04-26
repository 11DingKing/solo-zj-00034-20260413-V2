/**
 * router/index.ts
 *
 * Automatic routes for `./src/pages/*.vue`
 */

import { createRouter, createWebHistory } from "vue-router/auto";
import { setupLayouts } from "virtual:generated-layouts";
import { useAppStore } from "@/store/app";

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  extendRoutes: setupLayouts,
});

const publicRoutes = [
  "/login",
  "/register",
  "/forgot-password",
  "/reset-password",
];

router.beforeEach((to, _from, next) => {
  const appStore = useAppStore();

  const isPublicRoute = publicRoutes.some((route) => to.path.startsWith(route));
  const isAuthenticated = appStore.isAuthenticated;

  if (!isPublicRoute && !isAuthenticated) {
    next({ path: "/login", replace: true });
  } else if (
    isPublicRoute &&
    isAuthenticated &&
    to.path !== "/reset-password"
  ) {
    next({ path: "/", replace: true });
  } else {
    next();
  }
});

router.afterEach((to) => {
  if (to.meta) {
    to.meta.requiresAuth = !publicRoutes.some((route) =>
      to.path.startsWith(route),
    );
  }

  if (typeof window !== "undefined" && window.document) {
    let meta = window.document.querySelector('meta[name="cache-control"]');
    if (!meta) {
      meta = window.document.createElement("meta");
      meta.setAttribute("name", "cache-control");
      window.document.head.appendChild(meta);
    }
    meta.setAttribute("content", "no-cache, no-store, must-revalidate, max-age=0");

    let pragma = window.document.querySelector('meta[name="pragma"]');
    if (!pragma) {
      pragma = window.document.createElement("meta");
      pragma.setAttribute("name", "pragma");
      window.document.head.appendChild(pragma);
    }
    pragma.setAttribute("content", "no-cache");

    let expires = window.document.querySelector('meta[name="expires"]');
    if (!expires) {
      expires = window.document.createElement("meta");
      expires.setAttribute("name", "expires");
      window.document.head.appendChild(expires);
    }
    expires.setAttribute("content", "0");
  }
});

export default router;
