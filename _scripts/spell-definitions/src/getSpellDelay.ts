/** biome-ignore-all lint/performance/noAwaitInLoops: <IDC about performance> */
/** biome-ignore-all lint/style/useNamingConvention: <C# Interface> */
import { mkdir, readdir, readFile, writeFile } from "node:fs/promises";

import appRootPath from "app-root-path";

import type { ExtendedSpell, School, Spell } from "./interfaces/spell";
import { getHtml } from "./utils/axios.util";
import { Cheerio } from "./utils/cheerio.util";
import { exists } from "./utils/fs.util";
import {
  assertExtendedSpell,
  jsonAssertExtendedSpell,
  jsonAssertSpell,
} from "./utils/typia.util";
import { log } from "node:console";

appRootPath.setPath(
  appRootPath.path.endsWith("/dist")
    ? appRootPath.path
    : `${appRootPath.path}/dist`,
);

const SPELL_DEF_PATH = `${appRootPath.path}/../assets/spell-def.json`;
const SAVING_PATH = `${appRootPath.path}/../assets`;
const OVERRIDE = {
  "Dispel Evil": { castTime: "1.25", recoveryTime: "1.75" },
  "Consecrate Weapon": { castTime: "1.50", recoveryTime: "1.75" },
  "Enemy of One": { castTime: "1.50", recoveryTime: "1.75" },
  "Holy Light": { castTime: "1.75", recoveryTime: "1.75" },
  "Divine Fury": { castTime: "2.00", recoveryTime: "1.75" },
  "Cleanse by Fire": { castTime: "2.00", recoveryTime: "1.75" },
  "Noble Sacrifice": { castTime: "2.50", recoveryTime: "1.75" },
  "Close Wounds": { castTime: "2.50", recoveryTime: "1.75" },
  "Remove Curse": { castTime: "2.50", recoveryTime: "1.75" },
  "Sacred Journey": { castTime: "2.50", recoveryTime: "1.75" },
};
const CASTING_SPEEDS: Record<School, { FC: number; FCR: number }> = {
  Magery: { FC: 2, FCR: 5 },
  Necromancy: { FC: 2, FCR: 6 },
  Mysticism: { FC: 2, FCR: 6 },
  Ninjitsu: { FC: 4, FCR: 6 },
  Chivalry: { FC: 4, FCR: 6 },
  Spellweaving: { FC: 4, FCR: 6 },
  Unknown: { FC: 2, FCR: 6 },
};

async function scrap(
  url: string,
): Promise<
  | Pick<
      ExtendedSpell,
      | "CastTime"
      | "RecoveryTime"
      | "School"
      | "MaxFasterCasting"
      | "MaxFasterCastRecovery"
      | "CapChivalryFasterCasting"
    >
  | undefined
> {
  const html = await getHtml(url);
  if (!html) {
    return;
  }

  const cheerio = new Cheerio(html);

  const castingTime =
    cheerio.getTableValueFormat1() || cheerio.getTableValueFormat2();
  if (castingTime === undefined) {
    return;
  }

  const school = cheerio.getSchool();
  if (school === undefined) {
    return;
  }

  return {
    CastTime: castingTime,
    RecoveryTime: 1.5,
    School: school,
    MaxFasterCasting: CASTING_SPEEDS[school].FC,
    MaxFasterCastRecovery: CASTING_SPEEDS[school].FCR,
    CapChivalryFasterCasting: school === "Chivalry" || null,
  };
}

async function createJson(
  spell: Spell,
  pickedExtendedSpell: Pick<
    ExtendedSpell,
    "RecoveryTime" | "School" | "MaxFasterCasting" | "MaxFasterCastRecovery" | "CapChivalryFasterCasting" | "CastTime"
  >,
  jsonPath: string,
): Promise<void> {
  const extendedSpell: ExtendedSpell = {
    ...spell,
    ...pickedExtendedSpell,
  };
  const isValid = assertExtendedSpell(extendedSpell);
  if (!isValid) {
    throw new Error(`CreateJson Error: ${spell.Name}`);
  }
  const json = JSON.stringify(extendedSpell, null, 2);
  await writeFile(jsonPath, json);
}

async function readJson(path: string): Promise<string> {
  const jsonBuf = await readFile(path);
  const jsonStr = jsonBuf.toString();
  return jsonStr;
}

async function createIndividualJson(spells: Spell[]): Promise<void> {
  for (let i = 0; i < spells.length; i += 1) {
    const spell = spells[i];
    const { Name } = spell;
    const replacedName = Name.replace(/ /g, "_");
    const jsonPath = `${SAVING_PATH}/${replacedName}.json`;
    const isJsonExists = await exists(jsonPath);
    if (isJsonExists) {
      const extendedSpellStr = await readJson(jsonPath);
      const extendedSpell = jsonAssertExtendedSpell(extendedSpellStr);
      if (extendedSpell) {
        continue;
      }
    }

    const override = OVERRIDE[Name];
    if (override) {
      await createJson(
        spell,
        {
          RecoveryTime: +override.recoveryTime,
          School: "Chivalry",
          MaxFasterCasting: +CASTING_SPEEDS.Chivalry.FC,
          MaxFasterCastRecovery: +CASTING_SPEEDS.Chivalry.FCR,
          CapChivalryFasterCasting: true,
          CastTime: +override.castTime,
        },
        jsonPath,
      );
      continue;
    }

    {
      const pickExtendedSpell = await scrap(
        `https://www.uoguide.com/${replacedName}`,
      );
      if (pickExtendedSpell) {
        await createJson(spell, pickExtendedSpell, jsonPath);
        continue;
      }
    }

    {
      const pickExtendedSpell = await scrap(
        `https://www.uoguide.com/${replacedName}_(spell)`,
      );
      if (pickExtendedSpell) {
        await createJson(spell, pickExtendedSpell, jsonPath);
        continue;
      }
    }

    {
      const pickExtendedSpell = await scrap(
        `https://www.uoguide.com/${replacedName}_(Spell)`,
      );
      if (pickExtendedSpell) {
        await createJson(spell, pickExtendedSpell, jsonPath);
        continue;
      }
    }

    {
      const pickExtendedSpell = await scrap(
        `https://www.uoguide.com/Summon_${replacedName}`,
      );
      if (pickExtendedSpell) {
        await createJson(spell, pickExtendedSpell, jsonPath);
        continue;
      }
    }

    await createJson(
      spell,
      {
        RecoveryTime: 0,
        School: "Unknown",
        MaxFasterCasting: +CASTING_SPEEDS.Unknown.FC,
        MaxFasterCastRecovery: +CASTING_SPEEDS.Unknown.FCR,
        CapChivalryFasterCasting: null,
        CastTime: spell.CastTime,
      },
      jsonPath,
    );
  }
}

async function mergeIndividualJsons(): Promise<void> {
  const extendedSpells: ExtendedSpell[] = [];
  const files = await readdir(SAVING_PATH);
  for (let i = 0; i < files.length; i += 1) {
    const file = files[i];
    if (file === "MERGED.json" || file === "spell-def.json") {
      continue;
    }
    const fileContent = await readJson(`${SAVING_PATH}/${file}`);
    const extendedSpell = jsonAssertExtendedSpell(fileContent);
    if (!extendedSpell) {
      throw new Error(`MergeIndividualJsons Error: ${file}`);
    }
    extendedSpells.push(extendedSpell);
  }

  const sortedExtendedSpells = extendedSpells
    .toSorted((a, b) => {
      return a.ID - b.ID;
    });

  const json = JSON.stringify(sortedExtendedSpells, null, 2);
  await writeFile(`${SAVING_PATH}/MERGED.json`, json);
}

// biome-ignore lint/nursery/noFloatingPromises: <Top level async/await>
(async () => {
  const isSavingPathExists = await exists(SAVING_PATH);
  if (!isSavingPathExists) {
    await mkdir(SAVING_PATH);
  }

  const spellsStr = await readJson(SPELL_DEF_PATH);
  const spells = jsonAssertSpell(spellsStr);
  if (!spells) {
    log("ERROR");
    return;
  }

  await createIndividualJson(spells);
  await mergeIndividualJsons();
})();
