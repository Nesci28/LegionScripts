import axios from "axios";

import { isString } from "./primitive.util";

export async function getHtml(url: string): Promise<string | undefined> {
  try {
    const axiosRes = await axios.get<string | undefined>(url, {
      // biome-ignore lint/style/useNamingConvention: <axios typings>
      headers: { Accept: "application/html" },
    });
    const html = axiosRes.data;
    const isStr = isString(html);
    if (!isStr) {
      throw new Error("Did not receive html from uoguide");
    }
    return html;
  } catch (_err) {}
}
