/**
 * The initialization of the WebRTC Video stream from the Janus plugin.
 *
 * Import this as `type="module"`, to avoid polluting the global namespace.
 *
 * This file implicitly depends on the following libraries to be present in the
 * global namespace:
 * - Janus Gateway 1.0.0
 * - WebRTC Adapter 8.1.1
 *
 * See here for the Janus Gateway API reference:
 * https://janus.conf.meetecho.com/docs/JS.html
 */

// Parameters for the setup.
const config = {
  // Set to `true` to turn on all internal Janus logging. Make sure to set the
  // log level in your browser to debug/verbose.
  isDebug: false,

  // The hostname of the device. For development, you can replace this with the
  // hostname of your testing device.
  deviceHostname: location.host,

  // Whether the connection should be established with SSL.
  useSSL: location.protocol === "https:",
};

// Initialize library.
Janus.init({
  debug: config.isDebug ? "all" : false,
});

// Establish connection to the server.
const janus = new Janus({
  server: `${config.useSSL ? "wss" : "ws"}://${config.deviceHostname}/janus/ws`,
  success: attachToJanusPlugin,
  error: function (error) {
    console.error("Failed to connect to Janus: " + error);
  },
});

function attachToJanusPlugin() {
  let janusPluginHandle = null;

  janus.attach({
    plugin: "janus.plugin.ustreamer",
    opaqueId: "tinypilot-" + Janus.randomString(8),

    /**
     * This callback is triggered when the ICE state for the PeerConnection
     * associated to the handle changes.
     * ICE = Interactive Connectivity Establishment
     * See https://developer.mozilla.org/en-US/docs/Glossary/ICE
     * @param {string} state E.g., "connected" or "failed".
     */
    iceState: function (state) {
      console.debug("ICE Connection State changed to: " + state);
    },

    /**
     * @param {object} pluginHandle The Janus plugin handle.
     */
    success: function (pluginHandle) {
      janusPluginHandle = pluginHandle;
      console.debug("TinyPilot successfully attached uStreamer plugin");

      // This makes the uStreamer plugin generate a webrtc offer that will be
      // received in the onmessage handler.
      janusPluginHandle.send({ message: { request: "watch" } });
    },

    error: function (error) {
      console.error("Failed to attach to uStreamer plugin: " + error);
    },

    /**
     * @param {object} msg
     * @param {object|null} jsep JSEP = JavaScript Session Establishment Protocol
     */
    onmessage: function (msg, jsep) {
      if (!jsep) {
        return;
      }
      janusPluginHandle.createAnswer({
        jsep: jsep,
        // Client only receives media and does not interact with data channels.
        media: { audioSend: false, videoSend: false, data: false },
        success: function (jsep) {
          // Send back the generated webrtc response.
          janusPluginHandle.send({
            message: { request: "start" },
            jsep: jsep,
          });
        },
        error: function (error) {
          console.error("failed to create answer SDP: " + error);
        },
      });
    },

    /**
     * @param {MediaStreamTrack} track https://developer.mozilla.org/en-US/docs/Web/API/MediaStreamTrack
     * @param {string} mid The Media-ID.
     * @param {boolean} added Whether a track was added or removed.
     */
    onremotetrack: function (track, mid, added) {
      console.debug(`Remote track changed. mid:"${mid}" added:"${added}`);
      const videoElement = document.getElementById("webrtc-output");

      if (!added) {
        videoElement.srcObject = null;
        return;
      }

      // According to the examples/tests in the Janus repository, the track
      // object should be cloned.
      // https://github.com/meetecho/janus-gateway/blob/4110eea4568926dc18642a544718c87118629253/html/streamingtest.js#L249-L250
      const stream = new MediaStream();
      stream.addTrack(track.clone());
      videoElement.srcObject = stream;
    },
  });
}
