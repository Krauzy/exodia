import { program } from "commander";
import inquirer from "inquirer";
import ora from "ora";
import exploits from "./commands/exploits.js";

program.version("1.0.0").description("My Node CLI");

program.action(() => {
  inquirer
    .prompt([
      {
        type: "list",
        name: "choice",
        message: "What you want to do?",
        choices: ["exploits"],
      },
    ])
    .then((result) => {
      if (result.choice === 'exploits') {
        exploits();
      }
    });
});

export default program;
