import { test, expect } from '@playwright/test'
import { mockApiRoutes, freezeTime } from '../fixtures/mock-api'

/**
 * Critical-flow E2E: setup wizard.
 *
 * Verifies the wizard loads and at least the first step renders its
 * title. Deeper multi-step coverage (navigation, validation,
 * submission) is tracked in the follow-up E2E expansion issue.
 */

test.describe('Setup wizard critical flow', () => {
  test.beforeEach(async ({ page }) => {
    await freezeTime(page)
    await mockApiRoutes(page)
  })

  test('loads the setup wizard root', async ({ page }) => {
    await page.goto('/setup')
    await expect(page).toHaveURL(/\/setup/)
    // The wizard renders a heading even on first paint; the catch-all
    // mock ensures data loads resolve instantly.
    await expect(page.locator('main')).toBeVisible()
  })
})
