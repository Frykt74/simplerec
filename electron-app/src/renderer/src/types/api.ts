export interface FileItem {
  id: number;
  filename: string;
  filepath: string;
  file_hash: string;
  file_size: number;
  mime_type: string;
  is_processed: boolean;
  ocr_mode: string | null;
  created_at: string;
}

export interface SearchResult {
  document_id: number;
  filename: string;
  snippet: string;
  rank: number;
}

export interface Stats {
  files: {
    total: number;
    processed: number;
    pending: number;
    in_watch_folder: number;
  };
  documents: {
    total: number;
    avg_confidence: number;
  };
  processing: {
    total_time_seconds: number;
    avg_time_per_doc: number;
  };
  storage: {
    database_size_mb: number;
    database_path: string;
  };
}

export interface SettingsData {
  app_name: string;
  app_version: string;
  ocr: {
    default_engine: string;
    languages: string[];
    use_gpu: boolean;
    max_concurrent: number;
    confidence_threshold: number;
    allowed_engines: string[];
  };
  files: {
    supported_formats: string[];
    max_file_size_mb: number;
    pdf_dpi: number;
  };
  paths: {
    watch_folder: string;
    processed_folder: string;
    database_path: string;
    cache_dir: string;
    logs_dir: string;
  };
  server: {
    host: string;
    port: number;
  };
}
