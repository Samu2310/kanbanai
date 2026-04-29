import React, { useState, useEffect } from 'react';
import apiClient from '../api/client';
import { Clock } from 'lucide-react';
import './TaskHistory.css';

const fieldLabels = {
  column_id: 'columna',
  title: 'título',
  description: 'descripción',
  priority: 'prioridad',
  due_date: 'fecha límite',
  assignment: 'asignación'
};

const TaskHistory = ({ taskId }) => {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const response = await apiClient.get(`/tasks/${taskId}/history`);
        setHistory(response.data);
      } catch (error) {
        console.error("Error fetching history:", error);
      } finally {
        setLoading(false);
      }
    };

    if (taskId) {
      fetchHistory();
    }
  }, [taskId]);

  if (loading) return <div className="history-loading">Cargando historial...</div>;
  if (!history.length) return <div className="history-empty">No hay cambios registrados.</div>;

  return (
    <div className="task-history">
      <h4>Historial de Cambios</h4>
      <div className="history-list">
        {history.map((record) => (
          <div key={record.id} className="history-item">
            <div className="history-icon">
              <Clock size={16} />
            </div>
            <div className="history-content">
              <p>
                <strong>{record.author_name || 'Usuario'}</strong> cambió <code>{fieldLabels[record.field_name] || record.field_name}</code>
              </p>
              <div className="history-values">
                <span className="old-value">{record.old_value || 'N/A'}</span>
                <span className="arrow">→</span>
                <span className="new-value">{record.new_value || 'N/A'}</span>
              </div>
              <span className="history-date">
                {new Date(record.changed_at).toLocaleString()}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default TaskHistory;
