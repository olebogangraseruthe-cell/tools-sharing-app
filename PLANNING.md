Worked Example — Neighbourhood
Tool-Sharing App
A filled-in example using a project similar in scope to the Module 3 Django capstone, for
instructors to walk through in class before students attempt their own.
Business Case
Problem: People in a neighbourhood often own tools (drills, ladders, lawn equipment) they use
a few times a year, while neighbours buy duplicates they rarely need.
Who has this problem: A resident on a residential street who needs a tool for a weekend
project and doesn't want to buy one for one-time use.
Why now: Community WhatsApp groups already do this informally and messages get lost — a
simple shared list solves it properly.
Success looks like: A neighbour can list a tool and another neighbour can find and request it in
under two minutes.
Use Case
Primary actors: Tool Owner, Tool Borrower (same user model, different actions).
Stories: As a Tool Owner, I want to list a tool with a photo and description, so that neighbours
know it's available. As a Borrower, I want to search tools by category, so that I can find what I
need quickly. As a Borrower, I want to request a tool, so that the Owner is notified and can
approve it. As an Owner, I want to approve or decline requests, so that I control who borrows
my tools. As a user, I want to log in securely, so that my listings and requests are tied to my
account.
Happy path: (1) User registers/logs in. (2) Owner creates a tool listing. (3) Borrower searches
and finds it. (4) Borrower submits a request. (5) Owner approves. (6) Both see the tool marked
"borrowed" until returned.
Tech Spec
Stack: Django + PostgreSQL (or SQLite for development) — chosen because the built-in auth
and admin panel remove the need to build account management from scratch.
Data model: User (Django's built-in auth). Tool — owner (FK to User), name, category,
description, photo, status (available/borrowed). Request — tool (FK), borrower (FK), status
(pending/approved/declined), requested_at.
Core screens: Home/browse listings, Tool detail page, "Add a tool" form, "My requests"
dashboard, "My tools" dashboard (approve/decline).
Out of scope: No in-app messaging (use existing contact info), no payment/deposit handling,
no rating/review system, no mobile app — web only.
Stretch goal: Email notification when a request is approved.
