import { assert } from "typia";

import { assertParse } from "../../node_modules/typia/lib/json";
import type { ExtendedSpell, School, Spell } from "../interfaces/spell";

export function jsonAssertSpell(str: string): Spell[] | undefined {
  try {
    const res = assertParse<Spell[]>(str);
    return res;
  } catch (_err) {
    return;
  }
}

export function jsonAssertExtendedSpell(
  str: string,
): ExtendedSpell | undefined {
  try {
    const res = assertParse<ExtendedSpell>(str);
    return res;
  } catch (_err) {
    return;
  }
}

export function assertSchool(str: string): School | undefined {
  try {
    const res = assert<School>(str);
    return res;
  } catch (_err) {
    return;
  }
}

export function assertExtendedSpell(
  extendedSpell: unknown,
): ExtendedSpell | undefined {
  try {
    const res = assert<ExtendedSpell>(extendedSpell);
    return res;
  } catch (_err) {
    return;
  }
}
