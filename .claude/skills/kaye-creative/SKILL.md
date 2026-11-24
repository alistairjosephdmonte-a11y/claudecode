---
name: kaye-creative
description: "Turns a casual description into complete, photoreal prompts for cinematic AI videos with one consistent face: a character sheet from a selfie, location stills, multi-shot video prompts (Seedance 2.5) and image prompts (Seedream 5.5), plus targeted fixes when a take comes out wrong. Use it whenever someone wants to make a realistic or cinematic AI video, reel or short film of themselves or a character, asks for a character sheet, a location, a shot list, a 'prompt for Seedance' or 'for Seedream', wants to turn a childhood dream or story idea into a video, or says a generated shot looks off and needs fixing, even if they just describe the idea casually and never name the skill."
---

# Kaye Creative

This skill turns a person's casual words into full, ready-to-paste prompts for real-looking, cinematic AI videos in which the same face appears in every shot.

The method is a recipe with three ingredients, made in this order:

1. **Character sheet.** The person's face and outfit, locked in one picture.
2. **Locations.** Every place in the story, locked as a still photograph.
3. **The video.** Directed shot by shot, with the sheet and the locations attached.

People talk to you the way they would talk to a friend ("okay so take the person from photo 1 and put her in a cream dress…"). They should never have to write a technical prompt themselves. You write it. A good prompt here is long, specific and structured, because every detail you leave open is a detail the generator will invent, and invented details are what make AI video look fake and inconsistent.

Write every prompt in English, whatever language the person uses. Write everything else in their language.

## Which job is this?

Read the message for what it asks, then do one of five jobs:

| The person… | Job |
|---|---|
| has no idea yet, or asks what to make | **A. Find the idea** |
| sends a selfie or photo and describes an outfit | **B. Character sheet** |
| describes a place (a room, a house, a landscape) | **C. Location** |
| describes shots, durations, camera, and numbers their pictures | **D. Video** |
| reacts to a result ("this looks wrong", "I don't like how…") | **E. Fix** |

If one message asks for several things ("make me everything for this idea"), work through them in recipe order: sheet, then locations, then videos. Use one reply block per prompt. If the story isn't settled yet, pitch it first in a few lines, because the story decides which locations the person needs.

Make sensible choices instead of asking questions. Ask only when something vital is missing and cannot be chosen for them: for example, a character sheet with no picture of the person, or a video that needs a place nobody has described. When you choose something, say so in one short sentence.

## How every reply looks

For each prompt, the reply has these parts and nothing more:

1. **One or two sentences** saying what this generation is, in the person's own terms.
2. **Attach in this order:** a short numbered list of the pictures, if the prompt uses any. The order matters, because the prompt calls each picture by its number.
3. **The prompt**, complete, in one plain code block, so it has a copy button and nothing else gets pasted by accident.
4. **The settings line**, as plain text under the block: model, ratio, length, resolution, sound, and the picture order.
5. **At most one tip line**, only if it helps this generation (for example, "test it in draft first").

Do not add tables, checklists or long explanations around the prompt. The person wants to copy, paste and generate.

### Calling the pictures

Call each attached picture `@Image1`, `@Image2`, `@Image3`… by the order it is attached. That is how generators label uploaded pictures. If the person's generator turns typed tags into links, tell them once: after pasting, retype each tag with @ and pick the matching picture. If the person numbers their photos ("photo 1 is me, photo 2 is the bathroom"), keep their order.

## The house style (every prompt)

These rules are what make the results look filmed instead of generated. Each one fixes a failure that keeps coming back.

**Call it real.** Open with what the picture or film is: "ONE ORDINARY, ULTRA-REALISTIC DAYTIME PHOTOGRAPH", "real footage from a real camera". Even impossible things (a house lifted by balloons, a bridge that climbs into the sky) obey real light, real distance, real weight and real scale. Generators drift into fantasy art the moment the prompt sounds like fantasy.

**Never use names of films, cartoons, brands, characters or real people,** and never the word "game" or anything like "video-game look". Names pull in a cartoon or a logo, and some get the run blocked. Describe the look in plain words instead.

**Light: only what is already there.** The only light is the sun, the open sky or a lamp that is part of the place. The person is never lit: "Her face is NOT brighter than the surroundings next to her." Add a full ban on lighting gear (no key light, fill, rim, softbox, reflector, flash). Studio beauty lighting is the strongest sign of a fake video, and generators add it unless told not to.

**Every picture has a job, and only that job.** In an INPUTS block, give each picture one line in this form: "`@Image2` — THE PLACE, THE ONLY SOURCE OF THE LOCATION AND OF THE LIGHT: take …. TAKE NOTHING ELSE FROM `@Image2` — not …." A generator copies everything it sees in a reference unless told what to ignore: the grey backdrop of a character sheet, its three-panel layout, its pose, its studio light. For locations add: "THE REFERENCE DEFINES THE WORLD, NOT THE FRAMING: the camera positions are our own."

**The person's look comes only from the sheet.** Never describe their face, skin or hair colour in words, because words fight the picture. Write "her exact face and hair from `@Image1`". Describe the outfit, because the prompt has to keep it the same in every shot. Use the person's own pronouns. If you can't tell them from the message, write "the person" and "they", and add "ONE PERSON" to the hard requirements and "no second person" to the negatives, so "they" is never read as two people.

**Be exact.** Name materials ("thick, matte cotton"), colours by position ("red on the left, orange on the right"), counts ("EXACTLY ONE ENTRANCE DOOR"), sizes ("about the size of a fingertip") and where things sit in the frame ("in the left third of the frame"). Clear textures and boundaries stop the generator from inventing shiny plastic clothes and extra furniture.

**Put the riskiest things first.** Under a heading like "=== 4 HARD REQUIREMENTS ===", number the three to five things most likely to go wrong in this generation. Write the key words in CAPITALS. The capitals, the `===` rules and the repeated bans are deliberate emphasis, not shouting.

**End with a NEGATIVE list,** grouped by topic, naming the specific failures this generation is likely to produce. Do not use a generic list.

## A. Find the idea

When someone doesn't know what to make, don't suggest a trend. Ask two questions:

1. What did you love doing as a kid?
2. How exactly did you do it? Ask for one specific detail they can see.

If their message already answers both questions, don't ask them again. Go straight to the story.

The specific detail is what turns a memory into a picture. Build the answer into a short story in two videos of about 10 seconds each:

- **Video 1, the ordinary moment.** The person is in a real place, in the middle of something everyday. Then the impossible thing starts (a sound, a shake, a light) and they react in a small, real way.
- **Video 2, the reveal.** We see the impossible thing whole, with real weight and scale. End on a long, unhurried shot of the person taking it in.

Then list the ingredients the story needs (the sheet, each location) and offer to write them in order. For a series, the theme and the look stay the same, and each episode is a new dream.

## B. Character sheet

The person attaches a clear selfie or photo with good light on the face, and describes an outfit. Write one prompt for one image with exactly three panels on a seamless mid-grey backdrop:

- **Left:** a head-and-shoulders close-up, facing the camera.
- **Centre:** the whole body from head to shoes, with the head in frame.
- **Right:** a head-and-shoulders close-up in strict profile.

The three views work like a 360° map. When the camera moves around the person later, the video model doesn't have to guess their profile or how the clothes hang.

Follow the worked example's structure:

- INPUT: what to take from the photo, and TAKE NOTHING ELSE.
- WHAT CHANGES: the outfit, the backdrop, the light.
- THE LAYOUT.
- THE OUTFIT, garment by garment: cut, fabric, colours by position, length, shoes, "no jewellery, carries nothing" unless the story needs it.
- THE BACKDROP.
- LIGHT: available daylight only.
- ALIVE AND REAL: a relaxed, natural person with a hyper-real face (pores, fine hairs, real lashes, the person's own moles and freckles).
- NEGATIVE.

If they want coverage (closed neckline, sleeves, length), state it plainly and ban the opposite in the negatives.

If many shots will film the person from behind, use a back view instead of the profile.

Settings line: `Seedream 5.5 · 16:9 (so all three panels fit side by side) · 2K · one reference picture: the person.`

## C. Location

Write one prompt per place. Each one is a single still photograph with no people in it, so it can be used in every shot without a stranger appearing.

Follow the worked examples:

- **The camera,** placed by a real person: where they stand, at what height, which lens, square on or at an angle.
- **The layout:** wall by wall, or foreground, middle and distance, in thirds of the frame.
- **THE DETAILS, EXACTLY THESE, EACH IN ITS PLACE,** followed by "Nothing else is added."
- **Clear space** in the middle of the floor, where the person will stand later.
- **The light:** one direction for the sun, a hard patch of sunlight with a real shape, and real shadows that point away from the light.
- **REALISM** that comes from correct materials, light and scale, not from dirt.
- **NEGATIVE:** no lamps, no people, no readable text, no collage or split screen, plus the failures specific to this place.

When two places share something, attach the first picture to the second prompt and take ONE thing from it. For example, a bathroom whose window is the window seen from outside on the house. That shared thing is what makes the cuts in the video match.

For an impossible place, list the impossible things separately and number them. Say they obey the same real light, distance and scale as everything else.

Settings line: `Seedream 5.5 · 16:9 · 2K · reference pictures, if any, in the listed order.`

## D. Video

The person describes the shots casually: "Shot 1, 5.5 seconds: a tight over-the-shoulder close-up into the mirror… Shot 2…". Turn that into a full directing brief.

Check that every place in the shots has a still. If a shot happens somewhere with no picture yet (often the outside of a house whose kitchen they did attach), write that location prompt first, built from the picture they did attach, and say why in one line. Then write the video with it in the attach order. A place that exists only in words changes every time the camera cuts. Think like a film director: where the camera stands, how it moves and what the moment should feel like.

Use this structure, the same as the worked examples:

1. **Header line:** ratio, length, number of shots, exact cut times, "No speech", "NO MUSIC ANYWHERE IN THIS FILM — real recorded sound only".
2. **READ THIS FIRST:** "THIS IS A SEQUENCE OF N SHOTS, NOT A SINGLE TAKE", with the time range of each shot. Without this, generators often merge everything into one shot.
3. **=== HARD REQUIREMENTS ===**
4. **INPUTS,** one line per picture, in attach order.
5. **THE CAMERA:** handheld with a small, constant shake, and the zoom is never used ("closer means the operator walked closer"). Smooth gimbal moves and zooms are what make AI video look artificial.
6. **=== SHOT 1 — 0.0 to 5.5s — WHAT KIND OF SHOT ===**
   - Define the framing with a check the generator can test, for example: "If the basin, the vanity or the window can be seen, the shot is too wide and it is wrong."
   - Then the timed beats: "0.0–1.5s — …", "1.5–2.7s — …". Give each beat one event.
   - Spell out every physical mechanism: which hand, which side of the glass, which way a door swings, where its hinges are.
7. **=== CUT AT 5.5s ===**, then the next shot in the same way.
8. **NATURAL PERFORMANCE — NO ACTING:** the hands stop first, and only then does the face change. A blink, the brows drawing slightly together, the lips parting barely. No wide eyes, no dropped jaw.
9. **LIGHT:** available light only, described shot by shot. The person is never lit. Outdoors: "ONE SINGLE LIGHT FOR EVERYTHING", meaning one sun, one shadow direction, and nothing brighter or cleaner than the grass beside it.
10. **THE LOOK:** maximum realism; a soft, gentle picture with natural contrast; real textures.
11. **AUDIO — NO MUSIC AT ALL:** the real sounds of each shot. Music goes on in the edit.
12. **NEGATIVE.**

Three directing habits make the difference between AI slop and a film scene:

- **Give things weight.** "The house is real, full-size and heavy, not a toy… dirt falling off it." Without real weight and scale, the generator makes a light toy floating like a feather.
- **Describe what the camera physically sees.** Don't write "the house flies up". From inside the room, "the view slowly sinks down past the window frame".
- **Carry continuity across videos.** The same window, the same hand, the same mark on the eyelid: state it in every prompt that shows it, with the same words.

Let the last shot of a story run long and unhurried.

Settings line: `Seedance 2.5 · 9:16 · 10 seconds · sound on · reference pictures in this order: 1 …, 2 …, 3 … (as references, not as a start frame). Set the length and the ratio by hand: generators often start at 5 seconds and 16:9.`

Tip line: test a new video prompt in draft mode or the lowest resolution first. It costs a fraction, and you can make the final once the motion and acting are right. Two runs of the same prompt are never identical, so if a take has one odd moment, run it once more before changing the text.

## E. Fix

When most of a take is right and one thing is off, never throw the prompt away. Change only that thing.

1. Take the last prompt for that video. If it isn't in the chat, ask the person to paste it.
2. If they attached a reference photo of how it should look, it is for you only. Translate it into exact physical words: size, shape, texture, colour, where it sits and when it appears. Do not add the photo to the generation. In "Attach in this order", list the same pictures as before.
3. Rewrite only the parts that cause the problem. Move the event to one exact moment in the timed beats. Add or sharpen a hard requirement. Add the matching bans to the negatives. If the detail must last, carry it into later shots ("In shot 2 the smudge stays on her eyelid").
4. Keep everything else word for word, because it already works.
5. Return the complete updated prompt, not a patch. Put one line before it naming what changed.

## Worked example: the floating house

This is one complete story made with this method. A woman is putting on mascara in a mint-green bathroom when the house starts to shake. She opens the window. Outside, her whole lilac cottage is rising into the sky on thousands of balloons.

Each request below is the casual message that was typed. Under it is the prompt that was written for it. Use these as the standard for length, structure and precision, not as text to copy for a different idea.

### 1. Character sheet

Request, with a photo of the person attached:

> Okay, so take the person from photo 1 and keep her look and body proportions exactly the same. What I want is to put her in a cream-colored dress that's fully covered up, made of a thick, matte cotton. It should have a shirt-style collar with those long, pointy tips. Her shoulders and neckline are fully covered, and the sleeves come down to the elbow. The bodice is fitted at the waist, and then the skirt is really full and goes below the knee, made of three tiers. Each tier has a wavy edge trimmed with colored ribbon: the top tier has red and orange, the middle one has pink and lilac, and the bottom one has green and light blue. Just to be clear, it's below the knee, and the shoulders and chest area stay covered.

Prompt:

```text
16:9. ONE IMAGE: A PHOTOREAL CHARACTER REFERENCE SHEET OF EXACTLY THREE PANELS. NATURAL LIGHT ONLY — NO LAMPS OF ANY KIND.

INPUT: @Image1 — THE ONLY SOURCE OF HER FACE AND HER HAIR. Take from it: her exact face and identity, her hair exactly as it is, and her natural build and proportions. TAKE NOTHING ELSE — not the clothes, not the background, not the pose. Ignore the lighting of @Image1.

WHAT CHANGES — ONLY THREE THINGS: the outfit, the backdrop, the light. Her face and hair stay exactly as in @Image1.

THE LAYOUT: three photographs side by side with thin white gutters.
LEFT — head-and-shoulders close-up, facing the camera straight on.
CENTRE — her whole body from the top of her head to her shoes, WITH HER HEAD AND FACE IN FRAME, standing straight and relaxed, arms loose at her sides, a little empty space above her head and below her shoes.
RIGHT — head-and-shoulders close-up in strict side profile, facing left.
THE SAME WOMAN IN EVERY PANEL: identical face, identical hair, identical build, identical dress.

THE OUTFIT, identical in every panel: ONE CREAM-WHITE COTTON DRESS — matte, crisp ivory cotton with enough body to hold its shape; fully opaque.
— CLOSED AND MODEST: A SHIRT COLLAR WITH LONG POINTED TIPS, buttoned closed at the throat, its edge bound with a thin yellow ribbon; collarbones and chest are completely covered. SLEEVES TO THE ELBOW: both shoulders and upper arms are completely covered. A fitted bodice with a seam at the natural waist.
— THE SKIRT IS THE SIGNATURE: very full and bell-shaped, standing out wide on its own, made of THREE TIERS layered one over another, dividing the skirt into three equal bands. The lower edge of every tier is a WAVY, SCALLOPED LINE bound with a COLOURED RIBBON, and the ribbon changes colour at the centre front: TOP TIER — red on the left of the picture, orange on the right; MIDDLE TIER — pale pink on the left, lilac on the right; BOTTOM TIER, the hem — dark green on the left, sky blue on the right.
— THE HEM ENDS AT MID-CALF, clearly below the knee.
The ribbons are the only colour on the dress: no prints, no lace, no writing, no logos. On her feet, plain white sneakers. She wears no jewellery and carries nothing in her hands. In both close-ups the long-point collar with its yellow edge is visible at the bottom of the frame.

THE BACKDROP: a seamless neutral mid-grey paper backdrop, the same even grey in all three panels.

LIGHT — AVAILABLE LIGHT ONLY, LIKE A REAL DOCUMENTARY WITH NO LIGHTING CREW: there is NO film lighting in this photograph at all — no lamps, no softboxes, no reflectors, no bounce boards, no fill, no flash exist here. She is NEVER lit; she simply stands in soft, even daylight, the same daylight that falls on the grey behind her. Her face is NOT brighter than the backdrop next to her — it has the same brightness and colour as her surroundings. Her skin is matte, with natural texture, no sheen and no highlights on it; the only reflection in her eyes is the soft daylight.

ALIVE AND REAL: a real person standing calmly, not a posed mannequin — a relaxed neutral expression, shoulders soft, no model pose.
THE FACE MUST BE HYPER-REAL IN THE TWO CLOSE-UP PANELS: visible pores, fine peach-fuzz hairs along the jaw and hairline, natural skin grain, subtle unevenness in tone, her real moles and freckles exactly where they are in @Image1, real individual lash and brow hairs, faint moisture on the lips, macro-lens sharpness on the eyes.

NEGATIVE: NO LIGHTING ON THE PERSON — no key light, no fill light, no rim light, no hair light, no front light on her face, no softbox, no reflector, no bounce, no flash, no studio lighting, no beauty lighting, no commercial or advertising look, no catchlights from lamps, no shiny or glowing skin, no face brighter than the background, no separation light around her; no glow, no bloom, no halation on her. No white backdrop, no colour cast on the grey. No bare shoulders, no low neckline, no scoop neck, no V-neck, no straps, no sleeveless dress, no hem above the knee, no slit, no sheer or see-through fabric. No clothes from @Image1. No fourth panel, no extra panels, no text, no captions, no labels, no logos. No beauty filter, no airbrushing, no smoothed, plastic or waxy skin, no AI-smooth face, no changed face, no different person between panels, no extra fingers.
```

Settings: Seedream 5.5 · 16:9 · 2K · one reference picture: the person.

### 2. Location: the house

Request:

> Hey, I need a prompt for a soft lilac wooden house, but as a real photo: an ordinary summer day in the real countryside, ultra-realistic, not a fairy tale and not a render. It's a small, cozy, lived-in cottage: one story with an attic under a steep roof, a single front door with a window on each side and flower boxes of red geraniums under them, and two more windows on the side wall. All the windows are the same simple kind: two leaves side by side, one clear pane in each. The windows are clear, so you can see a cozy room inside: curtains, a plant on the sill, a shelf with books. It stands in a meadow with long grass and wildflowers, soft rolling green hills behind it and a blue sky with real clouds. At the very top of the roof there's a huge bunch of colorful helium balloons tied on, floating above the house. The whole house and all the balloons have to be in the frame. Only natural daylight, please don't add any artificial lighting, and nothing should look staged or too perfect.

Prompt:

```text
16:9 HORIZONTAL. ONE ORDINARY, ULTRA-REALISTIC DAYTIME PHOTOGRAPH, taken by a person standing in a meadow with a full-frame camera and a 35mm lens. A small, cosy, lived-in lilac wooden country house stands in green grass among gentle rolling hills, with a huge cluster of real helium balloons tied to its roof. It must look like a real event photographed on a real day in the real countryside, not surreal, not a fairy tale, not a render. NATURAL DAYLIGHT ONLY: the sun and the sky, no lamps of any kind.

=== 4 HARD REQUIREMENTS ===

1. A REAL COUNTRYSIDE ALL AROUND: the house stands in a real meadow of long, uneven summer grass with clover, dandelions and small wildflowers, some patches taller and some trampled. Behind it, soft green rolling hills recede in layers into the distance, with natural variation in tone, a few distant trees and bushes along the hill lines and faint natural haze only on the farthest hill. Above, a blue summer sky with real, varied cumulus clouds of different sizes and shapes, some with soft grey undersides.
2. THE ONLY LIGHT IS NATURAL DAYLIGHT: the sun of a clear late morning, high and to the left, plus the light of the open sky. No lighting equipment exists here.
3. EVERYTHING IS FULLY INSIDE THE FRAME: the whole house and the whole balloon cluster sit slightly off-centre, framed naturally in the landscape, with meadow in front, hills on both sides and open sky with clouds above the top balloon.
4. NOTHING LOOKS STAGED, PERFECT OR SYMMETRICAL: real proportions, real scale, real wear, real imperfections everywhere.

THE HOUSE: a real, full-size, small timber cottage with ONE STOREY and AN ATTIC under a steep gabled roof, the kind of old house someone actually lives in. The camera is at standing eye height, about thirty metres away, in a slight three-quarter view, so the front wall and one side wall are both visible. All walls stand vertical. The walls are horizontal wooden clapboards painted a SOFT PASTEL LILAC, a gentle pale lavender, slightly faded by the sun, with fine wood grain, small paint chips, slightly darker weathering near the bottom boards and thin shadow lines between the boards. The roof is worn wooden shingles in a deeper dusty lavender-grey with small irregularities and a little moss near the eaves: two plain slopes meeting in one straight ridge. One small brick chimney rises from the back slope. A metal gutter runs along the eaves with a downpipe at the corner. The house sits on a low foundation of old grey fieldstones, with grass growing up against it.
— FRONT WALL (the gable end): EXACTLY ONE ENTRANCE DOOR in the centre, a simple panelled wooden door of normal full height painted a slightly deeper lilac, with a worn brass handle, a small wooden porch step and a doormat. ONE WINDOW on each side of it, each with a wooden flower box of red geraniums underneath. The window to the right of the door is the larger of the two: about as wide as it is tall.
— ATTIC: ONE small window in the triangle of the gable, just under the ridge.
— SIDE WALL: TWO WINDOWS.
This is the only door of the house. A narrow trodden footpath through the grass leads to the step.

THE WINDOWS — CLEAR, TRANSPARENT, LIVED-IN: every window has white wooden frames with slightly peeling paint and real, perfectly transparent glass. EVERY WINDOW OF THE HOUSE IS BUILT THE SAME SIMPLE WAY: a casement with TWO EQUAL LEAVES side by side that meet in the middle, each leaf one white-painted frame around ONE SINGLE SHEET of glass, clear from its top rail to its bottom rail. Through the glass you can clearly see a cosy interior lit only by daylight: light linen curtains tied to the sides, a potted plant and a small jug of flowers on the sills, the back of a wooden chair, a shelf with books and cups, a wall with a small picture. The glass shows only faint natural reflections of the sky and clouds and does not hide the inside. No light glows from inside; the rooms are simply lit by the sun coming in.

THE BALLOONS: at the middle of the roof ridge, many hundreds of thin white strings are tied in one tight bundle around a sturdy hook. From this point they rise upward, taut, swaying slightly differently in a light breeze, and open into ONE ENORMOUS, DENSE CLUSTER OF THOUSANDS OF HELIUM BALLOONS floating above the house, wider than the house and about one and a half times as tall as it. They are ordinary round latex helium party balloons, small against the house, each about a third as wide as the door, with natural small differences in size and roundness, packed tightly layer behind layer. MULTICOLOURED and evenly mixed: red, orange, yellow, green, turquoise, blue and violet in clear natural colours. The sunlit latex is slightly translucent, with one small sun reflection and a soft sky reflection on each balloon, and the balloons in shadow at the back of the cluster are darker. The cluster casts a large soft coloured shadow onto the roof and part of the grass.

LIGHT AND SHADOW: real midday-to-morning sunlight from the upper left. The house casts a clear, soft-edged shadow on the grass to the right. There is natural shade under the eaves and on the side wall facing away from the sun, and the sunlit wall is warmer. The clouds throw a few large slow shadows across the distant hills. The exposure is natural and balanced, the highlights keep detail and the shadows stay open.

REALISM — SUPER-REALISTIC: a documentary photograph, as if taken on a real day by a real photographer. True-to-life colour, normal contrast, natural sharpness from the grass in front of the house to the top balloon, with the far hills slightly softened only by the air. Individual blades of grass, insects-scale detail in the flowers, real wood texture, real glass, real latex with tiny knots at each neck. Fine natural camera grain. The house is plain and real, with no signs, no text and no markings of any kind.

NEGATIVE: no surrealism, no fantasy, no fairy-tale look, no storybook look, no dreamy atmosphere, no animation-film look; no plain or grey background, no empty void, no studio backdrop; no opaque, mirrored, dark or black windows, no glowing windows, no interior lamps; no toy, miniature or dollhouse look, no tilt-shift; no perfectly clean or brand-new surfaces, no perfect symmetry; no oversaturation, no neon colour, no HDR look, no glow, no bloom, no lens flare, no fog; no studio lighting, no flash, no artificial light; no people, no cars, no roads, no power lines; no illustration, no cartoon, no CGI look, no 3D render, no plastic.
```

Settings: Seedream 5.5 · 16:9 · 2K · no reference pictures.

### 3. Location: the bathroom, built around the house's window

Request, with the picture of the house attached. The bathroom window has to be the same window the house shows from outside, so the house picture is the reference:

> Okay, now I need a bathroom location, with a mirror and a window. I'm attaching a photo of the house (photo 1): take the shape and structure of the windows from this photo, so the bathroom window is built exactly like them. It's the same window that's to the right of the front door, just seen from inside, with the meadow and the hills outside. The tiles are a soft emerald, kind of minty shade, and the floor is white tile. Next to the mirror there's a wooden vanity with a sink, and there's also a white bathtub. Add some of the usual bathroom details too, like a little cabinet, a bath mat, that kind of thing. And warm, direct sunlight should be coming in through the window.

Prompt:

```text
A SINGLE PHOTOREAL LOCATION PLATE, 16:9 HORIZONTAL. One frame, one photograph of a real bathroom on the ground floor of the lilac cottage of @Image1, empty of people. NATURAL LIGHT ONLY — the sun and the daylight through the window. NO LAMPS OF ANY KIND.

INPUT.
@Image1 — THE HOUSE THIS BATHROOM IS IN, THE ONLY SOURCE OF THE WINDOW: take ONE thing from it — the ground-floor window to the right of its front door, the larger of its two front windows, the one with the flower box under it. This bathroom is the room behind that window, and the window in its far wall is that very window seen from inside: the same white-painted wooden frame, the same two leaves that meet in the middle, each leaf ONE SINGLE SHEET of clear glass in its white frame, the same proportions, about as wide as it is tall, the same light curtains tied back at its two sides. TAKE NOTHING ELSE FROM @Image1 — not the outside of the house, not its lilac boards, not its balloons, not its framing. The meadow, the hills and the sky of @Image1 are only what is seen far outside through the glass.

CAMERA: a real photograph taken from the doorway at standing eye level, level and square on to the far wall. A natural wide view with both side walls visible; deep focus, rectilinear, straight verticals.

THE ROOM: a small, simple bathroom. ALL WALLS are covered from floor to ceiling in small square glazed ceramic tiles of a SOFT MINT GREEN — a gentle, pale emerald-mint — laid in a neat grid with thin white grout lines. THE FLOOR is plain WHITE matte floor tiles with thin pale-grey grout lines. The ceiling is plain white and bare.
— FAR WALL, CENTRE OF THE FRAME: ONE WINDOW, closed — the window of @Image1 seen from inside. A fixed white-painted wooden frame, the paint slightly peeling, and in it TWO EQUAL LEAVES side by side that meet in the middle, each a white-painted wooden rectangle around ONE SINGLE SHEET of clear glass that runs unbroken from its top rail to its bottom rail, so that through each leaf the meadow and the sky are seen whole. The two leaves are fastened by one small catch where they meet. THE WINDOW IS ABOUT AS WIDE AS IT IS TALL, exactly as in @Image1, so that each of its two leaves is about twice as tall as it is wide. Light linen curtains hang inside, tied back at its two sides, clear of the glass. Through it, the open country the house stands in: a sunlit meadow, low rolling green hills far away and a blue sky with white clouds — bright but still readable.
— LEFT WALL, LEFT THIRD OF THE FRAME: A WOODEN VANITY CABINET in warm natural oak with a white ceramic basin and one simple metal tap. On the wall directly above it hangs A PLAIN RECTANGULAR MIRROR in a thin wooden frame. From the doorway the mirror is seen at a steep angle and shows only the opposite mint-tiled wall and the edge of the bathtub.
— RIGHT WALL, RIGHT THIRD OF THE FRAME: A WHITE FREESTANDING BATHTUB, plain and smooth, standing along the wall with its long side towards the room, with one simple metal tap.

THE DETAILS — EXACTLY THESE, EACH IN ITS PLACE:
— ONE BATH MAT: a small woven cotton mat in a natural sand colour, lying on the floor right beside the bathtub.
— ONE SMALL WOODEN SIDE CABINET in the same warm oak, with one door, standing against the far wall in the left corner, between the vanity and the window. On its top lies a neat stack of three folded white towels.
— ONE LOW WOODEN STOOL at the far end of the bathtub, by the window wall, carrying a white dish with one bar of soap.
— ONE WHITE TOWEL draped over the rim of the bathtub.
— ON THE VANITY TOP, beside the basin: one plain white ceramic soap dispenser and one clear glass holding two toothbrushes.
— ON THE WINDOW SILL: one small green plant in a plain white pot.
— ONE WOVEN WICKER LAUNDRY BASKET with a lid, on the floor at the near end of the vanity.
THE MIDDLE OF THE FLOOR IS CLEAR AND EMPTY. Nothing else is added.

LIGHT — AVAILABLE DAYLIGHT ONLY, ZERO EQUIPMENT: there is no lighting kit here at all. The ONLY light sources are THE SUN and THE OPEN SKY, both entering through this one window. LOW WARM AFTERNOON SUN comes in at a slant from the upper left — the sun itself stays out of sight — and lays ONE HARD-EDGED PATCH OF WARM DIRECT SUNLIGHT, crossed by one thin upright shadow, the shadow of the two stiles where the leaves meet, diagonally across the white floor and the bath mat, and up the side of the bathtub and the tiles behind it. Where the sun lands, the white turns warm and the mint leaps to full colour. The rest of the room sits in soft, slightly cooler natural shade, filled only by daylight reflected off the tiles. REAL SHADOWS WITH DIRECTION: the bathtub and the vanity each throw one shadow away from the window. The air is clean and clear.

REALISM: the realism comes from correct materials, correct light and correct scale, NOT from dirt. Clean and clearly used, no showroom sterility: tiny differences of shade from tile to tile, slightly uneven grout, soft wear on the edges of the wood, real enamel on the bathtub, soft cotton with real folds. Natural colour, fine organic grain. No HDR, no digital sharpening, no oversaturation.

NEGATIVE: no ceiling lamp, no wall lamps, no light fixtures, no lit bulbs, no candles; no studio lighting, no key light, no fill light, no rim light, no softbox, no reflector, no flash; no glow, no bloom, no halation, no light beams in haze, no fog, no steam; no toilet, no shower curtain, no bottles, no wall shelves, no radiator, no blinds, no shower curtain rail; no brown or unpainted window frame, no horizontal bar across a leaf, no glazing bars, no leaf divided into panes, no tall narrow window, no wide low window, no tilting top pane, no garden wall or trees close outside the window, no part of the house exterior inside the room; no face in the mirror, no reflection of a person; no readable text, no logos, no labels; no three-panel layout, no collage, no split screen, no multiple views; no illustration, no CGI look.
```

Settings: Seedream 5.5 · 16:9 · 2K · one reference picture: the house.

### 4. Location: the view from the window

Request:

> New location, and it needs to look ultra-realistic. We're up on a tall grassy slope, above the clouds, looking down at a huge green plain full of fields, with the horizon set high. In the foreground there's grass on the slope and three white sheep on the left. Down on the plain you can see herds as little dots, with big cloud shadows on the right. On the left there's a sharp snowy mountain with a riverbed running from it down onto the plain, and a blue sea in the distance. The clouds are white and puffy, below us.
> There's also an endless white stone bridge on tall arches. It starts bottom right near us, runs straight across the whole plain, then curves up at the horizon into the sky. Behind the horizon, in the center and on the right, the land rises like a wall up to the top of the frame, covered in a city of thousands of towers seen from above, with clouds drifting over it and the bridge climbing up it. Top left is just clear blue sky.
> Colors are rich and vivid, not dull. It should look like a real photo, not fantasy or CGI, no fog, and only sunlight, no artificial lighting.

Prompt:

```text
A REAL PHOTOGRAPH OF A REAL PLACE, 16:9 HORIZONTAL. One frame, one photograph, taken with a real camera on a perfectly clear summer day, empty of people. Everything in it — including the two impossible things — obeys real light, real distance and real scale. NATURAL DAYLIGHT ONLY — the sun and the open sky.

COLOUR — RICH, VIVID, FULLY SATURATED: an intense fresh green land, a deep pure blue sea and sky, brilliant clean white clouds and white stone. Crisp contrast and high clarity, as in perfectly clear mountain air. The whole picture is brightly exposed.

THE VIEWPOINT: the camera stands at eye level on an open grassy mountainside, in full sun, very high above an immense plain, and looks out and slightly down over it. Nothing stands between the camera and the view. THE HORIZON SITS HIGH, IN THE UPPER THIRD OF THE FRAME. We are above the clouds: they float between us and the land.

THE FOREGROUND, ALONG THE BOTTOM EDGE: the steep sunlit slope we stand on — rough green mountain grass in tufts close to the lens, with a little bare earth. At the lower left THREE WHITE SHEEP graze on it.

THE PLAIN FAR BELOW: an immense, perfectly flat green plain seen from far above: a patchwork of meadows and fields in many greens, a few red-brown ploughed rectangles, hair-thin pale tracks, tiny pale specks of farms. Herds of cows and horses graze on it as scattered dots. Huge dark cloud shadows lie across the right half of the plain.

THE MOUNTAIN, ON THE LEFT: one sharp pyramid of dark rock streaked with snow rises from the plain, with lower snowy ridges around it and green lower slopes; a pale braided riverbed winds from its foot out onto the plain.

THE SEA: beyond the plain, a deep blue sea fills the distance to the horizon; on the left the coast curves into a bay with turquoise shallows.

THE CLOUDS: brilliant white cumulus, crisp-edged, float below us and at our own height in a loose band between us and the far coast.

THE TWO IMPOSSIBLE THINGS:

1. THE ENDLESS WHITE VIADUCT: a colossal classical viaduct of white stone — one long row of tall round arches, each as high as a ten-storey building, with a balustrade along the top. It enters the picture at the lower right, close to us, swings in one smooth curve to the left, and then runs DEAD STRAIGHT away across the plain through the centre of the frame, thinning to a white hair-line with its dark shadow beside it, all the way to the far coast. It does not stop at the horizon: there it bends smoothly UPWARD and keeps climbing into the sky, ever thinner, until it leaves the top of the frame.
2. THE WORLD FOLDS UP INTO THE SKY: beyond the horizon, in the centre and right of the upper third, the ground itself turns upward and stands like a colossal vertical wall that fills that part of the sky to the top edge. Its face is land seen from straight above, standing on end: an endless dense city of thousands of tiny towers, dark blue-grey with small sand-coloured and golden roofs, softened and blued by distance. White clouds drift across its face and pile up at its foot along the horizon. The viaduct climbs this wall. The upper left of the sky stays open, deep, pure blue.

LIGHT — AVAILABLE DAYLIGHT ONLY, ZERO EQUIPMENT: the ONLY light sources are THE SUN and THE OPEN SKY. High hard summer sun from the upper left, out of frame. The grass, the white stone and the cloud tops are in full sun; every arch, ridge and cloud has a real shaded side. REAL SHADOWS WITH DIRECTION. Colour leaps to full saturation wherever the sun lands.

REALISM: the realism comes from correct materials, correct light and correct scale. Real grass with visible blades in the foreground, real weathered white stone, real rock and snow, real animals in ordinary grazing poses. Deep focus: sharp from the nearest grass to the far coast; distance softens things only through the air. Fine organic grain.

NEGATIVE: no pale, dull, faded or washed-out colour, no grey haze, no fog, no flat low contrast; no fantasy concept art, no matte painting, no illustration, no CGI look; no underexposure, no vignette, no storm clouds, no sunset, no night; no studio lighting, no key light, no fill light, no rim light, no flash; no glow, no bloom, no halation, no lens flare, no light beams, no sparkles; no vehicles, no power lines; no readable text, no logos; no three-panel layout, no collage, no split screen, no multiple views.
```

Settings: Seedream 5.5 · 16:9 · 2K · no reference pictures.

### 5. Video 1, and how it was fixed

The first brief, with the character sheet, the bathroom and the house attached:

> Okay,now I need a prompt  for video generation in Seedance 2.5, 9:16, 10 seconds. Photo 1 is the girl, photo 2 is the bathroom location, photo 3 is the house from outside.
> Generation 1
> Shot 1, 5.5 seconds: a really tight over-the-shoulder close-up from her shoulder onto her reflection in the mirror, her face filling almost the whole frame so you can't see the room. She's putting on mascara. Then the house starts shaking like an earthquake, she flinches from the shaking, her hand with the wand jerks and the mascara smears a little on her face. Then she looks over toward the window.
> Shot 2, 4.5 seconds: a straight, level shot from outside of the bathroom window, which is the window to the right of the front door in photo 3, exactly that window, with the lilac boards of the house around it and its flower box of red geraniums under it. The whole window is in the frame, both of its leaves. The house is still shaking a bit and the glass trembles. She walks up to its left leaf, the mascara smear still on her face, and looks past the camera, mesmerized and a little surprised, without overacting. Then she opens that leaf from inside with her left hand: she turns the catch, which is on the room side, and pushes, and the leaf swings outward and to the left on its hinges like a door, the way a real window would. While it's shut she's entirely behind the glass, and her hand only comes out through the gap. By the end it's open about a hand's width.
> Every shot should feel alive, like it's handheld with a little shake, no push-ins or zooms. Don't add artificial light, just the location's own light. Maximum realism, soft image, warm sun highlights. No music, just sound effects.

The first take was 90% right, but the mascara mark appeared as a streak in a random spot on her cheek instead of where the wand touched. Instead of starting over, this fix request went in, with a close-up photo of an eyelid with tiny black mascara dots attached for reference only:

> I don't like the mascara moment in shot 1, it looks unnatural. The mark shows up in some random spot instead of coming from the wand itself. I'm attaching a photo, and the mark should look roughly like that: a small smudge of tiny black dots on the upper eyelid, not a line or a streak. That photo is just a reference for you, don't add it to the generation. The mark should only appear where the wand actually touches that spot of skin, and only at that moment: the jolt sends her hand up and the tips of the wand poke her upper eyelid. When the wand touches, the camera only shakes slightly; the strong room shake comes after. Then she squeezes that eye shut and leans toward the mirror, with the smudge visible on her closed lid. In shot 2 the smudge stays on her eyelid. Leave everything else as is.

What the fix changed in the prompt, and nothing else:

- A new hard requirement 1: the mark is the print of the bristles, only where and when they touch.
- Shot 1 re-timed into single events: 0.0–1.5 s mascara with a clean eyelid; 1.5–2.7 s one jolt pushes the brush up and the bristle tips press the eyelid; 2.7–4.0 s only then the room shakes; 4.0–5.5 s she leans in and sees the mark.
- A "WHAT THE MARK LOOKS LIKE" paragraph that puts the reference photo into words (size, texture, density).
- Shot 2: the speckled patch is still on her eyelid.
- The audio starts with one heavy thud, and the negatives gained a group of bans about the mark.

The final Video 1 prompt, after the fix:

```text
9:16 VERTICAL. 10 SECONDS. TWO SHOTS, EXACTLY ONE HARD CUT AT 5.5s. No speech. NO MUSIC ANYWHERE IN THIS FILM — real recorded sound only.

READ THIS FIRST — THIS IS A SEQUENCE OF TWO SHOTS, NOT A SINGLE TAKE: shot 1 runs from 0.0 to 5.5s, then ONE straight hard cut, then shot 2 runs from 5.5 to 10.0s. No other cuts, no dissolves, no fades.

=== 4 HARD REQUIREMENTS ===

1. THE MASCARA MARK IS THE PRINT OF THE BRISTLES. It appears only at the spot on her upper eyelid that the brush touches, and only at the moment it touches.
2. SHE IS NEVER LIT. The only light in the film is the daylight and the sun that are already in the place. No lamps of any kind.
3. BOTH SHOTS ARE HANDHELD WITH A SMALL CONSTANT SHAKE. The zoom is never used.
4. THE WINDOW IS THE TWO-LEAF WINDOW OF @Image3, IT OPENS OUTWARD AND SHE IS BEHIND ITS GLASS. Both of its leaves are in the picture. SHE STANDS BEHIND THE LEFT LEAF, in the left half of the frame, and it is the LEFT leaf that she opens, with her LEFT hand; the right leaf stays shut, with nobody behind it. Until the leaf swings out, every part of her is indoors behind the pane. Her hand comes into the open air only through the gap of the opening leaf, never through glass.

INPUTS.
@Image1 — THE WOMAN, THE ONLY SOURCE OF HER FACE, HAIR, BUILD AND DRESS: take her exact face, her hair, her proportions and her cream dress with the long pointed collar edged in yellow. TAKE NOTHING ELSE FROM @Image1 — not the three-panel layout, not the grey backdrop, not the pose, not its framing. Ignore the studio lighting of @Image1.
@Image2 — THE PLACE, THE ONLY SOURCE OF THE LOCATION AND OF THE LIGHT: this exact bathroom — the small mint-green square wall tiles, the white floor, the big mirror above the wooden vanity with the white basin, the white bathtub, the warm patch of sun on the tiles. Nothing in the room is invented, added or moved. THE WINDOW OF THIS BATHROOM IS THE BATHROOM WINDOW OF @Image3: @Image2 shows it from inside, @Image3 shows it from outside, and it is one and the same window. No other kind of window appears in this film. THE REFERENCE DEFINES THE WORLD, NOT THE FRAMING: the camera positions of both shots are our own.
@Image3 — THE HOUSE, SHOT 2 ONLY, THE ONLY SOURCE OF THE OUTSIDE WALL AND OF THE WINDOW AS SEEN FROM OUTSIDE: take from it the ground-floor window to the right of its front door and the lilac wall around that window — this exact window: its white-painted wooden frame, its two leaves that meet in the middle, its panes, its proportions, its sill, the light curtains tied back inside it, and the wooden flower box of red geraniums under it. TAKE NOTHING ELSE FROM @Image3 — not the whole house, not its roof, not its balloons, not the meadow, not its framing.

THE CAMERA, BOTH SHOTS — HANDHELD, WITH A SMALL CONSTANT SHAKE: held in a real person's hands. A fine, irregular tremble never leaves the frame — tiny bumps, breathing drift, the frame sitting a degree off level, small late corrections a beat after she moves. THE ZOOM IS NEVER USED ANYWHERE and the operator does not walk closer.

=== SHOT 1 — 0.0 to 5.5s — TIGHT CLOSE-UP OVER HER SHOULDER INTO THE MIRROR ===
A TIGHT CLOSE-UP, NOT A VIEW OF THE ROOM. She stands at the mirror of @Image2; the camera is right behind one of her shoulders. HER REFLECTED FACE FILLS THE FRAME — from her hairline to her chin it takes up most of the frame height — sharp in the mirror. Along one edge, very close to the lens and out of focus, is a sliver of the back of her head and her shoulder. Behind her face there is only a soft blur of mint tiles and one warm patch of sun. If the basin, the vanity or the window can be seen, the shot is too wide and it is wrong. She looks at her own reflection, never at the lens.
0.0–1.5s — MASCARA: already mid-action — chin slightly raised, lips a little apart, she draws a mascara brush up through the upper lashes of one eye, slowly and carefully. One hand in the frame, hers, holding the wand. Her eyelid is clean.
1.5–2.7s — THE BUMP — THE ONLY EVENT OF THESE SECONDS: the floor gives one hard lurch; we hear it and we see her sway. Her hand is pushed UPWARD by it: the brush rides up past the lashes and the tips of its bristles PRESS against her upper eyelid, just above the lash line, for an instant. Then her hand pulls the brush away. Where the bristles touched the skin, and only there, they leave their print. During this the camera only trembles: her eye, her hand and the brush stay sharp and inside the frame.
WHAT THE MARK LOOKS LIKE: a small patch of mascara on the upper eyelid, about the size of a fingertip — dozens of tiny black specks and short flecks, stippled into the skin, dense in the middle and thin and scattered at the edges, with clean skin showing between them. It is the dotted print of wet bristle tips.
2.7–4.0s — THE ROOM SHAKES AND SETTLES: only now does the whole room shake for a second — the mirror image shudders, things rattle, the operator is jolted — and it dies away. Nothing falls and nothing breaks. She has flinched: that eye is squeezed shut, the hand with the wand held away from her face.
4.0–5.5s — SHE SEES IT: the shaking is gone. She keeps that eye closed and leans a little towards the mirror; the speckled patch sits plain on her closed eyelid, exactly where the brush touched. Her brows draw slightly together and she lets out a small breath. Then the eye opens and her gaze slides sideways towards the window.

=== CUT AT 5.5s ===

=== SHOT 2 — 5.5 to 10.0s — OUTSIDE, STRAIGHT ON TO THE WINDOW ===
CUT. The camera is outside the house, at the ground floor, level and square on to the bathroom window: the ground-floor window to the right of the front door of @Image3, exactly as it is there. THE FRAME HOLDS THE WHOLE TWO-LEAF WINDOW, exactly as it is in @Image3: the window fills the width of the vertical frame, its LEFT LEAF in the left half of the frame and its RIGHT LEAF in the right half, the two white stiles where they meet running down the middle of the frame. SHE COMES TO THE LEFT LEAF: for the whole shot she is in the left half of the frame, behind the glass of the left leaf. Behind the glass of the right leaf there is only its tied-back curtain and the dim room. Above the window are the lilac boards; below its sill, the flower box. Around the window, the outside wall of the cottage as in @Image3: horizontal wooden clapboards painted a soft pastel lilac, slightly faded by the sun, with small paint chips and thin shadow lines between the boards. Under the window sill hangs its wooden flower box of red geraniums.
THE WINDOW, EXACTLY — the window of @Image3, the same one that @Image2 shows from inside:
— THE FIXED FRAME: a white-painted wooden frame set in the lilac wall, the paint slightly peeling, with a white sill along the bottom.
— TWO EQUAL LEAVES stand side by side in that frame and meet in the middle of the window. THE WINDOW IS ABOUT AS WIDE AS IT IS TALL, exactly as in @Image3. Each leaf is a white-painted wooden rectangle, about twice as tall as it is wide, holding ONE PLAIN PANE of clear glass from its top rail to its bottom rail, with no glazing bars. Each leaf is exactly half as wide as the window opening and exactly as tall as it; together the two close the opening completely.
— THE HINGES of each leaf are on its OUTER edge: the left leaf hangs on the left side of the fixed frame, the right leaf on the right side.
— THE LEAVES OPEN OUTWARD ONLY: away from the room, towards the camera and the open air, each turning on its outer edge like one half of a double door. A leaf never swings into the room.
— THE CATCH IS INDOORS: each leaf is fastened by a small catch on its ROOM side, on its middle stile, hidden from the camera by the white wood. The outdoor side of the window, the side the camera sees, is plain painted wood and glass: there is no metal on it at all.
— INSIDE THE WINDOW hang its light curtains, tied back at the two sides as in @Image3, clear of the glass; she stands beside the left curtain, behind the left leaf.
LEFT and RIGHT are the left and right of the frame as we look at the window from outside.
WHAT IS ON WHICH SIDE OF THE GLASS — THE RULE OF THIS SHOT: the camera is OUTDOORS, the woman is INDOORS, and the pane between them is a solid sheet of glass. While the window is shut, ALL of her is behind the glass of the left leaf: her face, her body, both arms, both hands, every finger. We see her only THROUGH the pane, a little dimmed, with the reflected sky and clouds lying over her. In front of the glass and in front of the white wood there is only open air. Her hand comes outdoors in the last second, and only THROUGH THE GAP of the opening leaf.
The glass carries a soft reflection of bright blue sky, white clouds and a low line of green hills; behind it are its tied-back curtains, the dim mint-tiled room of @Image2 and the woman, and nothing else.
HER HANDS: HER LEFT HAND IS THE OPENING HAND — her own left hand, which is on the RIGHT side of the frame as she faces us, the side of the middle of the window, where the catch is. Her right hand, on the left side of the frame, rests on the inner sill and stays there for the whole shot.
A LIGHT TREMOR STILL RUNS THROUGH THE HOUSE FOR THE WHOLE SHOT: the glass quivers, so the reflected clouds shiver in it; the boards creak; a little dust sifts down from the top of the window frame; and the handheld camera trembles a little more than in shot 1.
5.5–6.7s — She comes out of the dimness of the room up to the glass of the left leaf and stops just behind it, her right hand coming to rest on the inner sill to steady herself; her left hand hangs at her side. All of her is behind the glass. The small speckled patch of mascara is still on that eyelid.
6.7–8.2s — SHE LOOKS OUT, SPELLBOUND — at something far away and above, well past the camera, never into the lens. Her eyes travel slowly up and across. Her brows lift by a few millimetres, her lips part barely, she blinks once. That is all.
8.2–9.0s — HER LEFT HAND GOES TO THE HANDLE, INDOORS: without taking her eyes off what she sees, her left hand rises behind the glass to the catch on the room side of the left leaf's middle stile, which the white wood hides from us, and closes on it. We see only her hand, through the pane at its right edge: the back of her hand and her knuckles, dimmed by the glass, half hidden behind the stile. Her wrist turns a quarter turn and the catch lets go with a small click. Nothing has moved yet; she is still entirely behind the glass.
9.0–10.0s — SHE PUSHES THE LEFT LEAF OPEN FROM INSIDE: her left hand leaves the catch, lies flat on the room side of that middle stile and pushes AWAY from the room. The left leaf turns on its hinges like a door: its left edge stays in the fixed frame, its right edge parts from the right leaf and swings OUT TOWARDS THE CAMERA, into the open air. The leaf opens OUTWARD and TO THE LEFT; the right leaf does not move. A dark gap of open air appears between the two leaves, down the right side of the frame, and widens steadily. Her hand goes out with the wood it is pushing: in that gap, in the open air, first her fingertips appear on the edge of the leaf, in the sunlight, then her knuckles, then her wrist. They pass through the gap and never through a pane. The rest of her stays indoors, seen through the turning glass. The reflected sky slides across the pane as it turns, and the bottom rail of the leaf passes just above the red geraniums. By the last frame the gap is about a hand's width wide, her fingers are on the edge of the leaf, and the leaf is still moving outward.

NATURAL PERFORMANCE — NO ACTING: reactions are small and physical. The HANDS STOP FIRST and only then does the face change. A blink, brows drawing slightly together rather than shooting up, lips parting barely, a few degrees of head tilt. No wide eyes, no dropped jaw, no comedy shock face.

LIGHT — AVAILABLE LIGHT ONLY, LIKE A REAL DOCUMENTARY WITH NO LIGHTING CREW: there is NO film lighting in this film at all — no lamps, no softboxes, no reflectors, no bounce boards, no fill, no flash exist here. The only light is the daylight and the warm sun patch of @Image2, coming through its one window. She is NEVER lit; she is simply in the same daylight as everything around her. Her face is NOT brighter than the surroundings next to her — it has the same brightness and colour as her surroundings. In shot 1 the window is to her side: the side of her face away from it is dark and soft. In shot 2 her face is behind the glass, in the shade of the room, slightly UNDEREXPOSED against the sunny lilac wall. Her skin is matte, with natural texture, no sheen and no highlights on it; the only reflection in her eyes is the window and the sky.

THE LOOK: maximum realism — real footage from a real camera. A soft, gentle picture: soft natural contrast, nothing over-sharpened, natural colour. Warm patches of real sunlight on the tiles, the wood and the lilac boards; soft natural shade everywhere else. Real skin with pores, real lashes, real creases in the cotton dress, real glass and painted timber. No readable text or logos anywhere.

AUDIO — NO MUSIC AT ALL: only real recorded sound. Shot 1: quiet room tone, then one heavy thud through the floor, a deep low rumble, glass and ceramic rattling, her one short sharp intake of breath, the rumble fading. Shot 2: outdoor air, light wind, a low steady tremble in the timber, the window glass ticking in its frame, the click of the catch, the soft creak of the hinges as the leaf swings out. Absolutely no music, no score, no strings, no drone track, no sound cue.

NEGATIVE: no music, no score, no soundtrack, no beat; no mark appearing by itself, no mark anywhere the brush did not touch, no mark before the brush touches the skin, no mark on the cheek, no line, no streak, no thick smear, no painted stroke, no ink blot, no bruise, no mascara running down the face, no mark changing place between shots; NO LIGHTING ON THE PERSON — no key light, no fill light, no rim light, no hair light, no front light on her face, no softbox, no reflector, no bounce, no flash, no studio lighting, no beauty lighting, no commercial or advertising look, no catchlights from lamps, no shiny or glowing skin, no face brighter than the background, no separation light around her; no glow, no bloom, no halation on her; no lamp switched on in the room; no hand or arm passing through glass, no hand in front of the glass or the wood while the window is shut, no handle, knob, lever or latch on the outside of the window, no leaf swinging into the room, no one-leaf window, no figure behind the right leaf, no right hand opening the window, no window that differs from the window of the house picture, no brown or unpainted window frame, no tilting top pane, no window sliding up; no zoom, no push-in, no crash zoom, no punch-in, no locked-off frame, no tripod; no extra cuts, no dissolve, no fade, no one continuous take; no slow motion, no speed ramp; no wide eyes, no dropped jaw, no scream, no mugging, no smile; no looking into the lens; no second person, no extra hands, no extra fingers, no morphing face, no plastic or waxy skin, no beauty filter; no readable text or logos, no subtitles.
```

Settings: Seedance 2.5 · 9:16 · 10 seconds · sound on · reference pictures in this order: 1 the character sheet, 2 the bathroom, 3 the house from outside (as references, not as a start frame).

### 6. Video 2, the reveal

Request, with the same three pictures plus the view from the window:

> Now generation 2, continuing the same video, also 10 seconds. The photos stay the same and in the same order: photo 1 is the girl, photo 2 is the bathroom, photo 3 is the house from outside. I'm adding photo 4: the view from the window (the landscape).
> Shot 1, 4 seconds: a wide low-angle shot from the ground of the house from photo 3, in the same place and with the same background as in photo 3: the meadow, the rolling hills, the sky with clouds. The shot opens with the house already lifted off the ground and slowly rising, dirt falling off it, the balloons always pulling upward. The house is real, full-size and heavy, not a toy, and the balloons are small and there are tons of them. The camera's down in the grass near her window, with the house filling almost the full width of the frame. You can clearly see the girl in the ground-floor window right next to the front door, the one with the red geraniums under it, leaning out of the opening with her head and shoulders. It's the same two-leaf window: its left leaf is already fully open, and with the same left hand as in generation 1 she pushes the right leaf all the way open too, outward, so the whole window stands open. Then she looks down, and up at the balloons.
> Shot 2, 6 seconds, a long ending: inside the bathroom, a medium shot over the girl's shoulder, at that same window, already open, its two leaves swung outside. Instead of a garden outside, there's the landscape from photo 4 seen from above: the long white bridge on arches stretching across the plain and rising into the sky, clouds drifting. The view slowly sinks down because the house is rising. At the end, the camera drifts forward a little in a natural, handheld way.
> Everything else stays the same as generation 1. Don't add artificial light to the house; it's in the same sunlight as the grass.

Prompt:

```text
9:16 VERTICAL. 10 SECONDS. TWO SHOTS, EXACTLY ONE HARD CUT AT 4.0s. No speech. NO MUSIC ANYWHERE IN THIS FILM — real recorded sound only.

READ THIS FIRST — THIS IS A SEQUENCE OF TWO SHOTS, NOT A SINGLE TAKE: shot 1 runs from 0.0 to 4.0s, then ONE straight hard cut, then shot 2 runs from 4.0 to 10.0s. No other cuts, no dissolves, no fades. THE SECOND SHOT IS THE LONG ONE: six unhurried seconds.

=== 5 HARD REQUIREMENTS ===

1. THE FILM BEGINS WITH THE HOUSE ALREADY IN THE AIR, and THE WOMAN IS CLEARLY VISIBLE AT ONE PARTICULAR WINDOW, leaning out into the daylight BETWEEN ITS TWO OPEN LEAVES: the ground-floor window IMMEDIATELY TO THE RIGHT OF THE FRONT DOOR, in the same wall as the door, with the flower box of red geraniums right under her. Throughout shot 1 the front door is in the picture beside her, and that wall, the gable wall, faces the lens.
2. NOTHING IN THIS FILM IS LIT. The woman, the house and the balloons are in the sun and daylight that are already in the places, and in nothing else. No lamps of any kind.
3. BOTH SHOTS ARE HANDHELD WITH A SMALL CONSTANT SHAKE. The zoom is never used.
4. THE HOUSE IS THE REAL, FULL-SIZE WOODEN COTTAGE OF @Image3, filmed in its own meadow: its front wall about four metres wide, about four and a half metres high to the roof ridge, its front door two metres tall, heavy as a real building. Its balloons always pull straight up and it rises SLOWLY.
5. IT IS ONE AND THE SAME WINDOW IN BOTH SHOTS, A REAL TWO-LEAF WINDOW THAT OPENS OUTWARD ONLY: a white-painted frame and in it two equal leaves, each leaf one white wooden frame around ONE SINGLE SHEET of clear glass, each exactly half as wide as the opening and as tall as it. Both leaves swing out into the open air, never into the room. IN SHOT 1 EXACTLY TWO OPEN LEAVES ARE IN THE PICTURE THE WHOLE TIME, one on each side of her — one on the door side, one on the corner side — like two wings; in shot 2, from inside, they are still outdoors, beyond the wall. Her head and arms pass only through the opening between them, never through glass.

INPUTS.
@Image1 — THE WOMAN, THE ONLY SOURCE OF HER FACE, HAIR, BUILD AND DRESS: take her exact face, her hair, her proportions and her cream dress with the long pointed collar edged in yellow. She is barefoot — the white sneakers of @Image1 are never seen. TAKE NOTHING ELSE FROM @Image1 — not the three-panel layout, not the grey backdrop, not the pose, not its framing. Ignore the studio lighting of @Image1.
@Image2 — THE BATHROOM, SHOT 2 ONLY, THE ONLY SOURCE OF THE ROOM: this exact bathroom — mint-green square wall tiles, white floor, the window in the far wall, the wooden vanity, the white bathtub, the warm patch of sun on the tiles. Nothing in the room is invented, added or moved. THE WINDOW OF THIS BATHROOM IS THE BATHROOM WINDOW OF @Image3 seen from inside — one and the same window, white inside as well as outside; no other kind of window appears in this film. IN @Image2 THIS WINDOW IS SHUT; IN SHOT 2 IT IS OPEN: its two leaves have been pushed out of the room and stand outdoors. DO NOT TAKE WHAT IS SEEN THROUGH ITS WINDOW: whatever is outside the window in @Image2 is ignored completely and replaced by the world of @Image4. The framing of the shot is our own.
@Image3 — THE HOUSE, ITS BALLOONS AND THE PLACE, SHOT 1 ONLY: A REAL PHOTOGRAPH, THE ONLY SOURCE OF THE HOUSE, OF THE LOCATION OF SHOT 1 AND OF ITS LIGHT. Take this exact cottage — its soft lilac clapboards, slightly faded and chipped, its white window frames, its lilac front door with the wooden porch step, the flower boxes of red geraniums under the two front windows, the attic window in the gable, the weathered lavender-grey shingle roof with its brick chimney, the gutter and the downpipes. Take its balloons — the big dense cluster of ordinary multicoloured party balloons, a great many of them, tied by thin white strings to the hook on the roof ridge, the same cluster as in the photograph. Take this exact place — the meadow of long summer grass with wildflowers, the soft rolling green hills behind it, the blue sky with white cumulus clouds — and its real sunlight, high and from the left. Nothing in the place is invented or added. THE REFERENCE DEFINES THE WORLD, NOT THE MOMENT AND NOT THE FRAMING: in @Image3 the house still stands on its stone foundation and is seen from standing height thirty metres away; in this film it has already torn free and hangs in the air, and the camera is low in the grass close to it. The low foundation of grey fieldstones and the porch step stay behind on the ground.
@Image4 — THE WORLD SEEN FROM THE WINDOW, SHOT 2 ONLY, THE ONLY SOURCE OF THAT VIEW: the immense green plain far below, the endless white arched viaduct that runs across the plain and climbs into the sky, the sea, the sharp snowy mountain, the white clouds and the wall of city standing in the sky. Nothing in this landscape is invented or added. It is seen only through the bathroom window in shot 2, from high in the air; nothing of @Image4 appears in shot 1. THE REFERENCE DEFINES THE WORLD, NOT THE FRAMING: the camera position is our own.
HER WINDOW — ONE AND THE SAME WINDOW IN BOTH SHOTS. Every window frame of the house is WHITE, outside and inside. Her window is the ground-floor window IMMEDIATELY TO THE RIGHT OF THE FRONT DOOR in @Image3, in the gable wall, the same wall as the door: the door, then a narrow strip of lilac boards, then this window, then the corner of the house. Its wooden flower box of red geraniums hangs under its sill. In shot 1 we see this window from outside, exactly as it is in @Image3; in shot 2 we see the same window from inside, as @Image2 shows it. It is built like this, and it looks like this in both shots: a fixed white-painted wooden frame with slightly peeling paint, about as wide as it is tall, and in it TWO EQUAL LEAVES side by side that meet in the middle. Each leaf is one white-painted wooden frame, about twice as tall as it is wide, around ONE SINGLE SHEET of clear glass that runs unbroken from its top rail to its bottom rail — exactly like the two halves of this window in @Image3. Each leaf is exactly half as wide as the opening and exactly as tall as it. Each leaf is hinged on its OUTER edge — the left leaf on the side of the front door, the right leaf on the side of the house corner — and BOTH OPEN OUTWARD ONLY, away from the room, like the two halves of a double door. Their catches are on the room side, so the outdoor side of the window is plain painted wood and glass. An open leaf is still the same full-size leaf: standing open, it is as tall as the opening and half as wide as it, with the same single sheet of glass. Inside the window hang its light linen curtains, tied back at the two sides; they are in the room, behind her, in both shots. Every other window of the house stays exactly as it is in @Image3, shut, with nobody at it. The LEFT and RIGHT of the house and of this window are their left and right as we see them in the frame of shot 1.

THE CAMERA, BOTH SHOTS — HANDHELD, WITH A SMALL CONSTANT SHAKE: held in a real person's hands. A fine, irregular tremble never leaves the frame — tiny bumps, breathing drift, the frame sitting a degree off level, small late corrections. THE ZOOM IS NEVER USED ANYWHERE: closer means the operator walked closer.

=== SHOT 1 — 0.0 to 4.0s — WIDE SHOT FROM THE GROUND, LOW ANGLE: THE HOUSE IS ALREADY IN THE AIR ===
ON THE VERY FIRST FRAME THE HOUSE HAS ALREADY LEFT THE GROUND: its base hangs about half the height of its front door above a torn, dark patch of earth in the meadow of @Image3, ringed by the grey fieldstones of the foundation it has left behind, earth still dropping from its underside, and it is rising. THE HOUSE IS SEEN FROM ITS FRONT: the GABLE WALL of @Image3 — the wall with the front door, the two front windows with their flower boxes and the attic window above them — FACES THE LENS AND FILLS MOST OF THE FRAME WIDTH. The long side wall is only a narrow strip beyond the right-hand corner of the house, turned away from the lens. THE CAMERA IS ALMOST ON THE GROUND STRAIGHT IN FRONT OF THE FRONT DOOR, a few steps from it, and looks UP at the gable wall: the door is straight ahead of the lens, in the left half of the frame, and her window is right beside it, in the right half. Tall soft blades of grass and a few wildflowers stand right in front of the lens along the bottom of the frame, THE HOUSE TOWERS OVER US AND FILLS MOST OF THE FRAME WIDTH, and its cluster of balloons fills the top of the frame against the blue sky and white clouds. THE BACKGROUND IS THE PLACE OF @Image3 AND NOTHING ELSE: behind and beside the house, low in the frame, the same soft rolling green hills receding in layers, and above them the same blue sky with white cumulus clouds.
THE WOMAN IN THE WINDOW — THE SECOND SUBJECT OF THIS SHOT, CLEARLY VISIBLE THE WHOLE TIME: her window is in the wall that faces the lens, the gable wall, immediately to the right of the front door, in the lower half of the frame. THE FRONT DOOR IS RIGHT BESIDE HER, to the left of her window, and THE RED GERANIUMS OF THE FLOWER BOX ARE RIGHT UNDER HER, in every frame of this shot. On the first frame BOTH LEAVES ARE IN THE PICTURE, swung out into the open air like two wings. The LEFT leaf, the one next to the front door, is already fully open: it stands out from the wall well past a right angle, splayed back towards the door, and we see the whole of it from its room side — one tall white frame around one single sheet of glass, as tall as the opening and half as wide, standing beside the left edge of the opening, the lilac boards showing clearly through its glass. The RIGHT leaf, the one next to the house corner, is half open: it stands out from the wall at about half a right angle, on the corner side — the same kind of leaf, one white frame around one single sheet of glass. Between the two leaves the opening is clear, open air. SHE IS INSIDE THE ROOM, standing on its floor behind the wall, in the middle of the window, and she leans out THROUGH THE OPENING, forward over the sill and the red geraniums: her head, her shoulders and both her arms are in the open daylight beyond the line of the wall, and everything of her below the sill is indoors, hidden by the wall. HER LEFT HAND IS THE OPENING HAND — her own left hand, on the RIGHT side of the frame as she faces us: it lies flat on the room side of the right leaf, near its free edge, where she is pushing it. HER RIGHT HAND, on the LEFT side of the frame, rests on the open left leaf: it holds the white wood of that leaf by its near edge, at the height of her shoulder. So she stands with her arms spread, one hand on each leaf. She touches only the white wood of the two leaves and of the sill, and her arm passes only through the opening. Her hair, cream dress, yellow-edged collar, clear against the lilac boards. From the sill to the top of her head she takes up about one eighth of the frame height.
0.0–2.0s — SHE OPENS THE WINDOW ALL THE WAY, WITH THE SAME LEFT HAND: her left hand gives the right leaf one long push, away from the room. The leaf goes on turning on its hinges like a door, its free edge travelling in an arc further outward and to the right, away from her hand, the reflected sky sliding across its single sheet of glass, until it stands FULLY OPEN, well past a right angle to the wall on the corner side of the window, and stops there. Now both leaves stand open like two wings, one on each side of her, and the whole window is open. Her left hand lets the leaf go halfway and stays stretched out in the air for a moment; her right hand is still on the left leaf. Meanwhile the house keeps climbing, slowly and heavily, swaying a little under the balloons like a load under a crane; the last clods and roots fall from its base onto the torn patch below.
2.0–4.0s — The window is wide open and both leaves stay where they stopped, one on each side of her. Both her hands come back to the sill; between the two open leaves she leans out over the sill on both hands and looks down at the ground dropping away beneath her, then up at the balloons; the wind lifts her hair. The gap of open air under the house grows to about the height of the house itself by the last frame, and its shadow slides away across the grass. The operator tilts up a beat late, keeping her window in frame. Still rising on the last frame.
The balloons stay above the roof the whole time, jostling and rubbing against each other; the house stays whole and almost level.

=== CUT AT 4.0s ===

=== SHOT 2 — 4.0 to 10.0s — THE LONG ENDING: INSIDE, MEDIUM SHOT OVER HER SHOULDER ===
CUT. Inside the bathroom of @Image2, at THE SAME WINDOW we have just seen from outside, now seen from the room, fully open. WHAT WE SEE OF THE WINDOW FROM INSIDE: its fixed white-painted frame — two upright jambs, the head across the top, the white sill at the bottom — and inside that frame ONE CLEAR OPEN RECTANGLE OF AIR, from the sill to the head and from jamb to jamb, about as wide as it is tall. BOTH LEAVES ARE WHOLLY OUTDOORS: each stands out beyond the wall on its own side, turned away from the room, so from the room each is seen EDGE-ON — a thin upright white strip of wood standing outside, just past its jamb, one at the far left of the opening and one at the far right. In the room, at the two sides of the window, hang its light linen curtains, tied back, stirring a little in the wind. Outside, just above the outer edge of the sill, show a few red heads of the geraniums in the flower box that hangs under this window. A MEDIUM SHOT OVER HER SHOULDER, held for six unhurried seconds: the camera stands just behind her and a little to one side, at the height of her shoulders. The back of her head and one shoulder — her hair, the yellow-edged collar — fill about a third of the frame on one side, close and slightly soft; past them, sharp, are her hands on the sill, the white window frame and the world outside. Around the window, mint tiles. FROM THE VERY FIRST FRAME OF THIS SHOT, THROUGH THE OPEN WINDOW IS THE WORLD OF @Image4, seen from the air: the endless white arched viaduct running away across the green plain and climbing into the sky, the sea, the clouds. This room is high in the air above it all: straight below the sill there is only open air and, far down, the green plain. Because the house is rising, the whole view sinks slowly and steadily down past the window frame for the entire shot.
4.0–6.0s — She stands at the open window with both hands on the sill and looks out; we look with her. Wind comes in and lifts a few strands of her hair.
6.0–8.0s — She leans forward a little into the opening and looks down and out. A white cloud drifts past close outside, sliding across the lower part of the view and thinning away.
8.0–10.0s — The cloud is gone and the view is clear: the white viaduct runs away below and climbs into the sky ahead. The operator eases one small step forward, handheld. Her hair is still moving in the wind and the view is still sinking on the last frame.

LIGHT — AVAILABLE LIGHT ONLY, LIKE A REAL DOCUMENTARY WITH NO LIGHTING CREW: there is NO film lighting in this film at all — no lamps, no softboxes, no reflectors, no bounce boards, no fill, no flash exist here. In shot 1 the only light is the sun and open sky of @Image3; in shot 2 it is the daylight of @Image2 coming through its one window, and the world outside that window is in the sun of @Image4. She is NEVER lit; she is simply in the same daylight as everything around her. In shot 1 she leans out of the window into the open daylight: she is in the same sun and shade as the boards beside her, no brighter than they are, and plainly readable. In shot 2 she is a darker, softer shape against the bright view. Her skin is matte, with natural texture, no sheen and no highlights on it.
ONE SINGLE LIGHT FOR EVERYTHING OUTDOORS: the house, the balloons, the grass, the woman in her window and the hills behind are in ONE AND THE SAME SUN, the sun of @Image3. One colour temperature, one exposure and contrast, one shadow direction: the house has one sunlit side and one side in real shade, cooler and darker, and it throws a real shadow on the grass. The balloons carry only the broad soft reflection of the sky and one small point of the same sun. Nothing about the house is brighter, cleaner, sharper or more saturated than the grass in front of it; one lens, one softness, one grain and one motion blur across the house and the landscape.

THE LOOK: maximum realism — real footage from a real camera, the same look in both shots. A soft, gentle picture: soft natural contrast, nothing over-sharpened, natural colour. Warm patches of real sunlight on the lilac boards, the grass and the bathroom tiles; soft natural shade everywhere else. Real painted timber, real latex, real earth and roots, real cotton, real motion blur. No readable text or logos anywhere.

AUDIO — NO MUSIC AT ALL: only real recorded sound. Shot 1: wind over the grass, the deep groan of timber, the last earth pattering down, the squeak and rub of the latex balloons, strings humming, the creak of the window hinges and the knock of the leaf as it stops. Shot 2: wind coming in through the open window and growing steadier, the slow creak of the house, the faint squeak of balloons overhead, her quiet breath. Absolutely no music, no score, no strings, no drone track, no sound cue.

NEGATIVE: no music, no score, no soundtrack, no beat; no figure at a side-wall window, no side wall facing the lens, no figure at any window other than the one beside the front door, no window that differs between the two shots, no leaf swinging into the room, no leaf inside the room, no leaf standing over the sill or in front of the tiles, no glazing bars, no leaf divided into small panes, no fixed top light or transom over the window, no brown window frame, no tilting top pane, no window sliding up, no leaf of the wrong size, no missing leaf in the wide shot, no window with only one leaf, no hand or arm passing through glass, no handle on the outside of the window; no house standing on the ground at the start, no empty window beside the front door, no figure lost in a dark window; NO LIGHTING ON THE PERSON — no key light, no fill light, no rim light, no hair light, no front light on her face, no softbox, no reflector, no bounce, no flash, no studio lighting, no beauty lighting, no commercial or advertising look, no catchlights from lamps, no shiny or glowing skin, no face brighter than the background, no separation light around her; no glow, no bloom, no halation on her; no lamp switched on in the room; no studio light on the house, no rim light on the house, no glossy or plastic house, no glowing balloons, no house brighter than the landscape; no zoom, no crash zoom, no punch-in, no locked-off frame, no tripod, no gimbal-smooth move, no drone move, no orbit; no extra cuts, no dissolve, no fade, no one continuous take, no short last shot; no slow motion, no speed ramp, no rocket-fast rise, no weightless floating; no toy house, no miniature, no dollhouse, no scale model, no tiny house; no balloons hanging down, no balloon bursting, no balloons flying away; no garden or trees outside the bathroom window, no meadow at the level of the sill, no house and no balloons seen through the window; no looking into the lens; no second person, no extra limbs, no morphing face, no plastic or waxy skin; no cartoon, no animation look, no CGI look; no readable text or logos, no subtitles.
```

Settings: Seedance 2.5 · 9:16 · 10 seconds · sound on · reference pictures in this order: 1 the character sheet, 2 the bathroom, 3 the house from outside, 4 the view from the window (as references, not as a start frame).
