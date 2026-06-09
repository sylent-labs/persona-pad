# Projects and technical challenges

## current projects

Van Keith currently leads three projects at the same time. These are the named ones he can talk about in interviews and in async conversations.

### signalforge

SignalForge is a high volume azure log ingestion pipeline built around python, fastapi, databricks, and spark. The pipeline is designed to ingest around 150 million lines of data per hour. The work is making sure the architecture can survive real production volume. Diagrams that look good in a slide deck and pipelines that hold up at 150 million per hour are two different things. SignalForge is the evolution of the original log ingestion work that started as a daily batch and grew into a continuous, resumable, high throughput ingestion system.

### crustopher

Crustopher is an internal ai assistant for domino's store it operations. It lets the user ask questions like "are extracts caught up for this store?" or "what services are unhealthy?" and the system figures out which internal tools or apis to call. Van Keith leads the architecture that wires the chat ui, the agent reasoning loop, mcp tools, openapi driven internal service access, sse streaming, and human in the loop approvals into one operational assistant.

### pizzascope

Pizzascope is foundational observability infrastructure that Van Keith built from scratch. It is domino's internal observability library for python and fastapi services, now used across 74 codebases. The goal is to make logging and alerting consistent across services without every team having to design their own logging setup. It gives engineers structured json logs, request uuid propagation, timing, error alerting through teams, and azure log analytics friendly output. The real value sits in the production edge cases: preventing duplicate handlers, keeping request context clean across concurrent fastapi requests, handling third party library logs, splitting oversized log messages, and making adoption simple enough that teams can add it without a big migration. Pizzascope is foundational rather than flashy. When production breaks, it becomes very obvious who has it and who does not. If you have it, debugging is faster. If you do not, you are guessing in the dark.

## biggest technical challenges

### 150 million log ingestion pipeline (now signalforge)

One of the hardest technical challenges Van Keith led was scaling a log ingestion pipeline at retail scale. The original implementation handled around a million records and would time out, but the requirement pushed it to roughly 150 million logs and eventually to a steady 150 million lines per hour as the system matured. This work is now branded internally as signalforge. The bottlenecks that showed up:

- pandas memory pressure
- serial fetch and write flow
- redundant loops
- expensive deduplication checks
- database writes that degraded as the table grew

Van Keith led the redesign with a team of engineers. The new design moved toward:

- polars instead of pandas
- generators for streaming
- streaming batches
- larger write batches
- better deduplication
- resume safe processing
- cleaner database writes

He also analyzed performance complexity so the team could distinguish unavoidable o(n) work from unnecessary overhead.

The result was a pipeline that became significantly more scalable and reliable. Instead of treating 150 million logs as one massive batch problem, it became a bounded, resumable, optimized ingestion system that could support long term observability, model monitoring, incident analysis, and ai or data use cases across the platform.

### Apple Hide My Email account mismatch

iOS users who signed up using Apple’s Hide My Email feature were assigned a randomized private relay address, something like randomstring@privaterelay.appleid.com. When they later logged in through sso, Apple would sometimes return the real email instead, which caused an account mismatch.

The situation was harder because the third party legacy system the app integrated with did not have sso, and users could not log into the partner app because of the proxy email.

The fix was to handle Apple’s private relay emails properly during both signup and login. The authentication logic was updated so a user could log in with either:

- the private relay email Apple assigned at signup
- the real email, if Apple later provided it via sso

All users had to update their profiles to include their actual email so there was a single source of truth. That was tricky because there was no clean source of truth to start with, but it was resolved.

### rate limiting and api abuse monitoring

For protecting api endpoints from abuse and ddos style traffic, Van Keith pairs Sentry performance monitoring with rate limiting at the framework level.

Sentry setup:

- traces_sample_rate=1.0 so every request is logged for monitoring
- send_default_pii=True so user data gets captured for abuse correlation
- watch for surges from specific ips, users, or endpoints

Django rate limiting:

- install django-ratelimit
- apply rate limit decorators to views
- key by ip or user, with a sane rate
- mitigates basic ddos and api abuse without rewriting the stack
