import { assertParse } from "../../node_modules/typia/lib/json";
import type { Spell } from "../interfaces/spell";

export function assertSpell(str: string): Spell[] {
  const res = assertParse<Spell[]>(str);
  return res;
}
