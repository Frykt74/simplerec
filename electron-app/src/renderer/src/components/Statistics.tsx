import React from 'react';
import { Stats } from '../types/api';

interface StatisticsProps {
  stats: Stats;
}

const Statistics: React.FC<StatisticsProps> = ({ stats }) => {
  return (
    <div className="statistics">
      <h2>Статистика системы</h2>
      
      <div className="stats-grid">
        <div className="stat-card">
          <h3>📁 Файлы</h3>
          <div className="stat-value">{stats.files.total}</div>
          <div className="stat-details">
            <p>Обработано: {stats.files.processed}</p>
            <p>Ожидают: {stats.files.pending}</p>
            <p>В папке отслеживания: {stats.files.in_watch_folder}</p>
          </div>
        </div>

        <div className="stat-card">
          <h3>📄 Документы</h3>
          <div className="stat-value">{stats.documents.total}</div>
          <div className="stat-details">
            <p>Средняя уверенность: {(stats.documents.avg_confidence * 100).toFixed(1)}%</p>
          </div>
        </div>

        <div className="stat-card">
          <h3>⏱️ Обработка</h3>
          <div className="stat-value">
            {stats.processing.avg_time_per_doc.toFixed(1)}s
          </div>
          <div className="stat-details">
            <p>Среднее время на документ</p>
            <p>Всего: {stats.processing.total_time_seconds.toFixed(0)}s</p>
          </div>
        </div>

        <div className="stat-card">
          <h3>💾 Хранилище</h3>
          <div className="stat-value">{stats.storage.database_size_mb} MB</div>
          <div className="stat-details">
            <p>Размер базы данных</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Statistics;
