---
name: marketing-research-strategy
description: Execute systematic market research and produce actionable marketing strategy briefs for any brand. Use this skill whenever the user asks to conduct market research, competitive analysis, audience profiling, brand positioning, channel strategy, or marketing strategy development — even if they don't use the exact term "market research." Also trigger when users mention building a go-to-market plan, analyzing competitors, defining target audiences, developing a marketing brief, creating a brand strategy, or any combination of these marketing planning activities. This skill follows a structured 6-pillar SOP to ensure comprehensive, repeatable output.
---

# Marketing Research & Strategy

A structured skill for conducting comprehensive market research and producing actionable marketing strategy briefs. It follows a 6-pillar SOP methodology that builds each layer of analysis on top of the previous one, resulting in a complete, data-informed strategy document.

## Before You Begin: Brand Information Check

Before starting any research, verify that you have sufficient context about the brand. Read `references/brand-intake-questions.md` for the full intake questionnaire.

At minimum, confirm you know:

1. **Brand name and category** — What is the brand called, and what market does it operate in?
2. **Business stage** — Is this a startup, growth-stage, or established brand?
3. **Primary geography** — Which market(s) does the brand serve?
4. **Target audience sketch** — Any existing understanding of who the customer is?
5. **Core product/service** — What does the brand actually sell?
6. **Business objectives** — What is the brand trying to achieve (launch, growth, repositioning)?

If any of the above are missing or unclear, **stop and ask the user targeted questions** before proceeding. Don't guess — the quality of the entire strategy depends on getting these inputs right. Batch your questions into one message rather than asking them one at a time.

## Research Tool Priority

When conducting external research throughout this workflow:

1. **First choice: Perplexity MCP** — Check if the Perplexity MCP server is available. If so, use it as the primary research and retrieval tool for all external data gathering (market sizing, competitor info, trend analysis, etc.).
2. **Fallback: `search_web` and `read_url_content`** — If Perplexity MCP is unavailable, use these tools to complete your research. The research process must not be interrupted by tool availability.

Always cite your data sources regardless of which tool you use.

## The 6-Pillar Workflow

Execute these pillars **in strict sequence** — each builds on the findings of the previous one. Read `references/sop-pillars.md` for detailed research steps and output requirements for each pillar.

### Pillar 1: Market Landscape & Sizing
Define the market category, estimate size and growth trajectory, identify macro trends, map the market structure, and note seasonal demand patterns. This sets the strategic context for everything that follows.

### Pillar 2: Competitor Analysis
Identify 5–8 direct and 2–3 indirect competitors. Analyze their positioning, messaging, marketing channels, and customer experience. Synthesize findings into competitive gaps the brand can exploit.

### Pillar 3: Target Audience Deep Dive
Develop detailed audience personas covering demographics, psychographics, pain points, and decision-making triggers. Map the customer journey from awareness through loyalty.

### Pillar 4: Brand Positioning & Messaging Framework
Synthesize Pillars 1–3 into a clear positioning statement and messaging hierarchy. Draft core brand promise, primary and secondary messaging pillars, and proof points. Validate for differentiation.

### Pillar 5: Channel Strategy & Tactical Plan
Translate positioning into channel-specific tactics. Prioritize 3–5 channels, define objectives and KPIs, develop tactical playbooks, and build a 90-day campaign calendar.

### Pillar 6: Risk Assessment & Contingency Planning
Identify internal and external risks, assess likelihood and impact, develop contingency plans, and establish monitoring triggers.

## Final Output

After completing all 6 pillars, compile findings into a structured strategy brief using the template in `references/output-template.md`. The final deliverable should be a comprehensive Markdown document saved as `[Brand Name] Marketing Strategy Brief.md`.

Include an executive summary at the top that synthesizes the key findings and top-priority recommendations from all pillars.

## Keywords
market research, marketing strategy, competitive analysis, target audience, brand positioning, channel strategy, go-to-market, marketing brief, competitor analysis, audience persona, market sizing, marketing plan
