# Quimera Simplification Spec

**Date:** 2026-06-07  
**Status:** ACTIVE  
**Scope:** Remove evaluation pipeline, focus ONLY on design generation

## Problem Statement

Quimera tries to do 3 things:
1. Generate design
2. Evaluate design (8 criteria, iterative)
3. Generate code

This is too complex. Stitch focuses on #1 and #3. We should too.

## Solution

**2-step pipeline instead of 3:**

```
User Brief → Step 1: Generate DESIGN.md → Step 2: Generate React Component
                    (tokens + prose)
```

### What to Remove
- `backend/pipeline/scorers/` (wcag_contrast, color_harmony, llm_scorers) — ENTIRE FOLDER
- `backend/pipeline/step2_evaluate.py` — ENTIRE FILE
- `AestheticScores` model
- Evaluation, iteration, critique logic from main.py
- All scoring endpoints

### What to Simplify
- `DesignContext` — remove all evaluation fields
- `step1_analyze.py` → `step1_generate_design.py` — output a complete DESIGN.md
- `step3_generate.py` → `step2_generate_code.py` — read DESIGN.md and generate React

### Knowledge Base to Integrate
- Copy key files from `design.md-main/` as examples in prompts:
  - `design.md-main/examples/atmospheric-glass/DESIGN.md`
  - `design.md-main/examples/paws-and-paths/DESIGN.md`
  - `design.md-main/examples/totality-festival/DESIGN.md`
  - `design.md-main/docs/spec.md` — the DESIGN.md spec itself

## Gemini Prompts (Updated)

**Step 1 Prompt Template:**
```
You are an expert design system architect. Generate a complete DESIGN.md file based on the user's brief.

Reference examples (use these as inspiration, not templates):
[examples from design.md-main pasted here]

DESIGN.md Specification:
[design.md-main/docs/spec.md pasted here]

User Brief:
{user_brief}

Generate a DESIGN.md with:
1. YAML frontmatter: colors, typography, spacing, rounded, components
2. Markdown prose: Brand, Colors, Typography, Layout, Do's & Don'ts sections

Output ONLY the DESIGN.md file, nothing else.
```

**Step 2 Prompt Template:**
```
You are an expert React developer. Generate a production-ready React component implementing this design system.

DESIGN.md:
{design_markdown}

Requirements:
- Use Tailwind CSS with design tokens
- Create a showcase component that demonstrates:
  - All color tokens in action
  - Typography hierarchy
  - Component examples (buttons, cards, inputs)
  - Responsive layout
- Export as a default React component
- Include inline CSS or Tailwind config matching DESIGN.md tokens

Output the complete React component (TSX/JSX), no explanations.
```

## Success Criteria

- [ ] Removed `scorers/` folder
- [ ] Removed `step2_evaluate.py`
- [ ] Renamed pipeline files
- [ ] `DesignContext` simplified
- [ ] Gemini prompts updated
- [ ] Frontend shows DESIGN.md (not scorecard)
- [ ] Single request → DESIGN.md → React component flow works
- [ ] No evaluations, no iterations

## Files to Modify

1. `backend/models.py` — simplify DesignContext
2. `backend/main.py` — remove evaluate endpoint
3. `backend/pipeline/step1_generate_design.py` — NEW (was analyze)
4. `backend/pipeline/step2_generate_code.py` — NEW (was generate)
5. `backend/pipeline/__init__.py` — update imports
6. `backend/services/gemini_client.py` — no changes needed
7. `frontend/hooks/usePipeline.ts` — adapt to 2-step flow
8. `frontend/components/Scorecard.tsx` — REMOVE or hide
9. `frontend/components/DesignTokensView.tsx` — NEW (show DESIGN.md)

## Timeline

- Phase 1: Simplify models + remove scorers (1h)
- Phase 2: Rewrite pipeline steps (1h)
- Phase 3: Update frontend (1h)
- Phase 4: Integration test (30m)
