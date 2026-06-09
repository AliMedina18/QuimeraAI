"""
r08_flowbite.py - Integracion con Flowbite UI Library
Ensena a Gemini a usar Flowbite JS para interactividad y sus patrones
de componentes para diseños mas creativos y pulidos.
"""

FLOWBITE_COMPONENTS = """
## FLOWBITE UI LIBRARY - USE SELECTIVELY, NOT ALL AT ONCE

### THE RULE: Choose 2-4 components maximum per site
Read the brief and DESIGN.md first. Then pick ONLY the components that genuinely serve
that specific site. A photography portfolio needs a gallery and a contact form — not an
accordion, stepper, timeline, AND pricing toggle. Adding components that don't fit the
brief makes the site look chaotic and generic.

DO NOT: use every component just because it exists in this catalog.
DO: choose the 2-4 components most relevant to the brief's purpose.

### CDN LOADING (add only when you use at least one interactive component)
Place before </body>:
```
<script src="https://cdn.jsdelivr.net/npm/flowbite@2.3.0/dist/flowbite.min.js"></script>
```

This single script enables data-* attribute components (accordion, modal, drawer, dropdown,
tabs, toast, banner, popover). Only include it if you actually use one of these.
DO NOT load flowbite.min.css — style everything with DESIGN.md custom CSS variables instead.

### SELECTION GUIDE — match brief intent to components
Before writing any HTML, ask: "What does this site actually need?"

---

### INTERACTIVE COMPONENTS (use data-* attributes, Flowbite JS handles the rest)

#### ACCORDION / FAQ
```html
<div id="accordion-collapse" data-accordion="collapse">
  <h2 id="accordion-heading-1">
    <button type="button"
      class="accordion-trigger"
      data-accordion-target="#accordion-body-1"
      aria-expanded="false"
      aria-controls="accordion-body-1">
      <span>Question text here</span>
      <svg class="accordion-icon" width="16" height="16" fill="none" viewBox="0 0 24 24">
        <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m19 9-7 7-7-7"/>
      </svg>
    </button>
  </h2>
  <div id="accordion-body-1" class="hidden" aria-labelledby="accordion-heading-1">
    <div class="accordion-content">Answer text here</div>
  </div>
</div>
```
Style .accordion-trigger, .accordion-icon (rotate 180deg when aria-expanded=true), .accordion-content with custom CSS.

#### DROPDOWN MENU
```html
<button id="dropdownBtn" data-dropdown-toggle="dropdownMenu" type="button">
  Options
  <svg width="16" height="16" fill="none" viewBox="0 0 24 24">
    <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m19 9-7 7-7-7"/>
  </svg>
</button>
<div id="dropdownMenu" class="hidden dropdown-panel">
  <ul>
    <li><a href="#" class="dropdown-item">Option 1</a></li>
    <li><a href="#" class="dropdown-item">Option 2</a></li>
    <li><a href="#" class="dropdown-item">Option 3</a></li>
  </ul>
</div>
```
Style .dropdown-panel (position:absolute, z-index:50, background, shadow, border-radius) and .dropdown-item with custom CSS.

#### TABS
```html
<div data-tabs>
  <ul class="tabs-nav" role="tablist">
    <li role="presentation">
      <button class="tab-btn active" data-tabs-target="#tab-1" role="tab" aria-selected="true">Tab One</button>
    </li>
    <li role="presentation">
      <button class="tab-btn" data-tabs-target="#tab-2" role="tab" aria-selected="false">Tab Two</button>
    </li>
    <li role="presentation">
      <button class="tab-btn" data-tabs-target="#tab-3" role="tab" aria-selected="false">Tab Three</button>
    </li>
  </ul>
  <div>
    <div id="tab-1" role="tabpanel" class="tab-panel">Content for tab one...</div>
    <div id="tab-2" role="tabpanel" class="tab-panel hidden">Content for tab two...</div>
    <div id="tab-3" role="tabpanel" class="tab-panel hidden">Content for tab three...</div>
  </div>
</div>
```
Style .tabs-nav, .tab-btn, .tab-btn.active, .tab-panel with custom CSS.

#### MODAL (for CTAs, contact forms, demos)
```html
<!-- Trigger button -->
<button data-modal-target="cta-modal" data-modal-toggle="cta-modal" type="button" class="cta-btn">  <!-- use the same CTA button class defined in your site CSS -->
  Get Started
</button>
<!-- Modal -->
<div id="cta-modal" tabindex="-1" aria-hidden="true"
  class="hidden fixed inset-0 z-50 flex items-center justify-center bg-black/60">
  <div class="modal-card">
    <div class="modal-header">
      <h3 class="modal-title">Title Here</h3>
      <button data-modal-hide="cta-modal" type="button" class="modal-close" aria-label="Close">
        <svg width="20" height="20" fill="none" viewBox="0 0 24 24">
          <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18 17.94 6M18 18 6.06 6"/>
        </svg>
      </button>
    </div>
    <div class="modal-body">
      <!-- form or content here -->
    </div>
  </div>
</div>
```
Style .modal-card, .modal-header, .modal-title, .modal-close, .modal-body with custom CSS.

#### MOBILE NAVBAR TOGGLE
```html
<nav>
  <div class="nav-container">
    <a href="#" class="nav-logo">Brand</a>
    <!-- Desktop nav links (hidden on mobile via CSS) -->
    <ul class="nav-links-list">
      <li><a href="#features">Features</a></li>
      <li><a href="#pricing">Pricing</a></li>
      <li><a href="#contact">Contact</a></li>
    </ul>
    <!-- Desktop CTA button -->
    <a href="#contact" class="btn btn-primary nav-cta">Contactar</a>
    <!-- Hamburger (only on mobile) -->
    <button data-collapse-toggle="mobile-menu" type="button" class="nav-hamburger" aria-expanded="false">
      <svg width="24" height="24" fill="none" viewBox="0 0 24 24">
        <path stroke="currentColor" stroke-linecap="round" stroke-width="2" d="M5 7h14M5 12h14M5 17h14"/>
      </svg>
    </button>
  </div>
  <!-- Mobile menu: starts hidden, Flowbite toggles .hidden -->
  <div id="mobile-menu" class="mobile-menu hidden">
    <ul>
      <li><a href="#features">Features</a></li>
      <li><a href="#pricing">Pricing</a></li>
      <li><a href="#contact">Contact</a></li>
    </ul>
    <a href="#contact" class="btn btn-primary">Contactar</a>
  </div>
</nav>
```

CRITICAL RULES for nav CSS:
1. Nav link underline (::after) MUST target ul links only — NEVER buttons:
   CORRECT: .nav-links-list a::after { ... }
   WRONG:   .nav-links a::after { ... }   ← this hits .btn elements too, adding a line under them
2. Flowbite toggles .hidden class on #mobile-menu — do NOT add custom .open class logic
3. .hidden { display: none !important; } must be defined globally (already required by Flowbite)
4. Add .scrolled class to header via JS at scrollY > 50 (Flowbite does NOT handle this).

---

### CREATIVE COMPONENT PATTERNS (visual structure — style with DESIGN.md CSS vars)

#### TIMELINE (for history, process steps, roadmap)
```html
<ol class="timeline">
  <li class="timeline-item">
    <div class="timeline-dot"></div>
    <div class="timeline-content">
      <time class="timeline-date">2024</time>
      <h3 class="timeline-title">Milestone title</h3>
      <p class="timeline-body">Description of this milestone.</p>
    </div>
  </li>
  <!-- repeat -->
</ol>
```
CSS: .timeline { position:relative; padding-left:2rem; } .timeline-item { position:relative; margin-bottom:2.5rem; }
.timeline-dot { position:absolute; left:-2.25rem; top:0.25rem; width:12px; height:12px; border-radius:50%; background:var(--color-primary); }
.timeline::before { content:''; position:absolute; left:-1.75rem; top:0; bottom:0; width:2px; background:var(--color-border,#e5e7eb); }

#### STEPPER (for onboarding, how-it-works, process)
```html
<ol class="stepper">
  <li class="stepper-item">
    <div class="stepper-number">01</div>
    <div class="stepper-content">
      <h3 class="stepper-title">Step one</h3>
      <p class="stepper-desc">Brief explanation.</p>
    </div>
  </li>
  <!-- repeat for steps -->
</ol>
```
CSS: .stepper { display:flex; gap:2rem; } (horizontal) or flex-direction:column (vertical)
.stepper-number { font-size:3rem; font-weight:800; color:var(--color-primary); opacity:0.2; }
.stepper-item::after { content:''; flex:1; height:2px; background:var(--color-primary); } (connector line)

#### BADGE / PILL (for features, tags, status indicators)
```html
<span class="badge badge-primary">New</span>
<span class="badge badge-success">Available</span>
<span class="badge badge-outline">Open Source</span>
```
CSS: .badge { display:inline-flex; align-items:center; padding:2px 10px; font-size:0.75rem; font-weight:600; border-radius:9999px; }
.badge-primary { background:var(--color-primary); color:#fff; }
.badge-success { background:var(--color-success,#22c55e); color:#fff; }
.badge-outline { border:1px solid var(--color-primary); color:var(--color-primary); background:transparent; }
Use badges to tag features in feature cards, label pricing tiers, highlight status.

#### RATING STARS (for testimonials, reviews)
```html
<div class="rating" aria-label="5 out of 5 stars">
  <svg class="star filled" viewBox="0 0 22 20" width="20" height="20">
    <path d="M20.924 7.625a1.523 1.523 0 0 0-1.238-1.044l-5.051-.734-2.259-4.577a1.534 1.534 0 0 0-2.752 0L7.365 5.847l-5.051.734A1.535 1.535 0 0 0 1.463 9.2l3.656 3.563-.863 5.031a1.532 1.532 0 0 0 2.226 1.616L11 17.033l4.518 2.375a1.534 1.534 0 0 0 2.226-1.617l-.863-5.03L20.537 9.2a1.523 1.523 0 0 0 .387-1.575Z"/>
  </svg>
  <!-- repeat SVG 5x for 5 stars -->
</div>
```
CSS: .star { fill:var(--color-accent,#f59e0b); } .star.empty { fill:var(--color-border,#d1d5db); }
Place above testimonial quotes. Add name + role below.

#### PROGRESS BAR (for stats, skills, achievements)
```html
<div class="progress-wrap">
  <div class="progress-label">
    <span>Customer Satisfaction</span>
    <span>97%</span>
  </div>
  <div class="progress-track">
    <div class="progress-fill" style="width: 97%"></div>
  </div>
</div>
```
CSS: .progress-track { background:var(--color-surface-variant,#f3f4f6); border-radius:9999px; height:8px; }
.progress-fill { background:var(--color-primary); border-radius:9999px; height:100%; transition:width 1s ease; }
Animate width from 0 to final value using IntersectionObserver .visible class.

#### STAT CARD with ICON
```html
<div class="stat-card">
  <div class="stat-icon">
    <svg width="28" height="28" fill="none" viewBox="0 0 24 24">
      <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 15v4m6-6v6m6-4v4m6-6v6M3 11l6-5 6 5 5.5-5.5"/>
    </svg>
  </div>
  <div class="stat-number">24,000+</div>
  <div class="stat-label">Active Users</div>
</div>
```
CSS: .stat-icon { width:56px; height:56px; border-radius:var(--radius-card,12px); background:var(--color-primary); display:flex; align-items:center; justify-content:center; color:#fff; margin-bottom:1rem; }

---

### COMPONENT SELECTION (pick only what fits the brief — ignore the rest)

| Brief mentions...         | Use this component            |
|---------------------------|-------------------------------|
| FAQ, questions, help      | Accordion                     |
| Process, how it works     | Stepper or Timeline           |
| History, milestones, road | Timeline                      |
| Testimonials, reviews     | Rating stars + quote card     |
| Navigation menu           | Navbar + Drawer (mobile)      |
| Features / tags           | Badges on feature cards       |
| Stats, achievements       | Progress bars + stat cards    |
| Contact, demo, sign up    | Modal on CTA + Toast feedback |
| Services, portfolio items | Tabs                          |
| Team, pricing, plans      | Dropdown for extra info       |
| Trust signals, guarantees | Alert callouts near CTA       |
| Mobile navigation         | Drawer panel                  |
| Form submit feedback      | Toast notification            |
| Contact / quote / demo    | Contact form + Toast          |
| Pricing plans / billing   | Pricing toggle (monthly/annual)|
| Pricing feature details   | Popover tooltip               |
| Product launch / promo    | Announcement banner (top)     |
| Plan comparison / features| Comparison table              |
| App / SaaS / mobile tool  | Device mockup in hero         |
| Hero social proof         | Stacked avatars + user count  |
| Every site                | Multi-column footer           |

#### TOAST NOTIFICATION (for form feedback, success/error states)
```html
<!-- Trigger: show via JS after form submit -->
<div id="toast-success" class="toast" role="alert">
  <div class="toast-icon toast-icon-success">
    <svg width="20" height="20" fill="none" viewBox="0 0 24 24">
      <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
    </svg>
  </div>
  <div class="toast-message">Message sent! We'll be in touch soon.</div>
  <button type="button" data-dismiss-target="#toast-success" aria-label="Close" class="toast-close">
    <svg width="16" height="16" fill="none" viewBox="0 0 24 24">
      <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18 17.94 6M18 18 6.06 6"/>
    </svg>
  </button>
</div>

<!-- Error variant -->
<div id="toast-error" class="toast hidden" role="alert">
  <div class="toast-icon toast-icon-error">
    <svg width="20" height="20" fill="none" viewBox="0 0 24 24">
      <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v5m0 3h.01M12 2a10 10 0 1 0 0 20A10 10 0 0 0 12 2Z"/>
    </svg>
  </div>
  <div class="toast-message">Something went wrong. Please try again.</div>
  <button type="button" data-dismiss-target="#toast-error" aria-label="Close" class="toast-close">
    <svg width="16" height="16" fill="none" viewBox="0 0 24 24">
      <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18 17.94 6M18 18 6.06 6"/>
    </svg>
  </button>
</div>
```
CSS: .toast { display:flex; align-items:center; gap:12px; padding:14px 16px; border-radius:var(--radius-card,10px); background:var(--color-surface); border:1px solid var(--color-border); box-shadow:0 4px 16px rgba(0,0,0,.10); position:fixed; bottom:24px; right:24px; z-index:100; max-width:360px; }
.toast-icon { width:36px; height:36px; border-radius:50%; display:flex; align-items:center; justify-content:center; flex-shrink:0; }
.toast-icon-success { background:var(--color-success-soft,#dcfce7); color:var(--color-success,#16a34a); }
.toast-icon-error { background:var(--color-danger-soft,#fee2e2); color:var(--color-danger,#dc2626); }
.toast-message { flex:1; font-size:0.875rem; color:var(--color-text); }
.toast-close { background:none; border:none; cursor:pointer; color:var(--color-text-muted); padding:4px; }
JS: Show toast after form submit with document.getElementById('toast-success').classList.remove('hidden').
Flowbite handles the dismiss button automatically via data-dismiss-target.

#### DRAWER (slide-in panel for mobile nav or detail panels)
```html
<!-- Trigger button -->
<button type="button" data-drawer-target="site-drawer" data-drawer-show="site-drawer" aria-controls="site-drawer" class="nav-hamburger">
  <svg width="24" height="24" fill="none" viewBox="0 0 24 24">
    <path stroke="currentColor" stroke-linecap="round" stroke-width="2" d="M5 7h14M5 12h14M5 17h14"/>
  </svg>
</button>

<!-- Drawer panel -->
<div id="site-drawer" class="drawer" tabindex="-1" aria-labelledby="drawer-title">
  <div class="drawer-header">
    <span id="drawer-title" class="drawer-title">Menu</span>
    <button type="button" data-drawer-hide="site-drawer" aria-controls="site-drawer" class="drawer-close">
      <svg width="20" height="20" fill="none" viewBox="0 0 24 24">
        <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18 17.94 6M18 18 6.06 6"/>
      </svg>
    </button>
  </div>
  <nav class="drawer-nav">
    <a href="#features" class="drawer-link">Features</a>
    <a href="#pricing" class="drawer-link">Pricing</a>
    <a href="#about" class="drawer-link">About</a>
    <a href="#contact" class="drawer-link">Contact</a>
  </nav>
  <div class="drawer-footer">
    <a href="#" class="cta-btn" style="display:block;text-align:center;">Get Started</a>
  </div>
</div>
```
CSS: .drawer { position:fixed; top:0; left:0; z-index:50; height:100vh; padding:1.5rem; overflow-y:auto; transform:translateX(-100%); transition:transform 0.3s ease; background:var(--color-surface); width:min(320px,85vw); border-right:1px solid var(--color-border); }
Flowbite JS toggles the transform automatically. Use instead of the basic hamburger toggle for richer mobile experience.
.drawer-header { display:flex; justify-content:space-between; align-items:center; padding-bottom:1rem; margin-bottom:1.5rem; border-bottom:1px solid var(--color-border); }
.drawer-nav { display:flex; flex-direction:column; gap:0.25rem; }
.drawer-link { padding:0.75rem 1rem; border-radius:var(--radius-sm,6px); color:var(--color-text); text-decoration:none; font-weight:500; }
.drawer-link:hover { background:var(--color-surface-variant,#f5f5f5); }
.drawer-footer { margin-top:2rem; }

#### ALERT CALLOUT (trust signals, disclaimers, feature highlights — no JS needed)
```html
<!-- Info: highlight a key benefit or policy -->
<div class="alert alert-info" role="alert">
  <svg class="alert-icon" width="20" height="20" fill="none" viewBox="0 0 24 24">
    <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 11h2v5m-2 0h4m-2.592-8.5h.01M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z"/>
  </svg>
  <div><span class="alert-label">Free for 30 days.</span> No credit card required. Cancel anytime.</div>
</div>

<!-- Success: social proof or guarantee -->
<div class="alert alert-success" role="alert">
  <svg class="alert-icon" width="20" height="20" fill="none" viewBox="0 0 24 24">
    <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
  </svg>
  <div><span class="alert-label">Money-back guarantee.</span> If you're not satisfied within 30 days, we'll refund you in full.</div>
</div>

<!-- Warning: urgency or limitation -->
<div class="alert alert-warning" role="alert">
  <svg class="alert-icon" width="20" height="20" fill="none" viewBox="0 0 24 24">
    <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v4m0 4h.01M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0Z"/>
  </svg>
  <div><span class="alert-label">Limited spots available.</span> We only accept 50 clients per month.</div>
</div>
```
CSS: .alert { display:flex; align-items:flex-start; gap:12px; padding:14px 16px; border-radius:var(--radius-sm,8px); font-size:0.875rem; margin-bottom:1rem; }
.alert-icon { flex-shrink:0; margin-top:1px; }
.alert-label { font-weight:600; }
.alert-info { background:color-mix(in srgb, var(--color-primary) 10%, white); color:var(--color-primary); border-left:3px solid var(--color-primary); }
.alert-success { background:#f0fdf4; color:#166534; border-left:3px solid #16a34a; }
.alert-warning { background:#fffbeb; color:#92400e; border-left:3px solid #f59e0b; }
Use alert callouts near CTAs, pricing sections, or form fields for trust-building.

---


#### CONTACT FORM (use for any contact/quote/demo section — floating labels look polished)
```html
<form class="contact-form" id="contact-form">
  <!-- Two-column row -->
  <div class="form-row">
    <div class="form-field">
      <label for="cf-name" class="form-label">Full name</label>
      <input type="text" id="cf-name" name="name" class="form-input" placeholder="Jane Smith" required />
    </div>
    <div class="form-field">
      <label for="cf-email" class="form-label">Email address</label>
      <input type="email" id="cf-email" name="email" class="form-input" placeholder="jane@company.com" required />
    </div>
  </div>
  <!-- Single-column row -->
  <div class="form-field">
    <label for="cf-company" class="form-label">Company (optional)</label>
    <input type="text" id="cf-company" name="company" class="form-input" placeholder="Acme Inc." />
  </div>
  <div class="form-field">
    <label for="cf-message" class="form-label">Message</label>
    <textarea id="cf-message" name="message" rows="4" class="form-input form-textarea" placeholder="Tell us about your project..." required></textarea>
  </div>
  <button type="submit" class="cta-btn form-submit">Send message</button>
</form>
```
CSS:
.contact-form { display:flex; flex-direction:column; gap:1.25rem; }
.form-row { display:grid; grid-template-columns:1fr 1fr; gap:1.25rem; }
@media (max-width:640px) { .form-row { grid-template-columns:1fr; } }
.form-field { display:flex; flex-direction:column; gap:0.375rem; }
.form-label { font-size:0.875rem; font-weight:500; color:var(--color-text); }
.form-input { padding:0.625rem 0.875rem; background:var(--color-surface-variant,#f9fafb); border:1px solid var(--color-border,#e5e7eb); border-radius:var(--radius-sm,8px); font-size:0.875rem; color:var(--color-text); transition:border-color 0.15s, box-shadow 0.15s; outline:none; width:100%; }
.form-input:focus { border-color:var(--color-primary); box-shadow:0 0 0 3px color-mix(in srgb, var(--color-primary) 15%, transparent); }
.form-textarea { resize:vertical; min-height:120px; }
.form-submit { width:100%; padding:0.75rem; font-size:1rem; }
JS: Add to form submit handler — show toast-success on success, toast-error on network error.
```js
document.getElementById('contact-form').addEventListener('submit', function(e) {
  e.preventDefault();
  document.getElementById('toast-success').classList.remove('hidden');
  this.reset();
  setTimeout(() => document.getElementById('toast-success').classList.add('hidden'), 4000);
});
```

#### FLOATING LABEL INPUT (use when form feels too plain — premium feel)
```html
<!-- Outlined floating label variant -->
<div class="float-field">
  <input type="text" id="fl-name" class="float-input" placeholder=" " required />
  <label for="fl-name" class="float-label">Full name</label>
</div>
```
CSS:
.float-field { position:relative; }
.float-input { block:display; width:100%; padding:1rem 0.875rem 0.5rem; background:transparent; border:1px solid var(--color-border,#e5e7eb); border-radius:var(--radius-sm,8px); font-size:0.875rem; color:var(--color-text); outline:none; }
.float-input:focus { border-color:var(--color-primary); }
.float-label { position:absolute; top:50%; left:0.875rem; transform:translateY(-50%); font-size:0.875rem; color:var(--color-text-muted,#9ca3af); pointer-events:none; transition:all 0.15s; background:var(--color-surface); padding:0 4px; }
.float-input:focus ~ .float-label,
.float-input:not(:placeholder-shown) ~ .float-label { top:0; font-size:0.75rem; color:var(--color-primary); }
Use floating labels when the design aesthetic from DESIGN.md is premium/minimal.

#### PRICING TOGGLE (monthly / annual switch — pure CSS, no Flowbite JS needed)
```html
<div class="pricing-toggle">
  <span class="toggle-label">Monthly</span>
  <label class="toggle-switch">
    <input type="checkbox" id="billing-toggle" onchange="switchBilling(this)">
    <span class="toggle-track"></span>
  </label>
  <span class="toggle-label">Annual <span class="badge badge-success">Save 20%</span></span>
</div>
<!-- Price elements get data-monthly and data-annual attrs -->
<span class="price" data-monthly="49" data-annual="39">$49</span>
```
CSS:
.pricing-toggle { display:flex; align-items:center; gap:0.75rem; justify-content:center; margin-bottom:2.5rem; }
.toggle-label { font-size:0.9rem; font-weight:500; color:var(--color-text); }
.toggle-switch { position:relative; display:inline-block; width:44px; height:24px; }
.toggle-switch input { opacity:0; width:0; height:0; }
.toggle-track { position:absolute; inset:0; background:var(--color-border,#d1d5db); border-radius:9999px; cursor:pointer; transition:background 0.2s; }
.toggle-track::after { content:''; position:absolute; width:18px; height:18px; left:3px; top:3px; background:#fff; border-radius:50%; transition:transform 0.2s; }
input:checked + .toggle-track { background:var(--color-primary); }
input:checked + .toggle-track::after { transform:translateX(20px); }
JS:
```js
function switchBilling(toggle) {
  const key = toggle.checked ? 'annual' : 'monthly';
  document.querySelectorAll('.price').forEach(el => {
    el.textContent = '$' + el.dataset[key];
  });
}
```
Use whenever brief mentions pricing, plans, or subscriptions.

#### POPOVER TOOLTIP (for pricing feature explanations, glossary terms)
```html
<!-- Trigger -->
<button data-popover-target="pop-feature" type="button" class="popover-trigger" aria-describedby="pop-feature">
  <svg width="16" height="16" fill="none" viewBox="0 0 24 24">
    <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 11h2v5m-2 0h4m-2.592-8.5h.01M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z"/>
  </svg>
</button>
<!-- Popover panel -->
<div data-popover id="pop-feature" role="tooltip" class="popover">
  <div class="popover-header">Custom domains</div>
  <div class="popover-body">Connect your own domain name to your site. Available on Pro and Enterprise plans.</div>
  <div data-popper-arrow></div>
</div>
```
CSS:
.popover-trigger { background:none; border:none; cursor:pointer; color:var(--color-text-muted,#9ca3af); padding:2px; vertical-align:middle; }
.popover-trigger:hover { color:var(--color-primary); }
.popover { position:absolute; z-index:20; width:220px; font-size:0.8125rem; background:var(--color-surface); border:1px solid var(--color-border); border-radius:var(--radius-sm,8px); box-shadow:0 4px 16px rgba(0,0,0,.10); opacity:0; visibility:hidden; transition:opacity 0.2s; }
.popover[data-show] { opacity:1; visibility:visible; }
.popover-header { padding:0.5rem 0.75rem; font-weight:600; color:var(--color-text); border-bottom:1px solid var(--color-border); }
.popover-body { padding:0.5rem 0.75rem; color:var(--color-text-muted,#6b7280); line-height:1.5; }
Flowbite JS handles show/hide via data-popover-target. Place inside pricing table cells or feature lists.

---


#### ANNOUNCEMENT BANNER (sticky top bar for launches, promos, announcements)
```html
<div id="top-banner" tabindex="-1"
  class="site-banner">
  <div class="banner-content">
    <svg class="banner-icon" width="18" height="18" fill="none" viewBox="0 0 24 24">
      <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 9H5a1 1 0 0 0-1 1v4a1 1 0 0 0 1 1h6m0-6v6m0-6 5.419-3.87A1 1 0 0 1 18 5.942v12.114a1 1 0 0 1-1.581.814L11 15m7 0a3 3 0 0 0 0-6M6 15h3v5H6v-5Z"/>
    </svg>
    <p class="banner-text">
      <span class="banner-label">New:</span>
      We just launched version 2.0 with AI-powered features.
      <a href="#features" class="banner-link">Explore what's new</a>
    </p>
  </div>
  <button type="button" data-dismiss-target="#top-banner" aria-label="Close" class="banner-close">
    <svg width="16" height="16" fill="none" viewBox="0 0 24 24">
      <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18 17.94 6M18 18 6.06 6"/>
    </svg>
  </button>
</div>
```
CSS:
.site-banner { position:fixed; top:0; left:0; right:0; z-index:60; display:flex; align-items:center; justify-content:space-between; padding:0.625rem 1.25rem; background:var(--color-primary); color:#fff; font-size:0.875rem; }
.banner-content { display:flex; align-items:center; gap:0.5rem; margin:0 auto; }
.banner-icon { flex-shrink:0; opacity:0.9; }
.banner-text { margin:0; }
.banner-label { font-weight:700; margin-right:0.25rem; }
.banner-link { font-weight:600; text-decoration:underline; color:#fff; margin-left:0.375rem; }
.banner-link:hover { opacity:0.85; }
.banner-close { background:none; border:none; cursor:pointer; color:#fff; opacity:0.8; padding:4px; flex-shrink:0; }
.banner-close:hover { opacity:1; }
/* Offset navbar so it appears below banner */
body.has-banner nav { top:42px; }
body.has-banner { padding-top:42px; }
JS: Add class 'has-banner' to body on load, remove when banner dismissed.
Flowbite JS handles the dismiss button via data-dismiss-target.
Use for: product launches, promotions, beta announcements, important notices.

#### COMPARISON TABLE (for pricing plans, feature matrices, competitor comparison)
```html
<div class="table-wrap">
  <table class="comp-table">
    <thead>
      <tr>
        <th class="comp-th comp-th-feature">Feature</th>
        <th class="comp-th">Starter</th>
        <th class="comp-th comp-th-highlight">Pro</th>
        <th class="comp-th">Enterprise</th>
      </tr>
    </thead>
    <tbody>
      <tr class="comp-row">
        <td class="comp-td-feature">Users</td>
        <td class="comp-td">1</td>
        <td class="comp-td comp-td-highlight">Up to 10</td>
        <td class="comp-td">Unlimited</td>
      </tr>
      <tr class="comp-row comp-row-alt">
        <td class="comp-td-feature">Storage</td>
        <td class="comp-td">5 GB</td>
        <td class="comp-td comp-td-highlight">50 GB</td>
        <td class="comp-td">1 TB</td>
      </tr>
      <tr class="comp-row">
        <td class="comp-td-feature">API access</td>
        <td class="comp-td">
          <svg class="check-no" width="18" height="18" fill="none" viewBox="0 0 24 24"><path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18 17.94 6M18 18 6.06 6"/></svg>
        </td>
        <td class="comp-td comp-td-highlight">
          <svg class="check-yes" width="18" height="18" fill="none" viewBox="0 0 24 24"><path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
        </td>
        <td class="comp-td">
          <svg class="check-yes" width="18" height="18" fill="none" viewBox="0 0 24 24"><path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
        </td>
      </tr>
      <tr class="comp-row comp-row-alt">
        <td class="comp-td-feature">Priority support</td>
        <td class="comp-td">
          <svg class="check-no" width="18" height="18" fill="none" viewBox="0 0 24 24"><path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18 17.94 6M18 18 6.06 6"/></svg>
        </td>
        <td class="comp-td comp-td-highlight">
          <svg class="check-yes" width="18" height="18" fill="none" viewBox="0 0 24 24"><path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
        </td>
        <td class="comp-td">
          <svg class="check-yes" width="18" height="18" fill="none" viewBox="0 0 24 24"><path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
        </td>
      </tr>
    </tbody>
  </table>
</div>
```
CSS:
.table-wrap { overflow-x:auto; border-radius:var(--radius-card,12px); border:1px solid var(--color-border,#e5e7eb); box-shadow:0 1px 4px rgba(0,0,0,.06); }
.comp-table { width:100%; border-collapse:collapse; font-size:0.9rem; }
.comp-th { padding:1rem 1.25rem; text-align:center; font-weight:600; color:var(--color-text); background:var(--color-surface-variant,#f9fafb); border-bottom:2px solid var(--color-border); }
.comp-th-feature { text-align:left; }
.comp-th-highlight { background:color-mix(in srgb, var(--color-primary) 8%, white); color:var(--color-primary); border-bottom-color:var(--color-primary); }
.comp-row td { padding:0.875rem 1.25rem; text-align:center; color:var(--color-text); border-bottom:1px solid var(--color-border); }
.comp-row-alt td { background:var(--color-surface-variant,#f9fafb); }
.comp-td-feature { text-align:left; font-weight:500; }
.comp-td-highlight { background:color-mix(in srgb, var(--color-primary) 5%, white) !important; }
.check-yes { color:var(--color-success,#16a34a); display:inline-block; }
.check-no { color:var(--color-border,#d1d5db); display:inline-block; }
Use for: SaaS pricing comparison, feature matrices, plan comparisons. The highlighted column draws attention to the recommended plan.

---


#### DEVICE MOCKUPS (show product screenshots inside phone/laptop/tablet frames)
Use in hero or product showcase sections for SaaS, mobile apps, or web tools.
No Flowbite JS needed — pure CSS structure. Replace the img src with a card_* image URL.

**Phone mockup** (mobile app showcase):
```html
<div class="mockup-phone">
  <!-- Side buttons (decorative) -->
  <div class="mockup-btn mockup-btn-vol-up"></div>
  <div class="mockup-btn mockup-btn-vol-dn"></div>
  <div class="mockup-btn mockup-btn-power"></div>
  <!-- Screen -->
  <div class="mockup-screen mockup-screen-phone">
    <img src="REPLACE_WITH_card_1_URL" alt="App screenshot" class="mockup-img" loading="lazy">
  </div>
</div>
```
CSS:
.mockup-phone { position:relative; margin:0 auto; border:12px solid var(--color-mockup-frame,#1f2937); border-radius:2.5rem; width:240px; height:480px; box-shadow:0 20px 60px rgba(0,0,0,.25); }
.mockup-btn { position:absolute; background:var(--color-mockup-frame,#1f2937); border-radius:2px; }
.mockup-btn-vol-up { width:3px; height:36px; left:-15px; top:72px; }
.mockup-btn-vol-dn { width:3px; height:36px; left:-15px; top:118px; }
.mockup-btn-power { width:3px; height:52px; right:-15px; top:108px; }
.mockup-screen-phone { border-radius:2rem; overflow:hidden; width:100%; height:100%; }
.mockup-img { width:100%; height:100%; object-fit:cover; display:block; }

**Laptop mockup** (web app / dashboard showcase):
```html
<div class="mockup-laptop-wrap">
  <div class="mockup-laptop-screen">
    <div class="mockup-screen mockup-screen-laptop">
      <img src="REPLACE_WITH_card_1_URL" alt="Dashboard screenshot" class="mockup-img" loading="lazy">
    </div>
  </div>
  <div class="mockup-laptop-base">
    <div class="mockup-laptop-notch"></div>
  </div>
</div>
```
CSS:
.mockup-laptop-wrap { margin:0 auto; max-width:560px; }
.mockup-laptop-screen { border:8px solid var(--color-mockup-frame,#1f2937); border-radius:0.75rem 0.75rem 0 0; background:var(--color-mockup-frame,#1f2937); }
.mockup-screen-laptop { border-radius:0.375rem; overflow:hidden; aspect-ratio:16/10; }
.mockup-laptop-base { background:var(--color-mockup-frame,#1f2937); border-radius:0 0 0.75rem 0.75rem; height:18px; position:relative; }
.mockup-laptop-notch { position:absolute; left:50%; transform:translateX(-50%); top:0; width:80px; height:8px; background:var(--color-mockup-frame,#1f2937); border-radius:0 0 6px 6px; }

**Layout: phone + copy side by side** (hero pattern):
```html
<section class="mockup-hero">
  <div class="mockup-hero-copy">
    <h1>Your headline here</h1>
    <p>Supporting text about the product.</p>
    <a href="#" class="cta-btn">  <!-- use the same CTA button class defined in your site CSS -->Get started</a>
  </div>
  <div class="mockup-hero-visual">
    <!-- insert phone or laptop mockup here -->
  </div>
</section>
```
CSS: .mockup-hero { display:grid; grid-template-columns:1fr 1fr; gap:4rem; align-items:center; }
@media (max-width:768px) { .mockup-hero { grid-template-columns:1fr; } .mockup-hero-visual { order:-1; } }

Use when: brief mentions app, dashboard, platform, software, mobile app, SaaS tool.
Set --color-mockup-frame to match DESIGN.md dark tone (e.g. var(--color-text) or #1a1a2e).

---


#### STACKED AVATARS (social proof — "Join 10,000+ users" with overlapping faces)
```html
<div class="social-proof">
  <div class="avatar-stack">
    <img class="avatar-face" src="REPLACE_WITH_avatar_1_URL" alt="User" loading="lazy">
    <img class="avatar-face" src="REPLACE_WITH_avatar_2_URL" alt="User" loading="lazy">
    <img class="avatar-face" src="REPLACE_WITH_avatar_3_URL" alt="User" loading="lazy">
    <span class="avatar-count">+2.4k</span>
  </div>
  <p class="social-proof-text">
    <strong>10,000+</strong> teams already growing with us
  </p>
</div>
```
CSS:
.social-proof { display:flex; align-items:center; gap:0.875rem; }
.avatar-stack { display:flex; }
.avatar-face { width:40px; height:40px; border-radius:50%; border:2px solid var(--color-surface,#fff); object-fit:cover; margin-left:-10px; }
.avatar-face:first-child { margin-left:0; }
.avatar-count { width:40px; height:40px; border-radius:50%; border:2px solid var(--color-surface,#fff); background:var(--color-primary); color:#fff; font-size:0.7rem; font-weight:700; display:flex; align-items:center; justify-content:center; margin-left:-10px; }
.social-proof-text { font-size:0.875rem; color:var(--color-text-muted,#6b7280); margin:0; }
.social-proof-text strong { color:var(--color-text); }
Place directly below the hero CTA button for maximum conversion impact.
Use avatar_1, avatar_2, avatar_3 image slots from the image plan.

#### FOOTER (multi-column with social icons — use on every site)
```html
<footer class="site-footer">
  <div class="footer-inner">
    <!-- Brand column -->
    <div class="footer-brand">
      <a href="#" class="footer-logo">Brand Name</a>
      <p class="footer-tagline">Brief description of what the company does in one or two sentences.</p>
      <!-- Social icons -->
      <div class="footer-social">
        <a href="#" aria-label="Twitter" class="social-link">
          <svg width="20" height="20" fill="currentColor" viewBox="0 0 24 24"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-4.714-6.231-5.401 6.231H2.742l7.932-9.07-8.4-11.43H8.28l4.253 5.622 5.71-5.622Zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>
        </a>
        <a href="#" aria-label="GitHub" class="social-link">
          <svg width="20" height="20" fill="currentColor" viewBox="0 0 24 24"><path fill-rule="evenodd" d="M12 2a10 10 0 0 0-3.16 19.489c.5.092.682-.217.682-.482 0-.237-.008-.866-.013-1.7-2.782.603-3.369-1.341-3.369-1.341-.454-1.156-1.11-1.463-1.11-1.463-.908-.62.069-.608.069-.608 1.003.07 1.531 1.03 1.531 1.03.892 1.529 2.341 1.087 2.91.831.092-.646.35-1.086.636-1.336-2.22-.253-4.555-1.11-4.555-4.943 0-1.091.39-1.984 1.029-2.683-.103-.253-.446-1.27.098-2.647 0 0 .84-.268 2.75 1.026A9.578 9.578 0 0 1 12 6.836a9.59 9.59 0 0 1 2.504.337c1.909-1.294 2.747-1.026 2.747-1.026.546 1.377.202 2.394.1 2.647.64.699 1.028 1.592 1.028 2.683 0 3.842-2.339 4.687-4.566 4.935.359.309.678.919.678 1.852 0 1.336-.012 2.415-.012 2.743 0 .267.18.579.688.481A10.001 10.001 0 0 0 12 2Z" clip-rule="evenodd"/></svg>
        </a>
        <a href="#" aria-label="LinkedIn" class="social-link">
          <svg width="20" height="20" fill="currentColor" viewBox="0 0 24 24"><path fill-rule="evenodd" d="M12.51 8.796v1.697a3.738 3.738 0 0 1 3.288-1.684c3.455 0 4.202 2.16 4.202 4.97V19.5h-3.2v-5.072c0-1.21-.244-2.766-2.128-2.766-1.827 0-2.139 1.317-2.139 2.676V19.5h-3.19V8.796h3.168ZM7.2 6.106a1.61 1.61 0 0 1-.988 1.483 1.595 1.595 0 0 1-1.743-.348A1.607 1.607 0 0 1 5.6 4.5a1.601 1.601 0 0 1 1.6 1.606Z" clip-rule="evenodd"/><path d="M7.2 8.809H4V19.5h3.2V8.809Z"/></svg>
        </a>
      </div>
    </div>
    <!-- Link columns -->
    <div class="footer-links">
      <div class="footer-col">
        <h3 class="footer-col-title">Product</h3>
        <ul class="footer-list">
          <li><a href="#features" class="footer-link">Features</a></li>
          <li><a href="#pricing" class="footer-link">Pricing</a></li>
          <li><a href="#" class="footer-link">Changelog</a></li>
          <li><a href="#" class="footer-link">Roadmap</a></li>
        </ul>
      </div>
      <div class="footer-col">
        <h3 class="footer-col-title">Company</h3>
        <ul class="footer-list">
          <li><a href="#" class="footer-link">About</a></li>
          <li><a href="#" class="footer-link">Blog</a></li>
          <li><a href="#" class="footer-link">Careers</a></li>
          <li><a href="#contact" class="footer-link">Contact</a></li>
        </ul>
      </div>
      <div class="footer-col">
        <h3 class="footer-col-title">Legal</h3>
        <ul class="footer-list">
          <li><a href="#" class="footer-link">Privacy Policy</a></li>
          <li><a href="#" class="footer-link">Terms of Service</a></li>
          <li><a href="#" class="footer-link">Cookie Policy</a></li>
        </ul>
      </div>
    </div>
  </div>
  <!-- Bottom bar -->
  <div class="footer-bottom">
    <p class="footer-copy">&copy; 2025 Brand Name. All rights reserved.</p>
  </div>
</footer>
```
CSS:
.site-footer { background:var(--color-surface-alt,#111827); color:var(--color-text-inverse,#f9fafb); padding:4rem 0 0; margin-top:6rem; }
.footer-inner { max-width:1200px; margin:0 auto; padding:0 1.5rem 3rem; display:grid; grid-template-columns:1.5fr 2fr; gap:4rem; }
@media (max-width:768px) { .footer-inner { grid-template-columns:1fr; gap:2.5rem; } }
.footer-logo { font-size:1.25rem; font-weight:700; color:inherit; text-decoration:none; display:inline-block; margin-bottom:0.875rem; }
.footer-tagline { font-size:0.875rem; opacity:0.65; line-height:1.6; margin:0 0 1.25rem; max-width:260px; }
.footer-social { display:flex; gap:0.875rem; }
.social-link { opacity:0.6; transition:opacity 0.2s; }
.social-link:hover { opacity:1; }
.footer-links { display:grid; grid-template-columns:repeat(3,1fr); gap:2rem; }
@media (max-width:640px) { .footer-links { grid-template-columns:repeat(2,1fr); } }
.footer-col-title { font-size:0.8rem; font-weight:700; text-transform:uppercase; letter-spacing:0.08em; opacity:0.5; margin:0 0 1rem; }
.footer-list { list-style:none; padding:0; margin:0; display:flex; flex-direction:column; gap:0.625rem; }
.footer-link { font-size:0.875rem; opacity:0.7; text-decoration:none; color:inherit; transition:opacity 0.15s; }
.footer-link:hover { opacity:1; }
.footer-bottom { border-top:1px solid rgba(255,255,255,.1); padding:1.25rem 1.5rem; text-align:center; }
.footer-copy { font-size:0.8125rem; opacity:0.45; margin:0; }
IMPORTANT: Adapt footer background to DESIGN.md — dark sites use a slightly lighter shade, light sites use a dark section. Always use a contrasting footer color from the main palette.

---


### DO NOT ADD THESE UNLESS THE BRIEF EXPLICITLY NEEDS THEM
- Pricing toggle → only if brief mentions pricing plans or billing
- Stepper/Timeline → only if brief mentions process, history, or steps
- Comparison table → only if brief mentions plan comparison or features matrix
- Device mockup → only if brief mentions an app, dashboard, or software product
- Announcement banner → only if brief mentions a launch, promo, or announcement
- Modal → only if brief mentions a CTA, demo request, or contact popup
- Accordion → only if brief mentions FAQ, help center, or questions

### REQUIRED CSS: Add these base rules whenever using any Flowbite component
```css
.hidden { display: none !important; }  /* Required for Flowbite JS toggle behavior */
.cta-btn { /* Use your site's primary button style — do NOT redefine, extend existing */ }
```
DO NOT create a new `.btn-primary` or `.cta-btn` style from scratch.
Use the same button style you already defined for the rest of the site.

### STYLING RULE: Every Flowbite component must use DESIGN.md CSS variables
- Replace any color reference with: var(--color-primary), var(--color-surface), var(--color-text), etc.
- Replace any border-radius with: var(--radius-card), var(--radius-sm)
- Replace any font-family with: var(--font-body), var(--font-display)
- Do NOT hardcode color values like #3b82f6, bg-blue-500, etc.
"""
