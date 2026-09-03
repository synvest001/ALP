export class SyncEngine {
  private endpointUrl: string = 'https://script.google.com/macros/s/AKfycbwYOUR_SCRIPT_ID/exec'; // Replace with deployed GAS URL

  public async sync(): Promise<boolean> {
    const profileId = localStorage.getItem('alp_current_profile') || 'default_user';
    const localNodes = parseInt(localStorage.getItem('alp_nodes_completed') || '0', 10);
    const localStars = parseInt(localStorage.getItem('alp_stars') || '0', 10);

    const payload = {
      action: 'SYNC_PROGRESS',
      profileId: profileId,
      nodesCompleted: localNodes,
      stars: localStars,
      timestamp: new Date().toISOString()
    };

    console.log('[SyncEngine] Pushing payload:', payload);

    try {
      // In local dev without a real endpoint, we'll simulate a network request if the URL is a placeholder
      if (this.endpointUrl.includes('YOUR_SCRIPT_ID')) {
        console.warn('[SyncEngine] No real endpoint configured. Simulating successful sync.');
        await new Promise(resolve => setTimeout(resolve, 1000));
        return true;
      }

      const response = await fetch(this.endpointUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'text/plain;charset=utf-8', // GAS requires plain text for simple CORS
        },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log('[SyncEngine] Server responded:', data);

      if (data.status === 'success') {
        const serverNodes = parseInt(data.syncedNodes, 10);
        const serverStars = parseInt(data.syncedStars, 10);

        // Apply Server Truth (which has already applied Math.max conflict resolution)
        if (!isNaN(serverNodes) && serverNodes > localNodes) {
          console.log(`[SyncEngine] Overwriting local nodes (${localNodes}) with server nodes (${serverNodes})`);
          localStorage.setItem('alp_nodes_completed', serverNodes.toString());
        }

        if (!isNaN(serverStars) && serverStars > localStars) {
          console.log(`[SyncEngine] Overwriting local stars (${localStars}) with server stars (${serverStars})`);
          localStorage.setItem('alp_stars', serverStars.toString());
        }
        
        return true;
      } else {
        console.error('[SyncEngine] Sync failed:', data.message);
        return false;
      }
    } catch (e) {
      console.error('[SyncEngine] Network error during sync:', e);
      return false;
    }
  }
}
