import { test, expect } from '@playwright/test';

test('has title', async ({ page }) => {
  await page.goto('http://localhost:3000/');

  // Expect a title "to contain" a substring.
  await expect(page).toHaveTitle(/SADI/);
});

test('chat view is visible', async ({ page }) => {
  await page.goto('http://localhost:3000/');

  // Expect the chat view to be visible
  await expect(page.locator('text=¡Hola! Soy tu asistente de análisis de datos.')).toBeVisible();
});
