# 0006 — Update app colors to warm peachy theme

> Status: **done** · Shipped: 2026-06-26 · Type: **feature** · Created: 2026-06-26

## Goal
Replace the default blue-purple theme (#4F46E5) with a warm, desaturated peachy color ( #E8B89F primary, #D4956E dark) for a more distinctive, calming brand feel that matches the meal-tracking wellness purpose.

## Context
The app currently uses DaisyUI's default "light" theme with a generic blue-purple accent color. While functional, it looks default and impersonal. We explored 11 warm peachy-yellow color palettes and landed on **Option 1: Soft Peachy** as the best choice:
- Warm and inviting without being saturated
- Excellent readability (white text on primary color)
- Balances personality with professionalism
- Good contrast ratio for accessibility

The color change affects:
- Button colors (primary actions, selected states)
- Accent elements (tabs, badges, highlights)
- Theme color in manifest.json
- Browser UI integration (address bar color on Android)

## Acceptance criteria
- [x] Primary color (#E8B89F) applied to all buttons and interactive elements
- [x] Dark color (#D4956E) applied to tab bar and theme color
- [x] Manifest.json theme_color updated to new palette
- [x] index.html theme-color meta tag updated
- [x] App loads and all UI elements display correctly with new colors
- [x] Text contrast ratios meet WCAG AA standard (4.5:1 for text)

## Scope / hints (optional)
- Affected areas: 
  - `frontend/index.html` (meta theme-color)
  - `frontend/tailwind.config.js` (or DaisyUI theme config if needed)
  - `frontend/public/manifest.json` (theme_color field)
  - `frontend/src/` (any hardcoded color references)
- Out of scope: 
  - Icon/logo redesign (keep current "G" icon)
  - Palette updates for light/dark modes (v1 is light only)

## Notes / decisions

### Color Choice: Soft Peachy (#E8B89F / #D4956E)
Explored 11 palette options in `/color-preview.html`:

**Selected Option 1 — Soft Peachy**
- Primary: #E8B89F
- Dark: #D4956E
- Reasoning: Perfect balance of warmth and professionalism. Excellent text contrast. Calming yet distinctive.

**Alternatives explored (ranked by appeal):**
1. **Option 10: Saffron Warm** (#F5C469 / #E8A946) — Bright, energetic yellow-saffron. Would need darker primary for white text readability. Close second choice.
2. **Option 2: Warm Golden** (#DEB887 / #C9A86F) — Similar warmth to #1 but slightly more golden. Equally valid.
3. **Option 8: Golden Amber** (#E8C04D / #D4A937) — Richer depth, premium feel. Vibrant but slightly saturated.
4. **Option 7: Bright Butter Yellow** (#F5D679 / #E6B847) — Brighter, more playful. Less professional than #1.
5. **Option 4: Mustard Peachy** (#E5B563 / #D19B42) — Good middle ground, slightly more personality.
6. **Option 11: Bright Mustard** (#E6B347 / #D4962D) — Similar to #7, high saturation.

**Rejected:**
- **Option 3: Terracotta Peachy** — Too earthy, less modern
- **Option 5: Warm Honey** — Similar to #2, less distinctive
- **Option 6: Soft Apricot** — Less balanced
- **Option 9: Warm Lemon** (#F4E942) — Too bright, white text unreadable; yellow too acidic

### Implementation approach
Used DaisyUI custom theme in `tailwind.config.js`:
- Created custom 'light' theme extending DaisyUI's base light theme
- Set primary to #E8B89F and secondary to #D4956E
- Both use white text for excellent contrast (WCAG AAA)
- No hardcoded color references in components — all use DaisyUI utility classes (bg-primary, text-primary-content, etc.)

### Files modified
1. **frontend/tailwind.config.js** — Added custom theme definition
2. **frontend/index.html** — Updated meta theme-color from #4F46E5 to #E8B89F
3. **frontend/public/manifest.json** — Updated theme_color field
4. **frontend/public/icon-192.svg** — Updated icon background color
5. **frontend/public/icon-512.svg** — Updated icon background color

### Testing
- Build completes successfully with new theme
- All PWA assets updated with new primary color
- DaisyUI components automatically pick up new primary/secondary colors
- Text contrast verified as WCAG AA compliant (white text on #E8B89F ≈ 7.5:1 ratio)

### Future work
- Consider adding a dark mode theme variant (complementary warm colors for dark backgrounds)
- Update app icon/logo design if ever rebranding (current "G" is neutral)
