import { getNetworkInterfaceDisplayName } from "./network-interface.js";
import { describe, it } from "mocha";
import assert from "assert";

describe("getNetworkInterfaceDisplayName", () => {
  it("returns n/a for null input", () => {
    assert.strictEqual(getNetworkInterfaceDisplayName(null), "n/a");
  });

  it("returns n/a for undefined input", () => {
    assert.strictEqual(getNetworkInterfaceDisplayName(undefined), "n/a");
  });

  it("returns n/a for empty string", () => {
    assert.strictEqual(getNetworkInterfaceDisplayName(""), "n/a");
  });

  it("converts eth0 to LAN1", () => {
    assert.strictEqual(getNetworkInterfaceDisplayName("eth0"), "LAN1");
  });

  it("converts eth1 to LAN2", () => {
    assert.strictEqual(getNetworkInterfaceDisplayName("eth1"), "LAN2");
  });

  it("converts eth2 to LAN3", () => {
    assert.strictEqual(getNetworkInterfaceDisplayName("eth2"), "LAN3");
  });

  it("converts eth10 to LAN11", () => {
    assert.strictEqual(getNetworkInterfaceDisplayName("eth10"), "LAN11");
  });

  it("converts wlan0 to Wi-Fi", () => {
    assert.strictEqual(getNetworkInterfaceDisplayName("wlan0"), "Wi-Fi");
  });

  it("converts wlan1 to Wi-Fi", () => {
    assert.strictEqual(getNetworkInterfaceDisplayName("wlan1"), "Wi-Fi");
  });

  it("converts wlan5 to Wi-Fi", () => {
    assert.strictEqual(getNetworkInterfaceDisplayName("wlan5"), "Wi-Fi");
  });

  it("returns interface name as is for unknown interfaces", () => {
    assert.strictEqual(getNetworkInterfaceDisplayName("lo"), "lo");
  });

  it("returns interface name as is for docker interfaces", () => {
    assert.strictEqual(getNetworkInterfaceDisplayName("docker0"), "docker0");
  });

  it("returns interface name as is for veth interfaces", () => {
    assert.strictEqual(
      getNetworkInterfaceDisplayName("veth1234567"),
      "veth1234567",
    );
  });

  it("returns interface name as is for interfaces starting with eth but not matching pattern", () => {
    assert.strictEqual(getNetworkInterfaceDisplayName("ethernet"), "ethernet");
  });

  it("returns interface name as is for interfaces starting with wlan but not matching pattern", () => {
    assert.strictEqual(getNetworkInterfaceDisplayName("wlan-usb"), "wlan-usb");
  });
});
