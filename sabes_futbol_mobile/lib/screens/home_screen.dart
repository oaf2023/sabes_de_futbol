import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:sabes_futbol_mobile/config/theme.dart';
import 'package:sabes_futbol_mobile/providers/auth_provider.dart';

class HomeScreen extends ConsumerStatefulWidget {
  const HomeScreen({Key? key}) : super(key: key);

  @override
  ConsumerState<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends ConsumerState<HomeScreen> {
  int _selectedIndex = 0;

  @override
  Widget build(BuildContext context) {
    final authState = ref.watch(authProvider);
    final user = authState.user;

    return Scaffold(
      appBar: AppBar(
        title: Text('SABES DE FUTBOL'),
        centerTitle: true,
        actions: [
          IconButton(
            icon: Icon(Icons.logout),
            onPressed: () {
              ref.read(authProvider.notifier).logout();
            },
          ),
        ],
      ),
      body: SingleChildScrollView(
        child: Padding(
          padding: EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // User Info Card
              Card(
                child: Padding(
                  padding: EdgeInsets.all(16),
                  child: Column(
                    children: [
                      CircleAvatar(
                        radius: 40,
                        backgroundColor: SabesTheme.primario,
                        child: Text(
                          user?.nombre[0].toUpperCase() ?? 'U',
                          style: TextStyle(
                            fontSize: 24,
                            color: Colors.white,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                      SizedBox(height: 12),
                      Text(
                        user?.nombreCompleto ?? 'Usuario',
                        style: Theme.of(context).textTheme.titleLarge,
                      ),
                      SizedBox(height: 8),
                      Text(
                        'DNI: ${user?.dni ?? '---'}',
                        style: Theme.of(context).textTheme.bodyMedium,
                      ),
                    ],
                  ),
                ),
              ),
              SizedBox(height: 24),
              // Fichas disponibles
              Card(
                color: SabesTheme.secundario,
                child: Padding(
                  padding: EdgeInsets.all(16),
                  child: Column(
                    children: [
                      Text(
                        'FICHAS DISPONIBLES',
                        style: Theme.of(context).textTheme.bodySmall,
                      ),
                      SizedBox(height: 8),
                      Text(
                        '${user?.fichas ?? 0}',
                        style: TextStyle(
                          fontSize: 32,
                          fontWeight: FontWeight.bold,
                          color: SabesTheme.primario,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
              SizedBox(height: 24),
              // Main buttons
              ElevatedButton.icon(
                onPressed: () {
                  // TODO: Navegar a pantalla de juego
                },
                icon: Icon(Icons.sports_soccer),
                label: Text('JUGAR BOLETA'),
              ),
              SizedBox(height: 12),
              ElevatedButton.icon(
                onPressed: () {
                  // TODO: Navegar a pantalla de fixture
                },
                icon: Icon(Icons.calendar_today),
                label: Text('VER FIXTURE'),
              ),
              SizedBox(height: 12),
              ElevatedButton.icon(
                onPressed: () {
                  // TODO: Navegar a compra de fichas
                },
                icon: Icon(Icons.shopping_cart),
                label: Text('COMPRAR FICHAS'),
              ),
              SizedBox(height: 12),
              ElevatedButton.icon(
                onPressed: () {
                  // TODO: Navegar a historial
                },
                icon: Icon(Icons.history),
                label: Text('MI HISTORIAL'),
              ),
            ],
          ),
        ),
      ),
      bottomNavigationBar: BottomNavigationBar(
        items: [
          BottomNavigationBarItem(
            icon: Icon(Icons.home),
            label: 'Inicio',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.sports_soccer),
            label: 'Jugar',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.person),
            label: 'Perfil',
          ),
        ],
        currentIndex: _selectedIndex,
        onTap: (index) {
          setState(() {
            _selectedIndex = index;
          });
        },
      ),
    );
  }
}
