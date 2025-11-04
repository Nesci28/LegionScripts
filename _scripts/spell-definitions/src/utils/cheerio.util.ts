import * as cheerio from "cheerio";
import type { AnyNode } from "domhandler";

import type { School } from "../interfaces/spell";
import { assertSchool } from "../utils/typia.util";
import { isString } from "./primitive.util";

export class Cheerio {
  private cheerioApi: cheerio.CheerioAPI;

  constructor(private html: string) {
    this.cheerioApi = cheerio.load(this.html);
  }

  public getSchool(): School | undefined {
    const categoryText = this.cheerioApi("#catlinks li a")
      .first()
      .text()
      .trim();

    const match = categoryText.match(/^(\w+)/);
    const category = match ? match[1] : undefined;
    if (!category) {
      return;
    }

    const isSchool = assertSchool(category);
    return isSchool;
  }

  public getTableValueFormat1(): number | undefined {
    const row = this.cheerioApi("tbody tr").filter((_i, el) => {
      const thText = this.cheerioApi(el).find("th").text().trim();
      return thText === "Delay (seconds)" || thText === "Casting Delay";
    });

    if (row.length === 0) {
      return undefined;
    }

    const value = row
      .find("td")
      .text()
      .trim()
      .replace(/[^0-9.]/g, "");
    return isString(value) && !Number.isNaN(Number(value)) ? +value : undefined;
  }

  public getTableValueFormat2(): number | undefined {
    const rows = this.cheerioApi("tbody tr");

    for (let i = 0; i < rows.length; i++) {
      const headerRow = this.cheerioApi(rows[i]);
      const thTexts = headerRow
        .find("th")
        .map((_, el) => this.cheerioApi(el).text().trim())
        .get();

      let nextRow: cheerio.BasicAcceptedElems<AnyNode> | undefined;
      let labelIndex = 0;
      if (thTexts.includes("Casting Delay")) {
        labelIndex = thTexts.indexOf("Casting Delay");
        const _t = rows[i + 1];
        nextRow = rows[i + 1];
      }
      if (thTexts.includes("Delay (seconds)")) {
        labelIndex = thTexts.indexOf("Casting Delay");
        nextRow = rows[i + 1];
      }

      if (nextRow) {
        const value = this.cheerioApi(nextRow)
          .find("td")
          .eq(labelIndex)
          .text()
          .trim();
        return isString(value) && !Number.isNaN(Number(value))
          ? +value
          : undefined;
      }
    }

    return undefined;
  }
}
