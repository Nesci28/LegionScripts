import * as __typia_transform__assertGuard from "typia/lib/internal/_assertGuard.js";
import { assert } from "typia";
import { assertParse } from "../../node_modules/typia/lib/json";
import type { ExtendedSpell, School, Spell } from "../interfaces/spell";
export function jsonAssertSpell(str: string): Spell[] | undefined {
    try {
        const res = (() => { const _io0 = (input: any): boolean => "number" === typeof input.ID && "string" === typeof input.Name && "string" === typeof input.PowerWords && "number" === typeof input.CursorSize && "number" === typeof input.CastRange && "number" === typeof input.Hue && "number" === typeof input.CursorHue && "number" === typeof input.MaxDuration && "boolean" === typeof input.IsLinear && "number" === typeof input.CastTime && "boolean" === typeof input.ShowCastRangeDuringCasting && "boolean" === typeof input.FreezeCharacterWhileCasting; const _ao0 = (input: any, _path: string, _exceptionable: boolean = true): boolean => ("number" === typeof input.ID || __typia_transform__assertGuard._assertGuard(_exceptionable, {
            method: "assertParse",
            path: _path + ".ID",
            expected: "number",
            value: input.ID
        }, _errorFactory)) && ("string" === typeof input.Name || __typia_transform__assertGuard._assertGuard(_exceptionable, {
            method: "assertParse",
            path: _path + ".Name",
            expected: "string",
            value: input.Name
        }, _errorFactory)) && ("string" === typeof input.PowerWords || __typia_transform__assertGuard._assertGuard(_exceptionable, {
            method: "assertParse",
            path: _path + ".PowerWords",
            expected: "string",
            value: input.PowerWords
        }, _errorFactory)) && ("number" === typeof input.CursorSize || __typia_transform__assertGuard._assertGuard(_exceptionable, {
            method: "assertParse",
            path: _path + ".CursorSize",
            expected: "number",
            value: input.CursorSize
        }, _errorFactory)) && ("number" === typeof input.CastRange || __typia_transform__assertGuard._assertGuard(_exceptionable, {
            method: "assertParse",
            path: _path + ".CastRange",
            expected: "number",
            value: input.CastRange
        }, _errorFactory)) && ("number" === typeof input.Hue || __typia_transform__assertGuard._assertGuard(_exceptionable, {
            method: "assertParse",
            path: _path + ".Hue",
            expected: "number",
            value: input.Hue
        }, _errorFactory)) && ("number" === typeof input.CursorHue || __typia_transform__assertGuard._assertGuard(_exceptionable, {
            method: "assertParse",
            path: _path + ".CursorHue",
            expected: "number",
            value: input.CursorHue
        }, _errorFactory)) && ("number" === typeof input.MaxDuration || __typia_transform__assertGuard._assertGuard(_exceptionable, {
            method: "assertParse",
            path: _path + ".MaxDuration",
            expected: "number",
            value: input.MaxDuration
        }, _errorFactory)) && ("boolean" === typeof input.IsLinear || __typia_transform__assertGuard._assertGuard(_exceptionable, {
            method: "assertParse",
            path: _path + ".IsLinear",
            expected: "boolean",
            value: input.IsLinear
        }, _errorFactory)) && ("number" === typeof input.CastTime || __typia_transform__assertGuard._assertGuard(_exceptionable, {
            method: "assertParse",
            path: _path + ".CastTime",
            expected: "number",
            value: input.CastTime
        }, _errorFactory)) && ("boolean" === typeof input.ShowCastRangeDuringCasting || __typia_transform__assertGuard._assertGuard(_exceptionable, {
            method: "assertParse",
            path: _path + ".ShowCastRangeDuringCasting",
            expected: "boolean",
            value: input.ShowCastRangeDuringCasting
        }, _errorFactory)) && ("boolean" === typeof input.FreezeCharacterWhileCasting || __typia_transform__assertGuard._assertGuard(_exceptionable, {
            method: "assertParse",
            path: _path + ".FreezeCharacterWhileCasting",
            expected: "boolean",
            value: input.FreezeCharacterWhileCasting
        }, _errorFactory)); const __is = (input: any): input is Spell[] => Array.isArray(input) && input.every((elem: any) => "object" === typeof elem && null !== elem && _io0(elem)); let _errorFactory: any; const __assert = (input: any, errorFactory?: (p: import("typia").TypeGuardError.IProps) => Error): Spell[] => {
            if (false === __is(input)) {
                _errorFactory = errorFactory;
                ((input: any, _path: string, _exceptionable: boolean = true) => (Array.isArray(input) || __typia_transform__assertGuard._assertGuard(true, {
                    method: "assertParse",
                    path: _path + "",
                    expected: "Array<Spell>",
                    value: input
                }, _errorFactory)) && input.every((elem: any, _index2: number) => ("object" === typeof elem && null !== elem || __typia_transform__assertGuard._assertGuard(true, {
                    method: "assertParse",
                    path: _path + "[" + _index2 + "]",
                    expected: "Spell",
                    value: elem
                }, _errorFactory)) && _ao0(elem, _path + "[" + _index2 + "]", true) || __typia_transform__assertGuard._assertGuard(true, {
                    method: "assertParse",
                    path: _path + "[" + _index2 + "]",
                    expected: "Spell",
                    value: elem
                }, _errorFactory)) || __typia_transform__assertGuard._assertGuard(true, {
                    method: "assertParse",
                    path: _path + "",
                    expected: "Array<Spell>",
                    value: input
                }, _errorFactory))(input, "$input", true);
            }
            return input;
        }; return (input: string, errorFactory?: (p: import("typia").TypeGuardError.IProps) => Error): import("typia").Primitive<Spell[]> => __assert(JSON.parse(input), errorFactory) as any; })()(str);
        return res;
    }
    catch (_err) {
        return;
    }
}
export function jsonAssertExtendedSpell(str: string): ExtendedSpell | undefined {
    try {
        const res = (() => { const _io0 = (input: any): boolean => "number" === typeof input.RecoveryTime && ("Magery" === input.School || "Necromancy" === input.School || "Mysticism" === input.School || "Ninjitsu" === input.School || "Chivalry" === input.School || "Spellweaving" === input.School || "Unknown" === input.School) && "number" === typeof input.MaxFasterCasting && "number" === typeof input.MaxFasterCastRecovery && "number" === typeof input.ID && "string" === typeof input.Name && "string" === typeof input.PowerWords && "number" === typeof input.CursorSize && "number" === typeof input.CastRange && "number" === typeof input.Hue && "number" === typeof input.CursorHue && "number" === typeof input.MaxDuration && "boolean" === typeof input.IsLinear && "number" === typeof input.CastTime && "boolean" === typeof input.ShowCastRangeDuringCasting && "boolean" === typeof input.FreezeCharacterWhileCasting; const _ao0 = (input: any, _path: string, _exceptionable: boolean = true): boolean => ("number" === typeof input.RecoveryTime || __typia_transform__assertGuard._assertGuard(_exceptionable, {
            method: "assertParse",
            path: _path + ".RecoveryTime",
            expected: "number",
            value: input.RecoveryTime
        }, _errorFactory)) && ("Magery" === input.School || "Necromancy" === input.School || "Mysticism" === input.School || "Ninjitsu" === input.School || "Chivalry" === input.School || "Spellweaving" === input.School || "Unknown" === input.School || __typia_transform__assertGuard._assertGuard(_exceptionable, {
            method: "assertParse",
            path: _path + ".School",
            expected: "(\"Chivalry\" | \"Magery\" | \"Mysticism\" | \"Necromancy\" | \"Ninjitsu\" | \"Spellweaving\" | \"Unknown\")",
            value: input.School
        }, _errorFactory)) && ("number" === typeof input.MaxFasterCasting || __typia_transform__assertGuard._assertGuard(_exceptionable, {
            method: "assertParse",
            path: _path + ".MaxFasterCasting",
            expected: "number",
            value: input.MaxFasterCasting
        }, _errorFactory)) && ("number" === typeof input.MaxFasterCastRecovery || __typia_transform__assertGuard._assertGuard(_exceptionable, {
            method: "assertParse",
            path: _path + ".MaxFasterCastRecovery",
            expected: "number",
            value: input.MaxFasterCastRecovery
        }, _errorFactory)) && ("number" === typeof input.ID || __typia_transform__assertGuard._assertGuard(_exceptionable, {
            method: "assertParse",
            path: _path + ".ID",
            expected: "number",
            value: input.ID
        }, _errorFactory)) && ("string" === typeof input.Name || __typia_transform__assertGuard._assertGuard(_exceptionable, {
            method: "assertParse",
            path: _path + ".Name",
            expected: "string",
            value: input.Name
        }, _errorFactory)) && ("string" === typeof input.PowerWords || __typia_transform__assertGuard._assertGuard(_exceptionable, {
            method: "assertParse",
            path: _path + ".PowerWords",
            expected: "string",
            value: input.PowerWords
        }, _errorFactory)) && ("number" === typeof input.CursorSize || __typia_transform__assertGuard._assertGuard(_exceptionable, {
            method: "assertParse",
            path: _path + ".CursorSize",
            expected: "number",
            value: input.CursorSize
        }, _errorFactory)) && ("number" === typeof input.CastRange || __typia_transform__assertGuard._assertGuard(_exceptionable, {
            method: "assertParse",
            path: _path + ".CastRange",
            expected: "number",
            value: input.CastRange
        }, _errorFactory)) && ("number" === typeof input.Hue || __typia_transform__assertGuard._assertGuard(_exceptionable, {
            method: "assertParse",
            path: _path + ".Hue",
            expected: "number",
            value: input.Hue
        }, _errorFactory)) && ("number" === typeof input.CursorHue || __typia_transform__assertGuard._assertGuard(_exceptionable, {
            method: "assertParse",
            path: _path + ".CursorHue",
            expected: "number",
            value: input.CursorHue
        }, _errorFactory)) && ("number" === typeof input.MaxDuration || __typia_transform__assertGuard._assertGuard(_exceptionable, {
            method: "assertParse",
            path: _path + ".MaxDuration",
            expected: "number",
            value: input.MaxDuration
        }, _errorFactory)) && ("boolean" === typeof input.IsLinear || __typia_transform__assertGuard._assertGuard(_exceptionable, {
            method: "assertParse",
            path: _path + ".IsLinear",
            expected: "boolean",
            value: input.IsLinear
        }, _errorFactory)) && ("number" === typeof input.CastTime || __typia_transform__assertGuard._assertGuard(_exceptionable, {
            method: "assertParse",
            path: _path + ".CastTime",
            expected: "number",
            value: input.CastTime
        }, _errorFactory)) && ("boolean" === typeof input.ShowCastRangeDuringCasting || __typia_transform__assertGuard._assertGuard(_exceptionable, {
            method: "assertParse",
            path: _path + ".ShowCastRangeDuringCasting",
            expected: "boolean",
            value: input.ShowCastRangeDuringCasting
        }, _errorFactory)) && ("boolean" === typeof input.FreezeCharacterWhileCasting || __typia_transform__assertGuard._assertGuard(_exceptionable, {
            method: "assertParse",
            path: _path + ".FreezeCharacterWhileCasting",
            expected: "boolean",
            value: input.FreezeCharacterWhileCasting
        }, _errorFactory)); const __is = (input: any): input is ExtendedSpell => "object" === typeof input && null !== input && _io0(input); let _errorFactory: any; const __assert = (input: any, errorFactory?: (p: import("typia").TypeGuardError.IProps) => Error): ExtendedSpell => {
            if (false === __is(input)) {
                _errorFactory = errorFactory;
                ((input: any, _path: string, _exceptionable: boolean = true) => ("object" === typeof input && null !== input || __typia_transform__assertGuard._assertGuard(true, {
                    method: "assertParse",
                    path: _path + "",
                    expected: "ExtendedSpell",
                    value: input
                }, _errorFactory)) && _ao0(input, _path + "", true) || __typia_transform__assertGuard._assertGuard(true, {
                    method: "assertParse",
                    path: _path + "",
                    expected: "ExtendedSpell",
                    value: input
                }, _errorFactory))(input, "$input", true);
            }
            return input;
        }; return (input: string, errorFactory?: (p: import("typia").TypeGuardError.IProps) => Error): import("typia").Primitive<ExtendedSpell> => __assert(JSON.parse(input), errorFactory) as any; })()(str);
        return res;
    }
    catch (_err) {
        return;
    }
}
export function assertSchool(str: string): School | undefined {
    try {
        const res = (() => { const __is = (input: any): input is School => "Magery" === input || "Necromancy" === input || "Mysticism" === input || "Ninjitsu" === input || "Chivalry" === input || "Spellweaving" === input || "Unknown" === input; let _errorFactory: any; return (input: any, errorFactory?: (p: import("typia").TypeGuardError.IProps) => Error): School => {
            if (false === __is(input)) {
                _errorFactory = errorFactory;
                ((input: any, _path: string, _exceptionable: boolean = true) => "Magery" === input || "Necromancy" === input || "Mysticism" === input || "Ninjitsu" === input || "Chivalry" === input || "Spellweaving" === input || "Unknown" === input || __typia_transform__assertGuard._assertGuard(true, {
                    method: "assert",
                    path: _path + "",
                    expected: "(\"Chivalry\" | \"Magery\" | \"Mysticism\" | \"Necromancy\" | \"Ninjitsu\" | \"Spellweaving\" | \"Unknown\")",
                    value: input
                }, _errorFactory))(input, "$input", true);
            }
            return input;
        }; })()(str);
        return res;
    }
    catch (_err) {
        return;
    }
}
export function assertExtendedSpell(extendedSpell: unknown): ExtendedSpell | undefined {
    try {
        const res = (() => { const _io0 = (input: any): boolean => "number" === typeof input.RecoveryTime && ("Magery" === input.School || "Necromancy" === input.School || "Mysticism" === input.School || "Ninjitsu" === input.School || "Chivalry" === input.School || "Spellweaving" === input.School || "Unknown" === input.School) && "number" === typeof input.MaxFasterCasting && "number" === typeof input.MaxFasterCastRecovery && "number" === typeof input.ID && "string" === typeof input.Name && "string" === typeof input.PowerWords && "number" === typeof input.CursorSize && "number" === typeof input.CastRange && "number" === typeof input.Hue && "number" === typeof input.CursorHue && "number" === typeof input.MaxDuration && "boolean" === typeof input.IsLinear && "number" === typeof input.CastTime && "boolean" === typeof input.ShowCastRangeDuringCasting && "boolean" === typeof input.FreezeCharacterWhileCasting; const _ao0 = (input: any, _path: string, _exceptionable: boolean = true): boolean => ("number" === typeof input.RecoveryTime || __typia_transform__assertGuard._assertGuard(_exceptionable, {
            method: "assert",
            path: _path + ".RecoveryTime",
            expected: "number",
            value: input.RecoveryTime
        }, _errorFactory)) && ("Magery" === input.School || "Necromancy" === input.School || "Mysticism" === input.School || "Ninjitsu" === input.School || "Chivalry" === input.School || "Spellweaving" === input.School || "Unknown" === input.School || __typia_transform__assertGuard._assertGuard(_exceptionable, {
            method: "assert",
            path: _path + ".School",
            expected: "(\"Chivalry\" | \"Magery\" | \"Mysticism\" | \"Necromancy\" | \"Ninjitsu\" | \"Spellweaving\" | \"Unknown\")",
            value: input.School
        }, _errorFactory)) && ("number" === typeof input.MaxFasterCasting || __typia_transform__assertGuard._assertGuard(_exceptionable, {
            method: "assert",
            path: _path + ".MaxFasterCasting",
            expected: "number",
            value: input.MaxFasterCasting
        }, _errorFactory)) && ("number" === typeof input.MaxFasterCastRecovery || __typia_transform__assertGuard._assertGuard(_exceptionable, {
            method: "assert",
            path: _path + ".MaxFasterCastRecovery",
            expected: "number",
            value: input.MaxFasterCastRecovery
        }, _errorFactory)) && ("number" === typeof input.ID || __typia_transform__assertGuard._assertGuard(_exceptionable, {
            method: "assert",
            path: _path + ".ID",
            expected: "number",
            value: input.ID
        }, _errorFactory)) && ("string" === typeof input.Name || __typia_transform__assertGuard._assertGuard(_exceptionable, {
            method: "assert",
            path: _path + ".Name",
            expected: "string",
            value: input.Name
        }, _errorFactory)) && ("string" === typeof input.PowerWords || __typia_transform__assertGuard._assertGuard(_exceptionable, {
            method: "assert",
            path: _path + ".PowerWords",
            expected: "string",
            value: input.PowerWords
        }, _errorFactory)) && ("number" === typeof input.CursorSize || __typia_transform__assertGuard._assertGuard(_exceptionable, {
            method: "assert",
            path: _path + ".CursorSize",
            expected: "number",
            value: input.CursorSize
        }, _errorFactory)) && ("number" === typeof input.CastRange || __typia_transform__assertGuard._assertGuard(_exceptionable, {
            method: "assert",
            path: _path + ".CastRange",
            expected: "number",
            value: input.CastRange
        }, _errorFactory)) && ("number" === typeof input.Hue || __typia_transform__assertGuard._assertGuard(_exceptionable, {
            method: "assert",
            path: _path + ".Hue",
            expected: "number",
            value: input.Hue
        }, _errorFactory)) && ("number" === typeof input.CursorHue || __typia_transform__assertGuard._assertGuard(_exceptionable, {
            method: "assert",
            path: _path + ".CursorHue",
            expected: "number",
            value: input.CursorHue
        }, _errorFactory)) && ("number" === typeof input.MaxDuration || __typia_transform__assertGuard._assertGuard(_exceptionable, {
            method: "assert",
            path: _path + ".MaxDuration",
            expected: "number",
            value: input.MaxDuration
        }, _errorFactory)) && ("boolean" === typeof input.IsLinear || __typia_transform__assertGuard._assertGuard(_exceptionable, {
            method: "assert",
            path: _path + ".IsLinear",
            expected: "boolean",
            value: input.IsLinear
        }, _errorFactory)) && ("number" === typeof input.CastTime || __typia_transform__assertGuard._assertGuard(_exceptionable, {
            method: "assert",
            path: _path + ".CastTime",
            expected: "number",
            value: input.CastTime
        }, _errorFactory)) && ("boolean" === typeof input.ShowCastRangeDuringCasting || __typia_transform__assertGuard._assertGuard(_exceptionable, {
            method: "assert",
            path: _path + ".ShowCastRangeDuringCasting",
            expected: "boolean",
            value: input.ShowCastRangeDuringCasting
        }, _errorFactory)) && ("boolean" === typeof input.FreezeCharacterWhileCasting || __typia_transform__assertGuard._assertGuard(_exceptionable, {
            method: "assert",
            path: _path + ".FreezeCharacterWhileCasting",
            expected: "boolean",
            value: input.FreezeCharacterWhileCasting
        }, _errorFactory)); const __is = (input: any): input is ExtendedSpell => "object" === typeof input && null !== input && _io0(input); let _errorFactory: any; return (input: any, errorFactory?: (p: import("typia").TypeGuardError.IProps) => Error): ExtendedSpell => {
            if (false === __is(input)) {
                _errorFactory = errorFactory;
                ((input: any, _path: string, _exceptionable: boolean = true) => ("object" === typeof input && null !== input || __typia_transform__assertGuard._assertGuard(true, {
                    method: "assert",
                    path: _path + "",
                    expected: "ExtendedSpell",
                    value: input
                }, _errorFactory)) && _ao0(input, _path + "", true) || __typia_transform__assertGuard._assertGuard(true, {
                    method: "assert",
                    path: _path + "",
                    expected: "ExtendedSpell",
                    value: input
                }, _errorFactory))(input, "$input", true);
            }
            return input;
        }; })()(extendedSpell);
        return res;
    }
    catch (_err) {
        return;
    }
}
