/** biome-ignore-all lint/suspicious/noConsole: <logging> */

export function log(name: string, str: string): void {
  console.log(`${name} :>> ${str}`);
}
