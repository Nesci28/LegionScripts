# Mage 70 Suit Builder Algorithm

This document explains how the Mage 70 Suit Builder evaluates crafted armor, selects candidates, determines whether a valid suit exists, and decides which armor pieces should continue to be crafted.

---

# Goals

The builder attempts to create a six-piece leather mage suit that can achieve:

- 70 Physical Resist
- 70 Fire Resist
- 70 Cold Resist
- 70 Poison Resist
- 70 Energy Resist
- 100% Lower Reagent Cost
- 40% Lower Mana Cost

while maximizing remaining item intensity for:

- Mana Increase
- Mana Regeneration

and remaining within OSI imbuing limits.

---

# Step 1: Craft Armor

The builder continuously crafts exceptional leather armor for the six required slots:

- Cap
- Gorget
- Sleeves
- Gloves
- Tunic
- Leggings

Normal-quality armor is immediately discarded.

---

# Step 2: Evaluate Resistance Distribution

Each crafted piece is evaluated based on its natural resistances.

Example:

```text
Physical 4
Fire     10
Cold     11
Poison   3
Energy   5
```

The resistances are sorted from highest to lowest:

```text
Cold     11
Fire     10
Energy    5
Physical  4
Poison    3
```

The builder identifies:

- Highest resist
- Second-highest resist
- Third-highest resist

---

# Step 3: Determine Whether the Piece Is "Good"

A piece is considered useful only if it has a clearly defined resistance specialization.

Requirements:

- Exactly 2 dominant resistances
- Exactly 3 lower resistances
- Second-highest resist must be at least 3 points higher than the third-highest resist

Formula:

```text
SecondHighest - ThirdHighest >= 3
```

Example:

```text
11 - 5 = 6
```

Accepted.

Example:

```text
Physical 7
Fire     8
Cold     7
Poison   6
Energy   8
```

Sorted:

```text
Fire      8
Energy    8
Physical  7
Cold      7
Poison    6
```

Formula:

```text
8 - 7 = 1
```

Rejected.

The builder refers to these rejected pieces as "flat" pieces.

---

# Step 4: Determine the High Pair

Every accepted piece is classified by its two highest resistances.

Example:

```text
Physical 4
Fire     10
Cold     11
Poison   3
Energy   5
```

High pair:

```text
Fire / Cold
```

The builder stores the piece under that pair.

---

# Step 5: Compare Against Existing Owners

Only one piece can own a specific high-resist pair.

Example:

Current owner:

```text
Fire 10
Cold 11
```

High pair total:

```text
21
```

New piece:

```text
Fire 11
Cold 12
```

High pair total:

```text
23
```

The new piece becomes the owner.

The old piece is recycled.

The slot that lost its piece is marked for recrafting.

---

# Piece Ranking Rules

When two pieces share the same high pair, the builder selects the better piece using the following priorities:

## Priority 1

Highest combined high-pair total.

```text
Fire + Cold
```

Example:

```text
10 + 11 = 21
```

vs

```text
11 + 12 = 23
```

Winner:

```text
23
```

## Priority 2

Highest weaker high resist.

Example:

```text
11 / 11
```

beats

```text
12 / 10
```

because:

```text
11 > 10
```

## Priority 3

Highest stronger high resist.

Example:

```text
13 / 10
```

beats

```text
12 / 10
```

because:

```text
13 > 12
```

## Priority 4

Highest overall resist total.

Example:

```text
Total Resists = 35
```

beats

```text
Total Resists = 34
```

---

# Step 6: Generate Candidate Suits

The builder selects exactly one piece from each slot:

```text
Cap
Gorget
Sleeves
Gloves
Tunic
Leggings
```

A candidate suit consists of:

```text
1 Cap
1 Gorget
1 Sleeves
1 Gloves
1 Tunic
1 Leggings
```

---

# Step 7: Count High-Pair Coverage

Every selected piece contributes two dominant resistances.

Six pieces create:

```text
6 × 2 = 12
```

high-resist assignments.

Example:

```text
Cap      Fire / Poison
Gorget   Fire / Poison
Sleeves  Poison / Energy
Gloves   Cold / Energy
Tunic    Fire / Cold
Leggings Fire / Poison
```

Coverage:

```text
Physical 0
Fire     4
Cold     2
Poison   4
Energy   2
```

---

# Step 8: Validate Distribution

The builder requires balanced coverage.

Rules:

```text
Every resist must appear at least 2 times.
No resist may appear more than 3 times.
```

Valid:

```text
Physical 2
Fire     3
Cold     2
Poison   3
Energy   2
```

Invalid:

```text
Physical 0
Fire     4
Cold     2
Poison   4
Energy   2
```

Reason:

- Physical is underrepresented
- Fire is overrepresented
- Poison is overrepresented

---

# Step 9: Calculate Natural Suit Resists

The builder sums the natural resistances across all six selected pieces.

Example:

```text
Physical = 42
Fire     = 58
Cold     = 61
Poison   = 55
Energy   = 63
```

---

# Step 10: Calculate Missing Resistances

The builder determines how much is required to reach 70.

Formula:

```text
Missing Resist = 70 - Current Resist
```

Example:

```text
Physical = 70 - 42 = 28
Fire     = 70 - 58 = 12
Cold     = 70 - 61 = 9
Poison   = 70 - 55 = 15
Energy   = 70 - 63 = 7
```

---

# Step 11: Verify Imbuing Feasibility

A candidate suit is only valid if the missing resistances can legally be imbued.

Constraints:

- Maximum 15 imbued points per resist property
- Maximum 2 resist properties per item
- Item must still fit:
  - LRC 17
  - LMC 7
  - Mana Increase or Mana Regeneration
- Item intensity cannot exceed OSI limits

If the missing resistances cannot be distributed legally, the suit is rejected.

---

# Step 12: Score Valid Suits

Every valid suit receives a score.

The builder prefers:

1. Suits that can reach 70 all resists.
2. Lower total missing resist values.
3. Fewer resist imbues required.
4. Lower total imbued resist intensity.
5. Higher natural resist totals.
6. More remaining intensity for mana properties.

The highest-scoring suit becomes the selected solution.

---

# Step 13: Determine What To Keep Looking For

If no valid suit exists, the builder analyzes high-pair coverage.

For each resist:

```text
Deficit = max(0, 2 - Count)
Overflow = max(0, Count - 3)
```

Example:

```text
Physical 0
Fire     4
Cold     2
Poison   4
Energy   2
```

Results:

```text
Physical deficit = 2
Fire overflow    = 1
Poison overflow  = 1
```

The builder concludes:

```text
Need more Physical-high pieces.
```

---

# Preferred Missing Pairs

When a resist is underrepresented, the builder should prefer new pieces that increase that resist without increasing already-overrepresented resists.

Example:

Current coverage:

```text
Physical 0
Fire     4
Cold     2
Poison   4
Energy   2
```

Preferred new pairs:

```text
Physical / Cold
Physical / Energy
```

Less desirable:

```text
Physical / Fire
Physical / Poison
```

because Fire and Poison are already overrepresented.

---

# Summary

The Mage 70 Suit Builder continuously:

1. Crafts exceptional armor.
2. Rejects flat resist distributions.
3. Tracks the best owner of every high-resist pair.
4. Generates six-piece suit combinations.
5. Validates high-pair balance.
6. Calculates natural resist totals.
7. Verifies imbuing feasibility.
8. Scores valid suits.
9. Selects the best solution.
10. Identifies which resist pair coverage is currently missing and continues crafting until a valid balanced suit can be produced.