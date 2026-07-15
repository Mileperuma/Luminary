# Demo video — script + storyboard

A three-minute portfolio demo is the single most-watched artefact after the
README. Employers rarely have time to run the code themselves — the video
is where they decide whether to open the repo. Aim for 2:45 – 3:00 total.

## Setup (before recording)

- Use OBS Studio (free) or the built-in Windows Game Bar (`Win + G`).
- Record in **1080p @ 30 fps**, mp4, audio at 44.1 kHz.
- Chrome window at exactly **1440 × 900** for a clean frame.
- Zoom to **125 %** so text is legible on YouTube thumbnails.
- Close all other apps; hide bookmarks bar; use a fresh incognito window.
- Have **two demo accounts** pre-seeded: one brand-new (for onboarding) and
  one with 3-4 preferences already stored (for the returning-user greeting).
- Have `alice.new@luminary-demo.local` for the fresh account and
  `alice.returning@luminary-demo.local` for the seeded one.
- Practice the run-through **twice** end-to-end without recording. The
  awkward pauses vanish on the third take.

## Script

**Total target: 2:55.** Each section is a target time; the numbers are the
running clock, not the length of the segment.

### 0:00 – 0:20 · Problem hook

**On screen:** Chrome open on `luminary.vercel.app` landing page.

**Voice-over:**
> "Everyone I know uses at least three apps to figure out what to read or
> watch next. Goodreads for books, Letterboxd for films, Pocket for articles.
> None of them talk to each other, and every one of them treats you as a
> stranger on first visit."

> "Luminary is one taste profile across all three."

---

### 0:20 – 0:50 · Onboarding chat

**On screen:** Click "Create an account" → fill in form → land on `/home` →
click "Start chat" from the onboarding nudge.

**Voice-over:**
> "A new user gets a short chat, under five minutes. The assistant asks
> what they like across the three media types, then saves everything as a
> structured preference profile."

**Show:** Type a couple of realistic answers so the viewer sees the chat
respond. Reach the "saved 5 preferences" confirmation.

---

### 0:50 – 1:20 · First recommendation (Movies)

**On screen:** Click "See my picks" → click **Movies** card → wait for the
recommendation card to load.

**Voice-over:**
> "The backend queries TMDb for candidate films, ranks them against the
> user's preferences using a keyword score plus pgvector similarity, and
> asks Claude for a short plain-language explanation."

**Show:** Recommendation card with poster, LLM-written blurb, and embedded
YouTube trailer. Scroll to the "Similar to this" strip of four items.

---

### 1:20 – 1:40 · Feedback loop

**Voice-over:**
> "Every pick has four feedback buttons. Love it bumps that taste signal
> up. Not for me pushes it down. Show another gives a new pick immediately."

**Show:** Click "Love it" (brief thank-you). Click "Show another" — new
pick appears within a couple of seconds.

---

### 1:40 – 2:10 · Mood + cross-media

**On screen:** Scroll to the top; select the **Contemplative** mood pill;
watch a new pick load. Then scroll to the "Across media" strip.

**Voice-over:**
> "The mood selector lets the user tell the system what they're in the
> mood for right now — light, intense, contemplative, fun, or dark. The
> setting persists across sessions."

> "And this — the 'Across media' strip — is what no other tool does. If
> you loved this film, here's the source novel and a long-read essay
> about it. One taste profile, three media types, closely linked."

---

### 2:10 – 2:40 · Returning-user greeting

**On screen:** Log out. Log back in as the returning-user account.

**Voice-over:**
> "The best part is what happens on the second visit. The assistant
> greets the user with context — it names a specific preference from
> last time and shows fresh picks in that vein."

**Show:** Home page loads with the personalised greeting *"Welcome back,
Alice. You loved psychological thriller (watching) last time; here are
fresh picks in that vein."* Point at the "Recent picks" strip.

---

### 2:40 – 2:55 · Close

**On screen:** Cut to a title card with the GitHub URL and a
`docs/system_architecture.png` thumbnail.

**Voice-over:**
> "The whole thing is React on the front, FastAPI on the back, PostgreSQL
> with pgvector for similarity search. Full source and design docs on
> GitHub."

## Post-production checklist

- Trim any dead air > 500 ms.
- Add a soft outro card (2 seconds): repo URL + your name + contact.
- Upload to YouTube as **unlisted** first, watch it once end-to-end,
  then flip to **public** once you're happy.
- Paste the YouTube URL into README.md → **Demo video** slot at the top.
- Also add it to `docs/PORTFOLIO_ONE_PAGER.md` (below).

## Common mistakes to avoid

- Don't narrate every mouse click. Say what the *system* is doing.
- Don't apologise for latency — cut the pauses in post.
- Don't zoom in and out mid-shot. Set the zoom once, leave it there.
- Don't read the README out loud. The video is complementary, not a copy.
