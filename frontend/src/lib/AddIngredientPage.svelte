<script>
  import { createEventDispatcher, onMount } from 'svelte'
  import { api } from './api.js'
  import { t } from './i18n.js'

  const dispatch = createEventDispatcher()

  let foods = []
  let selectedFoodId = null
  let grams = ''
  let error = ''

  onMount(async () => {
    try {
      foods = await api.allFoods()
      selectedFoodId = foods[0]?.id ?? null
    } catch (e) {
      error = String(e)
    }
  })

  function pick() {
    if (!selectedFoodId || !grams) return (error = t('err_pick'))
    const food = foods.find((f) => f.id === selectedFoodId)
    dispatch('picked', { food_id: selectedFoodId, food_name: food.name, grams: Number(grams) })
    grams = ''
  }
</script>

<div class="flex flex-col h-dvh max-w-md mx-auto">
  <div class="flex items-center gap-2 px-3 py-2 border-b border-base-200 shrink-0">
    <button class="btn btn-ghost btn-sm" on:click={() => history.back()}>← {t('back')}</button>
    <span class="text-sm font-medium opacity-60">{t('add_ingredient')}</span>
  </div>

  {#if error}<div class="alert alert-error text-sm mx-2 my-1 shrink-0">{error}</div>{/if}

  <div class="flex-1 overflow-y-auto mx-2 border border-base-300 rounded-box">
    {#if foods.length === 0}
      <div class="flex items-center px-3 py-4 opacity-40">{t('none')}</div>
    {:else}
      {#each foods as f}
        <button
          class="w-full text-left px-3 py-3 border-b border-base-100 break-words leading-snug
            {selectedFoodId === f.id ? 'bg-primary text-primary-content' : 'hover:bg-base-200'}"
          on:click={() => (selectedFoodId = f.id)}
        >
          {f.name}
        </button>
      {/each}
    {/if}
  </div>

  <div class="shrink-0 p-2 border-t border-base-200">
    <div class="flex gap-2">
      <input
        class="input input-bordered flex-1"
        type="number"
        inputmode="decimal"
        placeholder={t('grams_ph')}
        bind:value={grams}
      />
      <button class="btn btn-primary" on:click={pick}>+</button>
    </div>
  </div>
</div>
