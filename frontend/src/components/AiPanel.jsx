import React, { useState, useEffect } from 'react';
import apiClient from '../api/client';
import Button from './ui/Button';
import { Bot, Loader2, Plus, X, AlertTriangle, Info, AlertCircle, RefreshCw, Sparkles } from 'lucide-react';
import './AiPanel.css';

const AiPanel = ({ isOpen, onClose, onAddTask, projectId, tasks }) => {
  const [analysis, setAnalysis] = useState(null);
  const [loadingAnalysis, setLoadingAnalysis] = useState(false);
  const [errorAnalysis, setErrorAnalysis] = useState(null);



  // Estados para la sección secundaria (generación de tareas)
  const [inputText, setInputText] = useState('');
  const [loadingGen, setLoadingGen] = useState(false);
  const [generatedTasks, setGeneratedTasks] = useState([]);
  const [showGenSection, setShowGenSection] = useState(false);

  // Ejecutar el análisis cuando el panel se abre o cuando cambian las tareas
  useEffect(() => {
    if (isOpen) {
      fetchAnalysis();
    }
  }, [isOpen, tasks]);

  const fetchAnalysis = async () => {
    setLoadingAnalysis(true);
    setErrorAnalysis(null);
    try {
      // El backend ahora recibe el project_id y hace la consulta directamente a la base de datos
      const payload = { project_id: projectId };
      console.log("PAYLOAD ENVIADO AL BACKEND:", payload);
      
      // NOTA: Se elimina el slash inicial para evitar que Axios sobreescriba la baseURL
      const response = await apiClient.post('ai/analyze', payload);
      setAnalysis(response.data);
    } catch (error) {
      console.error("Error analyzing board:", error);
      setErrorAnalysis("No se pudo completar el análisis del tablero.");
    } finally {
      setLoadingAnalysis(false);
    }
  };

  const handleGenerateTasks = async () => {
    if (!inputText.trim()) return;
    setLoadingGen(true);
    setGeneratedTasks([]);
    try {
      // Usamos el endpoint correcto para generar tareas (sin slash inicial)
      const response = await apiClient.post('ai/generate-tasks', { text: inputText });
      setGeneratedTasks(response.data.tasks || []);
    } catch (error) {
      console.error("Error generating tasks:", error);
      alert("Hubo un error al generar tareas con la IA.");
    } finally {
      setLoadingGen(false);
    }
  };

  if (!isOpen) return null;

  const renderRiskBadge = (level) => {
    const riskMap = {
      low: { label: 'Bajo', color: 'var(--success)', bg: 'rgba(16, 185, 129, 0.1)' },
      medium: { label: 'Medio', color: 'var(--warning)', bg: 'rgba(245, 158, 11, 0.1)' },
      high: { label: 'Alto', color: 'var(--danger)', bg: 'rgba(239, 68, 68, 0.1)' },
    };
    const risk = riskMap[level?.toLowerCase()] || riskMap.low;
    return (
      <span style={{ backgroundColor: risk.bg, color: risk.color, padding: '4px 10px', borderRadius: '12px', fontWeight: 600, fontSize: '0.8rem' }}>
        Riesgo {risk.label}
      </span>
    );
  };

  const renderAlertIcon = (type) => {
    switch (type) {
      case 'danger': return <AlertTriangle size={16} color="var(--danger)" />;
      case 'warning': return <AlertCircle size={16} color="var(--warning)" />;
      default: return <Info size={16} color="var(--primary)" />;
    }
  };

  return (
    <div className="ai-panel">
      <div className="ai-header">
        <div className="ai-title">
          <Bot size={20} color="var(--primary)" />
          <h3>Scrum Master IA</h3>
        </div>
        <button className="btn-icon" onClick={onClose}>
          <X size={18} />
        </button>
      </div>

      <div className="ai-body">
        {/* --- SECCIÓN PRINCIPAL: DIAGNÓSTICO --- */}
        <div className="ai-diagnostic-section">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <h4 style={{ margin: 0, fontSize: '1rem', color: 'var(--text-main)' }}>Diagnóstico del Tablero</h4>
            <button className="btn-icon" onClick={fetchAnalysis} title="Actualizar análisis">
              <RefreshCw size={14} className={loadingAnalysis ? "animate-spin" : ""} />
            </button>
          </div>

          {loadingAnalysis ? (
            <div style={{ display: 'flex', justifyContent: 'center', padding: '2rem 0' }}>
              <Loader2 className="animate-spin" size={24} color="var(--primary)" />
            </div>
          ) : errorAnalysis ? (
            <div style={{ color: 'var(--danger)', fontSize: '0.875rem' }}>{errorAnalysis}</div>
          ) : analysis ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.2rem' }}>

              {/* Nivel de Riesgo */}
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <span style={{ fontSize: '0.875rem', fontWeight: 500 }}>Nivel de Riesgo:</span>
                {renderRiskBadge(analysis.risk_level)}
              </div>

              {/* Resumen */}
              {analysis.summary && (
                <div style={{ background: 'var(--bg-main)', padding: '0.75rem', borderRadius: '0.5rem', fontSize: '0.85rem', color: 'var(--text-main)', border: '1px solid var(--border)' }}>
                  <p style={{ margin: 0, lineHeight: 1.5 }}>{analysis.summary}</p>
                </div>
              )}

              {/* Alertas */}
              {analysis.alerts && analysis.alerts.length > 0 && (
                <div>
                  <h5 style={{ fontSize: '0.85rem', marginBottom: '0.5rem', color: 'var(--text-muted)' }}>Alertas Detectadas</h5>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                    {analysis.alerts.map((alert, idx) => (
                      <div key={idx} style={{ display: 'flex', gap: '0.5rem', alignItems: 'flex-start', background: 'var(--bg-main)', padding: '0.5rem', borderRadius: '0.375rem', border: '1px solid var(--border)' }}>
                        <div style={{ marginTop: '2px' }}>{renderAlertIcon(alert.type)}</div>
                        <span style={{ fontSize: '0.8rem', lineHeight: 1.4 }}>{alert.message}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Recomendaciones */}
              {analysis.recommendations && analysis.recommendations.length > 0 && (
                <div>
                  <h5 style={{ fontSize: '0.85rem', marginBottom: '0.5rem', color: 'var(--text-muted)' }}>Recomendaciones</h5>
                  <ul style={{ margin: 0, paddingLeft: '1.2rem', fontSize: '0.8rem', color: 'var(--text-main)', display: 'flex', flexDirection: 'column', gap: '0.3rem' }}>
                    {analysis.recommendations.map((rec, idx) => (
                      <li key={idx} style={{ lineHeight: 1.4 }}>{rec}</li>
                    ))}
                  </ul>
                </div>
              )}

            </div>
          ) : null}
        </div>

        <hr style={{ border: 'none', borderTop: '1px solid var(--border)', margin: '0.5rem 0' }} />

        {/* --- SECCIÓN SECUNDARIA: GENERADOR DE TAREAS --- */}
        <div className="ai-generator-section">
          <button
            style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', width: '100%', background: 'none', border: 'none', color: 'var(--primary)', fontWeight: 500, cursor: 'pointer', padding: '0.5rem 0' }}
            onClick={() => setShowGenSection(!showGenSection)}
          >
            <Sparkles size={16} />
            {showGenSection ? 'Ocultar Generador de Tareas' : 'Generar Tareas con IA'}
          </button>

          {showGenSection && (
            <div className="ai-input-group" style={{ marginTop: '0.5rem' }}>
              <label>Describe el requerimiento a desglosar:</label>
              <textarea
                value={inputText}
                onChange={e => setInputText(e.target.value)}
                placeholder="Ej: Necesito un sistema de login con Google..."
                rows={3}
              />
              <Button
                className="btn-primary w-full"
                onClick={handleGenerateTasks}
                disabled={loadingGen || !inputText.trim()}
              >
                {loadingGen ? <Loader2 className="animate-spin" size={16} /> : 'Generar Tareas'}
              </Button>
            </div>
          )}

          {showGenSection && generatedTasks.length > 0 && (
            <div className="ai-suggestions" style={{ marginTop: '1.5rem' }}>
              <h4>Tareas Generadas:</h4>
              <div className="suggestions-list">
                {generatedTasks.map((sug, index) => (
                  <div key={index} className="suggestion-card">
                    <div className="suggestion-content">
                      <h5>{sug.title}</h5>
                      <p>{sug.description}</p>
                      <span className={`priority-badge ${sug.priority}`}>
                        {sug.priority === 'high' ? 'Alta' : sug.priority === 'medium' ? 'Media' : 'Baja'}
                      </span>
                    </div>
                    <button
                      className="btn-add-suggestion"
                      onClick={() => onAddTask(sug)}
                      title="Añadir como nueva tarea"
                    >
                      <Plus size={16} />
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AiPanel;
