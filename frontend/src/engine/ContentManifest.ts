import { getJson } from '../utils/http';
import { resolveAssetUrl } from '../utils/assets';

export interface ChunkManifestEntry {
  chunk: string;
  version: string;
  status: 'active' | 'retired';
  retired: string[];
}

export interface ContentManifest {
  format: 'alp-content-manifest';
  v: number;
  generated: string;
  total_chunks: number;
  chunks: { [subskillId: string]: ChunkManifestEntry };
}

export class ContentManifestManager {
  private static manifest: ContentManifest | null = null;
  private static retiredItemIds: { [itemId: string]: boolean } = {};
  private static retiredChunks: { [chunkId: string]: boolean } = {};
  private static lastCheckedSession: string | null = null;
  private static isLoaded: boolean = false;

  private static resolveManifestUrl(): string {
    return resolveAssetUrl('content-manifest.json');
  }

  /**
   * Checks the content manifest at most once per session start.
   * If already checked for this sessionId, returns cached manifest without network call.
   */
  public static checkManifestAtSessionStart(sessionId?: string): Promise<ContentManifest | null> {
    var sid = sessionId || 'default_session';
    if (ContentManifestManager.lastCheckedSession === sid && ContentManifestManager.isLoaded) {
      return Promise.resolve(ContentManifestManager.manifest);
    }
    ContentManifestManager.lastCheckedSession = sid;

    var url = ContentManifestManager.resolveManifestUrl();
    return getJson<ContentManifest>(url)
      .then(function (m) {
        if (m && m.format === 'alp-content-manifest' && m.chunks) {
          ContentManifestManager.applyManifest(m);
          try {
            localStorage.setItem('alp_content_manifest_cache', JSON.stringify(m));
          } catch (e) {}
        }
        return ContentManifestManager.manifest;
      })
      .catch(function () {
        // Fallback to cached manifest from localStorage if offline
        if (!ContentManifestManager.manifest) {
          try {
            var raw = localStorage.getItem('alp_content_manifest_cache');
            if (raw) {
              var cached = JSON.parse(raw);
              ContentManifestManager.applyManifest(cached);
            }
          } catch (e) {}
        }
        return ContentManifestManager.manifest;
      });
  }

  /**
   * Applies and indexes a manifest into fast lookup objects.
   */
  public static applyManifest(m: ContentManifest): void {
    ContentManifestManager.manifest = m;
    ContentManifestManager.retiredItemIds = {};
    ContentManifestManager.retiredChunks = {};

    if (m && m.chunks) {
      for (var sub in m.chunks) {
        if (Object.prototype.hasOwnProperty.call(m.chunks, sub)) {
          var entry = m.chunks[sub];
          if (entry.status === 'retired') {
            ContentManifestManager.retiredChunks[sub] = true;
          }
          if (entry.retired && entry.retired.length) {
            for (var i = 0; i < entry.retired.length; i++) {
              ContentManifestManager.retiredItemIds[entry.retired[i]] = true;
            }
          }
        }
      }
    }
    ContentManifestManager.isLoaded = true;
  }

  /** Returns true if the specific item ID is retired. */
  public static isItemRetired(itemId: string): boolean {
    return ContentManifestManager.retiredItemIds[itemId] === true;
  }

  /** Returns true if the entire subskill chunk is retired. */
  public static isChunkRetired(subskillId: string): boolean {
    return ContentManifestManager.retiredChunks[subskillId] === true;
  }

  /** Returns latest version for chunk, or null if unknown. */
  public static getChunkVersion(subskillId: string): string | null {
    if (ContentManifestManager.manifest && ContentManifestManager.manifest.chunks) {
      var entry = ContentManifestManager.manifest.chunks[subskillId];
      if (entry && entry.version) {
        return entry.version;
      }
    }
    return null;
  }

  /**
   * Determines if a chunk needs to be fetched or refreshed.
   * Refreshes chunks only when version changes.
   */
  public static shouldRefreshChunk(subskillId: string, isResident: boolean): boolean {
    if (!isResident) return true;
    var manifestVer = ContentManifestManager.getChunkVersion(subskillId);
    if (!manifestVer) return false;
    var storedVer = localStorage.getItem('alp_chunk_ver_' + subskillId);
    return storedVer !== null && storedVer !== manifestVer;
  }

  /** Mark chunk version as loaded into cache. */
  public static markChunkLoaded(subskillId: string): void {
    var ver = ContentManifestManager.getChunkVersion(subskillId);
    if (ver) {
      localStorage.setItem('alp_chunk_ver_' + subskillId, ver);
    }
  }

  /** Returns cached manifest if any */
  public static getManifest(): ContentManifest | null {
    return ContentManifestManager.manifest;
  }

  /** For tests: reset session state */
  public static resetForTest(): void {
    ContentManifestManager.manifest = null;
    ContentManifestManager.retiredItemIds = {};
    ContentManifestManager.retiredChunks = {};
    ContentManifestManager.lastCheckedSession = null;
    ContentManifestManager.isLoaded = false;
  }
}
