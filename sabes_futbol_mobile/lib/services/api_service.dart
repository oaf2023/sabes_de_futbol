import 'package:http/http.dart' as http;
import 'package:sabes_futbol_mobile/config/constants.dart';
import 'dart:convert';

/// Servicio base para llamadas HTTP a la API
class ApiService {
  final http.Client _client;

  ApiService({http.Client? client}) : _client = client ?? http.Client();

  /// GET request
  Future<dynamic> get(String endpoint) async {
    try {
      final response = await _client
          .get(
            Uri.parse('${AppConstants.API_BASE_URL}$endpoint'),
            headers: _headers,
          )
          .timeout(Duration(seconds: AppConstants.API_TIMEOUT_SECONDS));

      return _handleResponse(response);
    } catch (e) {
      throw ApiException('Error en GET $endpoint: $e');
    }
  }

  /// POST request
  Future<dynamic> post(String endpoint, {required Map<String, dynamic> body}) async {
    try {
      final response = await _client
          .post(
            Uri.parse('${AppConstants.API_BASE_URL}$endpoint'),
            headers: _headers,
            body: jsonEncode(body),
          )
          .timeout(Duration(seconds: AppConstants.API_TIMEOUT_SECONDS));

      return _handleResponse(response);
    } catch (e) {
      throw ApiException('Error en POST $endpoint: $e');
    }
  }

  /// PUT request
  Future<dynamic> put(String endpoint, {required Map<String, dynamic> body}) async {
    try {
      final response = await _client
          .put(
            Uri.parse('${AppConstants.API_BASE_URL}$endpoint'),
            headers: _headers,
            body: jsonEncode(body),
          )
          .timeout(Duration(seconds: AppConstants.API_TIMEOUT_SECONDS));

      return _handleResponse(response);
    } catch (e) {
      throw ApiException('Error en PUT $endpoint: $e');
    }
  }

  /// Procesar respuesta HTTP
  dynamic _handleResponse(http.Response response) {
    final statusCode = response.statusCode;
    final body = response.body;

    if (body.isEmpty) {
      return null;
    }

    try {
      final decoded = jsonDecode(body);

      if (statusCode >= 200 && statusCode < 300) {
        return decoded;
      } else {
        final message = decoded['error'] ?? 'Error del servidor';
        throw ApiException(message, statusCode);
      }
    } catch (e) {
      throw ApiException('Error decodificando respuesta: $e');
    }
  }

  /// Headers estándar para requests
  Map<String, String> get _headers => {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  };

  void dispose() {
    _client.close();
  }
}

/// Excepción personalizada para errores de API
class ApiException implements Exception {
  final String message;
  final int? statusCode;

  ApiException(this.message, [this.statusCode]);

  @override
  String toString() => message;
}
