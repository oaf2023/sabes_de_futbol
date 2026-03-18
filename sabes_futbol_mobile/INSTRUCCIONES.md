# SABES DE FUTBOL - Aplicación Mobile (Flutter)

## 📱 Estado del Proyecto

**Versión**: 1.0.0 (En desarrollo)  
**Framework**: Flutter 3.19.5  
**Plataformas**: iOS (14+) + Android (API 21+)  
**State Management**: Riverpod 2.6.1

---

## 🚀 Inicio Rápido

### Requisitos Previos
- **Flutter SDK 3.19.5+**: https://flutter.dev/docs/get-started/install
- **Xcode 14+** (para iOS)
- **Android Studio + SDK** (para Android)
- **Visual Studio Code** con extensión Flutter

### Instalar Dependencias
```bash
cd sabes_futbol_mobile
flutter pub get
```

### Ejecutar en Emulador
```bash
# iOS (macOS/Linux)
flutter run -d iPhone

# Android
flutter run -d emulator-5554

# Web (desarrollo)
flutter run -d web
```

---

## 📁 Estructura del Proyecto

```
lib/
├── main.dart                    # Entrada de la app
├── config/
│   ├── theme.dart              # 🎨 Tema visual
│   └── constants.dart          # ⚙️ Constantes globales
├── models/
│   ├── user.dart               # 👤 Usuario
│   ├── match.dart              # ⚽ Partido
│   ├── bet.dart               # 🎟️ Apuesta (TODO)
│   └── game.dart              # 🎮 Estado del juego (TODO)
├── services/
│   ├── api_service.dart        # 🌐 HTTP client
│   ├── firebase_service.dart   # 🔥 Firebase (TODO)
│   └── mercadopago_service.dart # 💳 Pagos (TODO)
├── providers/
│   ├── auth_provider.dart      # 🔐 Autenticación
│   ├── game_provider.dart      # 🎮 Lógica de juego (TODO)
│   └── bets_provider.dart      # 🎟️ Apuestas (TODO)
├── screens/
│   ├── auth/
│   │   ├── login_screen.dart   # ✅ Implementado
│   │   └── register_screen.dart# TODO
│   ├── home_screen.dart        # ✅ Implementado (WIP)
│   ├── bet_screen.dart         # TODO
│   ├── fixture_screen.dart     # TODO
│   ├── profile_screen.dart     # TODO
│   └── shop_screen.dart        # TODO
├── widgets/
│   ├── common/                 # Componentes reutilizables
│   │   ├── loading_spinner.dart
│   │   └── app_bar.dart
│   └── bet/                    # Widgets de apuestas
│       ├── match_selector.dart
│       └── bet_card.dart
└── utils/
    ├── date_formatter.dart     # Fechas Argentina
    ├── validators.dart         # Validación
    └── extensions.dart         # Extensiones (TODO)
```

---

## 📋 Checklist - Próximos Pasos

### ✅ Completado (Fase 1)
- [x] Instalar Flutter SDK y crear proyecto
- [x] Configurar Riverpod
- [x] Crear tema visual
- [x] Modelos de datos (User, Match)
- [x] Pantalla de Login (UI)
- [x] Pantalla de Home (UI)
- [x] Estructura de carpetas

### 🔄 En Progreso (Fase 2)
- [ ] Firebase Authentication (login real)
- [ ] Persistencia de usuario (SharedPreferences)
- [ ] Pantalla de Registro
- [ ] Validación de formularios

### 📅 Pendiente (Fase 3+)
- [ ] API Service (conectar con backend)
- [ ] Pantalla de Fixture (obtener partidos)
- [ ] Pantalla de Apuestas (selector de resultados)
- [ ] WebSocket para resultados en vivo
- [ ] Compra de fichas (MercadoPago)
- [ ] Historial de jugadas
- [ ] Perfil del usuario
- [ ] Notificaciones push

---

## 🔐 Configuración Firebase

### 1. Crear Proyecto en Firebase Console
```url
https://console.firebase.google.com/
```

### 2. Descargar Configuración

#### iOS: `GoogleService-Info.plist`
```bash
# Colocar en ios/Runner/
# (Ver instrucciones en Firebase Console)
```

#### Android: `google-services.json`
```bash
# Colocar en android/app/
# (Ver instrucciones en Firebase Console)
```

### 3. Configurar FlutterFire
```bash
# Instalar CLI
npm install -g firebase-tools

# Autenticarse
firebase login

# Configurar proyecto
flutterfire configure --project=sabes-futbol-app
```

---

## 🧪 Testing

### Unit Tests
```bash
flutter test test/unit/
```

### Widget Tests
```bash
flutter test test/widget/
```

### Coverage
```bash
flutter test --coverage
```

---

## 📦 Build para Producción

### iOS
```bash
flutter build ios --release
```

Luego, abrir `ios/Runner.xcworkspace` en Xcode para archivar y subir a TestFlight.

### Android
```bash
flutter build appbundle --release
```

Luego, subir a Google Play Console.

---

## 🐛 Solución de Problemas

### Error: "Building with plugins requires symlink support"
**Solución (Windows)**:
1. Presionar `Win + R` → `ms-settings:developers`
2. Habilitar "Developer Mode"
3. Ejecutar Flutter en PowerShell como Administrador

### Error: SDK's Git integration conflicts
```bash
flutter config --no-analytics
flutter clean
rm -rf pubspec.lock
flutter pub get
```

### Error: Firebase configuration issues
```bash
# Verificar que GoogleService-Info.plist esté en el proyecto
# Verificar que google-services.json esté en el proyecto
# Ejecutar flutterfire configure de nuevo
```

---

## 📚 Recursos Útiles

- **Documentación Flutter**: https://docs.flutter.dev
- **Riverpod Docs**: https://riverpod.dev
- **Firebase + Flutter**: https://firebase.flutter.dev
- **Material Design 3**: https://m3.material.io/
- **Google Fonts**: https://fonts.google.com/

---

## 👥 Equipo

- **Desarrollo**: OAF
- **Diseño**: Retro/Vintage (inspirado en boletas antiguas)
- **Backend**: Python Flask + Firebase

---

## 📝 Notas Importantes

1. **El código de Login es simulado** - Reemplazar con Firebase Auth real en Fase 2
2. **No hay conexión a API real** - Conectar en Fase 3
3. **Los Assets (logos) deben agregarse manualmente** en `assets/`
4. **El proyecto usa Riverpod** en lugar de Provider (más moderno)

---

## 🚀 Próxima Fase

Para continuar con **Fase 2 (Core Screens)**, necesitas:

1. Configurar Firebase Authentication
2. Implementar `firebase_service.dart`
3. Conectar `AuthNotifier` con Firebase
4. Agregar `shared_preferences` para persistencia
5. Implementar validación de formularios

¿Deseas que comience con Fase 2 ahora?

---

**Última actualización**: 17 de marzo de 2026  
**Versión del plan**: 1.0.0
