#!/usr/bin/env node

import chalk from "chalk";
import figlet from "figlet";
import program from '../src/cli.js';

console.log(
  chalk.magentaBright(figlet.textSync("EXODIA", { horizontalLayout: "full" }))
);

program.parse(process.argv);
