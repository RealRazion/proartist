import { ref, computed } from 'vue';
import api from '../api';
import { useToast } from './useToast';

export function useTaskFilters() {
  const { showToast } = useToast();
  
  const filters = ref({
    status: 'OPEN',
    priority: [],
    assignee: null,
    dueDateRange: null,
  });

  const filterLabels = {
    status: 'Status',
    priority: 'Priorität',
    assignee: 'Zugewiesen an',
    dueDateRange: 'Fälligkeitsdatum',
  };

  const activeFilterCount = computed(() => {
    return Object.entries(filters.value).filter(([_, v]) => {
      if (Array.isArray(v)) return v.length > 0;
      return v !== null && v !== undefined && v !== '';
    }).length;
  });

  const applyFilters = async (tasks) => {
    try {
      let filtered = [...tasks];

      if (filters.value.status) {
        filtered = filtered.filter(t => t.status === filters.value.status);
      }

      if (filters.value.priority?.length > 0) {
        filtered = filtered.filter(t => filters.value.priority.includes(t.priority));
      }

      if (filters.value.assignee) {
        filtered = filtered.filter(t => 
          t.assignees?.some(a => a.id === filters.value.assignee)
        );
      }

      return filtered;
    } catch (err) {
      showToast('Filter konnte nicht angewendet werden', 'error');
      return tasks;
    }
  };

  const resetFilters = () => {
    filters.value = {
      status: 'OPEN',
      priority: [],
      assignee: null,
      dueDateRange: null,
    };
  };

  return {
    filters,
    filterLabels,
    activeFilterCount,
    applyFilters,
    resetFilters,
  };
}

export function useTaskBoard() {
  const { showToast } = useToast();
  
  const tasks = ref([]);
  const loading = ref(false);
  const activeTask = ref(null);
  const selectedTasks = ref([]);

  const loadTasks = async (params = {}) => {
    loading.value = true;
    try {
      const response = await api.get('tasks/', { params });
      tasks.value = response.data.results || response.data;
      return tasks.value;
    } catch (err) {
      showToast('Tasks konnten nicht geladen werden', 'error');
      return [];
    } finally {
      loading.value = false;
    }
  };

  const updateTask = async (taskId, updates) => {
    try {
      const response = await api.patch(`tasks/${taskId}/`, updates);
      const index = tasks.value.findIndex(t => t.id === taskId);
      if (index !== -1) {
        tasks.value[index] = response.data;
      }
      showToast('Task aktualisiert', 'success');
      return response.data;
    } catch (err) {
      showToast('Task konnte nicht aktualisiert werden', 'error');
      throw err;
    }
  };

  const deleteTask = async (taskId) => {
    try {
      await api.delete(`tasks/${taskId}/`);
      tasks.value = tasks.value.filter(t => t.id !== taskId);
      showToast('Task gelöscht', 'success');
    } catch (err) {
      showToast('Task konnte nicht gelöscht werden', 'error');
      throw err;
    }
  };

  const selectTask = (taskId) => {
    if (selectedTasks.value.includes(taskId)) {
      selectedTasks.value = selectedTasks.value.filter(id => id !== taskId);
    } else {
      selectedTasks.value.push(taskId);
    }
  };

  const bulkUpdate = async (updates) => {
    try {
      await Promise.all(
        selectedTasks.value.map(id => updateTask(id, updates))
      );
      selectedTasks.value = [];
      showToast('Änderungen gespeichert', 'success');
    } catch (err) {
      showToast('Änderungen konnten nicht gespeichert werden', 'error');
    }
  };

  return {
    tasks,
    loading,
    activeTask,
    selectedTasks,
    loadTasks,
    updateTask,
    deleteTask,
    selectTask,
    bulkUpdate,
  };
}
