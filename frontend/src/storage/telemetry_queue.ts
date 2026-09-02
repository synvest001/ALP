// Telemetry queue that stores events offline and flushes when online
// Target endpoint: Google Apps Script Web App

export class TelemetryQueue {
  private db: any = null;
  private endpointUrl: string = 'https://script.google.com/macros/s/AKfycbz_YOUR_SCRIPT_ID/exec'; // Placeholder

  constructor() {
    if ((window as any).openDatabase) {
      this.db = (window as any).openDatabase('ALP_Magical_Kingdom_Telemetry', '1.0', 'Offline Telemetry', 2 * 1024 * 1024);
      this.initSchema();
      this.setupNetworkListeners();
    }
  }

  private initSchema() {
    if (!this.db) return;
    this.db.transaction((tx: any) => {
      tx.executeSql(
        'CREATE TABLE IF NOT EXISTS telemetry_queue (id INTEGER PRIMARY KEY AUTOINCREMENT, payload TEXT)',
        [],
        () => console.log('Schema initialized: telemetry_queue'),
        (_tx: any, err: any) => console.error('Error creating telemetry table:', err)
      );
    });
  }

  private setupNetworkListeners() {
    window.addEventListener('online', () => {
      console.log('Network online. Attempting to flush telemetry queue.');
      this.flushQueue();
    });
  }

  public trackEvent(eventName: string, data: any) {
    const payload = {
      event: eventName,
      data: data,
      timestamp: new Date().toISOString()
    };
    
    // Always store locally first
    this.storeLocally(payload).then(() => {
      // If online, immediately try to flush
      if (navigator.onLine) {
        this.flushQueue();
      }
    });
  }

  private storeLocally(payload: any): Promise<void> {
    return new Promise((resolve, reject) => {
      if (!this.db) return reject(new Error('No WebSQL DB'));
      const dataStr = JSON.stringify(payload);
      this.db.transaction((tx: any) => {
        tx.executeSql(
          'INSERT INTO telemetry_queue (payload) VALUES (?)',
          [dataStr],
          () => resolve(),
          (_tx: any, err: any) => reject(err)
        );
      });
    });
  }

  public flushQueue() {
    if (!this.db || !navigator.onLine) return;

    this.db.transaction((tx: any) => {
      tx.executeSql('SELECT * FROM telemetry_queue', [], (_tx: any, results: any) => {
        const events: any[] = [];
        const ids: number[] = [];
        for (let i = 0; i < results.rows.length; i++) {
          const row = results.rows.item(i);
          events.push(JSON.parse(row.payload));
          ids.push(row.id);
        }

        if (events.length > 0) {
          this.sendToServer(events).then(() => {
            this.clearFlushedEvents(ids);
          }).catch(err => {
            console.error('Failed to flush telemetry:', err);
          });
        }
      });
    });
  }

  private sendToServer(events: any[]): Promise<void> {
    return fetch(this.endpointUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(events)
    }).then(res => {
      if (!res.ok) throw new Error('Network response was not ok');
    });
  }

  private clearFlushedEvents(ids: number[]) {
    if (!this.db || ids.length === 0) return;
    const placeholders = ids.map(() => '?').join(',');
    this.db.transaction((tx: any) => {
      tx.executeSql(`DELETE FROM telemetry_queue WHERE id IN (${placeholders})`, ids, () => {
        console.log(`Cleared ${ids.length} flushed events.`);
      });
    });
  }
}
