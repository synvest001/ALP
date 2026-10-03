export function getJson<T = any>(url: string): Promise<T> {
  return new Promise<T>(function (resolve, reject) {
    try {
      const xhr = new XMLHttpRequest();
      xhr.open('GET', url, true);
      xhr.onload = function () {
        if (xhr.status < 200 || xhr.status >= 300) {
          reject(new Error('HTTP ' + xhr.status));
          return;
        }
        try {
          resolve(JSON.parse(xhr.responseText) as T);
        } catch (e: any) {
          reject(new Error('JSON parse failed: ' + (e && e.message ? e.message : e)));
        }
      };
      xhr.onerror = function () { reject(new Error('Network error')); };
      xhr.ontimeout = function () { reject(new Error('Timeout')); };
      xhr.send();
    } catch (e: any) {
      reject(new Error(String(e && e.message ? e.message : e)));
    }
  });
}
