import { contextBridge, ipcRenderer } from 'electron';

export interface ElectronAPI {
  getBackendUrl: () => Promise<string | null>;
  backendStatus: () => Promise<boolean>;
  apiRequest: (endpoint: string, options?: RequestInit) => Promise<any>;
}

contextBridge.exposeInMainWorld('electron', {
  getBackendUrl: () => ipcRenderer.invoke('get-backend-url'),
  backendStatus: () => ipcRenderer.invoke('backend-status'),
  apiRequest: (endpoint: string, options?: RequestInit) => 
    ipcRenderer.invoke('api-request', endpoint, options),
} as ElectronAPI);
