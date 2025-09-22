export const environment = {
  production: true,
  apiUrl: 'https://api.enova-cip.com/api',
  wsUrl: 'wss://api.enova-cip.com/ws',
  appName: 'Contract Intelligence Platform',
  appVersion: '1.0.0',
  maxFileSize: 50 * 1024 * 1024, // 50MB
  allowedFileTypes: [
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'image/jpeg',
    'image/png',
    'image/gif'
  ],
  features: {
    aiAssistant: true,
    realTimeUpdates: true,
    advancedReports: true,
    multiLanguage: true,
    darkTheme: true
  },
  auth: {
    tokenRefreshThreshold: 5 * 60 * 1000, // 5 minutes
    sessionTimeout: 8 * 60 * 60 * 1000 // 8 hours
  },
  pagination: {
    defaultPageSize: 20,
    pageSizeOptions: [10, 20, 50, 100]
  },
  maps: {
    apiKey: 'your-production-maps-api-key'
  },
  monitoring: {
    enableErrorTracking: true,
    enablePerformanceTracking: true
  }
};