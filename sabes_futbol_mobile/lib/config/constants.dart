/// Constantes de la aplicación
class AppConstants {
  // API Base
  static const String API_BASE_URL = 'http://localhost:5000/api';
  static const String Firebase_PROJECT_ID = 'sabes-futbol-app';
  
  // Timeouts
  static const int API_TIMEOUT_SECONDS = 30;
  static const int FIXTURE_REFRESH_SECONDS = 60;
  
  // Costo de jugada
  static const int COST_PER_BET = 2500; // fichas
  
  // Máximos y mínimos
  static const int MAX_BETS_PER_TICKET = 13;
  static const int MIN_CHIPS_TO_BUY = 100;
  
  // Duración de partidos (minutos)
  static const int MATCH_DURATION_MINUTES = 90;
  static const int MATCH_BUFFER_MINUTES = 15; // Buffer para 'en juego'
  
  // Mensajes de error estándar
  static const String ERROR_NETWORK = 'Error de conexión. Intenta de nuevo.';
  static const String ERROR_AUTH = 'Credenciales inválidas.';
  static const String ERROR_GENERIC = 'Algo salió mal. Intenta de nuevo.';
  
  // Regex para validación
  static const String REGEX_DNI = r'^\d{7,8}$';
  static const String REGEX_EMAIL = r'^[^@]+@[^@]+\.[^@]+$';
  static const String REGEX_PHONE = r'^[0-9\+\-\s()]{7,}$';
}
