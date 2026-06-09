# AI engineering philosophy

## ai engineering philosophy

Van Keith believes ai coding does not make software fundamentals less important. It makes them more important.

Core position:

- code is more a liability than an asset, especially in big systems
- if we let ai add code at 10x speed, what we get is not 10x performance, it is 10x chaos, and that leads to some kind of disaster
- bad code is extremely expensive, and humans are still the strategic layer
- ai is the tactical programmer, but the engineer guides design, interfaces, modules, testing strategy, and long term maintainability
- specs to code without understanding the codebase usually gets worse over time

He resonates with these quotes:

- “no one knows exactly what they want.” (David Thomas and Andrew Hunt, The Pragmatic Programmer)
- “with a ubiquitous language, conversations among developers and expressions of the code are all derived from the same domain model.” (Eric Evans, Domain Driven Design)
- “always take small, deliberate steps. the rate of feedback is your speed limit. never take on a task that’s too big.” (David Thomas and Andrew Hunt, The Pragmatic Programmer)
- “invest in the design of the system every day.” (Kent Beck, Extreme Programming Explained)
- “the best modules are deep. they allow a lot of functionality to be accessed through a simple interface.” (John Ousterhout, A Philosophy of Software Design)
- “simplicity is the ultimate sophistication.” (Leonardo da Vinci)

### the four common failure modes with ai agents

Van Keith frames the failures in working with ai coding agents in four buckets.

1. the agent didn’t do what i want. this is misalignment. fix it with a grilling session, making the agent ask detailed questions before it builds.
2. the agent is way too verbose. this is a missing shared language. fix it with a project glossary so the agent speaks the actual domain instead of inventing 20 words for one concept.
3. the code doesn’t work. this is missing feedback loops. fix it with static types, browser access, automated tests, red green refactor, and a clean debugging loop.
4. we built a ball of mud. this is accelerated software entropy. fix it by caring about design every day, asking which modules are touched before generating a prd, explaining code in the context of the whole system, and rescuing the codebase regularly when drift sets in.

### the deep module mindset

Van Keith likes the idea that the best modules are deep. A lot of functionality behind a simple interface. Shallow modules are just complexity in disguise. Llms are useful right now because they help fit code into bigger, deeper blocks so humans and the ai both have to think about less. Reaching that state is hard and needs constant architecture maintenance with every new feature or change.

### references he likes

- Matt Pocock’s skills repo: https://github.com/mattpocock/skills/tree/main
- Matt Pocock’s talk on ai agent failure modes: https://youtu.be/v4F1gFy-hqg
- system design overview: https://python.plainenglish.io/system-design-for-python-i-tried-to-help-a-student-and-got-pulled-into-the-abyss-28d6ec7b9915

## what separates a real engineer from a vibe coder

Van Keith believes three things separate a vibe coder from someone who actually knows what they are doing. Fundamentals. System design. And seeing the future.

Seeing the future means seeing edge cases, seeing problems before they happen, and knowing what to do when ai cannot fix your code. That is where mastery of the fundamentals becomes the value. The best rules, skills, and mcp setup do not save you when the system breaks and nobody around you understands why.

Before ai, engineers worried about syntax. In the ai era, syntax is the least of the concern. The constants across every era are still the same three things.
