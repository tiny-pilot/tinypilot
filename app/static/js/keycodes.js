"use strict";

//TODO: Fix these mappings.

// Mappings of characters to codes that are shared among different keyboard
// layouts.
const commonKeyCodes = {
  "\t": 9,
  "\n": 13,
  " ": 32,
  0: 48,
  ")": 48,
  1: 49,
  2: 50,
  3: 51,
  4: 52,
  $: 52,
  5: 53,
  "%": 53,
  6: 54,
  "^": 54,
  7: 55,
  "&": 55,
  8: 56,
  "*": 56,
  9: 57,
  "(": 57,
  ":": 59,
  ";": 59,
  a: "KeyA",
  b: "KeyB",
  c: "KeyC",
  d: "KeyD",
  e: "KeyE",
  f: "KeyF",
  g: "KeyG",
  h: "KeyH",
  i: "KeyI",
  j: "KeyJ",
  k: "KeyK",
  l: "KeyL",
  m: "KeyM",
  n: "KeyN",
  o: "KeyO",
  p: "KeyP",
  q: "KeyQ",
  r: "KeyR",
  s: "KeyS",
  t: "KeyT",
  u: "KeyU",
  v: "KeyV",
  w: "KeyW",
  x: "KeyX",
  y: "KeyY",
  z: "KeyZ",
  ",": 188,
  "<": 188,
  ".": 190,
  ">": 190,
  "/": 191,
  "?": 191,
  "[": 219,
  "{": 219,
  "|": 220,
  "]": 221,
  "}": 221,
  "'": 222,
};

// Given a character and a browser language, finds the matching code
export function findKeyCode(character, browserLanguage) {
  if (browserLanguage === "en-GB") {
    return findKeyCodeEnGb(character);
  }
  // Default to en-US if no other language matches.
  return findKeyCodeEnUs(character);
}

function joinDictionaries(a, b) {
  return Object.assign({}, a, b);
}

function findKeyCodeEnUs(character) {
  const usSpecificKeys = {
    "!": 49,
    "@": 50,
    "#": 51,
    "+": 187,
    "=": 187,
    "<": 188,
    "-": 189,
    _: 189,
    "~": 192,
    "`": 192,
    "\\": 220,
    '"': 222,
  };
  const lookup = joinDictionaries(commonKeyCodes, usSpecificKeys);
  return lookup[character];
}

function findKeyCodeEnGb(character) {
  const gbSpecificKeys = {
    '"': 50,
    "£": 51,
    "<": 60,
    "+": 61,
    "=": 61,
    "\\": 94,
    "!": 161,
    "~": 163,
    "#": 163,
    "-": 173,
    _: 173,
    "¬": 192,
    "@": 222,
    "`": 223,
    ç: 231,
  };
  const lookup = joinDictionaries(commonKeyCodes, gbSpecificKeys);
  return lookup[character];
}
