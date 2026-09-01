# Lumira — Brief portofoliu

**Ce este:** piesă de portofoliu fictivă (ca [[al-noir]] pentru restaurante și [[cassian-voicu]] pentru appointments) — de data asta pentru linia de e-commerce/produs: un brand de skincare cu diagnostic + rutină personalizată.

## Concept

Nu vinzi produse random — construiești o rutină. Utilizatorul intră, răspunde la câteva întrebări rapide despre ce-l preocupă, primește o rutină completă (dimineață + seară) construită din produse reale din catalog, cu motivul pentru fiecare pas. Poate salva rutina într-un cont și reveni oricând.

**Poziționare:** prietenos, fără jargon dermato-cosmetic greu, senzație "clean girl aesthetic" — nu clinic-rece, nu nici infantil.

## Flow diagnostic

1. **Ce te preocupă cel mai mult acum?** — hidratare / sensibilitate / imperfecțiuni / luminozitate / exces de sebum / semne de îmbătrânire (selecție unică, întrebarea principală)
2. **Tip de ten** — uscat / gras / mixt / normal / sensibil
3. **Experiență cu skincare** — începător / am deja o rutină / avansat → determină complexitatea rutinei (3 pași vs. 4-5 pași)
4. **(opțional) preferințe** — natural/vegan, fără parfum, buget

## Rezultat — rutina

- **Dimineața:** Cleanser → Ser (tratament pt. concern-ul principal) → Cremă hidratantă → SPF
- **Seara:** Cleanser → Tratament activ → Cremă de noapte

Fiecare pas afișează: produsul recomandat, categoria lui, și un motiv scurt ("de ce ți l-am pus aici").

## Cont utilizator

Login/register cu cont (nu doar sesiune) — rutina salvată automat, utilizatorul poate reface diagnosticul oricând și păstrează istoricul rutinelor anterioare. Urmează modelul Bookora/Platform Tickets (SaaS cu cont), nu modelul Al Noir/Cassian & Voicu (fără login client).

## Structură site

- **Acasă** — hero, cum funcționează, CTA spre diagnostic
- **Diagnostic** — quiz pas cu pas
- **Rutina mea** — rezultatul curent (dimineață/seară), CTA salvare
- **Produse** — catalog, filtrabil pe concern/tip ten
- **Cont** — rutinele salvate, istoric, refă diagnosticul
- **Despre** — brand story (fictiv, scurt)
- **Contact**

## Direcție vizuală

- **Mood:** soft pastel modern — playful dar curat, Gen Z/millennial
- **Paletă:** cremă/unt ca fundal, roz pudră și lavandă ca accente, o nuanță de plum/mov închis pentru text și contrast (nu totul pastel — are nevoie de un ancoraj închis)
- **Tipografie:** Bricolage Grotesque (titluri) + Instrument Sans (corp text) — pereche modernă, geometrică, nu clișeele uzuale (Inter/Fraunces)
- **Iconițe:** desenate, stroke-based, nu emoji

## Nume brand

**Lumira** — ales pornind de la „luminozitate"/lumină, una dintre cele 6 preocupări din diagnostic; se potrivește direcției soft-pastel și e ușor de reținut/pronunțat.

## Model de produs

**Brand propriu (private label)** — Lumira deține și „produce" propria linie; nu curatoriază/afiliază produse din alte branduri (vezi `docs/brand-brief.md`, secțiunea 1 și 7). Catalogul e fictiv (produse și prețuri demo), fără producție reală în spate — dar toate produsele din `Product` sunt Lumira, nu un brand extern editabil per produs.

## Tech (build)

Django (`lumira/` proiect, app `routines`). Models: `Concern`, `SkinType`, `Product` (categorie, concern-uri adresate, pas AM/PM), `DiagnosticResult`, `Routine`, `RoutineStep`, `UserProfile` (auth Django standard). Logica de diagnostic (`routines/diagnostics.py`): mapare concern + tip ten + nivel experiență → query produse pe categorie, ordonate în pașii rutinei. Cont utilizator cu Django auth (register/login/logout), rutini salvate per user, „Rutina curentă" marcată automat. Vezi `README.md` pentru instrucțiuni de rulare locală.

## Reguli de conținut

Brand, produse și copy = fictive, pentru demo — aceleași reguli ca la Al Noir și Cassian & Voicu, nu se prezintă ca reale. Copy-ul de interfață (mock final și build) este în engleză; documentele de strategie/portofoliu rămân în română.

## Mock

4 ecrane statice (nu prototip clickable): Acasă, Diagnostic, Rutina ta, Cont / Rutinele mele. Vezi [`docs/assets/lumira-skincare-mock.pdf`](./assets/lumira-skincare-mock.pdf).

## Vezi și

Analiza extinsă de poziționare, public țintă, propunere de valoare și model de business: [`docs/brand-brief.md`](./brand-brief.md).
