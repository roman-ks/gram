<script>
  import { createEventDispatcher } from 'svelte'
  import { api } from './api.js'

  const dispatch = createEventDispatcher()

  // required first, then optional label fields
  const REQUIRED = [
    ['calories', 'Calories (kcal)'],
    ['protein', 'Protein (g)'],
    ['carbohydrate', 'Carbs (g)'],
    ['fat', 'Fat (g)'],
  ]
  const OPTIONAL = [
    ['saturated_fat', 'Saturated (g)'],
    ['sugar', 'Sugar (g)'],
    ['fiber', 'Fiber (g)'],
    ['salt', 'Salt (g)'],
  ]

  let f = {
    name: '', calories: '', protein: '', carbohydrate: '', fat: '',
    saturated_fat: '', sugar: '', fiber: '', salt: '',
  }
  let error = ''
  let saving = false

  async function save() {
    error = ''
    if (!f.name.trim()) return (error = 'Name is required')
    for (const [k, label] of REQUIRED) {
      if (f[k] === '' || f[k] == null) return (error = `${label} is required`)
    }
    saving = true
    try {
      const body = { name: f.name.trim() }
      for (const [k] of REQUIRED) body[k] = Number(f[k])
      for (const [k] of OPTIONAL) body[k] = f[k] === '' ? null : Number(f[k])
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
    <h3 class="font-bold text-lg mb-3">New food <span class="opacity-50 text-sm">(per 100 g)</span></h3>

    {#if error}<div class="alert alert-error text-sm mb-3">{error}</div>{/if}

    <input class="input input-bordered w-full mb-2" placeholder="Name" bind:value={f.name} />
    <div class="grid grid-cols-2 gap-2">
      {#each REQUIRED as [k, label]}
        <input class="input input-bordered" type="number" inputmode="decimal"
               placeholder={label} bind:value={f[k]} />
      {/each}
      {#each OPTIONAL as [k, label]}
        <input class="input input-bordered" type="number" inputmode="decimal"
               placeholder={label + ' · opt'} bind:value={f[k]} />
      {/each}
    </div>

    <div class="modal-action">
      <button class="btn btn-ghost" on:click={() => dispatch('close')}>Cancel</button>
      <button class="btn btn-primary" on:click={save} disabled={saving}>Save food</button>
    </div>
  </div>
</div>
