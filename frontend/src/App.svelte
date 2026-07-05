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

  // ── Context menu ──────────────────────────────────────────────────────────

  let contextMenu = null  // null | { entryId, x, y }
  let pressTimer = null
  let pressStartX = 0
  let pressStartY = 0

  function onEntryContextMenu(e, entryId) {
    e.preventDefault()
    contextMenu = { entryId, x: e.clientX, y: e.clientY }
  }

  function onEntryTouchStart(e, entryId) {
    const touch = e.touches[0]
    pressStartX = touch.clientX
    pressStartY = touch.clientY
    pressTimer = setTimeout(() => {
      pressTimer = null
      contextMenu = { entryId, x: pressStartX, y: pressStartY }
    }, 500)
  }

  function onEntryTouchMove(e) {
    if (!pressTimer) return
    const touch = e.touches[0]
    if (Math.abs(touch.clientX - pressStartX) > 5 || Math.abs(touch.clientY - pressStartY) > 5) {
      clearTimeout(pressTimer)
      pressTimer = null
    }
  }

  function onEntryTouchEnd() {
    clearTimeout(pressTimer)
    pressTimer = null
  }

  function dismissMenu() {
    contextMenu = null
  }

  async function deleteEntry() {
    if (!contextMenu) return
    const id = contextMenu.entryId
    contextMenu = null
    try {
      await api.deleteEntry(id)
      await refreshToday()
    } catch (e) {
      error = String(e)
    }
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
              {#each slotEntries[slot] as entry}
                <li
                  class="select-none"
                  on:contextmenu={(e) => onEntryContextMenu(e, entry.id)}
                  on:touchstart={(e) => onEntryTouchStart(e, entry.id)}
                  on:touchmove={onEntryTouchMove}
                  on:touchend={onEntryTouchEnd}
                >
                  <div class="text-sm font-medium">{entry.food_name}</div>
                  <div class="flex flex-wrap gap-1 mt-0.5">
                    <span class="stat-tag bg-base-300">{entry.amount_grams}g</span>
                    <span class="stat-tag bg-amber-100">⚡{Math.round(entry.calories)}</span>
                    <span class="stat-tag bg-blue-100">💪{fmt1(entry.protein)}g</span>
                    <span class="stat-tag bg-green-100">🥑{fmt1(entry.fat)}g</span>
                    <span class="stat-tag bg-yellow-100">🌾{fmt1(entry.carbohydrate)}g</span>
                  </div>
                </li>
              {/each}
            </ul>
          {/if}
        </div>
      {/each}
    </div>

  </main>

  {#if contextMenu}
    <div
      class="fixed inset-0 z-40"
      on:click={dismissMenu}
      on:contextmenu|preventDefault={dismissMenu}
    />
    <div
      class="context-menu fixed z-50 bg-gray-800 text-white rounded-full shadow-lg flex items-center"
      style="left:{contextMenu.x}px; top:{contextMenu.y}px; transform:translate(-50%, calc(-100% - 10px))"
    >
      <button
        class="px-3 py-1.5 text-sm rounded-full transition-colors hover:bg-gray-700 active:bg-gray-600"
        on:click={deleteEntry}
      >
        🗑️ {t('delete')}
      </button>
    </div>
  {/if}
{/if}

<style>
  .context-menu::after {
    content: '';
    position: absolute;
    bottom: -6px;
    left: 50%;
    transform: translateX(-50%);
    border: 6px solid transparent;
    border-top-color: #1f2937;
    border-bottom: 0;
  }

  .stat-tag {
    display: inline-flex;
    align-items: center;
    padding: 0.1rem 0.4rem;
    border-radius: 0.3rem;
    font-size: 0.72rem;
    line-height: 1.4;
  }
</style>
