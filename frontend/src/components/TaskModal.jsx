import React, { useState, useEffect } from 'react';
import Button from './ui/Button';
import { X } from 'lucide-react';
import TaskHistory from './TaskHistory';
import './TaskModal.css';

const TaskModal = ({ isOpen, onClose, task, columns, onSave, onDelete, readOnly }) => {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [columnId, setColumnId] = useState('');
  const [priority, setPriority] = useState('medium');
  const [dueDate, setDueDate] = useState('');

  useEffect(() => {
    if (task) {
      setTitle(task.title || '');
      setDescription(task.description || '');
      setColumnId(task.column_id || columns[0]?.id || '');
      setPriority(task.priority || 'medium');
      setDueDate(task.due_date ? task.due_date.split('T')[0] : '');
    } else {
      setTitle('');
      setDescription('');
      setColumnId(columns[0]?.id || '');
      setPriority('medium');
      setDueDate('');
    }
  }, [task, columns, isOpen]);

  if (!isOpen) return null;

  const handleSubmit = (e) => {
    e.preventDefault();
    onSave({
      title,
      description,
      column_id: columnId,
      priority,
      due_date: dueDate || null
    });
  };

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <div className="modal-header">
          <h2>{task ? 'Editar Tarea' : 'Nueva Tarea'}</h2>
          <button className="btn-icon" onClick={onClose} type="button">
            <X size={20} />
          </button>
        </div>
        
        <form onSubmit={handleSubmit} className="modal-form">
          {readOnly && <div className="read-only-banner">Modo solo lectura: No tienes permisos para editar esta tarea.</div>}
          <div className="form-group">
            <label>Título</label>
            <input 
              type="text" 
              value={title} 
              onChange={e => setTitle(e.target.value)} 
              required 
              placeholder="Ej: Implementar login"
              disabled={readOnly}
            />
          </div>
          
          <div className="form-group">
            <label>Descripción</label>
            <textarea 
              value={description} 
              onChange={e => setDescription(e.target.value)}
              placeholder="Detalles de la tarea..."
              rows={4}
              disabled={readOnly}
            />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Columna</label>
              <select value={columnId} onChange={e => setColumnId(e.target.value)} required disabled={readOnly}>
                {columns.map(col => (
                  <option key={col.id} value={col.id}>{col.name}</option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label>Prioridad</label>
              <select value={priority} onChange={e => setPriority(e.target.value)} required disabled={readOnly}>
                <option value="low">Baja</option>
                <option value="medium">Media</option>
                <option value="high">Alta</option>
              </select>
            </div>
          </div>

          <div className="form-group">
            <label>Fecha de Vencimiento</label>
            <input 
              type="date" 
              value={dueDate} 
              onChange={e => setDueDate(e.target.value)} 
              disabled={readOnly}
            />
          </div>

          {task && <TaskHistory taskId={task.id} />}

          <div className="modal-actions" style={{ display: 'flex', justifyContent: 'space-between', width: '100%' }}>
            {task && !readOnly && onDelete ? (
              <Button className="btn-danger" type="button" onClick={() => {
                if (window.confirm('¿Estás seguro de eliminar esta tarea?')) {
                  onDelete(task.id);
                }
              }} style={{ backgroundColor: '#ef4444', color: 'white', border: 'none' }}>
                Eliminar
              </Button>
            ) : <div></div>}
            <div style={{ display: 'flex', gap: '1rem' }}>
              <Button className="btn-secondary" onClick={onClose} type="button">
                {readOnly ? 'Cerrar' : 'Cancelar'}
              </Button>
              {!readOnly && <Button className="btn-primary" type="submit">Guardar</Button>}
            </div>
          </div>
        </form>
      </div>
    </div>
  );
};

export default TaskModal;
