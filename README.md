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


------

### Tasks

- [ ] each function should return completion message + new state
- [ ] the state dom should be cleaned from previous trajectories.
- [ ] what happens when it tries to click, but hasn't scrolled to have that \#id visible
- [ ] track traces
- [ ] create a test dataset, run untill all work
- [ ] handle js/render waits
- [ ] human in the loop interaction, when to ask for help
- [ ] run it with webarena and submit results
- [ ] how to use other observation inputs