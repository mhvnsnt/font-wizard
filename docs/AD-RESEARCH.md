# AD RESEARCH — What the Best Ads of the Last 20 Years Teach Our Font Commercials

*Owner directive 2026-10-10: research the most popular ads of the last 20 years and make our ads/commercials better. This doc is the font-line application.*

## The campaigns that matter (2006–2026)

### 1. Old Spice — "The Man Your Man Could Smell Like" (2010)
Isaiah Mustafa, one continuous take, talking straight to camera while the world changes behind him. Funny first, product second. Sales more than doubled, website traffic up 300%, won the Cannes Lions Film Grand Prix and a Primetime Emmy. Then the Response Campaign: 180 personalized YouTube videos filmed in under 3 days answering fans and celebrities — 40M views in a week.
**What we steal:** absurdity as the vehicle, not the decoration. Deadpan delivery of ridiculous claims. A format that can answer the audience back.

### 2. Dollar Shave Club — "Our Blades Are F***ing Great" (2012)
Founder Mike Dubin walks through a warehouse, deadpan, controlled chaos behind him (machete, bear costume, forklifts). $4,500 budget. Value prop stated in the first 10 seconds: "For a dollar a month, we send high-quality razors right to your door." 12M views and 12,000 subscribers in 3 days; crashed the site. Their editing rule: *"If it wasn't 100 percent essential, it was gone."*
**What we steal:** the maker IS the ad. Humor with a point — every joke sells. State the offer early. Ruthless cutting.

### 3. Apple — "Shot on iPhone" / minimalism (2015–)
No actors, no script — user photos and videos as the whole campaign. The consumer is the hero. Earlier: "Think Different" (1997, still the template) and the white-background product spots.
**What we steal:** let the PRODUCT be the whole frame. Our fonts typing themselves full-screen is the "Shot on iPhone" of type. Minimalism reads as confidence.

### 4. Geico — "It's What You Do" (1999–present) + 15s unskippables
A joke format so consistent it ran for 25+ years: setup, punchline, tagline. Their unskippable 15s ads compress the whole joke into the first 5 seconds because they know when the skip button appears.
**What we steal:** a repeatable format beats a one-off genius. Our commercial script IS the Geico format: same beats, new font, rotating lines. And: front-load the good stuff — assume the viewer is one thumb-twitch from gone.

### 5. Snickers — "You're Not You When You're Hungry" (2010–)
One universal human insight, infinite executions (Betty White, Godzilla, Willem Dafoe). The format never changes; the casting does.
**What we steal:** find the one true sentence about each font ("WE made THIS") and never change the skeleton — change the casting (the font, the tagline, the CTA).

### 6. Spotify Wrapped (2016–)
Turned internal data into a personal story every user wanted to share. The audience does the distribution.
**What we steal:** make the audience part of the ad. "Type your name in Block Burner" style interactive hooks. Shareability is a feature you design in.

### 7. HeadOn — "Apply directly to the forehead" (2006)
Widely mocked, never forgotten. Pure repetition as branding. Proof that memorability doesn't require love.
**What we steal:** repetition of the CTA is a feature. "BUY IT." said three ways in 10 seconds is the HeadOn play — annoying is better than invisible.

### 8. TikTok ad grammar (2020–2026)
The modular formula: **Hook (0:00–0:03) → Body (0:04–0:15) → CTA (last 3–5s)**. Pattern interrupts (start mid-action, zoom, throw something). When an ad fatigues, keep the body and CTA — swap the HOOK. UGC/native style outperforms polished. Karaoke-style word-timed captions are now the default visual language.
**What we steal:** our 10s commercials already follow this. The rotation system (new tagline/CTA per font) is the anti-fatigue mechanism. Add karaoke-style captions to future cuts.

## Current font commercial layout (owner-locked 2026-10-10)
- **0–3s:** Font name types out **BIG, inside safety bounds** — never small in the margins. This is the hook.
- **3–4s:** CTA ("BUY IT." / rotating) — margins OK here.
- **4–5s:** 3-word tagline ("WE made THIS" / rotating) — margins OK.
- **5–7s:** CTA wavy trippy, white on black.
- **7–10s:** End card — font name in the font + itch.io link.
- Rotation: `pipeline/commercial_rotation.json` — new tagline + sometimes new CTA per font. Generator: `pipeline/make_commercial.py`.

## Techniques to steal — checklist for every font commercial
- [ ] Hook in the first 3 seconds: the font name, BIG, typing itself. No logos, no fade-ins, no throat-clearing.
- [ ] Maker voice present: "WE made THIS" — the DSC founder principle. The maker is the brand.
- [ ] Controlled chaos behind the product: trippy wavy backgrounds = our version of the DSC warehouse.
- [ ] Offer stated early and repeated: font name + where to buy, at least twice in 10 seconds.
- [ ] Humor with a point: every joke must sell the font. No decoration.
- [ ] Rotation active: new tagline and/or CTA vs. the last commercial (check `commercial_rotation.json`).
- [ ] Cut ruthlessly: if a frame isn't essential, it's gone (the DSC editing rule).
- [ ] CTA is a command, not a suggestion: "BUY IT." / "Get Yours" / "Purchase NOW!" — never "check it out maybe."
- [ ] End card readable for 3 full seconds: font name + buy link, no motion that kills legibility.
- [ ] Shareability designed in: one quotable 3-word line per commercial that works as a comment, caption, or hashtag.
