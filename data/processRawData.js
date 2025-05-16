import { appendFile, mkdir, readFile, readdir } from "node:fs/promises";
import path from "node:path";

const dataPath = "../load_testing_api/scenarios/results/2025-05-16";
const resultsPath = "./processed_data/load_testing_results";


const metrics = [
  "min",
  "max",
  "count",
  "mean",
  "p50",
  "median",
  "p75",
  "p90",
  "p95",
  "p99",
  "p999",
];

const loadTestToCsv = async () => {
  const branches = await readdir(dataPath);
  console.log(`Gevonden mappen in ${dataPath}:`, branches);

  for (const branch of branches) {
    const testFiles = await readdir(`${dataPath}/${branch}`);
    const tests = testFiles.map((filename) => path.parse(filename).name);

    console.log(`Verwerken van: ${branch}`);
    console.log(`Tests: ${tests.join(", ")}`);

    await mkdir(`${resultsPath}/${branch}`, { recursive: true });

    for (const test of tests) {
      console.log(`Schrijf ${test}.csv...`);

      await appendFile(
        `${resultsPath}/${branch}/${test}.csv`,
        `${["id", ...metrics].join(",")}\n`
      );

      const data = await readFile(`${dataPath}/${branch}/${test}.json`);
      const jsonData = JSON.parse(data);
      const results = jsonData.intermediate;

      for (let index = 1; index < results.length; index++) {
        const values = [];

        for (const metric of metrics) {
          const value = results[index].summaries["http.response_time"][metric];
          values.push(value);
        }

        await appendFile(
          `${resultsPath}/${branch}/${test}.csv`,
          `${index},${values.join(",")}\n`
        );
      }
    }
  }
};
const main = async () => {
  await loadTestToCsv();
};

main();