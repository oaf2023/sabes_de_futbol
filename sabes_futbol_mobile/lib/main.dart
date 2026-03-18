import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:sabes_futbol_mobile/config/theme.dart';
import 'package:sabes_futbol_mobile/providers/auth_provider.dart';
import 'package:sabes_futbol_mobile/screens/auth/login_screen.dart';
import 'package:sabes_futbol_mobile/screens/home_screen.dart';

void main() {
  runApp(
    const ProviderScope(
      child: MyApp(),
    ),
  );
}

class MyApp extends ConsumerWidget {
  const MyApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final authState = ref.watch(authProvider);

    return MaterialApp(
      title: 'Sabes de Fútbol',
      theme: SabesTheme.lightTheme,
      home: authState.isAuthenticated ? HomeScreen() : LoginScreen(),
      debugShowCheckedModeBanner: false,
    );
  }
}
