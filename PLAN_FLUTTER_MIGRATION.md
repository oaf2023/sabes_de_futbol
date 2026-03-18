# Plan de Transformación: React Web → Flutter Mobile

**Fecha**: 17 de marzo de 2026  
**Proyecto**: SABES DE FÚTBOL  
**Plataforma Destino**: iOS + Android (Flutter)  
**Estado**: En Planificación

---

## 1. Análisis de Viabilidad

### Origen: React + Vite (New_app)
```
New_app/
├── src/
│   ├── App.jsx            ← Componente raíz
│   ├── App.css            ← Estilos globales
│   ├── index.css          ← Responsividad (ya implementada)
│   ├── components/        ← 11 componentes principales
│   ├── utils/             ← Utilities (auth, fechas)
│   └── firebase.js        ← Backend (Firebase)
├── package.json           ← Deps: React, Vite, Firebase
└── vite.config.js
```

### Destino: Flutter Mobile
```
sabes_futbol_flutter/
├── lib/
│   ├── main.dart               ← Entrada principal
│   ├── screens/                ← Equivalente a componentes
│   ├── widgets/                ← Widgets reutilizables
│   ├── models/                 ← Data models
│   ├── services/               ← API + Firebase
│   ├── providers/              ← State management (Riverpod/BLoC)
│   ├── theme/                  ← Temas (colores, tipografía)
│   └── utils/                  ← Utilidades
├── pubspec.yaml                ← Dependencias
├── android/                    ← Android config
└── ios/                        ← iOS config
```

---

## 2. Mapeo de Componentes React → Widgets Flutter

| Componente React | Propósito | Widget Flutter | Notas |
|---|---|---|---|
| `AuthScreen.jsx` | Login/Registro | `AuthScreen` (Stateful) | Provider: Firebase Auth |
| `Boleta.jsx` | Selector de apuestas | `BustaWidget` | Provider: Game Logic |
| `BoletaEnCurso.jsx` | Apuesta activa | `ActiveBetWidget` | Realtime updates |
| `PanelSorteo.jsx` | Resultados en vivo | `LiveResultsPanel` | Stream de WebSocket |
| `TablaPremios.jsx` | Tabla de premios | `PrizesTable` | Scroll horizontal |
| `PanelFixture.jsx` | Fixture (partidos) | `FixturePanel` | Actualización cada 60s |
| `CompraFichasModal.jsx` | Modal de compra | `BuyChipsDialog` | MercadoPago integration |
| `MiCuentaModal.jsx` | Datos usuario | `AccountDialog` | Edit user profile |
| `PerfilJugador.jsx` | Carnet de socio | `PlayerProfileCard` | Avatar + Datos |
| `PerfilHistorico.jsx` | Historial de jugadas | `BetHistoryList` | Infinite scroll |
| `TicketModal.jsx` | Detalle de boleta | `TicketDetailDialog` | Screenshot export |

---

## 3. arquitectura Flutter Recomendada

### 3.1 State Management: Riverpod
```dart
// Opción elegida: Riverpod (más moderno que Provider)
// - Family modifiers para parámetros
// - Async providers para Firebase
// - Mejor testing

final userProvider = StateNotifierProvider<UserNotifier, User?>((ref) {
  return UserNotifier();
});

final betsProvider = FutureProvider<List<Bet>>((ref) async {
  final user = ref.watch(userProvider);
  return await fetchBets(user?.dni);
});
```

### 3.2 Estructura de Carpetas
```
lib/
├── main.dart                          # Entrada + Material App
├── config/
│   ├── theme.dart                     # Tema Sabes (colores, tipografía)
│   └── constants.dart                 # URLs, claves API
├── models/
│   ├── user.dart                      # Usuario (Equatable)
│   ├── bet.dart                       # Apuesta
│   ├── game.dart                      # Estado del juego
│   └── match.dart                     # Partido
├── services/
│   ├── api_service.dart               # HTTP client
│   ├── firebase_service.dart          # Firebase auth + DB
│   ├── mercadopago_service.dart       # Pago
│   └── websocket_service.dart         # Resultados en vivo
├── providers/                         # Riverpod providers
│   ├── auth_provider.dart             # Autenticación
│   ├── game_provider.dart             # Lógica de juego
│   ├── bets_provider.dart             # Apuestas
│   ├── fixture_provider.dart          # Fixture
│   └── user_provider.dart             # Usuario
├── screens/
│   ├── auth/
│   │   ├── login_screen.dart
│   │   └── register_screen.dart
│   ├── game/
│   │   ├── bet_screen.dart            # Pantalla de jugadas
│   │   ├── active_bet_screen.dart     # Apuesta en curso
│   │   └── results_screen.dart        # Resultados
│   ├── profile/
│   │   ├── profile_screen.dart
│   │   ├── history_screen.dart
│   │   └── account_screen.dart
│   ├── shop/
│   │   └── buy_chips_screen.dart
│   └── home_screen.dart               # Pantalla principal
├── widgets/
│   ├── common/
│   │   ├── app_bar.dart
│   │   ├── bottom_nav.dart            # Navegación inferior
│   │   └── loading_spinner.dart
│   ├── bet/
│   │   ├── bet_card.dart
│   │   ├── match_selector.dart
│   │   └── bet_confirmation.dart
│   ├── fixture/
│   │   ├── match_tile.dart
│   │   └── fixture_list.dart
│   └── profile/
│       ├── profile_header.dart
│       └── stats_card.dart
└── utils/
    ├── date_formatter.dart            # Formato de fechas Argentina
    ├── currency_formatter.dart        # Formato moneda
    └── validators.dart                # Validación de entrada
```

---

## 4. Dependencias Principales (pubspec.yaml)

```yaml
dependencies:
  flutter:
    sdk: flutter
  
  # State Management
  flutter_riverpod: ^2.4.0
  riverpod_annotation: ^2.1.0
  
  # Firebase
  firebase_core: ^24.0.0
  firebase_auth: ^4.10.0
  cloud_firestore: ^4.12.0
  firebase_storage: ^11.3.0
  
  # Networking
  http: ^1.1.0
  dio: ^5.3.0
  web_socket_channel: ^2.4.0
  
  # UI
  cupertino_icons: ^1.0.6
  flutter_svg: ^2.0.0
  cached_network_image: ^3.3.0
  
  # Pago
  mercado_pago_sdk_flutter: ^1.0.0
  
  # Utils
  equatable: ^2.0.5
  get_it: ^7.5.0
  intl: ^0.20.0
  shared_preferences: ^2.2.0
  
dev_dependencies:
  flutter_test:
    sdk: flutter
  flutter_lints: ^3.0.0
  riverpod_generator: ^2.2.0
  build_runner: ^2.4.6
```

---

## 5. Transformación de Funciones Clave

### 5.1 Autenticación Firebase

**React (actual)**:
```javascript
const handleLogin = async (dni, password) => {
  const user = await firebase.auth().signInWithEmailAndPassword(email, password);
  setUsuario(user);
};
```

**Flutter (nuevo)**:
```dart
final authProvider = StateNotifierProvider((ref) {
  return AuthNotifier(
    firebaseService: ref.watch(firebaseServiceProvider)
  );
});

class AuthNotifier extends StateNotifier<User?> {
  Future<void> login(String email, String password) async {
    state = await _firebaseService.signIn(email, password);
  }
}

// Uso en Widget
final auth = ref.watch(authProvider);
if (auth == null) {
  return LoginScreen();
} else {
  return HomeScreen();
}
```

### 5.2 Obtener Partidos en Vivo

**React**:
```javascript
useEffect(() => {
  fetchPartidos();
  const t = setInterval(fetchPartidos, 60_000);
  return () => clearInterval(t);
}, []);
```

**Flutter**:
```dart
final partidos = FutureProvider.autoDispose((ref) async {
  return await ApiService().getPartidos();
});

// Refresh automático cada 60s
class RefreshNotifier extends StateNotifier<void> {
  RefreshNotifier(this._ref) {
    Timer.periodic(Duration(seconds: 60), (_) {
      _ref.refresh(partidos);
    });
  }
}
```

### 5.3 Tabla con Scroll Horizontal

**React**:
```jsx
<div style={{ overflowX: 'auto' }}>
  <table>...</table>
</div>
```

**Flutter**:
```dart
SingleChildScrollView(
  scrollDirection: Axis.horizontal,
  child: DataTable(
    columns: [...],
    rows: [...],
  ),
)
```

---

## 6. Diferencias iOS vs Android

### iOS (Cupertino)
```dart
// Estilo iOS nativo
CupertinoPageScaffold(
  navigationBar: CupertinoNavigationBar(
    middle: Text('Sabes de Fútbol'),
  ),
  child: SafeArea(
    child: Column(...),
  ),
)
```

### Android (Material)
```dart
// Estilo Material
Scaffold(
  appBar: AppBar(title: Text('Sabes de Fútbol')),
  bottomNavigationBar: BottomNavigationBar(...),
  body: Column(...),
)
```

**Solución**: Usar `flutter_platform_widgets` o condicionales de plataforma para adaptar automáticamente.

---

## 7. Temas de la Aplicación

```dart
// theme.dart
class SabesTheme {
  static const Color primario = Color(0xFF1a5276);    // Azul AFA
  static const Color secundario = Color(0xFFf0e68c);  // Amarillo
  static const Color acento = Color(0xFF27ae60);      // Verde
  static const Color error = Color(0xFF922b21);       // Rojo
  static const Color fondo = Color(0xFFfdf5e6);       // Papel
  
  static ThemeData get lightTheme => ThemeData(
    primaryColor: primario,
    useMaterial3: true,
    colorScheme: ColorScheme.light(
      primary: primario,
      secondary: secundario,
      error: error,
      surface: fondo,
    ),
    textTheme: TextTheme(
      displayLarge: GoogleFonts.specialElite(fontSize: 32),
      bodyLarge: GoogleFonts.courierPrime(fontSize: 16),
    ),
  );
}
```

---

## 8. Datos del Usuario (Modelo Equatable)

```dart
// models/user.dart
class User extends Equatable {
  final String dni;
  final String nombre;
  final String email;
  final int fichas;
  final DateTime? fechaRegistro;
  
  const User({
    required this.dni,
    required this.nombre,
    required this.email,
    required this.fichas,
    this.fechaRegistro,
  });
  
  @override
  List<Object?> get props => [dni, nombre, email, fichas, fechaRegistro];
  
  // Convertir desde API JSON
  factory User.fromJson(Map<String, dynamic> json) => User(
    dni: json['dni'],
    nombre: json['nombre'],
    email: json['email'],
    fichas: json['fichas'] ?? 0,
    fechaRegistro: json['fecha_registro'] != null 
      ? DateTime.parse(json['fecha_registro'])
      : null,
  );
}
```

---

## 9. Navegación (GoRouter)

```dart
// config/router.dart
final routerProvider = Provider((ref) {
  final user = ref.watch(authProvider);
  
  return GoRouter(
    initialLocation: user == null ? '/login' : '/home',
    routes: [
      GoRoute(
        path: '/login',
        builder: (context, state) => LoginScreen(),
      ),
      GoRoute(
        path: '/home',
        builder: (context, state) => HomeScreen(),
        routes: [
          GoRoute(
            path: 'bet',
            builder: (context, state) => BetScreen(),
          ),
          GoRoute(
            path: 'profile',
            builder: (context, state) => ProfileScreen(),
          ),
        ],
      ),
    ],
  );
});
```

---

## 10. Plan de Implementación (Fases)

### **Fase 1: Setup Inicial** (1 semana)
- [x] Instalar Flutter SDK
- [x] Crear proyecto `sabes_futbol_flutter`
- [x] Configurar Xcode (iOS) y Android Studio
- [x] Setup Firebase (iOS + Android)
- [x] Configurar Riverpod y Router

### **Fase 2: Core Screens** (2 semanas)
- [ ] LoginScreen + RegisterScreen
- [ ] HomeScreen (Tab navigation)
- [ ] BetScreen (Selector de apuestas)
- [ ] ProfileScreen (Carnet de socio)

### **Fase 3: Features** (2 semanas)
- [ ] Fixture (Obtener partidos en vivo)
- [ ] Live Results (WebSocket)
- [ ] Buy Chips (MercadoPago)
- [ ] Bet History (Lista infinita)

### **Fase 4: Polish** (1 semana)
- [ ] Temas iOS vs Android
- [ ] Notificaciones push
- [ ] Testing (Unit + Widget tests)
- [ ] Build release

### **Fase 5: Deploy** (1 semana)
- [ ] TestFlight (iOS)
- [ ] Google Play Console (Android)
- [ ] Store listings + screenshots
- [ ] Go live

---

## 11. Checklist de Instalación

```bash
# Instalar Flutter
flutter --version
flutter doctor

# Crear proyecto
flutter create --org com.sabesfutbol sabes_futbol_flutter

# Entrar al proyecto
cd sabes_futbol_flutter

# Agregar dependencias
flutter pub add flutter_riverpod riverpod_annotation
flutter pub add firebase_core firebase_auth cloud_firestore
flutter pub add go_router http dio

# Ejecutar en iOS
cd ios && pod install && cd ..
flutter run -d iPhone

# Ejecutar en Android
flutter run -d emulator-5554
```

---

## 12. Recursos Clave

- **Documentación**: https://docs.flutter.dev
- **Riverpod**: https://riverpod.dev
- **Firebase + Flutter**: https://firebase.flutter.dev
- **GoRouter**: https://pub.dev/packages/go_router

---

## 13. Notas Importantes

1. **Reutilizar lógica**: La lógica de negocio de `services.py` (backend) se mantiene igual; Flutter consume API.
2. **Assets**: Los logos, iconos y fuentes se copian a `assets/` en Flutter.
3. **Seguridad**: Las claves API de Firebase se configuran en `google-services.json` (Android) e `GoogleService-Info.plist` (iOS).
4. **Base de datos local**: Usar `shared_preferences` para cache offline.

---

**Próximo paso**: ¿Comenzamos con el setup inicial en Fase 1?
