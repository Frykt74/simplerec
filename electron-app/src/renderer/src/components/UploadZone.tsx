import React, { useState, useRef } from 'react';

interface UploadZoneProps {
  onUploadSuccess: () => void;
}

const UploadZone: React.FC<UploadZoneProps> = ({ onUploadSuccess }) => {
  const [isDragging, setIsDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = async (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    
    const files = Array.from(e.dataTransfer.files);
    await uploadFiles(files);
  };

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files) return;
    const files = Array.from(e.target.files);
    await uploadFiles(files);
  };

  const uploadFiles = async (files: File[]) => {
    setUploading(true);
    
    for (const file of files) {
      const formData = new FormData();
      formData.append('file', file);
      
      try {
        const response = await fetch('http://localhost:8000/api/v1/upload', {
          method: 'POST',
          body: formData
        });
        
        if (response.ok) {
          console.log(`Uploaded: ${file.name}`);
        } else {
          const error = await response.json();
          alert(`Ошибка загрузки ${file.name}: ${error.detail}`);
        }
      } catch (error) {
        console.error(`Upload failed for ${file.name}:`, error);
        alert(`Ошибка загрузки ${file.name}`);
      }
    }
    
    setUploading(false);
    onUploadSuccess();
    
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div
      className={`upload-zone ${isDragging ? 'dragging' : ''} ${uploading ? 'uploading' : ''}`}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      onClick={() => fileInputRef.current?.click()}
    >
      <input
        ref={fileInputRef}
        type="file"
        multiple
        accept=".pdf"
        onChange={handleFileSelect}
        style={{ display: 'none' }}
      />
      
      {uploading ? (
        <>
          <div className="spinner"></div>
          <p>Загрузка файлов...</p>
        </>
      ) : (
        <>
          <div className="upload-icon">📤</div>
          <h3>Перетащите PDF файлы сюда</h3>
          <p>или нажмите для выбора файлов</p>
        </>
      )}
    </div>
  );
};

export default UploadZone;
