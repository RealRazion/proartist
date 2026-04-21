/**
 * API Error Handler Service
 * Zentrale Fehlerbehandlung für alle API-Anfragen
 */

export class ApiErrorHandler {
  constructor(options = {}) {
    this.debounceMs = options.debounceMs || 1200;
    this.maxRetries = options.maxRetries || 2;
    this.retryableStatuses = options.retryableStatuses || [408, 429, 500, 502, 503, 504];
    this.onErrorCallback = options.onErrorCallback || null;
  }

  /**
   * Extrahiert eine benutzerfreundliche Fehlermeldung aus der API-Antwort
   */
  extractMessage(error) {
    if (!error) return 'Ein unbekannter Fehler ist aufgetreten';

    // Error response mit detail/message
    if (error.response?.data) {
      const data = error.response.data;
      
      // Detail array (Validierungsfehler)
      if (Array.isArray(data.detail)) {
        return data.detail.map(d => d.msg || d).join(', ');
      }
      
      // Detail string
      if (typeof data.detail === 'string') {
        return data.detail;
      }
      
      // Message field
      if (typeof data.message === 'string') {
        return data.message;
      }

      // Custom error messages
      if (data.error) {
        return typeof data.error === 'string' ? data.error : JSON.stringify(data.error);
      }

      // Field-spezifische Fehler (z.B. Validation)
      if (typeof data === 'object') {
        const messages = Object.entries(data)
          .map(([key, value]) => {
            if (Array.isArray(value)) return value.join(', ');
            if (typeof value === 'object') return JSON.stringify(value);
            return `${key}: ${value}`;
          })
          .filter(m => m && !m.includes('undefined'));
        
        if (messages.length > 0) {
          return messages.join(' | ');
        }
      }
    }

    // HTTP Status Codes
    if (error.response?.status) {
      const status = error.response.status;
      const statusMessages = {
        400: 'Ungültige Anfrage',
        401: 'Authentifizierung erforderlich',
        403: 'Zugriff verweigert',
        404: 'Ressource nicht gefunden',
        409: 'Konflikt bei der Datenänderung',
        422: 'Validierungsfehler',
        429: 'Zu viele Anfragen - bitte später versuchen',
        500: 'Serverfehler',
        503: 'Service nicht verfügbar',
      };
      return statusMessages[status] || `Fehler ${status}`;
    }

    // Network errors
    if (error.message === 'Network Error') {
      return 'Netzwerkverbindung fehlgeschlagen';
    }

    if (error.code === 'ECONNABORTED') {
      return 'Anfrage hat zu lange gedauert';
    }

    return error.message || 'Ein unbekannter Fehler ist aufgetreten';
  }

  /**
   * Prüft, ob eine Anfrage wiederholt werden sollte
   */
  shouldRetry(error, config, attempt = 0) {
    // Nicht mehr als max Versuche
    if (attempt >= this.maxRetries) {
      return false;
    }

    // Nur GET Anfragen wiederholen
    if (config.method && config.method.toUpperCase() !== 'GET') {
      return false;
    }

    // Status-basierte Entscheidung
    if (error.response?.status) {
      return this.retryableStatuses.includes(error.response.status);
    }

    // Network Error oder Timeout
    if (error.code === 'ECONNABORTED' || error.message === 'Network Error') {
      return true;
    }

    return false;
  }

  /**
   * Exponential backoff für Retry
   */
  getRetryDelay(attempt) {
    return Math.min(1000 * Math.pow(2, attempt), 10000);
  }

  /**
   * Bestimmt die Schweregrad eines Fehlers
   */
  getSeverity(error) {
    if (!error.response) return 'error'; // Network error
    
    const status = error.response.status;
    if (status === 401 || status === 403) return 'warning';
    if (status >= 500) return 'error';
    if (status >= 400) return 'warning';
    
    return 'info';
  }

  /**
   * Formatiert Fehler für User-Display
   */
  formatForDisplay(error) {
    return {
      message: this.extractMessage(error),
      severity: this.getSeverity(error),
      retryable: this.shouldRetry(error, error.config || {}),
      timestamp: new Date().toISOString(),
    };
  }
}

// Singleton Export
export const apiErrorHandler = new ApiErrorHandler();
