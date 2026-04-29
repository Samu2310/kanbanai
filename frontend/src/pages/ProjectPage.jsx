import { useState, useEffect } from "react";
import { useParams, useNavigate } from 'react-router-dom';
import { useTasks } from '../hooks/useTasks';
import { useAuth } from '../context/AuthContext';
import { DragDropContext, Droppable, Draggable } from '@hello-pangea/dnd';
import { ArrowLeft, Plus, MoreVertical, Calendar, Bot, UserPlus, X, Send } from 'lucide-react';
import Button from '../components/ui/Button';
import TaskModal from '../components/TaskModal';
import AiPanel from '../components/AiPanel';
import InboxPanel from '../components/InboxPanel';
import apiClient from '../api/client';
import './kanban.css';

const ProjectPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const { tasks, columns, loading, moveTask, createTask, updateTask, deleteTask } = useTasks(id);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedTask, setSelectedTask] = useState(null);
  const [isAiPanelOpen, setIsAiPanelOpen] = useState(false);
  const [activeDropdown, setActiveDropdown] = useState(null);

  // Teacher feedback state
  const [isFeedbackModalOpen, setIsFeedbackModalOpen] = useState(false);
  const [feedbackList, setFeedbackList] = useState([]);
  const [newFeedback, setNewFeedback] = useState('');
  const [isSavingFeedback, setIsSavingFeedback] = useState(false);

  // Invite modal state
  const [isInviteOpen, setIsInviteOpen] = useState(false);
  const [inviteEmail, setInviteEmail] = useState('');
  const [inviteLoading, setInviteLoading] = useState(false);
  const [inviteMessage, setInviteMessage] = useState(null); // { type: 'success'|'error', text }

  const handleOpenModal = (task = null) => {
    setSelectedTask(task);
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setSelectedTask(null);
    setIsModalOpen(false);
  };


  useEffect(() => {
    const handleClickOutside = () => setActiveDropdown(null);
    document.addEventListener('click', handleClickOutside);
    return () => document.removeEventListener('click', handleClickOutside);
  }, []);

  const fetchFeedback = async () => {
    if (!id) return;
    try {
      const response = await apiClient.get(`/projects/${id}/feedback`);
      setFeedbackList(response.data.feedback || []);
    } catch (err) {
      console.error("Error cargando observaciones:", err);
    }
  };

  useEffect(() => {
    fetchFeedback();
  }, [id]);

  const handleAddFeedback = async (e) => {
    e.preventDefault();
    if (!newFeedback.trim()) return;
    setIsSavingFeedback(true);
    try {
      await apiClient.post(`/projects/${id}/feedback`, { feedback: newFeedback });
      setNewFeedback('');
      await fetchFeedback();
    } catch (err) {
      alert("Error al añadir observación");
    } finally {
      setIsSavingFeedback(false);
    }
  };

  const handleDeleteFeedback = async (feedbackId) => {
    if (!window.confirm("¿Estás seguro de eliminar esta observación?")) return;
    try {
      await apiClient.delete(`/projects/${id}/feedback/${feedbackId}`);
      await fetchFeedback();
    } catch (err) {
      alert("Error al eliminar");
    }
  };

  const handleResolveFeedback = async (feedbackId) => {
    try {
      await apiClient.patch(`/projects/${id}/feedback/${feedbackId}/resolve`);
      await fetchFeedback();
    } catch (err) {
      alert("Error al marcar como resuelto");
    }
  };

  const handleSaveTask = async (taskData) => {
    try {
      if (selectedTask) {
        await updateTask(selectedTask.id, taskData);
      } else {
        await createTask(taskData);
      }
      handleCloseModal();
    } catch (error) {
      const msg = error?.response?.data?.detail || String(error);
      alert(msg);
    }
  };

  const handleDeleteTask = async (taskId) => {
    try {
      await deleteTask(taskId);
      handleCloseModal();
    } catch (error) {
      alert(error);
    }
  };

  const handleAddAiSuggestion = async (suggestion) => {
    try {
      const columnId = columns[0]?.id;
      if (!columnId) throw new Error("No hay columnas en el proyecto");
      await createTask({
        title: suggestion.title,
        description: suggestion.description,
        priority: suggestion.priority,
        column_id: columnId,
        due_date: null
      });
      alert(`Tarea agregada: ${suggestion.title}`);
    } catch (error) {
      alert("Error agregando tarea: " + (error?.response?.data?.detail || error.message));
    }
  };

  const onDragEnd = (result) => {
    const { destination, source, draggableId } = result;
    if (!destination) return;
    if (destination.droppableId === source.droppableId && destination.index === source.index) return;
    moveTask(draggableId, destination.droppableId);
  };

  const handleSendInvite = async (e) => {
    e.preventDefault();
    const email = inviteEmail.trim();
    if (!email) return;

    setInviteLoading(true);
    setInviteMessage(null);
    console.log(`Enviando invitación para proyecto ${id} al correo: ${email}`);

    try {
      const response = await apiClient.post(`/projects/${id}/invitations`, { email });
      console.log("Respuesta de invitación:", response.data);
      setInviteMessage({ type: 'success', text: response.data.message });
      setInviteEmail('');
    } catch (error) {
      console.error("Error en invitación:", error.response || error);
      const errorMsg = error?.response?.data?.detail || 'Error enviando la invitación.';
      setInviteMessage({
        type: 'error',
        text: typeof errorMsg === 'string' ? errorMsg : JSON.stringify(errorMsg)
      });
    } finally {
      setInviteLoading(false);
    }
  };

  if (loading) return <div className="loading">Cargando tablero...</div>;

  const roleName = user?.role === 'professor' ? 'Profesor' : (user?.role === 'guest' ? 'Invitado' : 'Estudiante');
  const isGuest = user?.role === 'guest';
  const isStudent = user?.role === 'student';

  const canEditTask = (task) => {
    if (!task) return !isGuest;
    if (isGuest) return false;
    return true; // student, professor, admin pueden editar cualquier tarea
  };

  return (
    <div className="kanban-layout">
      <header className="kanban-header">
        <div className="header-left">
          <button className="btn-icon" onClick={() => navigate('/')}>
            <ArrowLeft size={20} />
          </button>
          <h1>Proyecto</h1>
          <span className={`role-badge ${user?.role}`}>{roleName}</span>
        </div>
        <div className="header-right">
          {/* Inbox / Notification Bell — visible for everyone */}
          <InboxPanel />

          {!isGuest && (
            <>
              <Button className="btn-secondary" onClick={() => { setIsInviteOpen(true); setInviteMessage(null); }}>
                <UserPlus size={16} /> Invitar
              </Button>
              <Button className="btn-secondary" onClick={() => setIsFeedbackModalOpen(true)}>
                <Calendar size={18} /> Observaciones
              </Button>
              <Button className="btn-secondary" onClick={() => setIsAiPanelOpen(!isAiPanelOpen)}>
                <Bot size={18} color="var(--primary)" /> IA
              </Button>
              <Button onClick={() => handleOpenModal()}><Plus size={18} /> Nueva Tarea</Button>
            </>
          )}
        </div>
      </header>

      {/* ── Invite Modal ─────────────────────────────────── */}
      {isInviteOpen && (
        <div className="modal-overlay">
          <div className="modal-content" style={{ maxWidth: '420px' }}>
            <div className="modal-header">
              <h2>Invitar Colaborador</h2>
              <button className="btn-icon" onClick={() => setIsInviteOpen(false)} type="button">
                <X size={20} />
              </button>
            </div>
            <form onSubmit={handleSendInvite} style={{ padding: '1.5rem' }}>
              <p style={{ color: 'var(--text-muted)', marginBottom: '1rem', fontSize: '0.875rem' }}>
                Ingresa el correo del usuario registrado en KanbanAI que deseas invitar. Recibirá una notificación en su bandeja.
              </p>
              {inviteMessage && (
                <div className={inviteMessage.type === 'success' ? 'invite-success-msg' : 'auth-error'} style={{ marginBottom: '1rem' }}>
                  {inviteMessage.text}
                </div>
              )}
              <div className="form-group">
                <label>Correo electrónico</label>
                <input
                  type="email"
                  value={inviteEmail}
                  onChange={e => setInviteEmail(e.target.value)}
                  placeholder="colaborador@ejemplo.com"
                  required
                />
              </div>
              <div className="modal-actions" style={{ marginTop: '1.5rem' }}>
                <Button className="btn-secondary" type="button" onClick={() => setIsInviteOpen(false)}>
                  Cancelar
                </Button>
                <Button type="submit" disabled={inviteLoading}>
                  <Send size={16} /> {inviteLoading ? 'Enviando...' : 'Enviar Invitación'}
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}

      <DragDropContext onDragEnd={onDragEnd}>
        <div style={{ display: 'flex', flexDirection: 'column', flex: 1, overflow: 'hidden' }}>
          
          {/* Observations Modal */}
          {isFeedbackModalOpen && (
            <div className="modal-overlay">
              <div className="modal-content" style={{ maxWidth: '600px', maxHeight: '85vh' }}>
                <div className="modal-header">
                  <h2>Observaciones del Profesor</h2>
                  <button className="btn-icon" onClick={() => setIsFeedbackModalOpen(false)}>
                    <X size={20} />
                  </button>
                </div>
                
                <div className="modal-body" style={{ padding: '1.5rem', overflowY: 'auto' }}>
                  {(user?.role === 'professor' || user?.role === 'admin') && (
                    <form onSubmit={handleAddFeedback} style={{ marginBottom: '2rem' }}>
                      <textarea
                        className="feedback-textarea"
                        value={newFeedback}
                        onChange={(e) => setNewFeedback(e.target.value)}
                        placeholder="Escribe una nueva observación académica..."
                        rows={3}
                        style={{ width: '100%', marginBottom: '0.5rem', padding: '0.75rem', borderRadius: '0.5rem', background: 'var(--bg-input)', border: '1px solid var(--border)', color: 'var(--text-main)' }}
                      />
                      <Button type="submit" disabled={isSavingFeedback || !newFeedback.trim()}>
                        {isSavingFeedback ? 'Añadiendo...' : 'Añadir Observación'}
                      </Button>
                    </form>
                  )}

                  <div className="feedback-list" style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                    {feedbackList.length === 0 ? (
                      <p className="text-muted" style={{ textAlign: 'center', fontStyle: 'italic' }}>No hay observaciones registradas.</p>
                    ) : (
                      [...feedbackList].reverse().map((item) => (
                        <div key={item.id} className={`feedback-item-card ${item.resolved ? 'resolved' : ''}`} style={{ padding: '1rem', borderRadius: '0.75rem', background: 'rgba(30, 41, 59, 0.5)', border: `1px solid ${item.resolved ? 'var(--success)' : 'var(--border)'}`, position: 'relative' }}>
                          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                            <span>{item.author_name} • {new Date(item.created_at).toLocaleString()}</span>
                            {item.resolved && <span style={{ color: 'var(--success)', fontWeight: 'bold' }}>RESUELTO</span>}
                          </div>
                          <p style={{ fontSize: '0.9375rem', color: 'var(--text-main)', whiteSpace: 'pre-wrap' }}>{item.content}</p>
                          
                          {(user?.role === 'professor' || user?.role === 'admin') && (
                            <div style={{ display: 'flex', gap: '0.75rem', marginTop: '1rem', justifyContent: 'flex-end' }}>
                              {!item.resolved && (
                                <button 
                                  onClick={() => handleResolveFeedback(item.id)}
                                  style={{ background: 'none', border: 'none', color: 'var(--success)', fontSize: '0.8125rem', cursor: 'pointer', fontWeight: '500' }}
                                >
                                  Marcar Resuelto
                                </button>
                              )}
                              <button 
                                onClick={() => handleDeleteFeedback(item.id)}
                                style={{ background: 'none', border: 'none', color: 'var(--danger)', fontSize: '0.8125rem', cursor: 'pointer', fontWeight: '500' }}
                              >
                                Eliminar
                              </button>
                            </div>
                          )}
                        </div>
                      ))
                    )}
                  </div>
                </div>
              </div>
            </div>
          )}

          <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
            <div className="kanban-board">
            {columns.map(column => (
              <div key={column.id} className="kanban-column">
                <div className="column-header">
                  <h3>{column.name}</h3>
                  <span className="count">{tasks.filter(t => t.column_id === column.id).length}</span>
                </div>

                <Droppable droppableId={column.id}>
                  {(provided) => (
                    <div
                      className="task-list"
                      {...provided.droppableProps}
                      ref={provided.innerRef}
                    >
                      {tasks
                        .filter(t => t.column_id === column.id)
                        .map((task, index) => {
                          const isDragDisabled = !canEditTask(task);
                          return (
                            <Draggable key={task.id} draggableId={task.id} index={index} isDragDisabled={isDragDisabled}>
                              {(provided) => (
                                <div
                                  className={`task-card ${isDragDisabled ? 'read-only' : ''}`}
                                  ref={provided.innerRef}
                                  {...provided.draggableProps}
                                  {...provided.dragHandleProps}
                                  onClick={() => handleOpenModal(task)}
                                >
                                  <div className="task-header">
                                    <span className={`priority-dot ${task.priority}`}></span>
                                    <div className="task-actions" style={{ position: 'relative' }}>
                                      <button
                                        className="btn-icon"
                                        onClick={(e) => {
                                          e.stopPropagation();
                                          setActiveDropdown(activeDropdown === task.id ? null : task.id);
                                        }}
                                      >
                                        <MoreVertical size={14} color="#94a3b8" />
                                      </button>
                                      {activeDropdown === task.id && (
                                        <div className="dropdown-menu">
                                          <button onClick={(e) => {
                                            e.stopPropagation();
                                            handleOpenModal(task);
                                            setActiveDropdown(null);
                                          }}>Editar</button>
                                          <button onClick={(e) => {
                                            e.stopPropagation();
                                            if (window.confirm('¿Estás seguro de eliminar esta tarea?')) {
                                              handleDeleteTask(task.id);
                                            }
                                            setActiveDropdown(null);
                                          }} className="danger-text">Eliminar</button>
                                        </div>
                                      )}
                                    </div>
                                  </div>
                                  <h4 onClick={() => handleOpenModal(task)}>{task.title}</h4>
                                  <p>{task.description}</p>
                                    <div className="task-footer">
                                    {task.due_date && (
                                      <div className="due-date">
                                        <Calendar size={12} />
                                        {new Date(task.due_date + 'T00:00:00').toLocaleDateString()}
                                      </div>
                                    )}
                                    <div className="assignee" title={task.created_by_name || 'Sin autor'}>
                                      {task.created_by_name ? task.created_by_name.charAt(0).toUpperCase() : ''}
                                    </div>
                                  </div>
                                </div>
                              )}
                            </Draggable>
                          );
                        })}
                      {provided.placeholder}
                    </div>
                  )}
                </Droppable>
              </div>
            ))}
          </div>

          {!isGuest && (
            <AiPanel
              isOpen={isAiPanelOpen}
              onClose={() => setIsAiPanelOpen(false)}
              onAddTask={handleAddAiSuggestion}
              projectId={id}
              tasks={tasks}
            />
          )}
          </div>
        </div>
      </DragDropContext>

      <TaskModal
        isOpen={isModalOpen}
        onClose={handleCloseModal}
        task={selectedTask}
        columns={columns}
        onSave={handleSaveTask}
        onDelete={handleDeleteTask}
        readOnly={selectedTask && !canEditTask(selectedTask)}
      />
    </div>
  );
};

export default ProjectPage;
