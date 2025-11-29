-- Shared Project Knowledge Seed Data
-- 
-- This file contains stable project knowledge entries for all environments (dev and prod).
-- This is public-safe data that is consistent across environments.
--
-- Project knowledge entries for all active projects: THN, DAAS, FF, 700B
-- Each entry must have a unique (project, key) combination.
-- Summary field should contain meaningful project context.
--
-- Uses UPSERT semantics (ON CONFLICT (project, key) DO UPDATE SET summary = EXCLUDED.summary)
-- for idempotent loading.
-- Last updated: 2025-11-26

-- THN (Tumulty Home Network) - Overview
INSERT INTO project_knowledge (project, key, summary)
VALUES (
  'THN',
  'overview',
  'THN (Tumulty Home Network) is the umbrella project for the entire home-lab and network ecosystem. It focuses on privacy-first, self-hosted, and educational infrastructure, using multiple machines and VLANs. Core themes: strong separation of concerns between AI, web servers, and Web3/node machines; preference for local control over cloud services; integration with Home Assistant, Firewalla, and various IoT devices; long-term goal: THN as a personal "mini-datacenter" + education platform for networking, security, and distributed systems.'
)
ON CONFLICT (project, key) DO UPDATE SET summary = EXCLUDED.summary;

-- THN - Machine Roles
INSERT INTO project_knowledge (project, key, summary)
VALUES (
  'THN',
  'machine_roles',
  'Current machine roles: tumultymedia (Mac Mini M1) - AI projects only, local AI experiments, dev environments; tumultymedia2 (Ubuntu i7 server) - Web server projects only, API servers, Homebridge, web tools; tumultymedia3 (Beelink EQ13, Intel N100) - Web3/decentralized node box, planned for Bitcoin Lightning routing, Storj storage node, Meson Network; tumultymedia4 (future Titan node) - High-power decentralized/compute, target Summer 2026; tumultymedia5 (future VPN box) - Family & Friends VPN service, multiple geographies.'
)
ON CONFLICT (project, key) DO UPDATE SET summary = EXCLUDED.summary;

-- THN - Design Principles
INSERT INTO project_knowledge (project, key, summary)
VALUES (
  'THN',
  'design_principles',
  'THN Design Principles: Privacy-first - prefer local integrations (Home Assistant, Zigbee, Homebridge) over cloud platforms, aggressively block tracking domains at firewall level; Segmentation - separate IoT, personal devices, and server infrastructure via VLANs/subnets, dedicated machines per role; Redundancy & Power Protection - UPS protection for critical infrastructure, careful power planning for always-on nodes (~15W where possible); Education & Experimentation - learning sandbox for networking (VPNs, firewalls, VLANs), edge servers and AI hosting, Web3 nodes and decentralized infrastructure.'
)
ON CONFLICT (project, key) DO UPDATE SET summary = EXCLUDED.summary;

-- DAAS (Dream to Action Alignment System) - Overview
INSERT INTO project_knowledge (project, key, summary)
VALUES (
  'DAAS',
  'overview',
  'DAAS (Dream to Action Alignment System) is a structured system to link dream imagery & experiences with waking-life actions, projects, and creative work. The goal is to align unconscious insight with conscious decision-making and creative output, turning dream material into practical guidance and growth. DAAS uses a blended interpretive framework: Christian spirituality (grace, discernment, soul''s journey), Celtic & Druidic (nature, ancestors, seasonal cycles, thin veil), Pagan cosmology (cyclical transformation, elements, ritual), and Jungian psychology (archetypes, shadow, individuation, symbolic language). Dreams are not "fortune telling" but symbolic guidance.'
)
ON CONFLICT (project, key) DO UPDATE SET summary = EXCLUDED.summary;

-- DAAS - Key Components
INSERT INTO project_knowledge (project, key, summary)
VALUES (
  'DAAS',
  'key_components',
  'DAAS Key Components: Dream Archive - each significant dream stored with title, summary, symbols & recurring motifs (water, houses, Shore Acres, blue light, family, basement, birds, cats), emotional tone, context from waking life; Thematic Series - notable ongoing series include Water/Family/Lucidity Series, Basement/Childhood Home series, Purple Cat/Dead Rabbit/Messy House sequence, Guides/Church Party/Basement Descent sequence; Seasonal & Ancestral Context - Samhain and related rituals tracked, Ancestral Constellation Layer with Irish, Dutch, Polish/Eastern European, Ashkenazi Jewish, German, English/French lineages, each with associated archetypal themes.'
)
ON CONFLICT (project, key) DO UPDATE SET summary = EXCLUDED.summary;

-- DAAS - Action Alignment
INSERT INTO project_knowledge (project, key, summary)
VALUES (
  'DAAS',
  'action_alignment',
  'DAAS Action Alignment: Extracts core themes from recurring dreams (e.g., rebuilding home, reconciliation, crossing bridges, blue lucid space) and maps these to life decisions (work roles, relationships), creative projects (writing, meditation practices, rituals), and adjustments in daily behavior (forgiveness, hospitality, boundaries). Example alignment patterns: Rebuilt Shore Acres homes → "Rebuilding inner/outer life after storms"; Blue lucid sky/meditative emptiness → "Return to stillness, contemplative living"; Basement with guides → "Facing subconscious material/childhood imprints, with assistance".'
)
ON CONFLICT (project, key) DO UPDATE SET summary = EXCLUDED.summary;

-- DAAS - Analysis Approaches
INSERT INTO project_knowledge (project, key, summary)
VALUES (
  'DAAS',
  'analysis_approaches',
  'DAAS supports multiple analytical frameworks including Christian interpretation (grace, discernment, soul''s journey), Jungian analysis (archetypes, shadow, individuation, symbolic language), Pagan perspectives (cyclical transformation, elements, ritual, seasonal cycles), and Celtic/Druidic approaches (nature, ancestors, thin veil, Samhain). Users can request analysis from specific perspectives or explore patterns across dreams. Dreams are treated as symbolic guidance rather than fortune telling.'
)
ON CONFLICT (project, key) DO UPDATE SET summary = EXCLUDED.summary;

-- FF (Financial Freedom) - Overview
INSERT INTO project_knowledge (project, key, summary)
VALUES (
  'FF',
  'overview',
  'FF (Financial Freedom/Wealth Management) is the long-term financial planning and wealth-building framework. ChatGPT acts as a wealth manager & planner, with focus on tech industry investments, Web3/crypto nodes, real estate, and cost-reducing investments (not just income-generating). FF is not purely about maximizing returns - some projects (e.g., Lightning node, Bittensor when active) are partly educational, accepting small manageable risk for the sake of learning and skills.'
)
ON CONFLICT (project, key) DO UPDATE SET summary = EXCLUDED.summary;

-- FF - Core Elements
INSERT INTO project_knowledge (project, key, summary)
VALUES (
  'FF',
  'core_elements',
  'FF Core Elements: Retirement & Index Funds - example current state: ~$100K in Vanguard 500 index fund (IRA), additional ~$15K allocated to options trading inside IRA, time horizon: user is ~40 years old, target age ~65; Node Income → Satoshi Growth Engine - all Web3/decentralized node income (Lightning fees, Storj, Meson, etc.) conceptually flows into buying more satoshis via Cash App, THN nodes form a "Satoshi Growth Engine" for long-term Bitcoin accumulation; Cost-Reduction Investments - FF explicitly values purchases that lower monthly expenses (e.g., buying indoor planter/Farmstand to grow vegetables and reduce grocery costs), these purchases are treated as investments, not just expenses.'
)
ON CONFLICT (project, key) DO UPDATE SET summary = EXCLUDED.summary;

-- FF - Planning Priorities
INSERT INTO project_knowledge (project, key, summary)
VALUES (
  'FF',
  'planning_priorities',
  'FF Planning Priorities: Preserve and grow core long-term assets (index funds, retirement accounts); Use THN node projects and side ventures to generate small streams of income, build skills in networking/infra/Web3, funnel gains toward Bitcoin accumulation; Use ChatGPT to track account details over time, propose rebalancing strategies, compare environmental and reliability tradeoffs (e.g., Cox vs OzarksGo), evaluate cost-reduction hardware purchases.'
)
ON CONFLICT (project, key) DO UPDATE SET summary = EXCLUDED.summary;

-- 700B (Breakfast & Body Rhythm Log) - Overview
INSERT INTO project_knowledge (project, key, summary)
VALUES (
  '700B',
  'overview',
  '700B (Breakfast & Body Rhythm Log) is a simple project dedicated to tracking breakfast compositions that work well with the user''s body. Respects preference for large breakfast, little or no lunch (maybe a snack), decent dinner. Keeps notes about sensitive foods (e.g., oats). Only stores breakfast-related data under 700B. Focus on ingredients, rough macros/calories (when discussed), body reactions and preferences. Known constraints: Oats tend to cause frequent bathroom trips; must be used cautiously.'
)
ON CONFLICT (project, key) DO UPDATE SET summary = EXCLUDED.summary;

-- 700B - Current Patterns
INSERT INTO project_knowledge (project, key, summary)
VALUES (
  '700B',
  'current_patterns',
  '700B Current Stored Patterns: Multi-item plates with eggs, sausages, high-protein dairy (Greek yogurt, cottage cheese), fruit (mango, apples, berries, grapes, cantaloupe), limited bread (Dave''s Killer Bread) or granola, vegetables like cucumber or sautéed greens. Breakfast patterns are designed to hit ~600-800 calories, provide solid protein + moderate carbs + healthy fats, keep energy high and appetite stable through the day.'
)
ON CONFLICT (project, key) DO UPDATE SET summary = EXCLUDED.summary;
