<script>
  import { onMount } from 'svelte'
  import { api } from './lib/api.js'
  import AddFoodPage from './lib/AddFoodPage.svelte'
  import { t } from './lib/i18n.js'

  const SLOTS = ['breakfast', 'lunch', 'dinner', 'snack']

  let page = 'today'   // 'today' | 'add'
  let activeMeal = 'breakfast'

  let entries = []
  let summary = { calories: 0, protein: 0, fat: 0, carbohydrate: 0 }
  let error = ''

  $: slotEntries = Object.fromEntries(SLOTS.map((s) => [s, entries.filter((e) => e.meal === s)]))

  async function refreshToday() {
    const [e, s] = await Promise.all([api.todayEntries(), api.todaySummary()])
    entries = e
    summary = s
  }

  function openAdd(meal) {
    activeMeal = meal
    page = 'add'
    history.pushState({ d: 1 }, '')
  }

  function onSaved() {
    refreshToday().catch((e) => (error = String(e)))
  }

  function handlePopState(e) {
    if (page === 'add' && (!e.state || e.state.d < 1)) {
      page = 'today'
      refreshToday().catch((err) => (error = String(err)))
    }
  }

  onMount(() => {
    refreshToday().catch((e) => (error = String(e)))
    window.addEventListener('popstate', handlePopState)
    return () => window.removeEventListener('popstate', handlePopState)
  })

  function fmt1(v) {
    return v == null ? null : Math.round(v * 10) / 10
  }
</script>

{#if page === 'add'}
  <AddFoodPage meal={activeMeal} on:saved={onSaved} />
{:else}
  <main class="max-w-md mx-auto p-4 space-y-4">

    <!-- summary: kcal centered, macros stacked to the right -->
    <div class="flex justify-center items-center gap-4 pt-2">
      <div class="text-center">
        <div class="text-5xl font-bold tabular-nums">{Math.round(summary.calories)}</div>
        <div class="text-sm opacity-60">{t('kcal_today')}</div>
      </div>
      <div class="flex flex-col gap-0.5 text-sm tabular-nums opacity-80">
        <span>💪 {fmt1(summary.protein)}g</span>
        <span>🥑 {fmt1(summary.fat)}g</span>
        <span>🌾 {fmt1(summary.carbohydrate)}g</span>
      </div>
    </div>

    {#if error}<div class="alert alert-error text-sm">{error}</div>{/if}

    <!-- entries grouped by slot -->
    <div class="space-y-3">
      {#each SLOTS as slot}
        <div>
          <!-- slot header -->
          <div class="flex items-center justify-between px-1 mb-1">
            <span class="font-semibold text-base">{t('slot_' + slot)}</span>
            <button
              class="btn btn-primary btn-xs"
              on:click={() => openAdd(slot)}
            >+</button>
          </div>

          <!-- slot entries -->
          {#if slotEntries[slot].length === 0}
            <div class="pl-3 text-sm opacity-30">{t('no_items')}</div>
          {:else}
            <ul class="pl-3 space-y-2">
              {#each slotEntries[slot] as e}
                <li>
                  <div class="text-sm font-medium">{e.food_name}</div>
                  <div class="flex flex-wrap gap-1 mt-0.5">
                    <span class="stat-tag bg-base-300">{e.amount_grams}g</span>
                    <span class="stat-tag bg-amber-100">⚡{Math.round(e.calories)}</span>
                    <span class="stat-tag bg-blue-100">💪{fmt1(e.protein)}g</span>
                    <span class="stat-tag bg-green-100">🥑{fmt1(e.fat)}g</span>
                    <span class="stat-tag bg-yellow-100">🌾{fmt1(e.carbohydrate)}g</span>
                  </div>
                </li>
              {/each}
            </ul>
          {/if}
        </div>
      {/each}
    </div>

  </main>
{/if}

<style>
  .stat-tag {
    display: inline-flex;
    align-items: center;
    padding: 0.1rem 0.4rem;
    border-radius: 0.3rem;
    font-size: 0.72rem;
    line-height: 1.4;
  }
</style>
