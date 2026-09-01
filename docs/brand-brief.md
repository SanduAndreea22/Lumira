# Lumira — Brief de brand & business

*Document strategic, piesă de portofoliu Andreea Tech. Completează secțiunea de piață pentru [[al-noir]] (restaurant) și [[cassian-voicu]] (appointments) cu un exemplu de e-commerce/produs personalizat.*

> **Notă privind limba:** brief-ul este redactat în română (documentul de portofoliu), dar produsul propriu-zis — site-ul/aplicația Lumira — este proiectat și va fi construit în limba engleză. Mockup-urile din `docs/assets/lumira-skincare-mock.pdf` sunt varianta de concept în română; interfața finală înlocuiește copy-ul cu text în engleză, păstrând tonul descris în secțiunea 6.

## 1. Poziționare de brand

Piața de skincare personalizat prin diagnostic are deja doi poli clari:

- **Pol clinic/prescriptiv** (tip Curology) — quiz + "recomandare" cu aer medical, rutina vine cu autoritate de specialist, model de abonament recurent.
- **Pol DIY/expert** (tip The Ordinary) — fără diagnostic; presupune că utilizatorul știe deja ce ingrediente caută (acizi, retinol, concentrații).

Lumira poate ocupa spațiul dintre cei doi poli: **diagnostic instant, fără barieră de cunoștințe și fără presiunea unui abonament forțat**. Nu trebuie nici dermatolog, nici să știi ce e niacinamida. Față de Function of Beauty (referința pentru "quiz → produs personalizat" pe haircare), Lumira rămâne mai simplă — nu promite formulare 100% custom, promite claritate: știi exact ce pui pe față și de ce.

**Rezolvat:** Lumira e brand propriu (private label) — deține linia de produse, ca Function of Beauty, nu curatoriază produse din alte branduri. Fiecare produs din catalog e Lumira; nu există model de "asistent de cumpărare"/afiliere. Asta fixează și modelul de date: `Product` nu are un câmp de brand extern editabil — implicit e „Lumira" pentru orice produs adăugat în catalog.

## 2. Public țintă detaliat

**Rezolvat:**

- **Vârstă:** toate vârstele — diagnosticul nu segmentează pe grupă de vârstă (nu există un pas de "câți ani ai" în quiz); concernul principal ("semne de îmbătrânire" vs. "imperfecțiuni") face implicit diferența, nu vârsta declarată.
- **Buget țintă:** **luxury.** Nu masstige, nu accesibil — catalogul e prețuit ca skincare premium (vezi secțiunea 5 și `routines/migrations/0005_luxury_pricing.py`). Asta ridică miza pe justificarea fiecărui produs din rutină ("de ce ți l-am pus aici" trebuie să simtă premium, nu doar corect).
- **Unde cumpără:** din Lumira direct — brand propriu (secțiunea 1), nu ghid către retaileri terți.

Ce rezultă deja din direcția vizuală aleasă (pastel modern, playful dar clean): public digital-first, confortabil cu o experiență de tip quiz/app, sensibil la estetică. Poziționarea luxury nu schimbă identitatea vizuală deja stabilită (secțiunea 6) — rămâne caldă, nu rece/corporate — dar înseamnă că tonul trebuie să sune ca lux accesibil emoțional (gen Aesop, Augustinus Bader), nu ca lux distant.

**Rămâne deschis:** nivelul de experiență cu skincare al publicului majoritar (începător complet vs. cineva cu rutină deja) — quiz-ul deja întreabă asta per utilizator (pasul 3), deci nu blochează build-ul, dar ar conta pentru ce nivel de experiență setăm ca "default"/cel mai comun în copy-ul de marketing (homepage, onboarding).

## 3. Propunere de valoare

- **Vs. cumpărat „la nimereală"**: nu mai ghicești ce produs ți se potrivește din zeci de opțiuni.
- **Vs. consultație dermatolog**: gratuit, instant, fără programare — pentru nevoi de bază, nu pentru probleme medicale.
- **Vs. research pe cont propriu** (Reddit, TikTok skincare): un răspuns structurat în 60 de secunde, nu ore de citit păreri contradictorii.
- **Vs. quiz-uri concurente**: rutina rămâne salvată în cont — nu o reiei de la zero la fiecare vizită sau cumpărare.

## 4. Logica diagnosticului

Deja stabilite: concern principal (hidratare/sensibilitate/imperfecțiuni/luminozitate/exces de sebum/semne de îmbătrânire), tip de ten, nivel de experiență.

Ce ar mai trebui luat în calcul pentru ca rutina să pară relevantă, nu superficială:

- **Rutina actuală** — dacă utilizatorul folosește deja un activ puternic (retinol, exfoliant), diagnosticul ar trebui să nu-l suprapună cu altul similar.
- **Vârstă/interval de vârstă** — influențează ce concentrații de activi sunt potrivite.
- **Alergii/ingrediente de evitat** — filtru de siguranță minim, nu profil medical detaliat.

Logica de bază: concernul principal alege **ingredientul-cheie** al rutinei (secțiunea 5); tipul de ten filtrează **textura** produselor eligibile (gel pentru ten gras, cremă bogată pentru ten uscat); nivelul de experiență decide **câți pași** primește rutina (3 pentru începători, 4-5 pentru cineva familiarizat).

## 5. Structura rutinei personalizate

Format fix, deja stabilit: **dimineața** cleanser → ser tratament → cremă hidratantă → SPF; **seara** cleanser → tratament activ → cremă de noapte.

Cum se traduce diagnosticul în produse concrete — fiecare concern principal mapează pe o categorie de ingredient-cheie pentru pasul de „tratament":

| Concern | Ingredient-cheie orientativ |
|---|---|
| Hidratare | Acid hialuronic |
| Luminozitate | Vitamina C / niacinamidă |
| Imperfecțiuni | Acid salicilic |
| Semne de îmbătrânire | Retinol (seara) |
| Sensibilitate | Centella / ceramide |
| Exces de sebum | Niacinamidă / argilă |

Cleanser, cremă și SPF rămân „stabile" ca rol în rutină — doar textura lor se ajustează după tipul de ten. Pasul de tratament e singurul care se schimbă radical în funcție de concern.

## 6. Ton și identitate de brand

- **Voce:** prietenoasă și directă, fără jargon dermato-cosmetic — ca o prietenă care se pricepe la skincare, nu ca eticheta unui laborator.
- **De evitat:** superlative goale ("revoluționar", "miraculos"), presiune de vânzare agresivă, ton rușinos în jurul imperfecțiunilor (neutru și normalizator, nu "scapă de problema ta").
- **Vizual:** deja stabilit — pastel (roz pudră, lavandă, unt), Bricolage Grotesque + Instrument Sans, iconițe desenate, nu emoji.
- **Reper de ton:** undeva între conversațional-prietenos (gen Glossier) și un instrument clar, utilitar — Lumira vinde în primul rând claritate, nu doar aspirație.
- **Limba interfeței:** engleză. Vocea de mai sus se traduce 1:1 în copy englezesc (ex. "Your skincare routine, built for your real skin." pentru headline-ul din mock), păstrând același nivel de simplitate și cald, nu formal.

## 7. Model de business (opțional — relevant doar dacă depășește stadiul de portofoliu)

Patru direcții posibile, fiecare cu implicații diferite:

- ~~**Marketplace/afiliere**~~ — exclus (secțiunea 1): Lumira nu recomandă produse din alte branduri.
- **Brand propriu (private label)** — **ales.** Lumira produce/etichetează propriile produse. Marjă mai mare, dar cost și risc de producție/stoc semnificativ — pentru stadiul de portofoliu, catalogul e fictiv (produse și prețuri demo), fără producție reală în spate.
- **Abonament pe rutină** — recurring box cu produsele din rutină. Venit predictibil, se pliază natural pe un brand propriu; rămâne o extensie posibilă peste catalogul actual, nu implementată încă.
- **Diagnostic gratuit + upsell** — quizul rămâne gratuit, monetizarea vine din produse (catalogul propriu) sau din funcții avansate (re-diagnostic prioritar, rutină extinsă).

## 8. Întrebări deschise

- ~~**Rolul brief-ului**~~ — rezolvat: **rămâne demo/portofoliu, momentan.** Nu se prezintă ca produs real, nu se colectează date reale de utilizatori. Dacă asta se schimbă vreodată, monetizarea, GDPR-ul și tot ce ține de "date sensibile" de mai jos trebuie re-evaluate serios.
- ~~**Model de produs**~~ — rezolvat: brand propriu (private label), nu curatoriere/afiliere (secțiunea 1, secțiunea 7).
- ~~**Public țintă exact**~~ — rezolvat: toate vârstele, buget luxury (secțiunea 2).
- **Monetizare** — nerelevantă cât timp rămâne demo (punctul de mai sus).
- ~~**Cât de „medical" poate deveni diagnosticul**~~ — rezolvat: **nu foarte medical, deliberat.** Diagnosticul rămâne la nivel de concern + tip de ten + experiență + preferințe (fragrance-free/vegan) — fără alergii, fără sarcină, fără istoric medical. `DiagnosticResult` nu are și nu va avea câmpuri de date medicale sensibile; asta ține brand-ul clar de partea DTC/lifestyle, nu de partea de serviciu medical (cu tot ce ar implica legal).
- ~~**Limba interfeței**~~ — rezolvat: site-ul e în engleză (vezi secțiunea 6); mockup-urile în română rămân doar concept vizual intern.

## Referințe

- Brief de concept (ce este produsul, flow, tech, mock): [`docs/concept-brief.md`](./concept-brief.md)
- Mockup vizual (concept, RO): [`docs/assets/lumira-skincare-mock.pdf`](./assets/lumira-skincare-mock.pdf) — landing page, quiz de diagnostic, pagina de rezultat a rutinei, dashboard „Rutinele mele".
