import { spawn, ChildProcess } from 'child_process';
import * as path from 'path';
import axios from 'axios';

export class BackendManager {
  private process: ChildProcess | null = null;
  private readonly port: number = 8000;
  private readonly host: string = '127.0.0.1';
  private readonly baseUrl: string;

  constructor() {
    this.baseUrl = `http://${this.host}:${this.port}`;
  }

  async start(): Promise<void> {
    console.log('Starting Python backend...');

    const backendPath = path.join(__dirname, '../../../python-backend');
    const pythonExe = path.join(backendPath, '.venv/Scripts/python.exe');

    console.log('Backend path:', backendPath);
    console.log('Python exe:', pythonExe);

    this.process = spawn(
      pythonExe,
      ['-m', 'uvicorn', 'app.main:app', '--host', this.host, '--port', this.port.toString()],
      {
        cwd: backendPath,
        stdio: 'pipe',
      }
    );

    this.process.stdout?.on('data', (data: Buffer) => {
      console.log(`[Backend] ${data.toString()}`);
    });

    this.process.stderr?.on('data', (data: Buffer) => {
      console.error(`[Backend Error] ${data.toString()}`);
    });

    this.process.on('close', (code: number | null) => {
      console.log(`Backend process exited with code ${code}`);
    });

    await this.waitForBackend();
    console.log('Backend is ready!');
  }

  private async waitForBackend(maxAttempts: number = 30, delay: number = 1000): Promise<boolean> {
    for (let i = 0; i < maxAttempts; i++) {
      try {
        const response = await axios.get(`${this.baseUrl}/api/v1/health`, { timeout: 1000 });
        if (response.data.status === 'ok') {
          return true;
        }
      } catch {
        // Backend not ready yet
      }
      await new Promise((resolve) => setTimeout(resolve, delay));
    }
    throw new Error('Backend failed to start');
  }

  async stop(): Promise<void> {
    if (this.process) {
      console.log('Stopping backend...');
      this.process.kill('SIGTERM');
      this.process = null;
    }
  }

  isRunning(): boolean {
    return this.process !== null;
  }

  getUrl(): string {
    return this.baseUrl;
  }
}
