import React, { useState } from 'react';
import { FileItem } from '../types/api';

interface FileListProps {
  files: FileItem[];
  onProcess: (fileId: number, engine: string, mode: string) => void;
  onDelete: (fileId: number) => void;
  loading: boolean;
}

const FileList: React.FC<FileListProps> = ({ files, onProcess, onDelete, loading }) => {
  const [selectedFile, setSelectedFile] = useState<number | null>(null);
  const [engine, setEngine] = useState<string>('paddleocr');
  const [mode, setMode] = useState<string>('printed');

  const handleProcess = (fileId: number) => {
    onProcess(fileId, engine, mode);
    setSelectedFile(null);
  };

  return (
    <div className="file-list">
      <h2>Список файлов ({files.length})</h2>
      
      {files.length === 0 ? (
        <div className="empty-state">
          <p>Файлов пока нет. Загрузите файлы для обработки.</p>
        </div>
      ) : (
        <table className="files-table">
          <thead>
            <tr>
              <th>Файл</th>
              <th>Размер</th>
              <th>Статус</th>
              <th>Режим OCR</th>
              <th>Дата</th>
              <th>Действия</th>
            </tr>
          </thead>
          <tbody>
            {files.map((file) => (
              <tr key={file.id} className={file.is_processed ? 'processed' : 'pending'}>
                <td className="filename">{file.filename}</td>
                <td>{(file.file_size / 1024).toFixed(1)} KB</td>
                <td>
                  <span className={`status-badge ${file.is_processed ? 'success' : 'pending'}`}>
                    {file.is_processed ? '✓ Обработан' : '⏳ Ожидает'}
                  </span>
                </td>
                <td>{file.ocr_mode || '-'}</td>
                <td>{new Date(file.created_at).toLocaleString('ru-RU')}</td>
                <td className="actions">
                  {!file.is_processed ? (
                    <>
                      {selectedFile === file.id ? (
                        <div className="process-controls">
                          <select
                            value={engine}
                            onChange={(e) => setEngine(e.target.value)}
                            disabled={loading}
                          >
                            <option value="paddleocr">PaddleOCR</option>
                            <option value="easyocr">EasyOCR</option>
                            <option value="auto">Авто</option>
                          </select>
                          
                          <select
                            value={mode}
                            onChange={(e) => setMode(e.target.value)}
                            disabled={loading}
                          >
                            <option value="printed">Печатный</option>
                            <option value="handwritten">Рукописный</option>
                            <option value="auto">Авто</option>
                          </select>
                          
                          <button
                            onClick={() => handleProcess(file.id)}
                            disabled={loading}
                            className="btn-process"
                          >
                            {loading ? '⏳' : '▶️'} Старт
                          </button>
                          
                          <button
                            onClick={() => setSelectedFile(null)}
                            disabled={loading}
                            className="btn-cancel"
                          >
                            ✕
                          </button>
                        </div>
                      ) : (
                        <button
                          onClick={() => setSelectedFile(file.id)}
                          className="btn-configure"
                        >
                          ⚙️ Обработать
                        </button>
                      )}
                    </>
                  ) : (
                    <button
                      onClick={() => window.open(`http://localhost:8000/api/v1/documents/${file.id}`, '_blank')}
                      className="btn-view"
                    >
                      👁️ Просмотр
                    </button>
                  )}
                  
                  <button
                    onClick={() => onDelete(file.id)}
                    className="btn-delete"
                    disabled={loading}
                  >
                    🗑️
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};

export default FileList;
