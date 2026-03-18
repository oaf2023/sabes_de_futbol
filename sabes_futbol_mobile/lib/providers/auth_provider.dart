import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:sabes_futbol_mobile/models/user.dart';

/// Estado de autenticación
class AuthState {
  final User? user;
  final bool isLoading;
  final String? error;

  AuthState({
    this.user,
    this.isLoading = false,
    this.error,
  });

  AuthState copyWith({
    User? user,
    bool? isLoading,
    String? error,
  }) {
    return AuthState(
      user: user ?? this.user,
      isLoading: isLoading ?? this.isLoading,
      error: error ?? this.error,
    );
  }

  bool get isAuthenticated => user != null;
}

/// Provider de autenticación
final authProvider = StateNotifierProvider<AuthNotifier, AuthState>((ref) {
  return AuthNotifier();
});

/// Notifier para manejar autenticación
class AuthNotifier extends StateNotifier<AuthState> {
  AuthNotifier() : super(AuthState());

  /// Simular login (reemplazar con Firebase Auth real)
  Future<void> login(String email, String password) async {
    state = state.copyWith(isLoading: true, error: null);

    try {
      // TODO: Implementar login con Firebase Auth
      // final user = await _firebaseService.signIn(email, password);
      
      // Simulación temporal
      await Future.delayed(Duration(seconds: 2));
      
      final mockUser = User(
        dni: '12345678',
        nombre: 'Juan',
        apellido: 'Pérez',
        email: email,
        fichas: 1000,
      );

      state = state.copyWith(user: mockUser, isLoading: false);
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: 'Error al iniciar sesión: $e',
      );
    }
  }

  /// Logout
  void logout() {
    state = AuthState();
  }

  /// Registrarse
  Future<void> register({
    required String dni,
    required String nombre,
    required String apellido,
    required String email,
    required String password,
  }) async {
    state = state.copyWith(isLoading: true, error: null);

    try {
      // TODO: Implementar registro con Firebase Auth
      
      final newUser = User(
        dni: dni,
        nombre: nombre,
        apellido: apellido,
        email: email,
        fichas: 0,
        fechaRegistro: DateTime.now(),
      );

      state = state.copyWith(user: newUser, isLoading: false);
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: 'Error al registrarse: $e',
      );
    }
  }

  /// Recargar datos del usuario
  Future<void> refreshUser() async {
    // TODO: Recargar desde API si el usuario está autenticado
  }
}
