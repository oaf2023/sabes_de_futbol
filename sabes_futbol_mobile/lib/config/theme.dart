import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

/// Tema visual de Sabes de Fútbol
/// Utiliza la paleta retro de la aplicación web
class SabesTheme {
  // Paleta de colores
  static const Color primario = Color(0xFF1a5276);      // Azul AFA
  static const Color secundario = Color(0xFFf0e68c);    // Amarillo
  static const Color acento = Color(0xFF27ae60);        // Verde cancha
  static const Color error = Color(0xFF922b21);         // Rojo derrota
  static const Color fondo = Color(0xFFfdf5e6);         // Papel envejecido
  static const Color maderaOscura = Color(0xFF5c3c1e);  // Madera oscura
  static const Color maderaClara = Color(0xFFc08752);   // Madera clara

  // Tipografías
  static TextTheme get _textTheme => TextTheme(
    displayLarge: GoogleFonts.specialElite(
      fontSize: 32,
      fontWeight: FontWeight.bold,
      color: primario,
    ),
    displayMedium: GoogleFonts.specialElite(
      fontSize: 24,
      fontWeight: FontWeight.bold,
      color: primario,
    ),
    titleLarge: GoogleFonts.specialElite(
      fontSize: 20,
      fontWeight: FontWeight.bold,
      color: primario,
    ),
    titleMedium: GoogleFonts.courierPrime(
      fontSize: 16,
      fontWeight: FontWeight.w600,
      color: primario,
    ),
    bodyLarge: GoogleFonts.courierPrime(
      fontSize: 16,
      color: Colors.black87,
    ),
    bodyMedium: GoogleFonts.courierPrime(
      fontSize: 14,
      color: Colors.black87,
    ),
  );

  static ThemeData get lightTheme => ThemeData(
    useMaterial3: true,
    colorScheme: ColorScheme.light(
      primary: primario,
      secondary: secundario,
      tertiary: acento,
      error: error,
      surface: fondo,
      onPrimary: Colors.white,
      onSecondary: primario,
      onError: Colors.white,
    ),
    textTheme: _textTheme,
    appBarTheme: AppBarTheme(
      backgroundColor: primario,
      foregroundColor: Colors.white,
      elevation: 0,
      centerTitle: true,
      titleTextStyle: GoogleFonts.specialElite(
        fontSize: 20,
        fontWeight: FontWeight.bold,
        color: Colors.white,
      ),
    ),
    bottomNavigationBarTheme: BottomNavigationBarThemeData(
      backgroundColor: maderaOscura,
      selectedItemColor: secundario,
      unselectedItemColor: Colors.white54,
      elevation: 8,
      type: BottomNavigationBarType.fixed,
    ),
    buttonTheme: ButtonThemeData(
      buttonColor: primario,
      textTheme: ButtonTextTheme.primary,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(8),
      ),
    ),
    elevatedButtonTheme: ElevatedButtonThemeData(
      style: ElevatedButton.styleFrom(
        backgroundColor: primario,
        foregroundColor: Colors.white,
        textStyle: GoogleFonts.specialElite(
          fontSize: 16,
          fontWeight: FontWeight.bold,
        ),
        padding: EdgeInsets.symmetric(horizontal: 24, vertical: 12),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(8),
        ),
      ),
    ),
    outlinedButtonTheme: OutlinedButtonThemeData(
      style: OutlinedButton.styleFrom(
        foregroundColor: primario,
        side: BorderSide(color: primario, width: 2),
        textStyle: GoogleFonts.courierPrime(
          fontSize: 14,
          fontWeight: FontWeight.bold,
        ),
      ),
    ),
    cardTheme: CardTheme(
      color: fondo,
      elevation: 4,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(8),
        side: BorderSide(color: primario, width: 2),
      ),
    ),
    inputDecorationTheme: InputDecorationTheme(
      filled: true,
      fillColor: Colors.white,
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(8),
        borderSide: BorderSide(color: primario, width: 1),
      ),
      enabledBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(8),
        borderSide: BorderSide(color: primario, width: 1),
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(8),
        borderSide: BorderSide(color: acento, width: 2),
      ),
      errorBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(8),
        borderSide: BorderSide(color: error, width: 2),
      ),
      contentPadding: EdgeInsets.symmetric(horizontal: 16, vertical: 12),
    ),
    scaffoldBackgroundColor: fondo,
  );
}
