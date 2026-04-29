import { useEffect, useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import apiClient from '../api/client';
import { useAuth } from '../context/AuthContext';
import './auth.css'; // Podemos reutilizar estilos de auth

const InvitePage = () => {
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token');
  const navigate = useNavigate();
  const { user, isAuthenticated } = useAuth();
  
  const [status, setStatus] = useState('processing'); // processing, success, error
  const [message, setMessage] = useState('Procesando invitación...');
  const [projectId, setProjectId] = useState(null);

  useEffect(() => {
    if (!token) {
      setStatus('error');
      setMessage('Token de invitación no proporcionado.');
      return;
    }

    if (!isAuthenticated) {
      // Redirigir al login guardando la URL actual para volver después
      sessionStorage.setItem('redirectAfterLogin', `/invite?token=${token}`);
      navigate('/login');
      return;
    }

    const acceptInvite = async () => {
      try {
        const response = await apiClient.post('/invitations/accept', { token });
        setStatus('success');
        setMessage(response.data.message);
        setProjectId(response.data.project_id);
        
        // Redirigir al proyecto después de 2 segundos
        setTimeout(() => {
          navigate(`/projects/${response.data.project_id}`);
        }, 2000);
      } catch (error) {
        setStatus('error');
        setMessage(error?.response?.data?.detail || 'Error al aceptar la invitación. Puede que el token haya expirado.');
      }
    };

    acceptInvite();
  }, [token, isAuthenticated, navigate]);

  return (
    <div className="auth-container animate-fade-in">
      <div className={`auth-card ${status}`}>
        <h2>Invitación al Proyecto</h2>
        <p>{message}</p>
        
        {status === 'error' && (
          <button onClick={() => navigate('/')} style={{marginTop: '20px'}}>
            Ir al Dashboard
          </button>
        )}
        
        {status === 'success' && (
          <p className="auth-footer">Redirigiendo al proyecto...</p>
        )}
      </div>
    </div>
  );
};

export default InvitePage;
