function checkJSString(input) {
  const patterns = [
    /^#\w+\s+"[^"]*"$/, // Case 1: #abc "hello world";
    /^#\w+\s+#\w+\s+\w+$/, // Case 2: #a #b hist;
    /^header\s+\w+\s+"[^"]*"$/, // Case 3: header abc_b "hello world";
  ];

  const name = ["variable", "chart", "header"];

  for (const idx in patterns) {
    const pattern = patterns[idx];
    if (pattern.test(input)) {
      return name[idx];
    }
  }

  throw new Error(`Cannot find an instruction for ${input}`);
}

class Header {
  constructor(name) {
    this.name = name;
    this.values = {
      price: [100, 200, 300, 400, 300, 300, 450, 500],
      year: [2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019],
    };
  }

  getValues() {
    return this.values[this.name];
  }
}

export class StackCompiler {
  constructor() {
    this.stack = [];
    this.headers = [];
    this.variables = [];
    this.lines = [];
  }

  // TODO: it's better to create classes for each type of chart.
  parse(input) {
    const tokens = input.split(" ");
    const type = checkJSString(input);
    if (type == "variable") {
      const name = tokens[0].substring(1);
      let value = tokens[1];

      // is a number
      if (!isNaN(value.substring(1, value.length - 1))) {
        value = Number(value.substring(1, value.length - 1));
      }
      this.lines.push(`let ${name} = ${value}`);
    } else if (type == "chart") {
      const v1 = tokens[0].substring(1);
      const v2 = tokens[1].substring(1);
      const chart_type = tokens[2];
      const type = {
        line: "lines",
        hist: "bar",
        scatter: "scatter",
      }[chart_type];
      this.lines.push(
        `const trace = {x: ${v1}.getValues(), y: ${v2}.getValues(), type: '${type}'}`,
      );
      this.lines.push(`const data = [trace]`);
    } else if (type == "header") {
      const name = tokens[1];
      let value = tokens[2];
      this.lines.push(`const ${name} = new Header(${value})`);
    } else {
      throw new Error(`${input} - is a invalid instruction`);
    }
  }

  parseVariable() {}

  translate() {
    return this.lines.join(";");
  }
}
