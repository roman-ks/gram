<script>
  import { createEventDispatcher, onMount, tick } from 'svelte'
  import { api } from './api.js'
  import NewFoodPage from './NewFoodPage.svelte'
  import { t } from './i18n.js'

  export let meal

  const dispatch = createEventDispatcher()

  onMount(() => {
    function handlePop(e) {
      if (showNewFood && e.state?.d === 1) showNewFood = false
    }
    window.addEventListener('popstate', handlePop)
    return () => window.removeEventListener('popstate', handlePop)
  })

  // Pin the page to window.visualViewport (top + height) instead of trusting
  // the layout viewport / 100dvh. When the on-screen keyboard opens on mobile,
  // the browser also tries to auto-scroll the focused input into view; if our
  // container isn't position:fixed, that native scroll drags the whole page
  // (header included) and fights with our own scrollIntoView below, causing
  // visible jumps. Pinning removes the native scroll: there's nothing left in
  // normal document flow for the browser to scroll, so only our JS-driven
  // resize (which only changes the list's height, not its scroll offset)
  // takes effect.
  let vvTop = 0
  let vvHeight = null  // null until visualViewport is available -> fall back to 100dvh

  onMount(() => {
    const vv = window.visualViewport
    if (!vv) return
    async function syncViewport() {
      vvTop = vv.offsetTop
      vvHeight = vv.height
      await tick()
      itemRefs[selectedFoodId]?.scrollIntoView({ block: 'nearest' })
    }
    syncViewport()
    vv.addEventListener('resize', syncViewport)
    vv.addEventListener('scroll', syncViewport)
    return () => {
      vv.removeEventListener('resize', syncViewport)
      vv.removeEventListener('scroll', syncViewport)
    }
  })

  const TABS = [
    { id: 'all',         key: 'src_all' },
    { id: 'recent',      key: 'src_recent' },
    { id: 'top_slot',    key: 'src_top_slot' },
    { id: 'top_overall', key: 'src_top_overall' },
  ]

  let source = 'recent'
  let suggestions = []
  let selectedFoodId = ''
  let grams = ''
  let loading = false
  let error = ''
  let showNewFood = false
  let foodsMap = {}  // food_id -> full food object (for nutrition preview)
  let itemRefs = {}  // food_id -> list item element (for scrollIntoView on keyboard open)

  const DEFAULT_GRAMS = 100

  $: source, meal, loadSuggestions()

  async function loadSuggestions() {
    error = ''
    try {
      if (source === 'all') {
        const [foods, history] = await Promise.all([
          api.allFoods(),
          api.popular(null, 1000).catch(() => []),
        ])
        foodsMap = Object.fromEntries(foods.map((f) => [f.id, f]))
        const lastAmountByFood = Object.fromEntries(history.map((h) => [h.food_id, h.last_amount_grams]))
        suggestions = foods.map((f) => ({
          food_id: f.id,
          food_name: f.name,
          last_amount_grams: lastAmountByFood[f.id] ?? DEFAULT_GRAMS,
        }))
      } else {
        if (Object.keys(foodsMap).length === 0) {
          api.allFoods().then((foods) => {
            foodsMap = Object.fromEntries(foods.map((f) => [f.id, f]))
          }).catch(() => {})
        }
        if (source === 'recent') {
          suggestions = await api.sameMeal(meal)
        } else if (source === 'top_slot') {
          suggestions = await api.popular(meal)
        } else {
          suggestions = await api.popular(null)
        }
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
      const entry = await api.addEntry({ food_id: selectedFoodId, amount_grams: Number(grams), meal })
      grams = ''
      dispatch('saved', entry)
    } catch (e) {
      error = String(e)
    } finally {
      loading = false
    }
  }

  function openNewFood() {
    showNewFood = true
    history.pushState({ d: 2 }, '')
  }

  function onFoodCreated(food) {
    showNewFood = false
    history.back()  // pop the d:2 entry we pushed when opening NewFoodPage
    foodsMap = { ...foodsMap, [food.id]: food }
    suggestions = [{ food_id: food.id, food_name: food.name, last_amount_grams: null }, ...suggestions]
    selectedFoodId = food.id
    grams = ''
  }

  function fmt1(v) {
    return v == null ? 0 : Math.round(v * 10) / 10
  }

  $: previewFood = foodsMap[selectedFoodId] ?? null
  $: previewG = Number(grams) || 0
  $: preview = {
    calories: previewFood ? Math.round(previewFood.calories * previewG / 100) : 0,
    protein:  previewFood ? fmt1(previewFood.protein  * previewG / 100) : 0,
    fat:      previewFood ? fmt1(previewFood.fat       * previewG / 100) : 0,
    carbs:    previewFood ? fmt1(previewFood.carbohydrate * previewG / 100) : 0,
  }
</script>

{#if showNewFood}
  <NewFoodPage
    on:created={(e) => onFoodCreated(e.detail)}
  />
{:else}
  <div
    class="fixed left-0 right-0"
    style="top: {vvTop}px; height: {vvHeight !== null ? vvHeight + 'px' : '100dvh'};"
  >
    <div class="flex flex-col h-full max-w-md mx-auto">
      <!-- back -->
      <div class="flex items-center gap-2 px-3 py-2 border-b border-base-200 shrink-0">
        <button class="btn btn-ghost btn-sm" on:click={() => history.back()}>
          ← {t('back')}
        </button>
        <span class="text-sm font-medium opacity-60">{t('slot_' + meal)}</span>
      </div>

      <!-- tab strip -->
      <div class="overflow-x-auto shrink-0 px-2 pt-2 pb-1">
        <div role="tablist" class="flex gap-1 flex-nowrap min-w-max">
          {#each TABS as tab}
            <button
              role="tab"
              class="px-3 py-1.5 rounded-full text-sm font-medium whitespace-nowrap transition-colors
                {source === tab.id
                  ? 'bg-primary text-primary-content'
                  : 'bg-base-200 text-base-content hover:bg-base-300'}"
              on:click={() => (source = tab.id)}
            >
              {t(tab.key)}
            </button>
          {/each}
        </div>
      </div>

      {#if error}<div class="alert alert-error text-sm mx-2 my-1 shrink-0">{error}</div>{/if}

      <!-- food list fills remaining space -->
      <div class="flex-1 overflow-y-auto mx-2 border border-base-300 rounded-box">
        {#if suggestions.length === 0}
          <div class="flex items-center px-3 py-4 opacity-40">{t('none')}</div>
        {:else}
          {#each suggestions as s}
            <button
              bind:this={itemRefs[s.food_id]}
              class="w-full text-left px-3 py-3 border-b border-base-100 break-words leading-snug
                {selectedFoodId === s.food_id
                  ? 'bg-primary text-primary-content'
                  : 'hover:bg-base-200'}"
              on:click={() => selectFood(s.food_id)}
            >
              {s.food_name}
            </button>
          {/each}
        {/if}
      </div>

      <!-- bottom bar: always visible -->
      <div class="shrink-0 p-2 border-t border-base-200 space-y-2">
        <button class="btn btn-outline btn-sm w-full" on:click={openNewFood}>
          {t('add_missing')}
        </button>
        <form class="flex gap-2" on:submit|preventDefault={save}>
          <input
            class="input input-bordered flex-1"
            type="number"
            inputmode="decimal"
            placeholder={t('grams_ph')}
            bind:value={grams}
          />
          <button type="submit" class="btn btn-primary" disabled={loading}>💾</button>
        </form>
        <div class="flex flex-wrap gap-1 px-1">
          <span class="stat-tag bg-amber-100">⚡{preview.calories}</span>
          <span class="stat-tag bg-blue-100">💪{preview.protein}g</span>
          <span class="stat-tag bg-green-100">🥑{preview.fat}g</span>
          <span class="stat-tag bg-yellow-100">🌾{preview.carbs}g</span>
        </div>
      </div>
    </div>
  </div>
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
