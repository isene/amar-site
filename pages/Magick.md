---
title: Magick
categories:
- Gods
- Magic
- Rules
- Spells
---

Magick in Amar RPG is a powerful and complex force. Spells are unique possessions - each spell exists as a specific instance of Magick that a character owns, and can be given to others through rituals.

<figure class="right">
<img src="images/Magick.jpg" width="420" alt="Magick" />
</figure>

## The Spell System

Each spell is described with specific properties that define how it works:

- **Name**: The spell's name
- **Encumbrance**: The magical "weight" of the spell - how much it burdens the caster's mind
- **Cooldown**: How long before the spell can be cast again after use
- **Casting Requirements**
  - **Casting Time (CT)**: How long it takes to cast
  - **Active/Passive (A/P)**: Whether the caster must actively focus on the spell while it lasts
  - **Restrictions**: Special conditions (e.g., "Can only be cast at midnight")
  - **DR(s)**: Difficulty Rating(s) - can require multiple skill rolls
- **Cost**: What casting consumes - typically Mental Fortitude, but can include Fortitude, special plants, gems, corpses, etc.
- **Attributes**
  - **Distance**: Range (fixed or flexible - modified by Range skill under SPIRIT → Casting)
  - **Duration**: How long effects last (fixed or flexible - modified by Duration skill)
  - **Weight/Targets/AoE**: Number of targets or area affected (fixed or flexible - modified by Weight, Number of Targets, or Area of Effect skills)
- **Effects**: The actual effects of the spell
- **Transfer Requirements**
  - **Receiving**: What the recipient needs in order to receive this spell
  - **Giving**: What the giver must do to transfer the spell (ritual duration, etc.)

## Spell Ownership and Transfer

Spells are owned by individual magicians. Key principles:

- Each spell is **given to a magician** who then owns it
- A spell owned can be **given to another** through a ritual (usually taking two weeks)
- A spell can be **put into a book** - the first person who reads it gets that spell
  - The spell is then **lost by the person when writing the book** (usually takes a month to write)
- **Spells are the base currency of Fenimaal** - highly valuable
- Upon death, **Kraagh collects the spells** and returns them to the God of the spell's domain (default to Fenimaal)

## Active Spell Capacity

A character can only have a certain number of spells **active** at any given moment. The number of active spells is limited by:

- **Total Encumbrance Capacity**: Determined by Mental Fortitude (MIND → Willpower → Mental Fortitude)
- Each spell has an **Encumbrance value** - the total of all active spells cannot exceed the character's capacity
- Inactive spells are "memorized" but not ready for immediate casting
- Activating/deactivating spells requires concentration and time (typically 10 minutes per spell)

## Casting Spells

To cast a spell, the character must:

1.  **Meet Requirements**: SPIRIT characteristic ≥ 2 AND total Casting (SPIRIT + Casting attribute) ≥ 5
2.  **Have Spell Active**: The spell must be in the character's active spell pool
3.  **Meet Casting Requirements**: Fulfill any restrictions, have casting time available
4.  **Make Skill Roll(s)**: Roll O6 + total skill vs DR

- - Typically uses **Attunement skills** (SPIRIT → Attunement → specific element/domain)
  - Some spells require multiple rolls

1.  **Pay Cost**: Expend Mental Fortitude or other resources
2.  **Apply Cooldown**: Spell cannot be cast again until cooldown expires

### Casting Roll Formula

**O6 + (SPIRIT + Attunement + Domain Skill) vs DR**

Example: Casting a Fire spell with SPIRIT 2, Attunement 3, Fire 4:

- Roll O6: 6, 5, 2 = 7
- Total: 7 + 2 (SPIRIT) + 3 (Attunement) + 4 (Fire) = 16
- If DR is 10, spell succeeds with margin of 6

### Flexible Spell Attributes

Some spell attributes are **flexible** and can be modified by Casting skills:

- **Range skill** (SPIRIT → Casting → Range): Increases or decreases spell distance
- **Duration skill** (SPIRIT → Casting → Duration): Extends or shortens spell duration
- **Area of Effect skill**: Expands spell area
- **Weight skill**: Allows spell to affect heavier objects
- **Number of Targets skill**: Allows spell to affect more targets

## Spell Domains

Spells are organized by domain, corresponding to Attunement skills:

- **Fire** - Flame, heat, destruction
- **Water** - Ice, liquid, purification
- **Air** - Wind, lightning, flight
- **Earth** - Stone, metal, growth
- **Life** - Healing, enhancement, protection
- **Death** - Necromancy, decay, shadow
- **Self** - Personal enhancement, meditation
- **Others** - God-specific domains, unique magicks

Each domain has associated spells that require the corresponding Attunement skill.

## Learning New Spells

Characters acquire spells through:

1.  **Direct Gift**: Another magician performs a ritual (usually 2 weeks) to transfer ownership
2.  **Reading Spell Books**: First reader gains the spell, book becomes blank
3.  **Divine Grant**: Gods may grant spells to worshippers (see Worship under SPIRIT)
4.  **Discovery**: Rare - finding ancient spell scrolls or artifacts

The recipient must meet the spell's **Receiving Requirements** (typically minimum Attunement in the spell's domain).

## Mental Fortitude and Spell Cost

**Mental Fortitude** (MIND → Willpower → Mental Fortitude) serves as the primary resource for spellcasting:

- Each spell cast consumes Mental Fortitude points (specified in spell cost)
- When Mental Fortitude reaches 0, the character **cannot cast spells** until recovery
- Mental Fortitude recovers with rest (typically 1 point per hour of rest, full recovery after 8 hours sleep)
- Some powerful spells may also cost physical Fortitude, special components, or other sacrifices

## Spell Examples

### Fire Domain

**Spark**

- Encumbrance: 1, Cooldown: 1 hour
- CT: 1 round, Active, DR: 5
- Cost: 1 Mental Fortitude
- Distance: 10m, Duration: Instant, AoE: Single target
- Effects: O6-2 fire damage
- Receiving: Fire Attunement 1, Giving: Ritual 1 week

**Fireball**

- Encumbrance: 5, Cooldown: 6 hours
- CT: 2 rounds, Active, DR: 10
- Cost: 3 Mental Fortitude
- Distance: 50m, Duration: Instant, AoE: 3m radius
- Effects: O6+2 fire damage to all in area
- Receiving: Fire Attunement 3, Giving: Ritual 2 weeks

### Water Domain

**Water Breathing**

- Encumbrance: 3, Cooldown: 2 hours
- CT: 1 round, Active, Restriction: Must be near water, DR: 8
- Cost: 2 Mental Fortitude
- Distance: Touch, Duration: 1 hour, AoE: Single target
- Effects: Target can breathe underwater
- Receiving: Water Attunement 2, Giving: Ritual 2 weeks

## See Also

- [The Character](The_Character.html): character creation with the SPIRIT characteristic
- [Spells](Spells.html): the complete spell list
