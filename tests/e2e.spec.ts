import { test, expect } from '@playwright/test';
import fs from 'fs';

// La URL base de la aplicación. Asegúrate de que coincida con la configuración de tu servidor de desarrollo.
const BASE_URL = 'http://localhost:3000';

test.describe('Flujo E2E Básico de SADI', () => {

  test('Debería cargar la página, mostrar el mensaje de bienvenida y permitir enviar un mensaje', async ({ page }) => {
    const consoleLogs: string[] = [];
    page.on('console', msg => {
      consoleLogs.push(`[${msg.type()}] ${msg.text()}`);
    });

    try {
      // 1. Navegar a la página principal
      await page.goto(BASE_URL);

      // 2. Verificar que el título principal es visible
      await expect(page.getByText('Sistema de Analítica de Datos Inteligente (SADI)')).toBeVisible();
    } catch (error) {
      // Si la prueba falla, tomar una captura de pantalla, guardar el HTML y los logs de la consola
      await page.screenshot({ path: 'test-failure-screenshot.png' });
      const htmlContent = await page.content();
      fs.writeFileSync('test-failure-page.html', htmlContent);
      console.error("--- CONSOLE LOGS ---");
      console.error(consoleLogs.join('\n'));
      console.error("--- END CONSOLE LOGS ---");
      throw error;
    }

    // 3. Verificar que el mensaje de bienvenida del bot está presente
    await expect(page.getByText('¡Hola! Soy tu asistente de análisis de datos.')).toBeVisible();

    // 4. Escribir un mensaje en el campo de entrada
    const input = page.getByPlaceholder('Escribe tu mensaje o usa el micrófono...');
    await input.fill('Hola, mundo');

    // 5. Verificar que el botón de enviar está habilitado
    const sendButton = page.getByRole('button', { name: 'Enviar' });
    await expect(sendButton).toBeEnabled();

    // 6. Hacer clic en el botón de enviar
    await sendButton.click();

    // 7. Verificar que el mensaje del usuario aparece en el chat
    await expect(page.getByText('Hola, mundo')).toBeVisible();

    // 8. Verificar que el bot está "pensando" (muestra el indicador de carga)
    // Usamos un selector CSS para el indicador de carga animado.
    await expect(page.locator('.animate-pulse')).toBeVisible();

    // En una prueba real, aquí esperaríamos la respuesta del bot.
    // Como depende de un backend que no está corriendo durante el test,
    // nos detenemos aquí. La prueba confirma que la UI es interactiva.
  });

});
