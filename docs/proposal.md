# Proposal — Lumira

*Reply to the brief in `docs/client-brief.md`. Portfolio artifact: this is the proposal the case study is built around, not an email actually sent anywhere.*

---

Hi Mara,

Thanks for the kind words about Cassian & Voicu — glad the booking flow read as real, that's always the goal.

Lumira is a good match for how I like to scope these: one sharp core loop (diagnostic → routine), proven first, with everything else layered on once that loop actually feels good. Here's how I'd phase it.

## Phase 1 — Diagnostic & routine builder (core)

The whole point of the product, so it goes first and gets the most attention:

- 4-question quiz: main concern, skin type, experience level, optional preferences (fragrance-free / vegan).
- Routine engine: concern picks the key active for the treatment step, skin type filters product texture, experience level sets routine complexity (3 steps for a beginner, up to 4-5 for someone experienced) — so the result never feels like a generic six-step regimen.
- Routine result screen: morning and evening, each step with a plain-language reason it's there.
- Visual system: pastel palette (cream/pink/lavender + a dark plum anchor so it doesn't go flat), the type pairing you liked, English copy throughout.

**Timeline:** 1.5–2 weeks. **Cost:** $2,400.

## Phase 2 — Accounts & routine history

Ships right after, since "don't make me redo the quiz" was one of your must-haves:

- Sign up / log in, save the routine that came out of the quiz.
- "My routines" dashboard — current routine flagged, past ones kept, one click to redo the diagnostic.

**Timeline:** 3–5 days. **Cost:** $1,000.

## Phase 3 — Product catalog

A browsable `/products` page, filterable by concern and skin type, using the same catalog the routine engine already draws from — so it's mostly wiring up a view onto data that already exists, not new modeling.

**Timeline:** 2–3 days. **Cost:** $700.

---

## Phase 4 — Cart & checkout (Stripe, test mode)

Added once phases 1-3 were live and you decided you wanted to actually sell, not just recommend:

- Session-based cart (add from the catalog, or "add routine to cart" in one click from a result), a cart page with removal and running total.
- Stripe Checkout (test mode) for the actual payment — no card numbers touch our server.
- A webhook (`checkout.session.completed`) records the paid order server-side, independent of whether the customer's browser makes it back to the success page — the more reliable pattern than trusting the redirect alone.

**Timeline:** 4–6 days. **Cost:** $1,300.

---

**Total for phases 1-4: ~4–5 weeks, $5,400.** Placeholder product copy and fictive pricing throughout — no real photography needed to start, exactly as you said. Test-mode Stripe only — no real charges, by design, until you're ready to go live with real Stripe keys.

## What I'd still hold off on

- A subscription/recurring-box model — only makes sense once you've picked a business model (private label vs. affiliate) for real.
- Merchandising tools for managing the catalog beyond Django admin.
- Real Stripe live-mode keys, shipping/tax calculation, order emails — needed before this could take real money.

Happy to start on Phase 1 as soon as you give the go-ahead.

Best,
Andreea

---

*Status in this repo: all four phases above are built — see `routines/diagnostics.py`, `routines/views.py` (`signup`/`my_routines`), the `/products/` catalog view, and `routines/cart.py` + the `checkout*` views for Phase 4.*
