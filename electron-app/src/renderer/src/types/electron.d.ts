export interface ElectronAPI {
  getBackendUrl: () => Promise<string | null>;
  backendStatus: () => Promise<boolean>;
  apiRequest: (endpoint: string, options?: RequestInit) => Promise<any>;
}

declare global {
  interface Window {
    electron: ElectronAPI;
  }
}
