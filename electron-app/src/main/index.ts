import { app, BrowserWindow, ipcMain } from 'electron';
import * as path from 'path';
import { BackendManager } from './backend';

const isDev = process.env.NODE_ENV === 'development' || !app.isPackaged;

let mainWindow: BrowserWindow | null;
let backendManager: BackendManager;

function createWindow(): void {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1200,
    minHeight: 700,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, '../preload/index.js'),
    },
    show: false,
    backgroundColor: '#ffffff',
  });

  const startUrl = isDev
    ? 'http://localhost:5173'
    : `file://${path.join(__dirname, '../../dist/renderer/index.html')}`;

  mainWindow.loadURL(startUrl);

  mainWindow.once('ready-to-show', () => {
    mainWindow?.show();
  });

  if (isDev) {
    mainWindow.webContents.openDevTools();
  }

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

app.whenReady().then(async () => {
  backendManager = new BackendManager();
  
  try {
    await backendManager.start();
  } catch (error) {
    console.error('Failed to start backend:', error);
  }

  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('before-quit', async () => {
  if (backendManager) {
    await backendManager.stop();
  }
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

// IPC handlers
ipcMain.handle('get-backend-url', (): string | null => {
  return backendManager ? backendManager.getUrl() : null;
});

ipcMain.handle('backend-status', (): boolean => {
  return backendManager ? backendManager.isRunning() : false;
});

ipcMain.handle('api-request', async (_event, endpoint: string, options?: RequestInit) => {
  if (!backendManager || !backendManager.isRunning()) {
    throw new Error('Backend is not running');
  }
  
  const baseUrl = backendManager.getUrl();
  const url = `${baseUrl}${endpoint}`;
  
  try {
    const response = await fetch(url, options);
    const contentType = response.headers.get('content-type');
    
    if (contentType && contentType.includes('application/json')) {
      return await response.json();
    }
    
    return await response.text();
  } catch (error) {
    console.error('API request failed:', error);
    throw error;
  }
});
