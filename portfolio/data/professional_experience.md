# Professional Experience (project deep-dives)

*Work history, education, and certifications are covered in the resume. This file goes deeper on specific projects and things a resume can't say.*

---

## Montu *(most recent role)*

**Stack:** TypeScript, Node.js, NestJS, React, AWS, Google BigQuery, Datadog

Luke's most recent professional role. Part of a clinic engineering team responsible for the patient management system and consultation scheduling platform — primarily backend, distributed systems, microservices, and third-party integrations in a regulated healthcare environment.

### Kafka migration
The scheduling system had grown fragile — synchronous chains of service calls that would cascade-fail under load. Led the technical spike and end-to-end implementation of a migration to an async event-driven pattern using Kafka: producers emit scheduling events, consumers process them independently, and the system recovers gracefully from downstream failures. The constraint was a regulated healthcare environment where downtime directly impacts patient access to care, so the migration was staged, observable at every step, and rolled out without service interruption.

### Feature flag audit and RFC
Conducted a multi repository-wide audit of feature flags across the patient management and scheduling systems, identifying flags eligible for removal and flagging dormant toggles accumulating technical debt. Produced internal documentation, tagged stakeholders on actionable flags, and authored an RFC proposing a standardised naming convention and a new definition of done: features are not considered complete until their release flag is removed (unless explicitly designated as permanent). LaunchDarkly was the feature flag management system.

### Legacy patient data migration
Migrated legacy Express business logic into the new modular xAPI facade NestJS architecture, including updating API contracts to align with the modernised service layer.

### Immediate consultation promo codes
Implemented promo code support for immediate doctor and nurse consultations — including the discount logic, validation rules, and downstream event updates to Kafka topics and SQS queues shared with other teams and used for patient comms.

---

## Flight Centre

**Stack:** TypeScript, Node.js, NestJS, Redis, AWS, Java, Spring, PHP, New Relic, Splunk, Snyk

Part of the Flights Global team responsible for GDS and NDC flight data aggregation, normalisation, and the maintenance of legacy flight orchestration microservices.

### GDS/NDC content normalisation
Worked closely with flight content providers TPConnects, Sabre, and Amadeus to normalise GDS (legacy SOAP-based) and NDC (modern XML/REST) content into a consistent internal format. Built the orchestration layer that abstracted both standards behind a unified API, so product teams could consume flight data without caring which distribution standard a carrier used. Handled retries, fallbacks, and content routing across providers.

### Fare rules and baggage normalisation
Designed and implemented a normalisation layer for fare rules, baggage inclusions, and ancillary add-ons across GDS and NDC content sources — each of which structures this data differently. The output was a consistent, frontend-ready format that allowed the UI to render fare conditions and baggage policies uniformly regardless of the underlying content source.

### Cheapest flight prediction pipeline
Implemented a real-time flight data pipeline to support a "probability of cheaper flights" feature. During live user searches, flight data for both one-way and combined itineraries was streamed asynchronously to Kinesis Firehose and processed via Lambda — offloaded from the main response path to avoid latency impact. The transformed data fed the data team's prediction model, which surfaced price trend insights to customers at the point of search.

---

## Codafication

**Stack (Lead):** TypeScript, Node.js, GraphQL, AWS, PostgreSQL, Kubernetes, Helm
**Stack (Engineer):** TypeScript, MobX, Node.js, React, GraphQL, AWS, PostgreSQL, Kubernetes

### Lead B2B platform/product vertical
Led the product vertical for a new enterprise client — owning the technical direction end-to-end. The role was as much about stakeholder management as engineering: working directly with the client to interpret their business logic, translate requirements into platform capabilities, and deliver custom workflow extensions and integrations. Managed release branches and deployment artefacts scoped to the client, and served as the primary technical liaison during high-stakes integrations where a failed deployment had direct operational impact on their business.

### Multi-client support
Worked across the full client portfolio as a generalist engineer — triaging and resolving bugs, delivering feature work, and maintaining system reliability across multiple concurrent product lines. The breadth of exposure across different codebases, client environments, and integration patterns built a strong foundation for the lead role that followed.

---

## Scrunch

**Stack (Lead):** JavaScript, React, Python, Starlette, PostgreSQL, AWS, Stripe
**Stack (Engineer):** JavaScript, React, Gatsby, GraphQL, Strapi, GSAP, Dart, Flutter, Firebase

At times the sole engineer at the company, working directly with the Founder and CEO on greenfield projects and platform evolution.

### SaaS platform features
Took ownership of new feature development on an existing React/Python Starlette/PostgreSQL SaaS platform. Delivered end-to-end across the stack — UI implementation from design, data modelling, API development, and third-party integrations. Key deliverables included a multi-tenant subscription model allowing companies to manage multiple user accounts under a single subscription, a data-saver mode that restricted platform access while preserving data during subscription lapses, and Scrunch University — a marketing education feature where the CEO authored content that was hosted and delivered directly within the platform.

### Public website and landing pages
Built the company's public-facing marketing website from design, with a focus on performance and visual impact. Used Gatsby for fast static rendering and GSAP for smooth scroll-driven animations. Implemented fully responsive layouts across mobile, tablet, and desktop breakpoints.

### HubSpot and live chat integrations
Integrated a live chat feature into the platform with intelligent routing: messages were dispatched to Slack during business hours and forwarded via email outside of them, ensuring no customer query went unnoticed regardless of when it came in.

### Blog CMS and content pipeline
Implemented the company's highest-traffic acquisition channel: a headless CMS-driven blog using Strapi and Gatsby. The Strapi admin UI allowed non-technical staff to author posts, upload images, and structure content through a form-based interface. On save, Gatsby's webhook integration with Strapi triggered an automatic rebuild, dynamically generating new blog pages without any developer involvement.

### Co-founder wellness app (mobile)
Early-career project — a Flutter mobile app for a co-founder's personal wellness startup. Implemented the onboarding flow and passwordless authentication using Magic (deep-link based magic links), providing a frictionless login experience without traditional password management.
