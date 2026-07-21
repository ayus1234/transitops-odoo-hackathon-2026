---
name: TransitOps Design System
colors:
  surface: '#f8f9fa'
  surface-dim: '#d9dadb'
  surface-bright: '#f8f9fa'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f3f4f5'
  surface-container: '#edeeef'
  surface-container-high: '#e7e8e9'
  surface-container-highest: '#e1e3e4'
  on-surface: '#191c1d'
  on-surface-variant: '#424654'
  inverse-surface: '#2e3132'
  inverse-on-surface: '#f0f1f2'
  outline: '#737785'
  outline-variant: '#c3c6d6'
  surface-tint: '#0056d2'
  primary: '#0040a1'
  on-primary: '#ffffff'
  primary-container: '#0056d2'
  on-primary-container: '#ccd8ff'
  inverse-primary: '#b2c5ff'
  secondary: '#1b6d24'
  on-secondary: '#ffffff'
  secondary-container: '#a0f399'
  on-secondary-container: '#217128'
  tertiary: '#773300'
  on-tertiary: '#ffffff'
  tertiary-container: '#9c4500'
  on-tertiary-container: '#ffcfb7'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#dae2ff'
  primary-fixed-dim: '#b2c5ff'
  on-primary-fixed: '#001847'
  on-primary-fixed-variant: '#0040a1'
  secondary-fixed: '#a3f69c'
  secondary-fixed-dim: '#88d982'
  on-secondary-fixed: '#002204'
  on-secondary-fixed-variant: '#005312'
  tertiary-fixed: '#ffdbca'
  tertiary-fixed-dim: '#ffb68e'
  on-tertiary-fixed: '#331200'
  on-tertiary-fixed-variant: '#773300'
  background: '#f8f9fa'
  on-background: '#191c1d'
  surface-variant: '#e1e3e4'
typography:
  display-lg:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 40px
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  title-sm:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '600'
    lineHeight: 24px
  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  body-sm:
    fontFamily: Inter
    fontSize: 13px
    fontWeight: '400'
    lineHeight: 18px
  label-caps:
    fontFamily: Inter
    fontSize: 11px
    fontWeight: '700'
    lineHeight: 16px
    letterSpacing: 0.05em
  data-tabular:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '500'
    lineHeight: 20px
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  base: 8px
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 32px
  gutter: 16px
  sidebar_width: 240px
---

## Brand & Style
The design system is engineered for high-stakes transport logistics and enterprise resource planning. The brand personality is **authoritative, efficient, and precise**, prioritizing utility over decoration to minimize cognitive load for Fleet Managers and Dispatchers.

The visual style is **Corporate / Modern**, taking inspiration from industry leaders like Odoo and SAP Fiori. It utilizes a structured, information-dense layout that maximizes screen real estate. The UI evokes a sense of "operational control" through clear grouping, logical sequencing of data, and a systematic approach to state management.

## Colors
The palette is rooted in professional reliability. 
- **Primary (Professional Blue):** Used for primary actions, navigation selection, and branding elements. It signifies stability.
- **Success (Green):** Specifically for "Available" statuses, completed trips, and positive ROI indicators.
- **Warning (Orange):** Highlights "Pending" actions or maintenance reminders.
- **Danger (Red):** Reserved for "Suspended" drivers, "Retired" vehicles, and critical system errors.
- **Neutral Grays:** A range of grays (#F8F9FA to #212529) defines the background, borders, and secondary text, creating a soft contrast that reduces eye strain during long shifts.

## Typography
This design system uses **Inter** exclusively to leverage its exceptional legibility in data-heavy environments. 

The scale is intentionally compact. **Body-sm (13px)** is the workhorse for dense tables and sidebar navigation. **Data-tabular** utilizes monospaced numbers (tnum) to ensure that numerical values (odometer readings, costs, capacities) align perfectly in vertical columns, facilitating quick scanning. Uppercase labels are used sparingly for section headers within forms to provide clear structural anchors.

## Layout & Spacing
The system follows a strict **8px grid** to ensure mathematical harmony across all components.

**Layout Architecture:**
- **Persistent Left Sidebar:** A 240px fixed-width navigation bar for primary modules (Dashboard, Vehicles, Drivers, Trips, Maintenance, Expenses).
- **Fluid Content Area:** The main stage uses a fluid grid that expands to fill the viewport, utilizing a 12-column system for form layouts.
- **Density:** High. Margins between cards are kept at 16px (md) to maximize information visibility without clutter.

**Responsive Behavior:**
- **Desktop (>1024px):** Full sidebar expanded.
- **Tablet (768px - 1023px):** Sidebar collapses to icons only.
- **Mobile (<767px):** Sidebar becomes a bottom navigation bar or a hamburger overlay; tables reflow into "stacked" card views.

## Elevation & Depth
Depth is used functionally to indicate interactivity and grouping rather than for aesthetic flourish.

- **Level 0 (Background):** #F8F9FA. The foundation for the entire application.
- **Level 1 (Cards/Surface):** White (#FFFFFF) with a 1px border (#E0E0E0). A very subtle ambient shadow (0px 2px 4px rgba(0,0,0,0.05)) is used to lift primary content containers.
- **Level 2 (Modals/Popovers):** Higher contrast shadows (0px 8px 16px rgba(0,0,0,0.1)) to focus attention on critical inputs or filter menus.
- **Tonal Layers:** The sidebar uses a slightly darker neutral (#F1F3F5) to visually separate navigation from the workspace.

## Shapes
The shape language balances modern approachability with professional structure. 
- **Base Radius:** 8px for buttons and small input fields.
- **Large Radius (rounded-lg):** 12px for main content cards and dashboard widgets.
- **Full Radius (rounded-pill):** Used exclusively for status chips (e.g., "On Trip", "In Shop") to differentiate them from interactive buttons.

## Components
### Data Tables (The Core)
Enterprise-grade tables with fixed headers. Rows should have a subtle hover state (#F8F9FA). Action buttons (View/Edit) appear on the far right. Use "Data-tabular" typography for all numerical cells.

### Status Chips
Pill-shaped indicators with low-opacity backgrounds and high-contrast text.
- **Available:** Green background (10% opacity) / Green text.
- **On Trip:** Blue background (10% opacity) / Blue text.
- **In Shop:** Orange background (10% opacity) / Orange text.

### Form Fields
Standardized height of 36px for high density. Labels are placed above the input in `body-sm` bold. Active states use a 2px Professional Blue border.

### Primary Sidebar
Dark or light neutral background. Active items use a vertical 4px Professional Blue "active indicator" on the left edge and a subtle background tint.

### KPI Cards
Located at the top of the Dashboard. They feature a large numerical value (`display-lg`), a descriptive label, and a small trend icon or sparkline.