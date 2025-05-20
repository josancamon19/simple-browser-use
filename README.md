## Making a Simple Browser Use Agent

This repo aims to make a fully working implementation of a browser agent without taking on existing implementations.

It shouldn't be that hard.


- Environment -> browser
- Actions -> click, scroll, type, new tab, back ...
- Actions (exec) -> playwright, selenium, puppeteer
- Observation space -> text/visual, DOM, accessibility tree, visual


-----

### Notes:

1. Playwright > Puppetter > Selenium -- Use playwright.
2. The accessibility tree is not the full DOM — it’s a filtered, semantic tree designed for screen readers and assistive technologies. It only includes nodes that are “accessible” (i.e., relevant for user interaction or understanding).
3. Playwright launches a real browser, headless (invisible) by default.
4. V1, works in 110 lines.
5. Some websites have blockers for agents (e.g. Google search)
6. sonnet-3-7 latest is best

------

### Tasks

- [ ] what happens when it tries to click, but hasn't scrolled to have that \#id visible
  - [ ] Quickly test playwright
- [ ] Prev state shouldn't be fully cleaned, (maybe summarized, what was this) cause when to backtrack
- [ ] Test playwright MCP standalone, how's performance, any tricks from there?
- [ ] More actions to include (?)
- [ ] Improve DOM Parser, and/or space observation tasks
- [ ] Make a cli


- [ ] create a test dataset, run untill all work
- [ ] run it with webarena, webvoyager, gaia and submit results
   - Try hud.so, benchflow + oyo

- [ ] human in the loop interaction, when to ask for help
- [ ] how to use other observation inputs
- [ ] How to handle context exceeded from a single state