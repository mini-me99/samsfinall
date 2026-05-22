<template>
  <div class="login-shell">
    <div class="sams-aurora" />

    <!-- left brand panel -->
    <aside class="login-brand">
      <div class="sams-mark login-brand__logo">
        <span class="sams-mark__dot" /> SAMS
      </div>

      <div class="login-brand__body">
        <div class="sams-eyebrow">Sports Academy OS</div>
        <h1 class="login-brand__title">
          Run your academy<br />
          like a <span class="accent">pro club.</span>
        </h1>
        <p class="login-brand__sub">
          Players, coaches, sessions, payments and analytics —
          one unified control room for every academy.
        </p>

        <ul class="login-brand__list">
          <li><span /> Multi-role access for coaches, ops & families</li>
          <li><span /> Live attendance, schedules & venues</li>
          <li><span /> Payments, dues and revenue at a glance</li>
        </ul>
      </div>

      <div class="login-brand__foot">© {{ year }} SAMS — Sports Academy Management System</div>
    </aside>

    <!-- right auth panel -->
    <section class="login-panel">
      <div class="login-card">
        <div class="sams-eyebrow">Welcome back</div>
        <h2 class="login-card__title">Sign in to your academy</h2>
        <p class="login-card__sub">Use the credentials issued by your admin.</p>

        <q-form @submit="onSubmit" class="q-gutter-md q-mt-md">
          <q-input
            v-model="email"
            outlined
            dark
            type="email"
            label="Email"
            required
          />
          <q-input
            v-model="password"
            outlined
            dark
            :type="show ? 'text' : 'password'"
            label="Password"
            required
          >
            <template v-slot:append>
              <q-icon
                :name="show ? 'visibility_off' : 'visibility'"
                class="cursor-pointer"
                @click="show = !show"
              />
            </template>
          </q-input>

          <q-btn
            type="submit"
            color="primary"
            class="full-width login-cta"
            :loading="loading"
            unelevated
            size="md"
          >
            Enter dashboard
            <q-icon name="arrow_forward" class="q-ml-sm" />
          </q-btn>
        </q-form>

        <div class="login-foot">
          Don't have an account? Ask your academy admin to create one.
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useQuasar } from 'quasar';
import { useAuthStore } from 'src/stores/auth';

const email = ref('');
const password = ref('');
const loading = ref(false);
const show = ref(false);
const auth = useAuthStore();
const router = useRouter();
const route = useRoute();
const $q = useQuasar();
const year = computed(() => new Date().getFullYear());

async function onSubmit() {
  loading.value = true;
  try {
    await auth.login(email.value, password.value);
    const redirect = (route.query.redirect as string) || '/';
    await router.push(redirect);
  } catch {
    $q.notify({ type: 'negative', message: 'Invalid credentials' });
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped lang="scss">
.login-shell {
  position: relative;
  min-height: 100vh;
  display: grid;
  grid-template-columns: 1.1fr 1fr;
  background: var(--sams-bg);
  overflow: hidden;

  @media (max-width: 900px) {
    grid-template-columns: 1fr;
  }
}

.login-brand {
  position: relative;
  z-index: 1;
  padding: 44px 56px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  background:
    radial-gradient(80% 60% at 0% 0%, rgba(198,242,78,0.10), transparent 60%),
    linear-gradient(180deg, #0b0e14 0%, #0a0c10 100%);
  border-right: 1px solid var(--sams-border);

  @media (max-width: 900px) { padding: 32px 24px; }
}

.login-brand__logo {
  font-size: 18px;
  color: var(--sams-text);
}

.login-brand__title {
  font-family: 'Space Grotesk', sans-serif;
  font-weight: 700;
  font-size: clamp(36px, 4.6vw, 60px);
  line-height: 1.02;
  letter-spacing: -0.03em;
  margin: 14px 0 18px;
  color: var(--sams-text);
}
.accent { color: var(--sams-accent); }

.login-brand__sub {
  color: var(--sams-text-dim);
  font-size: 16px;
  max-width: 460px;
  line-height: 1.55;
}

.login-brand__list {
  list-style: none;
  padding: 0;
  margin: 28px 0 0;
  display: grid;
  gap: 10px;
}
.login-brand__list li {
  display: flex;
  align-items: center;
  gap: 12px;
  color: var(--sams-text);
  font-size: 14.5px;
}
.login-brand__list li span {
  width: 6px; height: 6px; border-radius: 50%;
  background: var(--sams-accent);
  box-shadow: 0 0 8px var(--sams-accent);
  flex: none;
}

.login-brand__foot {
  color: var(--sams-text-mute);
  font-size: 12px;
  letter-spacing: 0.04em;
}

.login-panel {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 32px;
}

.login-card {
  width: 100%;
  max-width: 420px;
  background: linear-gradient(180deg, rgba(255,255,255,0.03), rgba(255,255,255,0)) , var(--sams-surface);
  border: 1px solid var(--sams-border-strong);
  border-radius: 18px;
  padding: 36px 32px;
  box-shadow: 0 30px 80px rgba(0,0,0,0.45), 0 0 0 1px rgba(198,242,78,0.04) inset;
}

.login-card__title {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 26px;
  font-weight: 600;
  margin: 6px 0 6px;
  color: var(--sams-text);
}
.login-card__sub {
  color: var(--sams-text-dim);
  font-size: 14px;
  margin: 0 0 4px;
}

.login-cta {
  height: 48px;
  border-radius: 12px;
  font-size: 15px;
}

.login-foot {
  margin-top: 22px;
  color: var(--sams-text-mute);
  font-size: 12.5px;
  text-align: center;
}
</style>
