import { useState, useEffect } from 'react';
import apiClient from '../api/client';
import { useAuth } from '../context/AuthContext';

export const useProjects = () => {
  const { isAuthenticated } = useAuth();
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchProjects = async () => {
    if (!isAuthenticated) return;
    setLoading(true);
    try {
      const response = await apiClient.get('/projects');
      setProjects(response.data.items);
      setError(null);
    } catch (err) {
      setError(err.response?.data?.detail || "Error al cargar proyectos");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProjects();
  }, [isAuthenticated]);

  const createProject = async (projectData) => {
    try {
      const response = await apiClient.post('/projects', projectData);
      setProjects(prev => [...prev, response.data]);
      return response.data;
    } catch (err) {
      throw err.response?.data?.detail || "Error al crear proyecto";
    }
  };

  const deleteProject = async (projectId) => {
    try {
      await apiClient.delete(`/projects/${projectId}`);
      setProjects(prev => prev.filter(p => p.id !== projectId));
    } catch (err) {
      throw err.response?.data?.detail || "Error al eliminar proyecto";
    }
  };

  return { projects, loading, error, fetchProjects, createProject, deleteProject };
};
