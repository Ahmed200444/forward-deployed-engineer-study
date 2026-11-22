---
title: "Forward deployed engineer: research, gap check and learning order"
date: 2026-11-22
---

# 1. What a forward deployed engineer (FDE) is

A forward deployed engineer is a software engineer who works **inside a customer's organisation** to get a product working on that customer's real problem, data and systems. Palantir created the title. Frontier AI labs (Anthropic, OpenAI) and many AI startups now hire FDEs to take their models from a demo to a production deployment at a large customer.

How it differs from the roles you already know:

| Role | Main job | Writes production code? | Customer-facing? |
|---|---|---|---|
| AI engineer (your current site) | Build LLM, RAG and agent systems for your own product | Yes, most of the time | Rarely |
| **Forward deployed engineer** | Build and ship those systems **in the customer's environment**, then turn what you learned into reusable tools | Yes ("contribute directly in the code") | Yes, a lot: 25–50 % travel in every posting below |
| Solutions / sales engineer | Demos and technical answers before a sale | Mostly prototypes | Yes |
| Consultant | Advice and plans | Sometimes | Yes |

**Short answer to your question:** an FDE is about 70 % AI engineer and 30 % customer work. Your site already teaches most of the technical 70 %. What it does not teach is the customer part (discovery, scoping, demos, stakeholders), working inside someone else's systems (enterprise integration, security rules, their cloud), and a second language (TypeScript/JavaScript).

# 2. What employers ask for (current postings)

| Posting | Experience | Key skills named | Travel | Pay (base) |
|---|---|---|---|---|
| Anthropic, FDE (Applied AI), US and London | 4+ years customer-facing technical role | Production LLM work: "advanced prompt engineering, agent development, evaluation frameworks"; MCP servers, sub-agents, agent skills; strong Python, ideally TypeScript or Java | 25–50 % | $200k–$300k (US), £225k–£255k (London) |
| OpenAI, FDE, San Francisco | 5+ years | Lead deployments end to end: discovery, scoping, system design, build, rollout; LLM systems; full-stack in Python/JavaScript; eval-driven feedback | up to 50 % | $185k–$300k + equity |
| OpenAI, Forward Deployed *Software* Engineer | 7+ years full-stack | Full-stack apps on OpenAI APIs; Postgres/MySQL; scopes of work and project plans | up to 50 % | $185k–$325k + equity |
| Palantir, Forward Deployed Software Engineer (London) | **6+ months** after college | Python/Java/C++/TypeScript; data at scale; LLM workflows; secure coding and access control; owning stakeholders "from the users in the weeds to the executives" | 25–50 % | not listed |

Two analyses of about 1,000 postings each (early 2026) agree on the pattern:

* **Core engineering (in almost every posting):** Python (66 %), TypeScript (35 %), SQL, a cloud (AWS 32 %, GCP 22 %, Azure 18 %), containers.
* **AI skills (most postings):** AI agents (35 %), LLM experience (31 %), RAG (12 %), prompts and evaluations. PyTorch appears in only 6 %.
* **Customer skills (70 %+ of postings):** requirements discovery, embedding with customers, pilots and demos, stakeholder management.
* **Traits:** ownership, breaking a vague problem into steps ("decomposition"), comfort with ambiguity, product sense.

**Honest reality check for you.** Most FDE postings ask for 4–7 years. Palantir is the main exception (6+ months). A junior route is realistic in two ways: (1) apply to entry-level FDE roles like Palantir's and at AI startups, or (2) get hired as an AI engineer first and move to FDE. Both use the same skills, so the plan below works for both and does not throw away your AI-engineer path.

Caveat: the two 1,000-posting analyses are published by companies that sell courses or tools. I used their percentages only where the official postings above agree with them.

# 3. Gap check: FDE skills against your site (v27.4)

## Already covered (will be marked "FDE" in the site)

| FDE skill | Where it is on your site |
|---|---|
| Python, testing, Git | Phase 0; Phase 1 lessons 1–7 |
| Coding interviews (Palantir and others test this) | Phase 1 lessons 8–14 (data structures and algorithms) |
| SQL and messy data | Phase 2 (all 8 lessons) |
| APIs, validation, auth, settings, Docker, CI/CD, FastAPI, async | Phase 5 lessons 1–10 |
| Production depth: serving, queues, scaling, tracing, SLOs | Phase 5 lessons 11–17 |
| LLM apps: prompts, structured output, cost, evaluations, guardrails, tool calling | Phase 7 lessons 1–13 |
| RAG and evaluation sets, access control in retrieval | Phase 8 (all lessons except 16) |
| Agents, MCP servers, permissions, evaluation and tracing, plans, frameworks | Phase 9 (all 16 lessons) |
| Interviews, resume, projects | Phase 10 |
| A/B tests and experiments (proving value to a customer) | Phase 4 lesson 17 |

## Partly covered (useful, but less central for FDE)

Phase 3 math, Phase 4 traditional ML and Phase 6 deep learning. FDE postings rarely ask for model training (PyTorch 6 %). Keep them for the AI-engineer path; for FDE, only embeddings and attention (Phase 6 lessons 6–7) and Phase 4 lessons 1–4 matter much.

## Missing (needs a new course)

1. **The FDE role and a deployment from start to finish.** Phases of an engagement, who does what, what "done" means.
2. **Customer discovery and scoping.** Turning a vague ask into requirements, success metrics, a scope document and an acceptance test.
3. **Integrating with the customer's systems.** Their APIs, OAuth 2 client credentials, webhooks with signatures, pagination and rate limits, mapping their data schema to yours.
4. **Security, privacy and regulated customers.** PII redaction, audit logs, data residency, least privilege, what a security review asks.
5. **Deploying in the customer's cloud.** The few services that matter on AWS, GCP and Azure (compute, storage, secrets, identity, networking) and how to choose. Concepts and decision exercises only: no cloud account, $0.
6. **JavaScript and TypeScript for FDEs.** Enough to read and change a customer's web app or a TypeScript MCP server. JavaScript runs natively in the browser, so exercises can run in the page.
7. **From pilot to production.** Eval-gated acceptance, staged rollout, runbook and handoff.
8. **Demos, writing and stakeholders.** Status updates, a design doc, handling "it doesn't work".
9. **Codifying patterns.** Turning one customer's code into a reusable tool or playbook (what the postings call "codify").
10. **FDE interviews.** The decomposition interview, the customer role-play, a scoping case.
11. **FDE capstone.** A simulated customer engagement: brief → scope → integration → evaluated agent/RAG → rollout plan.

# 4. Recommended learning order for an FDE

The site becomes a forward deployed engineer site. Courses are put in this order. Inside each course, every lesson gets a label: **FDE core** (do it now), **FDE interviews** (coding-round practice) or **Optional for FDE** (AI-engineer depth; come back later).

| Order | Course | FDE core lessons | Why here |
|---|---|---|---|
| 0 | Developer foundations | all | Everything builds on it |
| 1 | Professional Python | 1–7 core; 8–14 FDE interviews | Customer code must be clean and typed; coding rounds |
| 2 | Data, SQL and analysis | all | SQL is in nearly every posting; customer data is messy |
| 3 | Practical math for ML | 1–3, 6 core; rest optional | Similarity, probability and uncertainty are used by evaluations and RAG |
| 4 | Traditional machine learning | 1–4, 8, 14, 17 core; rest optional | Baselines, honest test sets, precision and recall, drift and A/B tests are what you show a customer |
| 5 | Shipping models | 1–10 core; 11–17 core (production depth) | You ship services into someone else's systems |
| 6 | LLM application engineering | 1–13 core; 14–15 optional | Core of an AI FDE |
| 7 | Retrieval and RAG | all core except 16 (benchmarking), which is optional | The most common customer deployment |
| 8 | Production AI systems and agents | all core | Agents, MCP and permissions are named directly in Anthropic's posting |
| **9** | **New: Forward deployed engineering** | all | The customer half of the job, a second language and the FDE capstone |
| 10 | Deep learning fundamentals | 6–7 core (embeddings, attention); rest optional | FDE postings rarely ask for model training (PyTorch in 6 %) |
| 11 | Career readiness | all, plus FDE interview rounds | Apply |

Moving the old Phase 6 (deep learning) later is the only change in course order. Phases 3 and 4 stay before the LLM courses because the LLM, RAG and agent lessons use cosine similarity, test sets, precision and recall, and drift from them.

# 5. What changes in the site (this release)

* Name and home page: "Forward Deployed Engineer Study", with what an FDE is and the path above.
* Course order and numbers as in section 4. Lesson text that says "Phase 7" and so on is updated to the new numbers.
* Every lesson shows its FDE label in the lesson list and at the top of the lesson.
* A new course 9, **Forward deployed engineering**: the 10 missing lessons from section 3, each with a quiz and exercises, a course project, interview prep and a checkpoint, plus the FDE capstone.
* Kept exactly: every existing lesson, exercise, project, route and your saved progress (the storage key does not change).

# 6. Sources

* Anthropic, Forward Deployed Engineer: https://job-boards.greenhouse.io/anthropic/jobs/4985877008 and https://www.anthropic.com/careers/jobs/5012991008
* Anthropic, FDE Custom Agents (closed, used as reference): https://jobs.generalcatalyst.com/companies/anthropic/jobs/69414582-forward-deployed-engineer-custom-agents
* OpenAI, FDE: https://openai.com/careers/forward-deployed-engineer-(fde)-sf-san-francisco/
* OpenAI, Forward Deployed Software Engineer: https://openai.com/careers/forward-deployed-software-engineer-sf/
* Palantir, Forward Deployed Software Engineer: https://jobs.lever.co/palantir/5168e8fd-fec1-4fea-b7a1-81bdaea65850
* Perspective AI, "2026 FDE hiring trends: what 1,000 job posts reveal" (June 2026): https://getperspective.ai/blog/2026-fde-hiring-trends-what-1000-job-posts-reveal
* Masai School, "Forward deployed engineer skills" (Oct 2026, citing Bloomberry data from Jan 2026): https://www.masaischool.com/blog/forward-deployed-engineer-skills/
