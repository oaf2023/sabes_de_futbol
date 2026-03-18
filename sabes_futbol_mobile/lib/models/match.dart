import 'package:equatable/equatable.dart';

/// Estados posibles de un partido
enum MatchStatus {
  pending,    // Pendiente (no comenzó)
  live,       // En juego
  finished,   // Finalizado
}

/// Resultados posibles de un partido
enum MatchResult {
  local,      // Ganó local (L)
  draw,       // Empate (E)
  visitor,    // Ganó visitante (V)
}

/// Modelo de Partido
class Match extends Equatable {
  final int id;
  final int fechaId;
  final String nombreLocal;
  final String nombreVisitante;
  final DateTime? fechaHora;
  final int? golesLocal;
  final int? golesVisitante;
  final MatchResult? resultado;
  final MatchStatus status;
  final String? marcadorFinal;

  const Match({
    required this.id,
    required this.fechaId,
    required this.nombreLocal,
    required this.nombreVisitante,
    this.fechaHora,
    this.golesLocal,
    this.golesVisitante,
    this.resultado,
    this.status = MatchStatus.pending,
    this.marcadorFinal,
  });

  /// Nombre corto del partido (local vs visitante)
  String get nombre => '$nombreLocal vs $nombreVisitante';

  /// Marcador formateado
  String get marcador => '$golesLocal - $golesVisitante';

  /// Determinar estado del partido
  factory Match.fromJson(Map<String, dynamic> json) {
    MatchStatus status = MatchStatus.pending;
    MatchResult? resultado;

    if (json['resultado'] != null) {
      status = MatchStatus.finished;
      final res = json['resultado'];
      if (res == 'L') resultado = MatchResult.local;
      else if (res == 'E') resultado = MatchResult.draw;
      else if (res == 'V') resultado = MatchResult.visitor;
    } else {
      // Verificar si está en juego
      if (json['fecha_hora'] != null) {
        final fechaHora = DateTime.tryParse(json['fecha_hora']);
        if (fechaHora != null) {
          final now = DateTime.now();
          final diff = now.difference(fechaHora).inMinutes;
          if (diff >= 0 && diff < 110) {
            status = MatchStatus.live;
          }
        }
      }
    }

    return Match(
      id: json['id'] ?? 0,
      fechaId: json['fecha_id'] ?? 0,
      nombreLocal: json['local'] ?? '',
      nombreVisitante: json['visitante'] ?? '',
      fechaHora: json['fecha_hora'] != null
          ? DateTime.tryParse(json['fecha_hora'])
          : null,
      golesLocal: json['goles_local'],
      golesVisitante: json['goles_visitante'],
      resultado: resultado,
      status: status,
      marcadorFinal: json['resultado_final'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'fecha_id': fechaId,
      'local': nombreLocal,
      'visitante': nombreVisitante,
      'fecha_hora': fechaHora?.toIso8601String(),
      'goles_local': golesLocal,
      'goles_visitante': golesVisitante,
      'resultado': resultado == MatchResult.local
          ? 'L'
          : resultado == MatchResult.draw
              ? 'E'
              : resultado == MatchResult.visitor
                  ? 'V'
                  : null,
      'resultado_final': marcadorFinal,
      'status': status.toString(),
    };
  }

  @override
  List<Object?> get props => [
    id,
    fechaId,
    nombreLocal,
    nombreVisitante,
    fechaHora,
    golesLocal,
    golesVisitante,
    resultado,
    status,
    marcadorFinal,
  ];
}
