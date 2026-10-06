# SyllabusGuard

### Study what matters, not everything you find.

SyllabusGuard is an Agent Skill that compares an official syllabus with student study material and previous-year questions.

It identifies:

- Covered topics
- Partially covered topics
- Missing topics
- Out-of-syllabus material
- Syllabus coverage
- PYQ-based priority
- Recommended study order

The project also includes a benchmark to evaluate whether the SyllabusGuard Skill actually improves an AI agent's performance.

---

## Problem

Students often have an official syllabus, notes, study material, and previous-year questions, but it can be difficult to determine what is actually important.

SyllabusGuard helps identify:

- What has already been covered
- What syllabus topics are still missing
- What study material is outside the syllabus
- Which topics have appeared in previous-year questions
- What should be studied first

The project also investigates whether an explicit Agent Skill improves AI performance on this task.

---

## Solution

SyllabusGuard uses an Agent Skill containing explicit rules for syllabus-aware analysis.

```text
Official Syllabus
        |
        v
Study Material
        |
        v
Previous-Year Questions
        |
        v
+---------------------------+
|     SyllabusGuard Skill   |
|                           |
| Topic Extraction          |
| Semantic Matching         |
| False Match Prevention    |
| Missing Topic Detection   |
| Out-of-Syllabus Detection |
| PYQ Analysis              |
| Priority Ranking          |
+-------------+-------------+
              |
              v
       Structured Analysis
              |
      +-------+-------+
      |       |       |
      v       v       v
   Covered  Missing  Out-of-
                     Syllabus
              |
              v
       Study Priority
              |
              v
      Recommended Order
      