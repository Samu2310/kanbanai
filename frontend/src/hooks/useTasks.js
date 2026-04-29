import { useState, useEffect } from 'react';
import apiClient from '../api/client';

export const useTasks = (projectId) => {
  const [tasks, setTasks] = useState([]);
  const [columns, setColumns] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchBoardData = async () => {
    if (!projectId) return;
    setLoading(true);
    try {
      // Cargar columnas y tareas en paralelo
      const [colsRes, tasksRes] = await Promise.all([
        apiClient.get(`/projects/${projectId}/columns`),
        apiClient.get(`/projects/${projectId}/tasks`)
      ]);
      setColumns(colsRes.data);
      setTasks(tasksRes.data);
      setError(null);
    } catch (err) {
      setError(err.response?.data?.detail || "Error al cargar el tablero");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBoardData();
  }, [projectId]);

  const moveTask = async (taskId, newColumnId) => {
    const previousTasks = [...tasks];
    // Optimistic update
    setTasks(prev => prev.map(t => t.id === taskId ? { ...t, column_id: newColumnId } : t));
    
    try {
      const response = await apiClient.patch(`/tasks/${taskId}`, {
        column_id: newColumnId
      });
      // Sync with backend response
      setTasks(prev => prev.map(t => t.id === taskId ? response.data : t));
      return response.data;
    } catch (err) {
      // Revert if failed
      setTasks(previousTasks);
      throw err.response?.data?.detail || "Error al mover tarea";
    }
  };

  const createTask = async (taskData) => {
    try {
      const payload = { ...taskData, project_id: projectId };
      const response = await apiClient.post(`/projects/${projectId}/tasks`, payload);
      setTasks(prev => [...prev, response.data]);
      return response.data;
    } catch (err) {
      throw err.response?.data?.detail || "Error al crear tarea";
    }
  };

  const updateTask = async (taskId, taskData) => {
    try {
      const response = await apiClient.patch(`/tasks/${taskId}`, taskData);
      setTasks(prev => prev.map(t => t.id === taskId ? response.data : t));
      return response.data;
    } catch (err) {
      throw err.response?.data?.detail || "Error al actualizar tarea";
    }
  };

  const deleteTask = async (taskId) => {
    try {
      await apiClient.delete(`/tasks/${taskId}`);
      setTasks(prev => prev.filter(t => t.id !== taskId));
    } catch (err) {
      throw err.response?.data?.detail || "Error al eliminar tarea";
    }
  };

  return { tasks, columns, loading, error, fetchBoardData, moveTask, createTask, updateTask, deleteTask };
};
