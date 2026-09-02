// WebSQL wrapper for legacy iOS 9.3.5 support
// Handles storing and retrieving session bundles offline.

export class WebSQLEngine {
  private db: any = null;

  constructor(dbName: string = 'ALP_Magical_Kingdom', version: string = '1.0', description: string = 'Offline Session Bundles', size: number = 5 * 1024 * 1024) {
    if ((window as any).openDatabase) {
      this.db = (window as any).openDatabase(dbName, version, description, size);
      this.initSchema();
    } else {
      console.warn('WebSQL is not supported in this browser. Falling back to LocalStorage (not implemented yet).');
    }
  }

  private initSchema() {
    if (!this.db) return;
    this.db.transaction((tx: any) => {
      tx.executeSql(
        'CREATE TABLE IF NOT EXISTS session_bundles (id TEXT UNIQUE, profile_id TEXT, data TEXT)',
        [],
        () => console.log('Schema initialized: session_bundles'),
        (_tx: any, err: any) => console.error('Error creating table:', err)
      );
    });
  }

  public saveBundle(bundleId: string, profileId: string, data: any): Promise<void> {
    return new Promise((resolve, reject) => {
      if (!this.db) return reject(new Error('No WebSQL DB'));
      const dataStr = JSON.stringify(data);
      this.db.transaction((tx: any) => {
        tx.executeSql(
          'REPLACE INTO session_bundles (id, profile_id, data) VALUES (?, ?, ?)',
          [bundleId, profileId, dataStr],
          () => resolve(),
          (_tx: any, err: any) => reject(err)
        );
      });
    });
  }

  public getBundle(bundleId: string, profileId: string): Promise<any> {
    return new Promise((resolve, reject) => {
      if (!this.db) return reject(new Error('No WebSQL DB'));
      this.db.transaction((tx: any) => {
        tx.executeSql(
          'SELECT data FROM session_bundles WHERE id = ? AND profile_id = ?',
          [bundleId, profileId],
          (_tx: any, results: any) => {
            if (results.rows.length > 0) {
              try {
                resolve(JSON.parse(results.rows.item(0).data));
              } catch (e) {
                reject(e);
              }
            } else {
              resolve(null);
            }
          },
          (_tx: any, err: any) => reject(err)
        );
      });
    });
  }
}
