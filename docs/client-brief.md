# The ask

*Fictional inbound brief — the "client email" that frames this portfolio case study. Lumira and Mara are not real; this is the origin story for the demo, in the same spirit as [[al-noir]] and [[cassian-voicu]].*

> Hi,
>
> I came across your portfolio (loved the Cassian & Voicu site, by the way — the booking flow felt way more real than most demo sites I've seen) and I think you might be a good fit for what I'm trying to build.
>
> I'm putting together a skincare brand called Lumira. The core idea: most people buy skincare products by guessing — they don't know what actually fits their skin, so they end up with a bathroom shelf of stuff that doesn't work together. I want the site to fix that with a quick diagnostic quiz ("what's bothering you right now" — hydration, sensitivity, breakouts, dullness, that kind of thing), and based on the answers, it builds an actual routine for them: separate steps for morning and evening, not just a pile of product recommendations.
>
> A few things that matter to me:
>
> - People need to be able to create an account and save their routine — I don't want them redoing the quiz every time they come back.
> - The vibe should feel soft and approachable, not clinical. Think more Glossier than a dermatology clinic. I was thinking pastel — pink, lavender, cream — playful but still clean, not childish.
> - My audience skews younger, Gen Z/millennial, and honestly a good chunk of them aren't in Romania, so I'd want the site itself in English.
> - I don't need this to look like a huge tech platform. Simple, fast, good-looking, and the quiz-to-routine flow needs to feel smooth — that's the whole point of the product.
>
> I'm early stage, so I don't have real product photography yet — happy to start with placeholder/sample products if that helps move faster.
>
> Could you put together a proposal for me? I'd love to know what this would look like in phases (I assume the diagnostic + routine builder is the core, and things like the product catalog or account history could come after), roughly what it'd cost, and how long it'd realistically take.
>
> Looking forward to hearing from you.
>
> Best,
> Mara — Founder, Lumira

## What this became

Everything Mara asked for in the brief now exists in this repo:

- Diagnostic quiz → generated AM/PM routine (`routines/diagnostics.py`, section 4-5 of `docs/brand-brief.md`).
- Accounts with saved routine history (`routines/views.py`: `signup`, `login`, `my_routines`).
- Soft pastel visual system in English copy (`static/css/style.css`, `docs/concept-brief.md`).
- A filterable product catalog (`/products/`) as the phase-3 add-on she flagged.

See `docs/proposal.md` for the phased proposal this brief turned into.
