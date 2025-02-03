export const environment = {
  production: true,
  apiUrl: 'https://api.stark-security.com',
  wsUrl: 'wss://api.stark-security.com/ws',
  mlServiceUrl: 'https://ml.stark-security.com',
  auth: {
    domain: 'stark-security.auth0.com',
    clientId: 'your-client-id',
    audience: 'https://api.stark-security.com'
  },
  monitoring: {
    applicationInsights: {
      instrumentationKey: 'your-key'
    }
  }
};