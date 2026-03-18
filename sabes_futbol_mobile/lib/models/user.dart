import 'package:equatable/equatable.dart';

/// Modelo de Usuario en la aplicación
class User extends Equatable {
  final String dni;
  final String nombre;
  final String apellido;
  final String email;
  final int fichas;
  final String? avatar;
  final DateTime? fechaRegistro;
  final bool activo;

  const User({
    required this.dni,
    required this.nombre,
    required this.apellido,
    required this.email,
    required this.fichas,
    this.avatar,
    this.fechaRegistro,
    this.activo = true,
  });

  /// Nombre completo del usuario
  String get nombreCompleto => '$nombre $apellido';

  /// Copiar usuario con cambios opcionales
  User copyWith({
    String? dni,
    String? nombre,
    String? apellido,
    String? email,
    int? fichas,
    String? avatar,
    DateTime? fechaRegistro,
    bool? activo,
  }) {
    return User(
      dni: dni ?? this.dni,
      nombre: nombre ?? this.nombre,
      apellido: apellido ?? this.apellido,
      email: email ?? this.email,
      fichas: fichas ?? this.fichas,
      avatar: avatar ?? this.avatar,
      fechaRegistro: fechaRegistro ?? this.fechaRegistro,
      activo: activo ?? this.activo,
    );
  }

  /// Convertir desde JSON (respuesta de API)
  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      dni: json['dni'] ?? '',
      nombre: json['nombre'] ?? '',
      apellido: json['apellido'] ?? '',
      email: json['email'] ?? '',
      fichas: json['fichas'] ?? 0,
      avatar: json['avatar'],
      fechaRegistro: json['fecha_registro'] != null
          ? DateTime.tryParse(json['fecha_registro'])
          : null,
      activo: json['activo'] ?? true,
    );
  }

  /// Convertir a JSON
  Map<String, dynamic> toJson() {
    return {
      'dni': dni,
      'nombre': nombre,
      'apellido': apellido,
      'email': email,
      'fichas': fichas,
      'avatar': avatar,
      'fecha_registro': fechaRegistro?.toIso8601String(),
      'activo': activo,
    };
  }

  @override
  List<Object?> get props => [
    dni,
    nombre,
    apellido,
    email,
    fichas,
    avatar,
    fechaRegistro,
    activo,
  ];
}
