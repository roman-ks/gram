<script>
  import { onMount } from 'svelte'
  import { api } from './lib/api.js'
  import NewFoodModal from './lib/NewFoodModal.svelte'

  const SLOTS = ['breakfast', 'lunch', 'dinner', 'snack']
  const SOURCES = [
    { id: 'recent', label: 'Recent (same meal)' },
    { id: 'top_slot', label: 'Top this slot' },
    { id: 'top_overall', label: 'Top overall' },
  ]

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

  // remember last-used meal slot (DESIGN §9)
  $: localStorage.setItem('lastMeal', meal)
  // refetch suggestions whenever slot or source changes
  $: meal, source, loadSuggestions()

  async function refreshToday() {
    const [e, s] = await Promise.all([api.todayEntries(), api.todaySummary()])
    entries = e
    summary = s
  }

  async function loadSuggestions() {
    error = ''
    try {
      if (source === 'recent') suggestions = await api.sameMeal(meal)
      else if (source === 'top_slot') suggestions = await api.popular(meal)
      else suggestions = await api.popular(null)

      if (!suggestions.some((s) => s.food_id === selectedFoodId)) {
        selectedFoodId = suggestions[0]?.food_id ?? ''
        prefillGrams()
      }
    } catch (e) {
      error = String(e)
    }
  }

  function prefillGrams() {
    const s = suggestions.find((x) => x.food_id === selectedFoodId)
    grams = s?.last_amount_grams ?? ''
  }

  async function save() {
    error = ''
    if (!selectedFoodId || !grams) return (error = 'Pick a food and enter a weight')
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
    <div class="text-sm opacity-60">kcal today</div>
  </div>

  <!-- today's items: flat list, names only -->
  <ul class="menu bg-base-200 rounded-box w-full">
    {#if entries.length === 0}
      <li class="px-4 py-2 opacity-40">No items yet</li>
    {:else}
      {#each entries as e}
        <li><span class="px-4 py-2">{e.food_name}</span></li>
      {/each}
    {/if}
  </ul>

  {#if error}<div class="alert alert-error text-sm">{error}</div>{/if}

  <!-- add-item form -->
  <div class="space-y-2">
    <select class="select select-bordered w-full capitalize" bind:value={meal}>
      {#each SLOTS as s}<option value={s} class="capitalize">{s}</option>{/each}
    </select>

    <div class="flex gap-2">
      <select class="select select-bordered flex-1" bind:value={source}>
        {#each SOURCES as s}<option value={s.id}>{s.label}</option>{/each}
      </select>
      <select
        class="select select-bordered flex-1"
        bind:value={selectedFoodId}
        on:change={prefillGrams}
      >
        {#if suggestions.length === 0}<option value="">— none —</option>{/if}
        {#each suggestions as s}<option value={s.food_id}>{s.food_name}</option>{/each}
      </select>
    </div>

    <button class="btn btn-outline btn-sm w-full" on:click={() => (showModal = true)}>
      + Add missing
    </button>

    <div class="flex gap-2">
      <input
        class="input input-bordered flex-1"
        type="number"
        inputmode="decimal"
        placeholder="grams"
        bind:value={grams}
      />
      <button class="btn btn-primary" on:click={save} disabled={loading}>Save</button>
    </div>
  </div>
</main>

{#if showModal}
  <NewFoodModal on:created={(e) => onFoodCreated(e.detail)} on:close={() => (showModal = false)} />
{/if}
