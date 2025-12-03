# 📧 Guía: Configurar Gmail para envío de emails

## 🎯 Pasos para obtener App Password de Gmail

### 1️⃣ **Activar Verificación en 2 pasos**
1. Ve a tu cuenta de Google: https://myaccount.google.com/security
2. En "Cómo inicias sesión en Google", busca **"Verificación en 2 pasos"**
3. Si no está activada, actívala siguiendo los pasos de Google

### 2️⃣ **Crear App Password**
1. Una vez activada la verificación en 2 pasos, ve a:
   https://myaccount.google.com/apppasswords
2. Inicia sesión si te lo solicita
3. Selecciona:
   - **App:** Correo
   - **Dispositivo:** Otro (nombre personalizado)
4. Ingresa un nombre descriptivo (ej: "Sistema Gestión API")
5. Haz clic en **Generar**
6. Google te mostrará una contraseña de 16 caracteres (ej: `abcd efgh ijkl mnop`)
7. **¡COPIA ESTA CONTRASEÑA INMEDIATAMENTE!** No podrás verla de nuevo

### 3️⃣ **Configurar en tu proyecto**

Edita tu archivo `.env` y agrega:

```env
GMAIL_EMAIL=tu_email@gmail.com
GMAIL_PASSWORD=abcdefghijklmnop
FRONTEND_URL=http://localhost:4200
```

⚠️ **IMPORTANTE:** 
- Pega el App Password **SIN ESPACIOS** (quita los espacios que Gmail muestra)
- NO uses tu contraseña normal de Gmail
- Si ves el App Password como `abcd efgh ijkl mnop`, debes pegarlo como `abcdefghijklmnop`

### 4️⃣ **Probar la configuración**

Reinicia tu servidor FastAPI:

```bash
cd server-python
uvicorn app.main:app --reload
```

Cuando crees un usuario, deberías ver en consola:
```
✅ Email de verificación enviado a: usuario@ejemplo.com
```

---

## 🚫 Si NO quieres configurar Gmail ahora

El sistema funcionará de todas formas, pero los emails se mostrarán en consola:

```
📧 EMAIL DE VERIFICACIÓN (MODO DESARROLLO - SIN SMTP)
======================================================================
📨 Para: usuario@ejemplo.com
👤 Usuario: Juan Pérez
🔑 Token: abc123...
🔗 URL de verificación: http://localhost:4200/auth/verify-email?token=abc123...
======================================================================
```

Puedes copiar manualmente la URL de verificación para probar.

---

## 📊 Límites de Gmail

- **Cuenta gratuita:** 500 emails/día
- **Google Workspace:** 2,000 emails/día
- Si superas el límite: bloqueo temporal de 24 horas

---

## ❓ Problemas comunes

### Error: "Username and Password not accepted"
- ✅ Verifica que la verificación en 2 pasos esté activada
- ✅ Asegúrate de usar App Password, NO tu contraseña normal
- ✅ Quita todos los espacios del App Password
- ✅ Revisa que el email sea correcto

### Error: "SMTP Authentication Error"
- ✅ Regenera el App Password desde Google
- ✅ Verifica que pegaste correctamente en el .env
- ✅ Reinicia el servidor después de cambiar .env

### Email no llega
- ✅ Revisa la carpeta de spam
- ✅ Verifica que el email del destinatario sea válido
- ✅ Revisa los logs del servidor para ver errores

---

## 🔒 Seguridad

- ❌ **NUNCA** compartas tu archivo `.env`
- ❌ **NUNCA** subas tu `.env` a GitHub
- ✅ Usa `.gitignore` para excluir `.env`
- ✅ Puedes revocar el App Password desde Google cuando quieras
