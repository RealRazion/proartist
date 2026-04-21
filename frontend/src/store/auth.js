/**
 * Auth Store mit Pinia/Vue Pattern
 * Zentralisiert Authentifizierung und Profil-Management
 */

import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import api from '../api';

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null);
  const token = ref(localStorage.getItem('auth_token') || null);
  const isLoading = ref(false);
  const error = ref(null);

  const isAuthenticated = computed(() => !!token.value && !!user.value);
  
  const isTeam = computed(() => user.value?.team_profiles?.length > 0);
  
  const currentTeam = computed(() => {
    if (!isTeam.value) return null;
    return user.value.team_profiles[0];
  });

  // Fetch current user profile
  const fetchProfile = async () => {
    if (!token.value) return null;
    
    isLoading.value = true;
    error.value = null;
    
    try {
      const response = await api.get('profiles/me/');
      user.value = response.data;
      return response.data;
    } catch (err) {
      error.value = err.message;
      logout();
      throw err;
    } finally {
      isLoading.value = false;
    }
  };

  // Login
  const login = async (email, password) => {
    isLoading.value = true;
    error.value = null;
    
    try {
      const response = await api.post('auth/login/', { email, password });
      token.value = response.data.token;
      localStorage.setItem('auth_token', token.value);
      await fetchProfile();
      return response.data;
    } catch (err) {
      error.value = err.message;
      throw err;
    } finally {
      isLoading.value = false;
    }
  };

  // Logout
  const logout = () => {
    token.value = null;
    user.value = null;
    localStorage.removeItem('auth_token');
  };

  // Update profile
  const updateProfile = async (updates) => {
    isLoading.value = true;
    error.value = null;
    
    try {
      const response = await api.patch('profiles/me/', updates);
      user.value = response.data;
      return response.data;
    } catch (err) {
      error.value = err.message;
      throw err;
    } finally {
      isLoading.value = false;
    }
  };

  // Check token on store init
  const initialize = async () => {
    if (token.value) {
      try {
        await fetchProfile();
      } catch {
        logout();
      }
    }
  };

  return {
    // State
    user,
    token,
    isLoading,
    error,
    
    // Getters
    isAuthenticated,
    isTeam,
    currentTeam,
    
    // Actions
    fetchProfile,
    login,
    logout,
    updateProfile,
    initialize,
  };
});
