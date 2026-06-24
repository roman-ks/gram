<script>
  import { createEventDispatcher } from 'svelte'
  import { api } from './api.js'

  const dispatch = createEventDispatcher()

  // Each row: [key, label, required]
  const ROWS = [
    [['calories',     'Calories (kcal)', true],  ['protein',       'Protein (g)',       true]],
    [['carbohydrate', 'Carbs (g)',       true],  ['sugar',         'Sugar (g)',         false]],
    [['fat',          'Fat (g)',         true],  ['saturated_fat', 'Saturated fat (g)', false]],
    [['fiber',        'Fiber (g)',       false], ['salt',          'Salt (g)',          false]],
  ]

  const REQUIRED = ['calories', 'protein', 'carbohydrate', 'fat']
  const OPTIONAL = ['sugar', 'saturated_fat', 'fiber', 'salt']
  const LABELS = { calories: 'Calories', protein: 'Protein', carbohydrate: 'Carbs', fat: 'Fat' }

  let f = {
    name: '', calories: '', protein: '', carbohydrate: '', fat: '',
    saturated_fat: '', sugar: '', fiber: '', salt: '',
  }
  let error = ''
  let saving = false

  async function save() {
    error = ''
    if (!f.name.trim()) return (error = 'Name is required')
    for (const k of REQUIRED) {
      if (f[k] === '' || f[k] == null) return (error = `${LABELS[k]} is required`)
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
</script>

<div class="modal modal-open">
  <div class="modal-box">
    <h3 class="font-bold text-lg mb-4">New food <span class="opacity-50 text-sm">(per 100 g)</span></h3>

    {#if error}<div class="alert alert-error text-sm mb-3">{error}</div>{/if}

    <div class="field mb-3">
      <input id="f-name" class="input input-bordered w-full" placeholder=" " bind:value={f.name} />
      <label for="f-name">Name</label>
    </div>

    <div class="grid grid-cols-2 gap-2">
      {#each ROWS as row}
        {#each row as [key, label, required]}
          <div class="field">
            <input id="f-{key}" type="number" inputmode="decimal" placeholder=" "
                   class="input input-bordered w-full" bind:value={f[key]} />
            <label for="f-{key}">
              {label}{#if !required}<span class="opt"> opt</span>{/if}
            </label>
          </div>
        {/each}
      {/each}
    </div>

    <div class="modal-action">
      <button class="btn btn-ghost" on:click={() => dispatch('close')}>Cancel</button>
      <button class="btn btn-primary" on:click={save} disabled={saving}>Save food</button>
    </div>
  </div>
</div>

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
