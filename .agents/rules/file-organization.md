# File Organization

## Agent Rules File Location

**Maintain shared agent rules in `.agents/rules/`.** Declare Claude adapter scopes in `.agents/scopes.json`, generate adapters, and route the same rules from `AGENTS.md`.

## Module Structure

- Keep related functionality together
- Use clear, descriptive file names
- Avoid unnecessary module docstrings that just describe the file contents

## Import Organization

- Group imports logically
- Use absolute imports when possible
- Keep imports clean and minimal
