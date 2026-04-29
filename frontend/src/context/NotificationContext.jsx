import { createContext, useState, useEffect, useContext } from 'react';
import apiClient from '../api/client';
import { useAuth } from './AuthContext';

const NotificationContext = createContext();

export const NotificationProvider = ({ children }) => {
  const { isAuthenticated } = useAuth();
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [inviteCount, setInviteCount] = useState(0);

  const fetchNotifications = async () => {
    if (!isAuthenticated) return;
    try {
      const response = await apiClient.get('/notifications');
      const all = response.data;
      setNotifications(all);
      setUnreadCount(all.filter(n => !n.is_read).length);
      setInviteCount(all.filter(n => n.type === 'project_invite' && !n.is_read).length);
    } catch (error) {
      console.error("Error fetching notifications:", error);
    }
  };

  useEffect(() => {
    if (isAuthenticated) {
      fetchNotifications();
      const interval = setInterval(fetchNotifications, 30000); // Poll every 30s
      return () => clearInterval(interval);
    } else {
      setNotifications([]);
      setUnreadCount(0);
      setInviteCount(0);
    }
  }, [isAuthenticated]);

  const markAsRead = async (id) => {
    try {
      await apiClient.patch(`/notifications/${id}/read`);
      setNotifications(prev => prev.map(n => n.id === id ? { ...n, is_read: true } : n));
      setUnreadCount(prev => Math.max(0, prev - 1));
    } catch (error) {
      console.error("Error marking notification as read:", error);
    }
  };

  const acceptInvitation = async (token) => {
    const response = await apiClient.post('/invitations/accept', { token });
    await fetchNotifications(); // Refresh badge counts
    return response.data;
  };

  const declineInvitation = async (token) => {
    await apiClient.post('/invitations/decline', { token });
    await fetchNotifications();
  };

  return (
    <NotificationContext.Provider value={{
      notifications,
      unreadCount,
      inviteCount,
      fetchNotifications,
      markAsRead,
      acceptInvitation,
      declineInvitation
    }}>
      {children}
    </NotificationContext.Provider>
  );
};

export const useNotifications = () => useContext(NotificationContext);
