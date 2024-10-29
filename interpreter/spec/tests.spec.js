import { StackCompiler } from "../main.js";

function t(s) {
  return s.replace(/\s/g, "").replace(/\n/g, "");
}

function checksTwoCodes(code1, code2) {
  expect(t(code1)).toBe(t(code2));
}

describe("Interpreter", function () {
  let interpreter;

  beforeEach(() => {
    interpreter = new StackCompiler();
  });

  describe("Define Headers", () => {
    ["my_he", "myhe"].forEach((header_name) =>
      it("should create a header to hold a string value", function () {
        interpreter.parse(`header ${header_name} "princing"`);
        const result = interpreter.translate();
        expect(result).toBe(`const ${header_name} = new Header("princing")`);
      }),
    );
  });

  describe("Define Variables", () => {
    it("should create a variable to hold a string value", function () {
      interpreter.parse('#my_var "abc"');
      const result = interpreter.translate();
      expect(result).toBe('let my_var = "abc"');
    });

    it("should create a variable to hold a number value", function () {
      interpreter.parse('#my_var "10"');
      const result = interpreter.translate();
      expect(result).toBe("let my_var = 10");
    });
  });

  describe("Line chart", () => {
    it("should create a line chart", function () {
      interpreter.parse("#price #time line");
      const result = interpreter.translate();
      checksTwoCodes(
        result,
        "const trace = {x: price.getValues(), y: time.getValues(), type: 'lines'}; const data = [trace]",
      );
    });
  });

  describe("Histogram chart", () => {
    it("should create a histogram chart", function () {
      interpreter.parse("#price #time hist");
      const result = interpreter.translate();
      checksTwoCodes(
        result,
        "const trace = {x: price.getValues(), y: time.getValues(), type: 'bar'}; const data = [trace]",
      );
    });
  });

  describe("Scatter chart", () => {
    it("should create a histogram chart", function () {
      interpreter.parse("#price #time scatter");
      const result = interpreter.translate();
      checksTwoCodes(
        result,
        "const trace = {x: price.getValues(), y: time.getValues(), type: 'scatter'}; const data = [trace]",
      );
    });
  });

  describe("Code", () => {
    it("simple line chart", () => {
      interpreter.parse('header year "year"');
      interpreter.parse('header price "price"');
      interpreter.parse("#year #price line");
      const result = interpreter.translate();
      checksTwoCodes(
        result,
        `
        const year = new Header("year");
        const price = new Header("price");
        const trace = {x: year.getValues(), y: price.getValues(), type: 'lines'};
        const data = [trace]
        `,
      );
    });
  });

  it("tmp", () => {
    interpreter.parse(`header price "price"`);
    interpreter.parse(`header time "time"`);
    interpreter.parse(`header taxes "taxes"`);
    interpreter.parse(`#time #price line`);
    const result = interpreter.translate();
    console.log(result);
  });
});
