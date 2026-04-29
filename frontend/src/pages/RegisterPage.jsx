import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './auth.css';

const RegisterPage = () => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    role: 'student'
  });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [loading, setLoading] = useState(false);
  
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    
    try {
      await register(formData);
      setSuccess(true);
      setTimeout(() => navigate('/login'), 2000);
    } catch (err) {
      const errorMsg = err?.response?.data?.detail || err?.message || 'Error al registrar usuario. El email podría ya existir.';
      setError(typeof errorMsg === 'string' ? errorMsg : JSON.stringify(errorMsg));
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <div className="auth-container">
        <div className="auth-card success animate-fade-in">
          <h2>¡Cuenta creada!</h2>
          <p>Redirigiéndote al login...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="auth-container animate-fade-in">
      <div className="auth-card">
        <h1>Crea tu cuenta</h1>
        <p>Únete a la plataforma de gestión inteligente</p>
        
        <form onSubmit={handleSubmit}>
          {error && <div className="auth-error">{error}</div>}
          
          <div className="form-group">
            <label>Nombre Completo</label>
            <input 
              name="name"
              type="text" 
              value={formData.name} 
              onChange={handleChange} 
              placeholder="Juan Pérez"
              required 
            />
          </div>
          
          <div className="form-group">
            <label>Email</label>
            <input 
              name="email"
              type="email" 
              value={formData.email} 
              onChange={handleChange} 
              placeholder="juan@universidad.edu"
              required 
            />
          </div>
          
          <div className="form-group">
            <label>Contraseña</label>
            <input 
              name="password"
              type="password" 
              value={formData.password} 
              onChange={handleChange} 
              placeholder="Mínimo 8 caracteres"
              required 
              minLength="8"
            />
          </div>

          <div className="form-group">
            <label>Rol</label>
            <select name="role" value={formData.role} onChange={handleChange}>
              <option value="student">Estudiante</option>
              <option value="professor">Profesor</option>
              <option value="guest">Invitado</option>
            </select>
          </div>
          
          <button type="submit" disabled={loading}>
            {loading ? 'Creando cuenta...' : 'Registrarse'}
          </button>
        </form>
        
        <p className="auth-footer">
          ¿Ya tienes cuenta? <Link to="/login">Inicia sesión</Link>
        </p>
      </div>
    </div>
  );
};

export default RegisterPage;
