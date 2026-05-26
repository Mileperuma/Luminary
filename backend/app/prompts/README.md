# Prompt templates

LLM prompts live here as Markdown so a non-developer can read and tweak them
without touching Python code.

Each template has three sections:

```markdown
# <name>

## System
<system prompt — sets role, tone, constraints>

## Example user
<one example user message>

## Example assistant
<one example assistant response in the desired format>
```

Templates to add (per the sprint plan):

| File                          | Purpose                                                |
|-------------------------------|--------------------------------------------------------|
| `onboarding_chat.md`          | Multi-turn chat that captures media preferences.       |
| `recommendation_summary.md`   | Writes the "why we picked this" blurb per recommendation. |
| `welcome_back.md`             | Returning-user greeting referencing stored preferences. |

The `LLMClient` adapter loads these templates by name and never inlines prompts in code.
