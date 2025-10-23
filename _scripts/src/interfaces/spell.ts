export interface Spell {
  // biome-ignore lint/style/useNamingConvention: <From C# Typings>
  ID: number;
  Name: string;
  PowerWords: string;
  CursorSize: number;
  CastRange: number;
  Hue: number;
  CursorHue: number;
  MaxDuration: number;
  IsLinear: boolean;
  CastTime: number;
  ShowCastRangeDuringCasting: boolean;
  FreezeCharacterWhileCasting: boolean;
}

export interface ExtendedSpell extends Spell {
  RecoveryTime: number;
  School: School;
  MaxFasterCasting: number;
  MaxFasterCastRecovery: number;
}

export type School =
  | "Magery"
  | "Necromancy"
  | "Mysticism"
  | "Ninjitsu"
  | "Chivalry"
  | "Spellweaving"
  | "Unknown";
