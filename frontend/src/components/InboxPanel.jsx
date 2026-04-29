import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Bell, X, Check, UserPlus, CheckCheck } from 'lucide-react';
import { useNotifications } from '../context/NotificationContext';
import './InboxPanel.css';

const InboxPanel = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [activeTab, setActiveTab] = useState('invites'); // 'invites' | 'all'
  const [loadingToken, setLoadingToken] = useState(null);
  const navigate = useNavigate();

  const {
    notifications,
    unreadCount,
    inviteCount,
    markAsRead,
    acceptInvitation,
    declineInvitation
  } = useNotifications();

  const invites = notifications.filter(n => n.type === 'project_invite' && !n.is_read);
  const others = notifications.filter(n => n.type !== 'project_invite');

  const handleAccept = async (notif) => {
    setLoadingToken(notif.invitation_token);
    try {
      const result = await acceptInvitation(notif.invitation_token);
      setIsOpen(false);
      navigate(`/projects/${result.project_id}`);
    } catch (err) {
      alert(err?.response?.data?.detail || 'Error aceptando la invitación.');
    } finally {
      setLoadingToken(null);
    }
  };

  const handleDecline = async (notif) => {
    setLoadingToken(notif.invitation_token);
    try {
      await declineInvitation(notif.invitation_token);
    } catch (err) {
      alert(err?.response?.data?.detail || 'Error rechazando la invitación.');
    } finally {
      setLoadingToken(null);
    }
  };

  const formatDate = (dateStr) => {
    const d = new Date(dateStr);
    return d.toLocaleDateString('es-ES', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className="inbox-wrapper">
      {/* Bell button */}
      <button className="inbox-trigger" onClick={() => setIsOpen(!isOpen)} id="inbox-bell-btn">
        <Bell size={20} />
        {unreadCount > 0 && (
          <span className="inbox-badge">{unreadCount > 9 ? '9+' : unreadCount}</span>
        )}
      </button>

      {/* Panel */}
      {isOpen && (
        <>
          <div className="inbox-backdrop" onClick={() => setIsOpen(false)} />
          <div className="inbox-panel">
            <div className="inbox-header">
              <h3>Bandeja</h3>
              <button className="btn-icon" onClick={() => setIsOpen(false)}><X size={16} /></button>
            </div>

            {/* Tabs */}
            <div className="inbox-tabs">
              <button
                className={`inbox-tab ${activeTab === 'invites' ? 'active' : ''}`}
                onClick={() => setActiveTab('invites')}
              >
                <UserPlus size={14} /> Invitaciones
                {inviteCount > 0 && <span className="tab-badge">{inviteCount}</span>}
              </button>
              <button
                className={`inbox-tab ${activeTab === 'all' ? 'active' : ''}`}
                onClick={() => setActiveTab('all')}
              >
                <Bell size={14} /> Todas
                {unreadCount - inviteCount > 0 && (
                  <span className="tab-badge">{unreadCount - inviteCount}</span>
                )}
              </button>
            </div>

            <div className="inbox-body">
              {/* Invitations Tab */}
              {activeTab === 'invites' && (
                invites.length === 0 ? (
                  <div className="inbox-empty">
                    <UserPlus size={32} color="#475569" />
                    <p>No tienes invitaciones pendientes</p>
                  </div>
                ) : (
                  invites.map(notif => (
                    <div key={notif.id} className="invite-card">
                      <div className="invite-icon"><UserPlus size={18} color="#818cf8" /></div>
                      <div className="invite-content">
                        <p className="invite-title">{notif.title}</p>
                        <p className="invite-msg">{notif.message}</p>
                        <p className="invite-date">{formatDate(notif.created_at)}</p>
                        <div className="invite-actions">
                          <button
                            className="btn-accept"
                            disabled={loadingToken === notif.invitation_token}
                            onClick={() => handleAccept(notif)}
                          >
                            <Check size={14} />
                            {loadingToken === notif.invitation_token ? 'Entrando...' : 'Aceptar'}
                          </button>
                          <button
                            className="btn-decline"
                            disabled={loadingToken === notif.invitation_token}
                            onClick={() => handleDecline(notif)}
                          >
                            <X size={14} /> Rechazar
                          </button>
                        </div>
                      </div>
                    </div>
                  ))
                )
              )}

              {/* All Notifications Tab */}
              {activeTab === 'all' && (
                notifications.length === 0 ? (
                  <div className="inbox-empty">
                    <CheckCheck size={32} color="#475569" />
                    <p>No hay notificaciones</p>
                  </div>
                ) : (
                  notifications
                    .filter(n => n.type !== 'project_invite')
                    .map(notif => (
                      <div
                        key={notif.id}
                        className={`notif-item ${!notif.is_read ? 'unread' : ''}`}
                        onClick={() => !notif.is_read && markAsRead(notif.id)}
                      >
                        <div className="notif-dot" />
                        <div className="notif-content">
                          <p className="notif-title">{notif.title}</p>
                          <p className="notif-msg">{notif.message}</p>
                          <p className="notif-date">{formatDate(notif.created_at)}</p>
                        </div>
                      </div>
                    ))
                )
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default InboxPanel;
