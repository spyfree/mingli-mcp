import { cloudflareTest } from '@cloudflare/vitest-pool-workers';
import { defineConfig } from 'vitest/config';

export default defineConfig({
  plugins: [
    cloudflareTest({
      miniflare: {
        compatibilityDate: '2026-03-07',
        compatibilityFlags: ['global_fetch_strictly_public'],
      },
    }),
  ],
  test: {
    include: ['cloudflare/**/*.test.mjs'],
  },
});
