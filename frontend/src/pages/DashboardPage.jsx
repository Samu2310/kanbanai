import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useProjects } from '../hooks/useProjects';
import { useAuth } from '../context/AuthContext';
import Button from '../components/ui/Button';
import InboxPanel from '../components/InboxPanel';
import { Plus, Layout, Users, Clock, LogOut, Trash2 } from 'lucide-react';
import './dashboard.css';

const DashboardPage = () => {
  const { projects, loading, createProject, deleteProject } = useProjects();
  const { user, logout } = useAuth();
  const [showModal, setShowModal] = useState(false);
  const [newProject, setNewProject] = useState({ name: '', description: '' });
  const navigate = useNavigate();

  const handleCreate = async (e) => {
    e.preventDefault();
    try {
      const proj = await createProject(newProject);
      setShowModal(false);
      setNewProject({ name: '', description: '' });
      navigate(`/projects/${proj.id}`);
    } catch (err) {
      alert(err);
    }
  };

  const handleDeleteProject = async (e, projectId) => {
    e.stopPropagation(); // prevent navigating to project
    if (window.confirm("¿Estás seguro de eliminar este proyecto y TODAS sus tareas?")) {
      try {
        await deleteProject(projectId);
      } catch (err) {
        alert(err);
      }
    }
  };

  return (
    <div className="dashboard-layout">
      <aside className="sidebar">
        <div className="sidebar-header">
          <div className="logo">
            <Layout size={24} color="#6366f1" />
            <span>KanbanAI</span>
          </div>
        </div>
        
        <nav className="sidebar-nav">
          <div className="nav-item active">
            <Layout size={20} />
            <span>Proyectos</span>
          </div>
        </nav>

        <div className="sidebar-footer">
          <div className="user-info">
            <div className="avatar">{user?.name?.charAt(0)}</div>
            <div className="details">
              <p className="name">{user?.name}</p>
              <p className="role">{user?.role}</p>
            </div>
          </div>
          <button className="btn-logout" onClick={logout}>
            <LogOut size={18} />
          </button>
        </div>
      </aside>

      <main className="dashboard-content">
        <header className="content-header">
          <h1>Mis Proyectos</h1>
          <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
            <InboxPanel />
            <Button onClick={() => setShowModal(true)}>
              <Plus size={18} />
              Nuevo Proyecto
            </Button>
          </div>
        </header>

        {loading ? (
          <div className="loading">Cargando proyectos...</div>
        ) : (
          <div className="projects-grid">
            {projects.map(project => (
              <div key={project.id} className="project-card" onClick={() => navigate(`/projects/${project.id}`)}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <h3>{project.name}</h3>
                  <button 
                    className="btn-icon" 
                    onClick={(e) => handleDeleteProject(e, project.id)} 
                    style={{ color: '#ef4444', padding: '4px' }}
                    title="Eliminar proyecto"
                  >
                    <Trash2 size={16} />
                  </button>
                </div>
                <p>{project.description || 'Sin descripción'}</p>
                <div className="project-meta">
                  <span><Clock size={14} /> {new Date(project.created_at).toLocaleDateString()}</span>
                </div>
              </div>
            ))}
            
            {projects.length === 0 && (
              <div className="empty-state">
                <p>No tienes proyectos aún. ¡Crea el primero!</p>
              </div>
            )}
          </div>
        )}
      </main>

      {showModal && (
        <div className="modal-overlay">
          <div className="modal-content animate-fade-in">
            <h2>Crear Nuevo Proyecto</h2>
            <form onSubmit={handleCreate}>
              <div className="form-group">
                <label>Nombre del Proyecto</label>
                <input 
                  type="text" 
                  value={newProject.name} 
                  onChange={(e) => setNewProject({...newProject, name: e.target.value})}
                  placeholder="Ej: Tesis de Grado"
                  required 
                />
              </div>
              <div className="form-group">
                <label>Descripción (Opcional)</label>
                <textarea 
                  value={newProject.description} 
                  onChange={(e) => setNewProject({...newProject, description: e.target.value})}
                  placeholder="De qué trata este proyecto..."
                />
              </div>
              <div className="modal-actions">
                <Button variant="secondary" onClick={() => setShowModal(false)}>Cancelar</Button>
                <Button type="submit">Crear Proyecto</Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default DashboardPage;
