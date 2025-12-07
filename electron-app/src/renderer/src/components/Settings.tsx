import React, { useState } from 'react';
import { SettingsData } from '../types/api';

interface SettingsProps {
  settings: SettingsData;
  onUpdate: () => void;
}

const Settings: React.FC<SettingsProps> = ({ settings, onUpdate }) => {
  const [defaultEngine, setDefaultEngine] = useState(settings.ocr.default_engine);
  const [useGpu, setUseGpu] = useState(settings.ocr.use_gpu);
  const [saving, setSaving] = useState(false);

  const handleSave = async () => {
    setSaving(true);
    try {
      const response = await fetch('http://localhost:8000/api/v1/settings', {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          default_ocr_engine: defaultEngine,
          ocr_gpu: useGpu
        })
      });
      
      if (response.ok) {
        const result = await response.json();
        alert(`Настройки сохранены. ${result.requires_restart.length > 0 ? 'Требуется перезапуск.' : ''}`);
        onUpdate();
      }
    } catch (error) {
      console.error('Save failed:', error);
      alert('Ошибка сохранения настроек');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="settings">
      <h2>⚙️ Настройки</h2>
      
      <div className="settings-section">
        <h3>OCR движок</h3>
        
        <div className="setting-item">
          <label>Движок по умолчанию:</label>
          <select
            value={defaultEngine}
            onChange={(e) => setDefaultEngine(e.target.value)}
          >
            {settings.ocr.allowed_engines.map((engine) => (
              <option key={engine} value={engine}>
                {engine === 'paddleocr' ? 'PaddleOCR' : 'EasyOCR'}
              </option>
            ))}
          </select>
        </div>

        <div className="setting-item">
          <label>
            <input
              type="checkbox"
              checked={useGpu}
              onChange={(e) => setUseGpu(e.target.checked)}
            />
            Использовать GPU
          </label>
        </div>

        <div className="setting-info">
          <h4>Доступные языки:</h4>
          <p>{settings.ocr.languages.join(', ')}</p>
          
          <h4>Параметры:</h4>
          <p>Макс. одновременных задач: {settings.ocr.max_concurrent}</p>
          <p>Порог уверенности: {(settings.ocr.confidence_threshold * 100).toFixed(0)}%</p>
          <p>DPI для PDF: {settings.files.pdf_dpi}</p>
        </div>
      </div>

      <div className="settings-section">
        <h3>Пути</h3>
        <div className="path-info">
          <p><strong>Папка отслеживания:</strong> {settings.paths.watch_folder}</p>
          <p><strong>База данных:</strong> {settings.paths.database_path}</p>
          <p><strong>Логи:</strong> {settings.paths.logs_dir}</p>
        </div>
      </div>

      <button
        onClick={handleSave}
        disabled={saving}
        className="btn-save"
      >
        {saving ? '⏳ Сохранение...' : '💾 Сохранить настройки'}
      </button>
    </div>
  );
};

export default Settings;
