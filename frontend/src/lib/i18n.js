const T = {
  en: {
    kcal_today: 'kcal today',
    no_items: 'No items yet',
    slot_breakfast: 'Breakfast',
    slot_lunch: 'Lunch',
    slot_dinner: 'Dinner',
    slot_snack: 'Snack',
    src_recent: 'Recent (same meal)',
    src_top_slot: 'Top this slot',
    src_top_overall: 'Top overall',
    none: '— none —',
    add_missing: '+ Add missing',
    grams_ph: 'grams',
    err_pick: 'Pick a food and enter a weight',
    modal_title: 'New food',
    per_100g: 'per 100 g',
    fld_name: 'Name',
    fld_calories: 'Calories (kcal)',
    fld_protein: 'Protein (g)',
    fld_carbohydrate: 'Carbs (g)',
    fld_sugar: 'Sugar (g)',
    fld_fat: 'Fat (g)',
    fld_saturated_fat: 'Saturated fat (g)',
    fld_fiber: 'Fiber (g)',
    fld_salt: 'Salt (g)',
    lbl_calories: 'Calories',
    lbl_protein: 'Protein',
    lbl_carbohydrate: 'Carbs',
    lbl_fat: 'Fat',
    opt: 'opt',
    cancel: 'Cancel',
    save_food: 'Save food',
    err_name_req: 'Name is required',
    err_field_req: (label) => `${label} is required`,
  },
  uk: {
    kcal_today: 'ккал сьогодні',
    no_items: 'Ще немає записів',
    slot_breakfast: 'Сніданок',
    slot_lunch: 'Обід',
    slot_dinner: 'Вечеря',
    slot_snack: 'Перекус',
    src_recent: 'Нещодавні (цей прийом)',
    src_top_slot: 'Топ цього прийому',
    src_top_overall: 'Топ загалом',
    none: '— немає —',
    add_missing: '+ Додати відсутній',
    grams_ph: 'грами',
    err_pick: 'Оберіть страву та введіть вагу',
    modal_title: 'Нова страва',
    per_100g: 'на 100 г',
    fld_name: 'Назва',
    fld_calories: 'Калорії (ккал)',
    fld_protein: 'Білки (г)',
    fld_carbohydrate: 'Вуглеводи (г)',
    fld_sugar: 'Цукор (г)',
    fld_fat: 'Жири (г)',
    fld_saturated_fat: 'Насичені жири (г)',
    fld_fiber: 'Клітковина (г)',
    fld_salt: 'Сіль (г)',
    lbl_calories: 'Калорії',
    lbl_protein: 'Білки',
    lbl_carbohydrate: 'Вуглеводи',
    lbl_fat: 'Жири',
    opt: 'дод',
    cancel: 'Скасувати',
    save_food: 'Зберегти страву',
    err_name_req: "Назва обов'язкова",
    err_field_req: (label) => `${label} обов'язково`,
  },
}

function detectLang() {
  // URL param ?lang= takes precedence (useful for testing and manual override)
  if (typeof location !== 'undefined') {
    const param = new URLSearchParams(location.search).get('lang')
    if (param) return param.toLowerCase().startsWith('uk') ? 'uk' : 'en'
  }
  const langs = typeof navigator !== 'undefined'
    ? (navigator.languages?.length ? Array.from(navigator.languages) : [navigator.language ?? 'en'])
    : ['en']
  for (const l of langs) {
    if (l && l.toLowerCase().startsWith('uk')) return 'uk'
  }
  return 'en'
}

export const lang = detectLang()

export function t(key, ...args) {
  const entry = T[lang]?.[key] ?? T.en[key]
  if (entry === undefined) return key
  return typeof entry === 'function' ? entry(...args) : entry
}
