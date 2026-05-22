import { defineBoot } from '#q-app/wrappers';
import pinia from 'src/stores';

// Register Pinia BEFORE any boot file that calls a store (auth.ts).
export default defineBoot(({ app }) => {
  app.use(pinia);
});
