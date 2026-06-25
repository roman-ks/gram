<script>
  import { onMount } from 'svelte'
  import { api } from './lib/api.js'
  import NewFoodModal from './lib/NewFoodModal.svelte'
  import { t } from './lib/i18n.js'

  const SLOTS = ['breakfast', 'lunch', 'dinner', 'snack']
  const TABS = [
    { id: 'all',         key: 'src_all' },
    { id: 'recent',      key: 'src_recent' },
    { id: 'top_slot',    key: 'src_top_slot' },
    { id: 'top_overall', key: 'src_top_overall' },
  ]

  // Item height used as the fixed unit for list height calculation (2.75rem = 44px).
  const ITEM_H = '2.75rem'
  const LIST_ITEMS = 5

  let meal = localStorage.getItem('lastMeal') || 'breakfast'
  let source = 'recent'
  let suggestions = []
  let selectedFoodId = ''
  let grams = ''
  let entries = []
  let summary = { calories: 0 }
  let loading = false
  let error = ''
  let showModal = false

  $: localStorage.setItem('lastMeal', meal)
  $: meal, source, loadSuggestions()

  async function refreshToday() {
    const [e, s] = await Promise.all([api.todayEntries(), api.todaySummary()])
    entries = e
    summary = s
  }

  async function loadSuggestions() {
    error = ''
    try {
      if (source === 'all') {
        const foods = await api.allFoods()
        suggestions = foods.map((f) => ({ food_id: f.id, food_name: f.name, last_amount_grams: null }))
      } else if (source === 'recent') {
        suggestions = await api.sameMeal(meal)
      } else if (source === 'top_slot') {
        suggestions = await api.popular(meal)
      } else {
        suggestions = await api.popular(null)
      }

      if (!suggestions.some((s) => s.food_id === selectedFoodId)) {
        selectedFoodId = suggestions[0]?.food_id ?? ''
        prefillGrams()
      }
    } catch (e) {
      error = String(e)
    }
  }

  function prefillGrams() {
    const item = suggestions.find((x) => x.food_id === selectedFoodId)
    grams = item?.last_amount_grams ?? ''
  }

  function selectFood(foodId) {
    selectedFoodId = foodId
    prefillGrams()
  }

  async function save() {
    error = ''
    if (!selectedFoodId || !grams) return (error = t('err_pick'))
    loading = true
    try {
      await api.addEntry({ food_id: selectedFoodId, amount_grams: Number(grams), meal })
      grams = ''
      await refreshToday()
    } catch (e) {
      error = String(e)
    } finally {
      loading = false
    }
  }

  function onFoodCreated(food) {
    showModal = false
    suggestions = [{ food_id: food.id, food_name: food.name, last_amount_grams: null }, ...suggestions]
    selectedFoodId = food.id
    grams = ''
  }

  onMount(() => {
    refreshToday().catch((e) => (error = String(e)))
  })
</script>

<main class="max-w-md mx-auto p-4 space-y-4 min-h-screen">
  <!-- today total -->
  <div class="text-center pt-2">
    <div class="text-5xl font-bold tabular-nums">{Math.round(summary.calories)}</div>
    <div class="text-sm opacity-60">{t('kcal_today')}</div>
  </div>

  <!-- today's items: flat list, names only -->
  <ul class="menu bg-base-200 rounded-box w-full">
    {#if entries.length === 0}
      <li class="px-4 py-2 opacity-40">{t('no_items')}</li>
    {:else}
      {#each entries as e}
        <li><span class="px-4 py-2">{e.food_name}</span></li>
      {/each}
    {/if}
  </ul>

  {#if error}<div class="alert alert-error text-sm">{error}</div>{/if}

  <!-- add-item form -->
  <div class="space-y-2">
    <select
      class="select select-bordered w-full"
      bind:value={meal}
      on:change={() => (source = 'recent')}
    >
      {#each SLOTS as s}<option value={s}>{t('slot_' + s)}</option>{/each}
    </select>

    <!-- source tab strip -->
    <div class="overflow-x-auto">
      <div role="tablist" class="tabs tabs-bordered flex-nowrap min-w-full">
        {#each TABS as tab}
          <button
            role="tab"
            class="tab whitespace-nowrap {source === tab.id ? 'tab-active' : ''}"
            on:click={() => (source = tab.id)}
          >
            {t(tab.key)}
          </button>
        {/each}
      </div>
    </div>

    <!-- food list: fixed height = 5 items, scrolls if more -->
    <div
      class="border border-base-300 rounded-box overflow-y-auto"
      style="height: calc({LIST_ITEMS} * {ITEM_H})"
    >
      {#if suggestions.length === 0}
        <div
          class="flex items-center px-3 opacity-40 break-words"
          style="min-height: {ITEM_H}"
        >
          {t('none')}
        </div>
      {:else}
        {#each suggestions as s}
          <button
            class="w-full text-left px-3 break-words leading-snug
              {selectedFoodId === s.food_id
                ? 'bg-primary text-primary-content'
                : 'hover:bg-base-200'}"
            style="min-height: {ITEM_H}; display: flex; align-items: center;"
            on:click={() => selectFood(s.food_id)}
          >
            {s.food_name}
          </button>
        {/each}
      {/if}
    </div>

    <button class="btn btn-outline btn-sm w-full" on:click={() => (showModal = true)}>
      {t('add_missing')}
    </button>

    <div class="flex gap-2">
      <input
        class="input input-bordered flex-1"
        type="number"
        inputmode="decimal"
        placeholder={t('grams_ph')}
        bind:value={grams}
      />
      <button class="btn btn-primary" on:click={save} disabled={loading}>💾</button>
    </div>
  </div>
</main>

{#if showModal}
  <NewFoodModal on:created={(e) => onFoodCreated(e.detail)} on:close={() => (showModal = false)} />
{/if}
