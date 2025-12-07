import React, { useState, useEffect } from 'react';
import FileList from './components/FileList';
import UploadZone from './components/UploadZone';
import Statistics from './components/Statistics';
import Settings from './components/Settings';
import Search from './components/Search';
import { FileItem, Stats, SettingsData } from './types/api';

type Tab = 'files' | 'search' | 'stats' | 'settings';

const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<Tab>('files');
  const [files, setFiles] = useState<FileItem[]>([]);
  const [stats, setStats] = useState<Stats | null>(null);
  const [settings, setSettings] = useState<SettingsData | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadFiles();
    loadStats();
    loadSettings();
    
    const interval = setInterval(() => {
      loadFiles();
      loadStats();
    }, 5000);
    
    return () => clearInterval(interval);
  }, []);

  const loadFiles = async () => {
    try {
      const data = await window.electron.apiRequest('/api/v1/files');
      setFiles(data);
    } catch (error) {
      console.error('Failed to load files:', error);
    }
  };

  const loadStats = async () => {
    try {
      const data = await window.electron.apiRequest('/api/v1/stats');
      setStats(data);
    } catch (error) {
      console.error('Failed to load stats:', error);
    }
  };

  const loadSettings = async () => {
    try {
      const data = await window.electron.apiRequest('/api/v1/settings');
      setSettings(data);
    } catch (error) {
      console.error('Failed to load settings:', error);
    }
  };

  const handleUploadSuccess = () => {
    loadFiles();
    loadStats();
  };

  const handleProcessFile = async (fileId: number, engine: string, mode: string) => {
    setLoading(true);
    try {
      await window.electron.apiRequest(
        `/api/v1/ocr/process/${fileId}?engine=${engine}&mode=${mode}`,
        { method: 'POST' }
      );
      
      await loadFiles();
      await loadStats();
      alert('Файл успешно обработан!');
    } catch (error) {
      console.error('Processing failed:', error);
      alert('Ошибка обработки файла');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteFile = async (fileId: number) => {
    if (!confirm('Удалить файл?')) return;
    
    try {
      await window.electron.apiRequest(`/api/v1/files/${fileId}`, {
        method: 'DELETE'
      });
      loadFiles();
      loadStats();
    } catch (error) {
      console.error('Delete failed:', error);
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>🔍 SimpleRec</h1>
        <p>Распознавание документов с EasyOCR и PaddleOCR</p>
      </header>

      <nav className="app-nav">
        <button
          className={activeTab === 'files' ? 'active' : ''}
          onClick={() => setActiveTab('files')}
        >
          📁 Файлы
        </button>
        <button
          className={activeTab === 'search' ? 'active' : ''}
          onClick={() => setActiveTab('search')}
        >
          🔎 Поиск
        </button>
        <button
          className={activeTab === 'stats' ? 'active' : ''}
          onClick={() => setActiveTab('stats')}
        >
          📊 Статистика
        </button>
        <button
          className={activeTab === 'settings' ? 'active' : ''}
          onClick={() => setActiveTab('settings')}
        >
          ⚙️ Настройки
        </button>
      </nav>

      <main className="app-content">
        {activeTab === 'files' && (
          <>
            <UploadZone onUploadSuccess={handleUploadSuccess} />
            <FileList
              files={files}
              onProcess={handleProcessFile}
              onDelete={handleDeleteFile}
              loading={loading}
            />
          </>
        )}
        
        {activeTab === 'search' && <Search />}
        
        {activeTab === 'stats' && stats && <Statistics stats={stats} />}
        
        {activeTab === 'settings' && settings && (
          <Settings settings={settings} onUpdate={loadSettings} />
        )}
      </main>
    </div>
  );
};

export default App;
