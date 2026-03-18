cd c:\sabes_de_futbol

git add backend/fixtures.json
git add backend/app.py backend/models.py backend/requirements.txt
git add backend/auth.py backend/services.py backend/activar_fecha.py backend/migrate_fecha_hora.py
git add frontend/src/components/PanelFixture.jsx
git add frontend/src/components/PerfilJugador.jsx frontend/src/components/MiCuentaModal.jsx
git add frontend/src/components/CompraFichasModal.jsx frontend/src/components/TicketModal.jsx
git add frontend/src/App.jsx frontend/src/index.css frontend/vite.config.js
git add frontend/src/utils/
git add frontend/src/components/AuthScreen.jsx frontend/src/components/Boleta.jsx
git add frontend/src/components/PanelSorteo.jsx frontend/src/components/PerfilHistorico.jsx
git add frontend/src/components/TablaPremios.jsx
git add frontend/dist/
git add .gitignore

git commit -m "Fix: Panel Fixture v2 retro + resultados Fecha 10 actualizados"

git push origin main
