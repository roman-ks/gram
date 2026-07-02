<script>
  import { createEventDispatcher } from 'svelte'
  import { api } from './api.js'
  import { t } from './i18n.js'
  import AddIngredientPage from './AddIngredientPage.svelte'

  const dispatch = createEventDispatcher()

  // ── Meal tab ────────────────────────────────────────────────────────────────
  const ROWS = [
    [['calories',     'fld_calories',     true],  ['protein',       'fld_protein',       true]],
    [['carbohydrate', 'fld_carbohydrate', true],  ['sugar',         'fld_sugar',         false]],
    [['fat',          'fld_fat',          true],  ['saturated_fat', 'fld_saturated_fat', false]],
    [['fiber',        'fld_fiber',        false], ['salt',          'fld_salt',          false]],
  ]
  const REQUIRED = ['calories', 'protein', 'carbohydrate', 'fat']
  const OPTIONAL = ['sugar', 'saturated_fat', 'fiber', 'salt']

  let f = {
    name: '', calories: '', protein: '', carbohydrate: '', fat: '',
    saturated_fat: '', sugar: '', fiber: '', salt: '',
  }

  // ── Recipe tab ───────────────────────────────────────────────────────────────
  let recipeName = ''
  let ingredients = []   // [{food_id, food_name, grams}]
  let cookedWeight = ''
  let showIngredientPicker = false

  // ── Shared ──────────────────────────────────────────────────────────────────
  let activeTab = 'meal'   // 'meal' | 'recipe'
  let error = ''
  let saving = false

  async function saveMeal() {
    error = ''
    if (!f.name.trim()) return (error = t('err_name_req'))
    for (const k of REQUIRED) {
      if (f[k] === '' || f[k] == null) return (error = t('err_field_req', t(`lbl_${k}`)))
    }
    saving = true
    try {
      const body = { name: f.name.trim() }
      for (const k of REQUIRED) body[k] = Number(f[k])
      for (const k of OPTIONAL) body[k] = f[k] === '' ? null : Number(f[k])
      const food = await api.addFood(body)
      dispatch('created', food)
    } catch (e) {
      error = String(e)
    } finally {
      saving = false
    }
  }

  async function saveRecipe() {
    error = ''
    if (!recipeName.trim()) return (error = t('err_recipe_name_req'))
    if (ingredients.length === 0) return (error = t('err_no_ingredients'))
    if (!cookedWeight) return (error = t('err_cooked_weight_req'))
    saving = true
    try {
      const food = await api.createRecipe({
        name: recipeName.trim(),
        cooked_weight: Number(cookedWeight),
        ingredients: ingredients.map((i) => ({ food_id: i.food_id, grams: i.grams })),
      })
      dispatch('created', food)
    } catch (e) {
      error = String(e)
    } finally {
      saving = false
    }
  }

  function onIngredientPicked(event) {
    const { food_id, food_name, grams } = event.detail
    ingredients = [...ingredients, { food_id, food_name, grams }]
    showIngredientPicker = false
  }

  function removeIngredient(i) {
    ingredients = ingredients.filter((_, idx) => idx !== i)
  }
</script>

{#if showIngredientPicker}
  <AddIngredientPage
    on:picked={onIngredientPicked}
    on:back={() => (showIngredientPicker = false)}
  />
{:else}
  <div class="flex flex-col h-dvh max-w-md mx-auto">
    <!-- header -->
    <div class="flex items-center gap-2 px-3 py-2 border-b border-base-200 shrink-0">
      <button class="btn btn-ghost btn-sm" on:click={() => dispatch('back')}>← {t('back')}</button>
    </div>

    <!-- tab strip -->
    <div class="shrink-0 px-2 pt-2 pb-1">
      <div role="tablist" class="flex gap-1">
        {#each [['meal', t('tab_meal')], ['recipe', t('tab_recipe')]] as [id, label]}
          <button
            role="tab"
            class="px-3 py-1.5 rounded-full text-sm font-medium whitespace-nowrap transition-colors
              {activeTab === id
                ? 'bg-primary text-primary-content'
                : 'bg-base-200 text-base-content hover:bg-base-300'}"
            on:click={() => { activeTab = id; error = '' }}
          >
            {label}
          </button>
        {/each}
      </div>
    </div>

    {#if error}<div class="alert alert-error text-sm mx-2 my-1 shrink-0">{error}</div>{/if}

    <!-- ── Meal tab ─────────────────────────────────────────────────────────── -->
    {#if activeTab === 'meal'}
      <div class="flex-1 overflow-y-auto p-3 space-y-3">
        <p class="text-xs opacity-50">{t('per_100g')}</p>

        <div class="field">
          <input id="f-name" class="input input-bordered w-full" placeholder=" " bind:value={f.name} />
          <label for="f-name">{t('fld_name')}</label>
        </div>

        <div class="grid grid-cols-2 gap-2">
          {#each ROWS as row}
            {#each row as [key, labelKey, required]}
              <div class="field">
                <input
                  id="f-{key}"
                  type="number"
                  inputmode="decimal"
                  placeholder=" "
                  class="input input-bordered w-full"
                  bind:value={f[key]}
                />
                <label for="f-{key}">
                  {t(labelKey)}{#if !required}<span class="opt"> {t('opt')}</span>{/if}
                </label>
              </div>
            {/each}
          {/each}
        </div>
      </div>

      <div class="shrink-0 p-3 border-t border-base-200">
        <button class="btn btn-primary w-full" on:click={saveMeal} disabled={saving}>
          {t('save_food')}
        </button>
      </div>

    <!-- ── Recipe tab ───────────────────────────────────────────────────────── -->
    {:else}
      <div class="flex-1 overflow-y-auto p-3 space-y-3">
        <input
          class="input input-bordered w-full"
          placeholder={t('recipe_name_ph')}
          bind:value={recipeName}
        />

        <div class="flex items-center justify-between">
          <span class="text-sm font-medium">{t('ingredients')}</span>
          <button class="btn btn-primary btn-xs" on:click={() => (showIngredientPicker = true)}>+</button>
        </div>

        <div class="border border-base-300 rounded-box overflow-hidden">
          {#if ingredients.length === 0}
            <div class="px-3 py-4 text-sm opacity-40">{t('none')}</div>
          {:else}
            {#each ingredients as ing, i}
              <div class="flex items-center justify-between px-3 py-2 border-b border-base-100 last:border-0">
                <span class="text-sm break-words flex-1">{ing.food_name}</span>
                <span class="text-sm tabular-nums opacity-60 mx-2">{ing.grams}g</span>
                <button class="btn btn-ghost btn-xs" on:click={() => removeIngredient(i)}>✕</button>
              </div>
            {/each}
          {/if}
        </div>

        <div class="field">
          <input
            id="cooked-weight"
            class="input input-bordered w-full"
            type="number"
            inputmode="decimal"
            placeholder=" "
            bind:value={cookedWeight}
          />
          <label for="cooked-weight">{t('cooked_weight_ph')}</label>
        </div>
      </div>

      <div class="shrink-0 p-3 border-t border-base-200">
        <button class="btn btn-primary w-full" on:click={saveRecipe} disabled={saving}>
          {t('save_recipe')}
        </button>
      </div>
    {/if}
  </div>
{/if}

<style>
  .field {
    position: relative;
  }

  .field input {
    height: 3.5rem;
    padding-top: 1.25rem;
    padding-bottom: 0.25rem;
  }

  .field label {
    position: absolute;
    left: 0.875rem;
    top: 50%;
    transform: translateY(-50%);
    font-size: 0.875rem;
    color: rgb(0 0 0 / 0.4);
    transition: top 0.15s ease, transform 0.15s ease, font-size 0.15s ease, color 0.15s ease;
    pointer-events: none;
    white-space: nowrap;
  }

  .field input:focus ~ label,
  .field input:not(:placeholder-shown) ~ label {
    top: 0.5rem;
    transform: none;
    font-size: 0.65rem;
    color: oklch(var(--p));
  }

  .opt {
    opacity: 0.55;
  }
</style>
